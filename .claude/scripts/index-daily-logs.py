#!/usr/bin/env python3
"""
SQLite FTS5 index for daily logs.

Scans 05-daily/*.md, splits each file into session entries on '---'
separators, and indexes them into a SQLite database with full-text
search. Idempotent via a manifest table that tracks indexed files
by path and mtime.

Usage:
    python3 index-daily-logs.py                        # index all logs
    python3 index-daily-logs.py --search "session hooks"  # search
    python3 index-daily-logs.py --search "MCP" --limit 5  # search with limit
"""

import argparse
import os
import re
import sqlite3
import sys
from datetime import datetime

VAULT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DAILY_DIR = os.path.join(VAULT_DIR, "05-daily")
DB_PATH = os.path.join(VAULT_DIR, ".claude", "logs", "daily-index.db")


# ---------------------------------------------------------------------------
# Database setup
# ---------------------------------------------------------------------------

def get_db() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            session_time TEXT,
            event_type TEXT,
            content TEXT NOT NULL,
            source_file TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS entries_fts
        USING fts5(content, content='entries', content_rowid='id')
    """)
    # Triggers to keep FTS in sync with the entries table
    conn.executescript("""
        CREATE TRIGGER IF NOT EXISTS entries_ai AFTER INSERT ON entries BEGIN
            INSERT INTO entries_fts(rowid, content) VALUES (new.id, new.content);
        END;
        CREATE TRIGGER IF NOT EXISTS entries_ad AFTER DELETE ON entries BEGIN
            INSERT INTO entries_fts(entries_fts, rowid, content) VALUES ('delete', old.id, old.content);
        END;
        CREATE TRIGGER IF NOT EXISTS entries_au AFTER UPDATE ON entries BEGIN
            INSERT INTO entries_fts(entries_fts, rowid, content) VALUES ('delete', old.id, old.content);
            INSERT INTO entries_fts(rowid, content) VALUES (new.id, new.content);
        END;
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS manifest (
            source_file TEXT PRIMARY KEY,
            mtime REAL NOT NULL,
            indexed_at TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

HEADER_RE = re.compile(
    r"^###\s+Session\s+Log\s+\((\d{1,2}:\d{2}),\s*(.+?)\)\s*$",
    re.MULTILINE,
)


def parse_daily_log(filepath: str) -> list[dict]:
    """Split a daily log into session entries."""
    with open(filepath, "r") as f:
        text = f.read()

    basename = os.path.basename(filepath)
    date_str = basename.replace(".md", "")

    # Strip frontmatter
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            text = text[end + 5:]

    # Split on --- separators into raw blocks
    blocks = re.split(r"\n---\n", text)

    entries = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue

        # Try to parse session header
        m = HEADER_RE.search(block)
        session_time = m.group(1) if m else None
        event_type = m.group(2) if m else None

        # The content is everything after the header line (or the whole block)
        if m:
            content = block[m.end():].strip()
        else:
            # Skip the top-level "# Daily Log: ..." header if that's all it is
            if re.match(r"^#\s+Daily Log:", block) and block.count("\n") < 2:
                continue
            content = block

        if not content or len(content) < 20:
            continue

        entries.append({
            "date": date_str,
            "session_time": session_time,
            "event_type": event_type,
            "content": content,
            "source_file": basename,
        })

    return entries


# ---------------------------------------------------------------------------
# Indexing
# ---------------------------------------------------------------------------

def index_all(conn: sqlite3.Connection) -> int:
    """Scan 05-daily/ and index new or modified files. Returns count indexed."""
    if not os.path.isdir(DAILY_DIR):
        print(f"Daily directory not found: {DAILY_DIR}")
        return 0

    files = sorted(
        f for f in os.listdir(DAILY_DIR) if f.endswith(".md")
    )

    indexed = 0
    for fname in files:
        filepath = os.path.join(DAILY_DIR, fname)
        mtime = os.path.getmtime(filepath)

        # Check manifest
        row = conn.execute(
            "SELECT mtime FROM manifest WHERE source_file = ?", (fname,)
        ).fetchone()

        if row and row[0] == mtime:
            continue  # already indexed at this mtime

        # Re-index: delete old entries for this file, then insert fresh
        conn.execute("DELETE FROM entries WHERE source_file = ?", (fname,))

        entries = parse_daily_log(filepath)
        for entry in entries:
            conn.execute(
                "INSERT INTO entries (date, session_time, event_type, content, source_file) "
                "VALUES (?, ?, ?, ?, ?)",
                (entry["date"], entry["session_time"], entry["event_type"],
                 entry["content"], entry["source_file"]),
            )

        # Update manifest
        conn.execute(
            "INSERT OR REPLACE INTO manifest (source_file, mtime, indexed_at) VALUES (?, ?, ?)",
            (fname, mtime, datetime.now().isoformat()),
        )
        conn.commit()
        indexed += 1
        print(f"  Indexed {fname}: {len(entries)} entries")

    return indexed


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

def search_daily_logs(
    query: str, limit: int = 10, conn: sqlite3.Connection | None = None
) -> list[dict]:
    """Full-text search over daily log entries, ranked by relevance."""
    close_after = False
    if conn is None:
        conn = get_db()
        close_after = True

    rows = conn.execute(
        """
        SELECT e.id, e.date, e.session_time, e.event_type,
               snippet(entries_fts, 0, '>>>', '<<<', '...', 40) AS snippet,
               e.source_file, rank
        FROM entries_fts
        JOIN entries e ON e.id = entries_fts.rowid
        WHERE entries_fts MATCH ?
        ORDER BY rank
        LIMIT ?
        """,
        (query, limit),
    ).fetchall()

    if close_after:
        conn.close()

    return [
        {
            "id": r[0],
            "date": r[1],
            "session_time": r[2],
            "event_type": r[3],
            "snippet": r[4],
            "source_file": r[5],
            "rank": r[6],
        }
        for r in rows
    ]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Daily log FTS5 index")
    parser.add_argument("--search", "-s", type=str, help="Search query")
    parser.add_argument("--limit", "-n", type=int, default=10, help="Max results (default: 10)")
    args = parser.parse_args()

    conn = get_db()

    if args.search:
        results = search_daily_logs(args.search, limit=args.limit, conn=conn)
        if not results:
            print(f"No results for: {args.search}")
        else:
            print(f"Found {len(results)} result(s) for: {args.search}\n")
            for r in results:
                time_str = r["session_time"] or "??"
                event_str = r["event_type"] or "unknown"
                print(f"  [{r['date']} {time_str}] ({event_str}) {r['source_file']}")
                print(f"    {r['snippet']}")
                print()
    else:
        print("Indexing daily logs...")
        count = index_all(conn)
        total = conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
        files = conn.execute("SELECT COUNT(*) FROM manifest").fetchone()[0]
        print(f"\nDone. {count} file(s) indexed this run. Total: {total} entries across {files} files.")

    conn.close()


if __name__ == "__main__":
    main()
