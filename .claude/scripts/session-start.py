#!/usr/bin/env python3
"""Session start hook: loads memory layer files into Claude's context."""

import json
import os
import re
import sys
from datetime import date

VAULT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

FILES_TO_LOAD = [
    (".claude/soul.md", "soul.md"),
    (".claude/user.md", "user.md"),
    (".claude/memory.md", "memory.md"),
    ("02-knowledge/index.md", "02-knowledge/index.md"),
]

# Token budget limits (Primitive 5)
TOKEN_BUDGET = {
    "max_turns": 50,
    "max_input_tokens": 150_000,
}


def read_file(path: str) -> str:
    try:
        with open(path, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "(not found)"
    except Exception as e:
        return f"(error reading: {e})"


def main():
    # Read stdin (hook input) but we don't need it for session-start
    try:
        json.loads(sys.stdin.read())
    except Exception:
        pass

    parts = []
    for rel_path, label in FILES_TO_LOAD:
        full_path = os.path.join(VAULT_DIR, rel_path)
        content = read_file(full_path)
        if content and content not in ("(not found)", ""):
            parts.append(f"--- {label} ---\n{content}")

    budget_line = (
        f"TOKEN BUDGET: {TOKEN_BUDGET['max_turns']} turns max, "
        f"{TOKEN_BUDGET['max_input_tokens']:,} input tokens max. "
        "Summarize and start a new session before hitting these limits."
    )

    # Voice evolution review check
    voice_review_msg = ""
    voice_log_path = os.path.join(VAULT_DIR, "03-reflections", "voice-evolution-log.md")
    voice_log_content = read_file(voice_log_path)
    if voice_log_content not in ("(not found)", ""):
        # Parse the last row's Next Review Date (YYYY-MM-DD)
        rows = re.findall(r"\|\s*v[\d.]+\s*\|.*?\|\s*(\d{4}-\d{2}-\d{2})\s*\|", voice_log_content)
        if rows:
            try:
                next_review = date.fromisoformat(rows[-1])
                if date.today() >= next_review:
                    # Find the last update date
                    date_matches = re.findall(r"\|\s*v[\d.]+\s*\|\s*(\d{4}-\d{2}-\d{2})\s*\|", voice_log_content)
                    last_update = date_matches[-1] if date_matches else "unknown"
                    voice_review_msg = (
                        f"\n\n--- voice profile review ---\n"
                        f"Voice profile review due. Your last update was {last_update}. "
                        f"Run the voice update workflow or defer to next session."
                    )
            except ValueError:
                pass

    if parts:
        message = (
            "=== MEMORY LAYER LOADED (session-start hook) ===\n\n"
            + "\n\n".join(parts)
            + f"\n\n--- token budget ---\n{budget_line}"
            + voice_review_msg
            + "\n\n=== END MEMORY LAYER ==="
        )
    else:
        message = "=== MEMORY LAYER: no files found ==="

    output = {"result": "continue", "message": message}
    print(json.dumps(output))


if __name__ == "__main__":
    main()
