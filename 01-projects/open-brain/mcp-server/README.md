# Open Brain MCP Server

MCP server exposing semantic search, recent entries, stats, and write tools across the Open Brain Supabase database.

## Prerequisites

```bash
pip install fastmcp openai supabase
```

## Environment Variables

Set these before running the server:

| Variable | Description |
|---|---|
| `SUPABASE_URL` | Supabase project URL (e.g., `https://xxx.supabase.co`) |
| `SUPABASE_SERVICE_KEY` | Service role key (bypasses RLS) |
| `OPENAI_API_KEY` | OpenAI API key for text-embedding-3-small |

Load from the vault `.env`:

```bash
export $(grep -v '^#' ~/second-brain/.env | xargs)
```

## Database Setup

Run the migrations in order against your Supabase SQL Editor:

1. `architecture/schemas/migrations/001_initial_schema.sql` (tables, triggers, RLS)
2. `architecture/schemas/migrations/002_indexes.sql` (HNSW vector indexes)
3. `architecture/schemas/migrations/003_match_documents_rpc.sql` (semantic search RPC)

## Running

```bash
# Standalone (stdio transport, for Claude Code)
python server.py

# Or with fastmcp CLI
fastmcp run server.py
```

## Connecting to Claude Code

Add to `.claude/settings.json`:

```json
{
  "mcpServers": {
    "open-brain": {
      "command": "python",
      "args": ["/path/to/second-brain/01-projects/open-brain/mcp-server/server.py"],
      "env": {
        "SUPABASE_URL": "${SUPABASE_URL}",
        "SUPABASE_SERVICE_KEY": "${SUPABASE_SERVICE_KEY}",
        "OPENAI_API_KEY": "${OPENAI_API_KEY}"
      }
    }
  }
}
```

## Tools

### semantic_search (read-only)
Search across all tables by meaning using pgvector cosine similarity.
- `query` (string, required): Natural language search query
- `tables` (list, optional): Tables to search. Default: all four
- `limit` (int, optional): Max results per table. Default: 10
- `min_similarity` (float, optional): Cosine similarity threshold. Default: 0.7

### list_recent (read-only)
Return recent entries from a specified table.
- `table` (string, required): captures, people, projects, or ideas
- `limit` (int, optional): Records to return. Default: 20
- `offset` (int, optional): Records to skip. Default: 0

### stats (read-only)
Return counts, last updated, and embedding coverage per table. No parameters.

### write (mutating)
Insert or upsert a record. Generates embedding automatically.
- `table` (string, required): Target table
- `data` (object, required): Record fields
- `confirm` (boolean, required for execution): Must be `true` to execute. Without it, returns a preview.

Every write is logged to `.claude/logs/mcp-writes.log`.

### get_tool_registry (read-only)
Returns metadata for all tools without executing them (Primitive 1).

## Write Log

All mutating operations are logged as JSONL to:
```
~/second-brain/.claude/logs/mcp-writes.log
```

Each entry: `{"timestamp": "...", "table": "...", "operation": "insert|upsert", "record_id": "..."}`
