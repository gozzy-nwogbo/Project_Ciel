#!/usr/bin/env python3
"""
Flush process: extracts concepts and connections from daily logs
and raw inbox files, writes them to 02-knowledge/, and updates index.md.

Two-pass processing:
  1. Daily logs in 06-daily/ (extracted, marked with frontmatter flag)
  2. Raw inbox files in 00-inbox/raw/ (extracted, marked, moved to 00-inbox/staging/)

Idempotent: marks processed files with a frontmatter flag so they
are not re-processed on subsequent runs.

Can run standalone or be spawned as a background process.

Usage:
    python flush.py              # process all unprocessed files
    python flush.py --background <payload.json>  # internal: background worker
"""

import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime
from importlib.machinery import SourceFileLoader

VAULT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DAILY_DIR = os.path.join(VAULT_DIR, "06-daily")
INBOX_RAW = os.path.join(VAULT_DIR, "00-inbox", "raw")
INBOX_STAGING = os.path.join(VAULT_DIR, "00-inbox", "staging")

_event_log = SourceFileLoader(
    "event_log", os.path.join(os.path.dirname(__file__), "event-log.py")
).load_module()
KNOWLEDGE_DIR = os.path.join(VAULT_DIR, "02-knowledge")
CONCEPTS_DIR = os.path.join(KNOWLEDGE_DIR, "concepts")
CONNECTIONS_DIR = os.path.join(KNOWLEDGE_DIR, "connections")
INDEX_PATH = os.path.join(KNOWLEDGE_DIR, "index.md")
LOG_FILE = os.path.join(VAULT_DIR, ".claude", "logs", "flush-debug.log")

PROCESSED_MARKER = "flush_processed: true"


def log_debug(msg: str):
    """Append debug info to flush log file."""
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(f"[{datetime.now().isoformat()}] {msg}\n")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Detect unprocessed daily logs
# ---------------------------------------------------------------------------

def is_processed(filepath: str) -> bool:
    """Check if a daily log has already been flushed."""
    try:
        with open(filepath, "r") as f:
            # Check first 10 lines for frontmatter marker
            for i, line in enumerate(f):
                if i > 10:
                    break
                if PROCESSED_MARKER in line:
                    return True
    except Exception:
        pass
    return False


def mark_processed(filepath: str):
    """Add frontmatter marker to a daily log so it is not re-processed."""
    try:
        with open(filepath, "r") as f:
            content = f.read()

        # If file already has frontmatter, insert marker into it
        if content.startswith("---\n"):
            end = content.find("\n---\n", 4)
            if end != -1:
                frontmatter = content[4:end]
                rest = content[end + 4:]
                content = f"---\n{frontmatter}\n{PROCESSED_MARKER}\n---\n{rest}"
            else:
                content = f"---\n{PROCESSED_MARKER}\n---\n{content}"
        else:
            content = f"---\n{PROCESSED_MARKER}\n---\n{content}"

        with open(filepath, "w") as f:
            f.write(content)
    except Exception as e:
        log_debug(f"Failed to mark {filepath} as processed: {e}")


def get_unprocessed_logs() -> list[str]:
    """Return list of daily log paths that have not been flushed."""
    if not os.path.isdir(DAILY_DIR):
        return []

    logs = []
    for fname in sorted(os.listdir(DAILY_DIR)):
        if not fname.endswith(".md"):
            continue
        path = os.path.join(DAILY_DIR, fname)
        if not is_processed(path):
            # Skip files with no real content (just headers, no substance)
            with open(path, "r") as f:
                text = f.read()
            # Strip frontmatter, headers, and whitespace
            clean = re.sub(r"^---.*?---\s*", "", text, flags=re.DOTALL)
            clean = re.sub(r"^#.*$", "", clean, flags=re.MULTILINE).strip()
            if len(clean) < 50:
                log_debug(f"Skipping {fname}: too little content ({len(clean)} chars)")
                continue
            logs.append(path)

    return logs


# ---------------------------------------------------------------------------
# API extraction
# ---------------------------------------------------------------------------

