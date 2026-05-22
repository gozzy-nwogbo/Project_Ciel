#!/usr/bin/env python3
"""Session start hook: loads memory layer files into Claude's context.
Also surfaces unresolved ACT NOW items older than 24h (Phase 6.2)."""

import json
import os
import re
import subprocess
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
    voice_log_path = os.path.join(VAULT_DIR, "04-reflections", "voice-evolution-log.md")
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

    # Staging reminder: surface deep-parse-due reminder if check-staging.py wrote one
    staging_reminder_msg = ""
    reminder_path = os.path.join(VAULT_DIR, ".claude", "reminders", "deep-parse-due.md")
    reminder_content = read_file(reminder_path)
    if reminder_content not in ("(not found)", ""):
        staging_reminder_msg = (
            f"\n\n--- staging deep-parse reminder ---\n{reminder_content}"
        )

    # ACT NOW: surface unresolved items older than 24h (Phase 6.2)
    act_now_msg = ""
    act_now_script = os.path.join(
        VAULT_DIR, "01-projects", "open-brain", "scripts", "write_act_now.py"
    )
    if os.path.isfile(act_now_script):
        try:
            result = subprocess.run(
                [sys.executable, act_now_script, "--query-stale"],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode == 0 and result.stdout.strip():
                items = json.loads(result.stdout)
                if items:
                    lines = []
                    for i, item in enumerate(items, 1):
                        priority = item.get("priority", "medium")
                        text = item.get("item", "")
                        source = item.get("source_session", "")
                        lines.append(f"  {i}. [{priority}] {text} (from {source})")
                    act_now_msg = (
                        f"\n\n--- unresolved ACT NOW items ---\n"
                        f"You have {len(items)} unresolved ACT NOW item(s) from previous sessions:\n"
                        + "\n".join(lines)
                    )
        except Exception:
            pass  # Non-blocking: if query fails, skip silently

    # Permission log: write session_start entry (Phase 6.7)
    log_permission_script = os.path.join(
        VAULT_DIR, "01-projects", "open-brain", "scripts", "log_permission.py"
    )
    if os.path.isfile(log_permission_script):
        try:
            subprocess.run(
                [
                    sys.executable, log_permission_script,
                    "--integration", "system",
                    "--tool", "session_start",
                    "--tier", "read-only",
                    "--action", "session opened",
                    "--inputs", "context files loaded, memory layer initialized",
                    "--result", "success",
                    "--reason", "session initialization — context loaded",
                ],
                capture_output=True, text=True, timeout=10,
            )
        except Exception:
            pass  # Non-blocking: if permission log fails, skip silently

    if parts:
        message = (
            "=== MEMORY LAYER LOADED (session-start hook) ===\n\n"
            + "\n\n".join(parts)
            + f"\n\n--- token budget ---\n{budget_line}"
            + voice_review_msg
            + staging_reminder_msg
            + act_now_msg
            + "\n\n=== END MEMORY LAYER ==="
        )
    else:
        message = "=== MEMORY LAYER: no files found ==="

    output = {"result": "continue", "message": message}
    print(json.dumps(output))


if __name__ == "__main__":
    main()
