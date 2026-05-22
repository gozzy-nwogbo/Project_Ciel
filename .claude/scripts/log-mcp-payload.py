#!/usr/bin/env python3
"""PostToolUse hook: logs MCP tool response payload sizes to system-events.jsonl."""

import json
import os
import sys
from importlib.machinery import SourceFileLoader

_event_log = SourceFileLoader(
    "event_log",
    os.path.join(os.path.dirname(__file__), "event-log.py"),
).load_module()


def main():
    raw = sys.stdin.read()
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        print(json.dumps({"result": "continue"}))
        return

    tool_name = data.get("tool_name", "")
    if not tool_name.startswith("mcp__"):
        print(json.dumps({"result": "continue"}))
        return

    result = data.get("tool_response", "")
    if isinstance(result, str):
        text = result
    elif isinstance(result, dict):
        text = result.get("text", json.dumps(result))
    else:
        text = json.dumps(result) if result else ""

    response_bytes = len(text.encode("utf-8"))
    response_tokens_est = round(response_bytes / 4)

    session_id = data.get("session_id")

    _event_log.log_event(
        "tool_call",
        "mcp_tool_call",
        tool_name,
        {"response_bytes": response_bytes, "response_tokens_est": response_tokens_est},
        session_id,
    )

    print(json.dumps({"result": "continue"}))


if __name__ == "__main__":
    main()
