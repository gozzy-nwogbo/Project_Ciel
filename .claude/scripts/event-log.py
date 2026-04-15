#!/usr/bin/env python3
"""
System event log: records what the agent DID, not what was said.

Separate from conversation transcripts and daily logs. Writes to
.claude/logs/system-events.jsonl (one JSON object per line).

Importable:
    from importlib.machinery import SourceFileLoader
    el = SourceFileLoader("event_log", "<path>/event-log.py").load_module()
    el.log_event("tool_call", "write", "mcp__open-brain__write",
                 {"table": "people"}, "abc-123")

CLI:
    python3 event-log.py --tail 20
    python3 event-log.py --category tool_call
    python3 event-log.py --session <id>
    python3 event-log.py --since 2026-04-10
    python3 event-log.py --category tool_call --since 2026-04-10
"""

import argparse
import json
import os
import sys
from datetime import datetime

VAULT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LOG_PATH = os.path.join(VAULT_DIR, ".claude", "logs", "system-events.jsonl")

VALID_CATEGORIES = {
    "context_load",
    "tool_call",
    "permission_decision",
    "state_transition",
    "error",
}


# ---------------------------------------------------------------------------
# Write
# ---------------------------------------------------------------------------

def log_event(
    category: str,
    action: str,
    tool: str | None = None,
    details: dict | str | None = None,
    session_id: str | None = None,
) -> dict:
    """Append a single event to the system event log. Returns the event dict."""
    if category not in VALID_CATEGORIES:
        raise ValueError(
            f"Invalid category '{category}'. Must be one of: {', '.join(sorted(VALID_CATEGORIES))}"
        )

    event = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "category": category,
        "action": action,
        "tool": tool,
        "details": details,
        "session_id": session_id,
    }

    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(event, separators=(",", ":")) + "\n")

    return event


# ---------------------------------------------------------------------------
# Read / query
# ---------------------------------------------------------------------------

def _iter_events():
    """Yield all events from the log file."""
    if not os.path.isfile(LOG_PATH):
        return
    with open(LOG_PATH, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def query_events(
    category: str | None = None,
    session_id: str | None = None,
    since: str | None = None,
    tail: int | None = None,
) -> list[dict]:
    """Filter and return events matching criteria."""
    events = list(_iter_events())

    if category:
        events = [e for e in events if e.get("category") == category]
    if session_id:
        events = [e for e in events if e.get("session_id") == session_id]
    if since:
        events = [e for e in events if e.get("timestamp", "") >= since]
    if tail:
        events = events[-tail:]

    return events


def print_events(events: list[dict]):
    """Pretty-print a list of events to stdout."""
    if not events:
        print("No events found.")
        return

    for e in events:
        ts = e.get("timestamp", "?")[:19]
        cat = e.get("category", "?")
        action = e.get("action", "?")
        tool = e.get("tool") or ""
        sid = e.get("session_id") or ""
        details = e.get("details")

        tool_str = f" [{tool}]" if tool else ""
        sid_str = f" (session: {sid[:12]})" if sid else ""
        print(f"  {ts}  {cat:20s}  {action}{tool_str}{sid_str}")

        if details:
            if isinstance(details, dict):
                for k, v in details.items():
                    val = str(v)
                    if len(val) > 100:
                        val = val[:100] + "..."
                    print(f"    {k}: {val}")
            else:
                detail_str = str(details)
                if len(detail_str) > 120:
                    detail_str = detail_str[:120] + "..."
                print(f"    {detail_str}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="System event log query")
    parser.add_argument("--tail", "-t", type=int, help="Show last N events")
    parser.add_argument("--category", "-c", type=str, help="Filter by category")
    parser.add_argument("--session", "-s", type=str, help="Filter by session ID")
    parser.add_argument("--since", type=str, help="Events since date (YYYY-MM-DD)")
    parser.add_argument("--stats", action="store_true", help="Show event counts by category")
    args = parser.parse_args()

    if args.stats:
        events = list(_iter_events())
        counts: dict[str, int] = {}
        for e in events:
            cat = e.get("category", "unknown")
            counts[cat] = counts.get(cat, 0) + 1
        print(f"Total events: {len(events)}")
        for cat in sorted(counts):
            print(f"  {cat}: {counts[cat]}")
        return

    events = query_events(
        category=args.category,
        session_id=args.session,
        since=args.since,
        tail=args.tail,
    )

    count_label = f" (last {args.tail})" if args.tail else ""
    filters = []
    if args.category:
        filters.append(f"category={args.category}")
    if args.session:
        filters.append(f"session={args.session[:12]}")
    if args.since:
        filters.append(f"since={args.since}")
    filter_label = f" [{', '.join(filters)}]" if filters else ""

    print(f"{len(events)} event(s){count_label}{filter_label}\n")
    print_events(events)


if __name__ == "__main__":
    main()