def extract_with_api(daily_content: str, date_str: str) -> dict:
    """Call Anthropic API (Haiku) to extract concepts and connections."""
    try:
        import anthropic
    except ImportError:
        log_debug("anthropic SDK not installed")
        return {}

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        log_debug("ANTHROPIC_API_KEY not set")
        return {}

    client = anthropic.Anthropic(api_key=api_key)

    max_chars = 15000
    if len(daily_content) > max_chars:
        daily_content = daily_content[:max_chars] + "\n\n[...truncated...]"

    prompt = f"""You are a knowledge extraction agent for a personal second brain vault.

Given this daily log from {date_str}, extract:

1. **Concepts**: Distinct ideas, techniques, tools, or patterns worth remembering as standalone knowledge entries. Each concept should be independently useful outside the context of this specific day.

2. **Connections**: Relationships between concepts, or between a concept and a project/decision. Connections describe how two things relate, not the things themselves.

Rules:
- Only extract concepts that have durable value (not ephemeral task status)
- Each concept needs a clear, specific title (not generic like "debugging")
- Each connection must name exactly two endpoints and describe the relationship
- No em-dashes. Active voice. Concise.
- If the daily log has no extractable concepts or connections, return empty arrays

Return valid JSON only, no markdown fencing:
{{
  "concepts": [
    {{
      "title": "slug-friendly-title",
      "name": "Human Readable Name",
      "summary": "2-3 sentence description of the concept",
      "source_date": "{date_str}",
      "tags": ["tag1", "tag2"]
    }}
  ],
  "connections": [
    {{
      "title": "slug-friendly-title",
      "from": "concept or project name",
      "to": "concept or project name",
      "relationship": "1 sentence describing how they connect",
      "source_date": "{date_str}"
    }}
  ]
}}

Daily log:
{daily_content}"""

    try:
        log_debug(f"Calling Anthropic API for {date_str} (prompt: {len(prompt)} chars)")
        _event_log.log_event(
            "tool_call", "anthropic_api_call",
            "claude-haiku-4-5-20251001", {"purpose": "flush_extraction", "date": date_str, "prompt_chars": len(prompt)},
        )
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.content[0].text
        log_debug(f"API response for {date_str}: {len(text)} chars")

        # Parse JSON, handling possible markdown fencing
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)

        return json.loads(text)
    except json.JSONDecodeError as e:
        log_debug(f"Failed to parse API response as JSON for {date_str}: {e}")
        log_debug(f"Raw response: {text[:500]}")
        return {}
    except Exception as e:
        log_debug(f"API call failed for {date_str}: {e}")
        return {}


# ---------------------------------------------------------------------------
# Write knowledge files
# ---------------------------------------------------------------------------

def write_concept(concept: dict):
    """Write a single concept as a markdown file in 02-knowledge/concepts/."""
    os.makedirs(CONCEPTS_DIR, exist_ok=True)

    title = concept.get("title", "untitled")
    # Sanitize filename
    slug = re.sub(r"[^a-z0-9-]", "", title.lower().replace(" ", "-"))
    if not slug:
        slug = f"concept-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    filepath = os.path.join(CONCEPTS_DIR, f"{slug}.md")

    # Do not overwrite existing concepts (idempotent)
    if os.path.exists(filepath):
        log_debug(f"Concept already exists, skipping: {slug}")
        return slug

    tags = concept.get("tags", [])
    tags_str = ", ".join(tags) if tags else ""

    content = f"""---
title: {concept.get('name', title)}
type: concept
source_date: {concept.get('source_date', 'unknown')}
tags: [{tags_str}]
---

{concept.get('summary', '')}
"""

    with open(filepath, "w") as f:
        f.write(content)

    log_debug(f"Wrote concept: {slug}")
    return slug


def write_connection(connection: dict):
    """Write a single connection as a markdown file in 02-knowledge/connections/."""
    os.makedirs(CONNECTIONS_DIR, exist_ok=True)

    title = connection.get("title", "untitled")
    slug = re.sub(r"[^a-z0-9-]", "", title.lower().replace(" ", "-"))
    if not slug:
        slug = f"connection-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    filepath = os.path.join(CONNECTIONS_DIR, f"{slug}.md")

    # Do not overwrite existing connections (idempotent)
    if os.path.exists(filepath):
        log_debug(f"Connection already exists, skipping: {slug}")
        return slug

    content = f"""---
title: {title}
type: connection
from: {connection.get('from', 'unknown')}
to: {connection.get('to', 'unknown')}
source_date: {connection.get('source_date', 'unknown')}
---

**{connection.get('from', '?')}** -> **{connection.get('to', '?')}**

{connection.get('relationship', '')}
"""

    with open(filepath, "w") as f:
        f.write(content)

    log_debug(f"Wrote connection: {slug}")
    return slug


# ---------------------------------------------------------------------------
# Update index.md
# ---------------------------------------------------------------------------

