#!/usr/bin/env python3
"""
Open Brain MCP Server

Exposes four tools over the Model Context Protocol:
  - semantic_search: cosine similarity search across all tables via pgvector
  - list_recent: paginated recent entries from any table
  - stats: counts, last updated, and embedding coverage per table
  - write: insert/upsert records with embedding generation and write logging

Requires environment variables:
  SUPABASE_URL          — Supabase project URL
  SUPABASE_SERVICE_KEY  — Service role key (bypasses RLS)
  OPENAI_API_KEY        — For text-embedding-3-small embeddings
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

VALID_TABLES = ["captures", "people", "projects", "ideas"]

VAULT_DIR = Path(__file__).resolve().parent.parent.parent
WRITE_LOG = VAULT_DIR / ".claude" / "logs" / "mcp-writes.log"

# Embedding text templates per table (from database-schemas.md section 6)
EMBEDDING_TEXT_TEMPLATES = {
    "captures": lambda r: r.get("original_text", ""),
    "people": lambda r: " ".join(filter(None, [
        r.get("name", ""),
        r.get("context", ""),
        r.get("notes", ""),
    ])),
    "projects": lambda r: " ".join(filter(None, [
        r.get("name", ""),
        r.get("description", ""),
        r.get("notes", ""),
    ])),
    "ideas": lambda r: " ".join(filter(None, [
        r.get("title", ""),
        r.get("body", ""),
    ])),
}

# Columns to return per table (exclude embedding vector from results)
DISPLAY_COLUMNS = {
    "captures": "id, created_at, updated_at, source, original_text, destination, confidence, status, topics, entities, action_items, processed_at",
    "people": "id, created_at, updated_at, name, context, company, role, email, last_contact, contact_method, health_score, importance, notes, topics, next_action, next_action_due",
    "projects": "id, created_at, updated_at, name, description, status, category, next_action, next_action_due, last_activity, related_people, vault_path, notes, topics",
    "ideas": "id, created_at, updated_at, title, body, status, source, source_capture_id, related_projects, related_ideas, topics, priority",
}

# ---------------------------------------------------------------------------
# Clients (lazy-initialized)
# ---------------------------------------------------------------------------

_supabase_client = None
_openai_client = None


def get_supabase():
    global _supabase_client
    if _supabase_client is None:
        from supabase import create_client
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_KEY")
        if not url or not key:
            raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
        _supabase_client = create_client(url, key)
    return _supabase_client


def get_openai():
    global _openai_client
    if _openai_client is None:
        import openai
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY must be set")
        _openai_client = openai.OpenAI(api_key=api_key)
    return _openai_client


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def generate_embedding(text: str) -> list[float]:
    """Generate embedding vector using OpenAI text-embedding-3-small."""
    client = get_openai()
    text = text.strip()
    if not text:
        return []
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return response.data[0].embedding


def log_write(table: str, operation: str, record_id: str | None = None):
    """Log mutating operations to mcp-writes.log."""
    WRITE_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "table": table,
        "operation": operation,
        "record_id": record_id,
    }
    with open(WRITE_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")


def validate_table(table: str):
    """Raise if table name is not in the allowed list."""
    if table not in VALID_TABLES:
        raise ValueError(f"Invalid table: {table}. Must be one of: {VALID_TABLES}")


# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------

mcp = FastMCP(
    "Open Brain",
    instructions="Personal second brain MCP server. Semantic search, recent entries, stats, and writes across captures, people, projects, and ideas.",
)


@mcp.tool()
def semantic_search(
    query: str,
    tables: list[str] | None = None,
    limit: int = 10,
    min_similarity: float = 0.7,
) -> dict[str, Any]:
    """Search across all four tables by meaning using pgvector cosine similarity.

    Args:
        query: Natural language search query.
        tables: Tables to search. Default: all four (captures, people, projects, ideas).
        limit: Max results per table. Default: 10.
        min_similarity: Minimum cosine similarity threshold (0-1). Default: 0.7.

    Returns:
        Dict with results per table, each entry includes similarity score.
    """
    if tables is None:
        tables = VALID_TABLES
    for t in tables:
        validate_table(t)

    query_embedding = generate_embedding(query)
    if not query_embedding:
        return {"error": "Empty query, cannot generate embedding"}

    db = get_supabase()
    results = {}

    for table in tables:
        # Use Supabase RPC to run cosine similarity query
        # We call a raw SQL query via postgrest
        response = db.rpc("match_documents", {
            "query_embedding": query_embedding,
            "match_table": table,
            "match_limit": limit,
            "match_threshold": min_similarity,
        }).execute()

        if response.data:
            results[table] = response.data
        else:
            results[table] = []

    # Flatten and sort cross-table by similarity
    all_results = []
    for table, rows in results.items():
        for row in rows:
            row["_table"] = table
            all_results.append(row)

    all_results.sort(key=lambda r: r.get("similarity", 0), reverse=True)

    return {
        "query": query,
        "min_similarity": min_similarity,
        "total_results": len(all_results),
        "results": all_results[:limit],
    }


@mcp.tool()
def list_recent(
    table: str,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    """Return recent entries from a specified table, ordered by creation date.

    Args:
        table: Table to query (captures, people, projects, ideas).
        limit: Number of records to return. Default: 20.
        offset: Number of records to skip. Default: 0.

    Returns:
        Dict with table name, count, and list of records.
    """
    validate_table(table)
    db = get_supabase()

    columns = DISPLAY_COLUMNS[table]
    response = (
        db.table(table)
        .select(columns)
        .is_("deleted_at", "null")
        .order("created_at", desc=True)
        .range(offset, offset + limit - 1)
        .execute()
    )

    return {
        "table": table,
        "count": len(response.data),
        "offset": offset,
        "records": response.data,
    }


@mcp.tool()
def stats() -> dict[str, Any]:
    """Return counts, last updated timestamp, and embedding coverage for each table.

    Returns:
        Dict with per-table statistics.
    """
    db = get_supabase()
    table_stats = {}

    for table in VALID_TABLES:
        # Total active count
        total_resp = (
            db.table(table)
            .select("id", count="exact")
            .is_("deleted_at", "null")
            .execute()
        )
        total = total_resp.count or 0

        # Count with embeddings
        embedded_resp = (
            db.table(table)
            .select("id", count="exact")
            .is_("deleted_at", "null")
            .not_.is_("embedding", "null")
            .execute()
        )
        embedded = embedded_resp.count or 0

        # Most recent record
        latest_resp = (
            db.table(table)
            .select("updated_at")
            .is_("deleted_at", "null")
            .order("updated_at", desc=True)
            .limit(1)
            .execute()
        )
        last_updated = None
        if latest_resp.data:
            last_updated = latest_resp.data[0]["updated_at"]

        table_stats[table] = {
            "total": total,
            "with_embedding": embedded,
            "embedding_coverage": f"{(embedded / total * 100):.0f}%" if total > 0 else "N/A",
            "last_updated": last_updated,
        }

    return {"tables": table_stats}


@mcp.tool()
def write(
    table: str,
    data: dict[str, Any] | str,
    confirm: bool = False,
) -> dict[str, Any]:
    """Insert or upsert a record into a specified table. MUTATING operation.

    This tool generates an embedding automatically and logs every call.
    You MUST set confirm=True to execute the write. Without confirmation,
    this tool returns a preview of what would be written.

    Args:
        table: Target table (captures, people, projects, ideas).
        data: Record fields as key-value pairs. Do not include id, created_at,
              updated_at, deleted_at, or embedding (these are managed automatically).
        confirm: Must be True to execute the write. Default: False (preview only).

    Returns:
        Preview of the write (if confirm=False) or the written record (if confirm=True).
    """
    validate_table(table)

    # FastMCP bridge may serialize dict as JSON string
    if isinstance(data, str):
        data = json.loads(data)

    # Strip managed fields
    managed_fields = {"id", "created_at", "updated_at", "deleted_at", "embedding"}
    clean_data = {k: v for k, v in data.items() if k not in managed_fields}

    if not clean_data:
        return {"error": "No writable fields provided"}

    # Check for upsert (if id is provided separately)
    record_id = data.get("id")
    operation = "upsert" if record_id else "insert"

    # Generate embedding text
    embed_fn = EMBEDDING_TEXT_TEMPLATES.get(table)
    embed_text = embed_fn(clean_data) if embed_fn else ""

    if not confirm:
        return {
            "preview": True,
            "table": table,
            "operation": operation,
            "data": clean_data,
            "embedding_source_text": embed_text[:200] + ("..." if len(embed_text) > 200 else ""),
            "message": "Set confirm=True to execute this write.",
        }

    # Generate embedding
    if embed_text:
        embedding = generate_embedding(embed_text)
        if embedding:
            clean_data["embedding"] = embedding

    db = get_supabase()

    if record_id:
        # Upsert: update existing record
        response = (
            db.table(table)
            .update(clean_data)
            .eq("id", record_id)
            .execute()
        )
        log_write(table, "upsert", record_id)
    else:
        # Insert new record
        response = db.table(table).insert(clean_data).execute()
        if response.data:
            record_id = response.data[0].get("id")
        log_write(table, "insert", record_id)

    # Return without embedding vector (too large for display)
    result = response.data[0] if response.data else {}
    result.pop("embedding", None)

    return {
        "success": True,
        "table": table,
        "operation": operation,
        "record": result,
    }


# ---------------------------------------------------------------------------
# list_tools (Primitive 1: Tool Registry)
# ---------------------------------------------------------------------------

def list_tools() -> list[dict[str, Any]]:
    """Return metadata for all MCP tools without executing them.

    This satisfies Primitive 1 (Tool Registry) from the PRD.
    """
    return [
        {
            "name": "semantic_search",
            "description": "Search across tables by meaning using pgvector cosine similarity",
            "permission_tier": "read-only",
            "parameters": {
                "query": {"type": "string", "required": True},
                "tables": {"type": "list[string]", "required": False, "default": "all"},
                "limit": {"type": "integer", "required": False, "default": 10},
                "min_similarity": {"type": "float", "required": False, "default": 0.7},
            },
        },
        {
            "name": "list_recent",
            "description": "Return recent entries from a specified table",
            "permission_tier": "read-only",
            "parameters": {
                "table": {"type": "string", "required": True},
                "limit": {"type": "integer", "required": False, "default": 20},
                "offset": {"type": "integer", "required": False, "default": 0},
            },
        },
        {
            "name": "stats",
            "description": "Return counts, last updated, and embedding coverage per table",
            "permission_tier": "read-only",
            "parameters": {},
        },
        {
            "name": "write",
            "description": "Insert or upsert a record into a specified table. MUTATING.",
            "permission_tier": "mutating",
            "parameters": {
                "table": {"type": "string", "required": True},
                "data": {"type": "object", "required": True},
                "confirm": {"type": "boolean", "required": False, "default": False},
            },
        },
    ]


# Also expose list_tools as an MCP tool itself
@mcp.tool()
def get_tool_registry() -> list[dict[str, Any]]:
    """Return metadata for all available MCP tools without executing them.
    Use this to discover capabilities before calling any tool."""
    return list_tools()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