def rebuild_index():
    """Rebuild 02-knowledge/index.md from all current knowledge files."""
    sections = {}

    # Scan all subdirectories of 02-knowledge/
    for entry in sorted(os.listdir(KNOWLEDGE_DIR)):
        entry_path = os.path.join(KNOWLEDGE_DIR, entry)
        if entry == "index.md":
            continue
        if os.path.isdir(entry_path):
            files = []
            for fname in sorted(os.listdir(entry_path)):
                if fname.endswith(".md"):
                    fpath = os.path.join(entry_path, fname)
                    # Read title from frontmatter
                    title = fname.replace(".md", "").replace("-", " ").title()
                    try:
                        with open(fpath, "r") as f:
                            for line in f:
                                if line.startswith("title:"):
                                    title = line.split(":", 1)[1].strip()
                                    break
                                if line.strip() == "---" and title != fname.replace(".md", "").replace("-", " ").title():
                                    break
                    except Exception:
                        pass
                    rel_path = f"{entry}/{fname}"
                    files.append((title, rel_path))
            if files:
                sections[entry] = files

    # Build index content
    lines = ["# Knowledge Index", ""]
    lines.append(f"*Auto-generated by flush process. Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    lines.append("")

    if not sections:
        lines.append("No knowledge files yet.")
    else:
        for section_name in sorted(sections.keys()):
            display_name = section_name.replace("-", " ").title()
            lines.append(f"## {display_name}")
            lines.append("")
            for title, rel_path in sections[section_name]:
                lines.append(f"- [{title}]({rel_path})")
            lines.append("")

    with open(INDEX_PATH, "w") as f:
        f.write("\n".join(lines))

    log_debug(f"Rebuilt index.md with {sum(len(v) for v in sections.values())} entries across {len(sections)} sections")


# ---------------------------------------------------------------------------
# Raw inbox processing
# ---------------------------------------------------------------------------

def _extract_date_from_frontmatter(filepath: str) -> str | None:
    """Try to read a date from frontmatter fields: created, published, date."""
    try:
        with open(filepath, "r") as f:
            first = f.readline().strip()
            if first != "---":
                return None
            for line in f:
                line = line.strip()
                if line == "---":
                    break
                for field in ("created:", "published:", "date:"):
                    if line.lower().startswith(field):
                        val = line.split(":", 1)[1].strip().strip('"').strip("'")
                        # Take just the date portion (YYYY-MM-DD)
                        if val and len(val) >= 10:
                            return val[:10]
                        elif val:
                            return val
    except Exception:
        pass
    return None


def get_unprocessed_raw() -> list[str]:
    """Return list of .md files in 00-inbox/raw/ not yet flushed."""
    if not os.path.isdir(INBOX_RAW):
        return []

    files = []
    for fname in sorted(os.listdir(INBOX_RAW)):
        if not fname.endswith(".md"):
            continue
        path = os.path.join(INBOX_RAW, fname)
        if not is_processed(path):
            # Skip very small files
            try:
                with open(path, "r") as f:
                    text = f.read()
                clean = re.sub(r"^---.*?---\s*", "", text, flags=re.DOTALL)
                clean = re.sub(r"^#.*$", "", clean, flags=re.MULTILINE).strip()
                if len(clean) < 50:
                    log_debug(f"Skipping raw file {fname}: too little content ({len(clean)} chars)")
                    continue
            except Exception:
                continue
            files.append(path)

    return files


def flush_raw_inbox() -> tuple[int, int, int]:
    """Process unprocessed files in 00-inbox/raw/. Returns (files, concepts, connections)."""
    unprocessed = get_unprocessed_raw()

    if not unprocessed:
        log_debug("No unprocessed raw inbox files found")
        return 0, 0, 0

    log_debug(f"Found {len(unprocessed)} unprocessed raw inbox file(s)")
    os.makedirs(INBOX_STAGING, exist_ok=True)
    total_concepts = 0
    total_connections = 0

    for raw_path in unprocessed:
        fname = os.path.basename(raw_path)

        # Determine date_str from frontmatter or file mtime
        date_str = _extract_date_from_frontmatter(raw_path)
        if not date_str:
            mtime = os.path.getmtime(raw_path)
            date_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")

        with open(raw_path, "r") as f:
            content = f.read()

        log_debug(f"Processing raw file {fname} ({len(content)} chars, date={date_str})")

        extracted = extract_with_api(content, date_str)

        if not extracted:
            log_debug(f"No extraction results for raw file {fname}, marking as processed anyway")
            mark_processed(raw_path)
            _move_to_staging(raw_path)
            continue

        concepts = extracted.get("concepts", [])
        connections = extracted.get("connections", [])

        for concept in concepts:
            write_concept(concept)
            total_concepts += 1

        for connection in connections:
            write_connection(connection)
            total_connections += 1

        mark_processed(raw_path)
        _move_to_staging(raw_path)
        log_debug(f"Flushed raw file {fname}: {len(concepts)} concepts, {len(connections)} connections")

    return len(unprocessed), total_concepts, total_connections


def _move_to_staging(raw_path: str):
    """Move a processed raw file to 00-inbox/staging/."""
    os.makedirs(INBOX_STAGING, exist_ok=True)
    fname = os.path.basename(raw_path)
    dest = os.path.join(INBOX_STAGING, fname)
    # Avoid overwriting: append a counter if name collision
    if os.path.exists(dest):
        base, ext = os.path.splitext(fname)
        counter = 1
        while os.path.exists(dest):
            dest = os.path.join(INBOX_STAGING, f"{base}-{counter}{ext}")
            counter += 1
    try:
        os.rename(raw_path, dest)
        log_debug(f"Moved {fname} to staging: {dest}")
    except Exception as e:
        log_debug(f"Failed to move {fname} to staging: {e}")


# ---------------------------------------------------------------------------
# Main flush logic
# ---------------------------------------------------------------------------

def flush_daily_logs():
    """Process all unprocessed daily logs and raw inbox files: extract, write, index, mark."""
    # --- Pass 1: Daily logs ---
    unprocessed = get_unprocessed_logs()
    daily_count = 0
    total_concepts = 0
    total_connections = 0

    if unprocessed:
        log_debug(f"Found {len(unprocessed)} unprocessed daily log(s)")

        for log_path in unprocessed:
            fname = os.path.basename(log_path)
            date_str = fname.replace(".md", "")

            with open(log_path, "r") as f:
                content = f.read()

            log_debug(f"Processing {fname} ({len(content)} chars)")

            extracted = extract_with_api(content, date_str)

            if not extracted:
                log_debug(f"No extraction results for {fname}, marking as processed anyway")
                mark_processed(log_path)
                continue

            concepts = extracted.get("concepts", [])
            connections = extracted.get("connections", [])

            for concept in concepts:
                write_concept(concept)
                total_concepts += 1

            for connection in connections:
                write_connection(connection)
                total_connections += 1

            mark_processed(log_path)
            log_debug(f"Flushed {fname}: {len(concepts)} concepts, {len(connections)} connections")

        daily_count = len(unprocessed)
    else:
        log_debug("No unprocessed daily logs found")

    # --- Pass 2: Raw inbox ---
    raw_count, raw_concepts, raw_connections = flush_raw_inbox()
    total_concepts += raw_concepts
    total_connections += raw_connections

    # --- Rebuild index if anything was processed ---
    if daily_count > 0 or raw_count > 0:
        rebuild_index()

    # --- Summary ---
    parts = []
    if daily_count > 0:
        parts.append(f"{daily_count} daily log(s)")
    if raw_count > 0:
        parts.append(f"{raw_count} raw inbox file(s)")
    if not parts:
        print("No unprocessed files to flush.")
        return

    source_str = ", ".join(parts)
    summary = f"Flush complete: {source_str} processed, {total_concepts} concept(s), {total_connections} connection(s)"
    log_debug(summary)
    _event_log.log_event(
        "state_transition", "flush_complete",
        "flush.py", {
            "daily_logs": daily_count, "raw_files": raw_count,
            "concepts": total_concepts, "connections": total_connections,
        },
    )
    print(summary)


# ---------------------------------------------------------------------------
# Background worker entry point
# ---------------------------------------------------------------------------

def run_background(payload_path: str):
    """Entry point for detached background process."""
    try:
        with open(payload_path, "r") as f:
            payload = json.load(f)
    except Exception as e:
        log_debug(f"[bg] Failed to read payload {payload_path}: {e}")
        return
    finally:
        try:
            os.unlink(payload_path)
        except OSError:
            pass

    log_debug("[bg] Background flush worker started")
    flush_daily_logs()
    log_debug("[bg] Background flush worker finished")


def spawn_background():
    """Spawn flush as a detached background process and return immediately."""
    payload = {"spawned_at": datetime.now().isoformat()}

    fd, payload_path = tempfile.mkstemp(prefix="flush-", suffix=".json")
    with os.fdopen(fd, "w") as f:
        json.dump(payload, f)

    subprocess.Popen(
        [sys.executable, __file__, "--background", payload_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        start_new_session=True,
        env={**os.environ},
    )
    log_debug(f"Spawned background flush worker: {payload_path}")
    print("Flush spawned in background.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "--background":
        run_background(sys.argv[2])
    elif len(sys.argv) >= 2 and sys.argv[1] == "--detach":
        spawn_background()
    else:
        # Default: run synchronously (useful for testing and manual runs)
        flush_daily_logs()
