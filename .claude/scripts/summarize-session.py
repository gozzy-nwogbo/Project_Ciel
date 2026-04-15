#!/usr/bin/env python3
"""
Session-end and pre-compact hook: summarizes conversation transcript
and writes to 05-daily/YYYY-MM-DD.md using the Anthropic SDK.

The hook itself returns immediately. The API call runs in a detached
background process so the hook never blocks on network I/O.

Used by both SessionEnd and PreCompact hooks.
"""

import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime
from importlib.machinery import SourceFileLoader

VAULT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DAILY_DIR = os.path.join(VAULT_DIR, "05-daily")
LOG_FILE = os.path.join(VAULT_DIR, ".claude", "logs", "hook-debug.log")

_event_log = SourceFileLoader(
    "event_log", os.path.join(os.path.dirname(__file__), "event-log.py")
).load_module()


def log_debug(msg: str):
    """Append debug info to hook log file."""
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(f"[{datetime.now().isoformat()}] {msg}\n")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Background worker: called with --background <payload.json>
# ---------------------------------------------------------------------------

def summarize_with_api(transcript: str) -> str:
    """Call Anthropic API (Haiku) to produce a structured daily log summary."""
    log_debug(f"[bg] summarize_with_api() entered, transcript length: {len(transcript)} chars")
    try:
        import anthropic
    except ImportError:
        log_debug("[bg] anthropic SDK not installed")
        return ""

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        log_debug("[bg] ANTHROPIC_API_KEY not set")
        return ""

    client = anthropic.Anthropic(api_key=api_key)

    max_chars = 20000
    if len(transcript) > max_chars:
        transcript = transcript[:max_chars] + "\n\n[...truncated...]"

    prompt = f"""Summarize this Claude Code session transcript into a structured daily log entry.

Format:
## What Was Done
- (bullet points of completed work)

## Decisions Made
- (key decisions and their rationale)

## Open Questions
- (unresolved items, blockers, next steps)

Keep it concise. No em-dashes. Active voice.

Transcript:
{transcript}"""

    try:
        log_debug(f"[bg] Calling Anthropic API (model=claude-haiku-4-5-20251001, prompt length: {len(prompt)} chars)")
        _event_log.log_event(
            "tool_call", "anthropic_api_call",
            "claude-haiku-4-5-20251001", {"prompt_chars": len(prompt)},
        )
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        result = response.content[0].text
        log_debug(f"[bg] API call succeeded, response length: {len(result)} chars")
        return result
    except Exception as e:
        log_debug(f"[bg] API call failed: {e}")
        return ""


def write_daily_log(summary: str, event_type: str):
    """Append or create the daily log file."""
    os.makedirs(DAILY_DIR, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    log_path = os.path.join(DAILY_DIR, f"{today}.md")

    now = datetime.now().strftime("%H:%M")
    header = f"\n\n---\n\n### Session Log ({now}, {event_type})\n\n"

    if os.path.exists(log_path):
        with open(log_path, "a") as f:
            f.write(header + summary + "\n")
    else:
        with open(log_path, "w") as f:
            f.write(f"# Daily Log: {today}\n")
            f.write(header + summary + "\n")

    log_debug(f"[bg] Wrote daily log to {log_path}")
    _event_log.log_event(
        "state_transition", "daily_log_written",
        "summarize-session", {"path": log_path, "event_type": event_type},
    )


def run_background(payload_path: str):
    """Entry point for the detached background process."""
    try:
        with open(payload_path, "r") as f:
            payload = json.load(f)
    except Exception as e:
        log_debug(f"[bg] Failed to read payload {payload_path}: {e}")
        return
    finally:
        # Clean up the temp file
        try:
            os.unlink(payload_path)
        except OSError:
            pass

    transcript = payload.get("transcript", "")
    event_type = payload.get("event_type", "unknown")
    session_id = payload.get("session_id", "unknown")

    log_debug(f"[bg] Background worker started: session={session_id}, transcript={len(transcript)} chars")

    if transcript:
        summary = summarize_with_api(transcript)
        if summary:
            write_daily_log(summary, event_type)
        else:
            excerpt = transcript[:500] + ("..." if len(transcript) > 500 else "")
            write_daily_log(
                f"(Auto-summary unavailable. Transcript excerpt:)\n\n{excerpt}",
                event_type,
            )
    else:
        write_daily_log(
            f"Session ended (session_id: {session_id}). "
            "No transcript data available from hook input.",
            event_type,
        )

    log_debug(f"[bg] Background worker finished: session={session_id}")


# ---------------------------------------------------------------------------
# Hook entry point: reads stdin, spawns background worker, exits immediately
# ---------------------------------------------------------------------------

def extract_transcript(hook_input: dict) -> str:
    """Extract conversation transcript from hook input JSON."""
    for key in ["transcript", "messages", "conversation", "summary",
                "transcript_summary", "content"]:
        if key in hook_input and hook_input[key]:
            val = hook_input[key]
            if isinstance(val, str):
                return val
            if isinstance(val, list):
                parts = []
                for item in val:
                    if isinstance(item, str):
                        parts.append(item)
                    elif isinstance(item, dict):
                        role = item.get("role", "unknown")
                        content = item.get("content", "")
                        if isinstance(content, list):
                            content = " ".join(
                                c.get("text", str(c))
                                for c in content
                                if isinstance(c, dict)
                            )
                        parts.append(f"{role}: {content}")
                return "\n".join(parts)

    for key in ["stop_hook_input", "session", "data"]:
        if key in hook_input and isinstance(hook_input[key], dict):
            nested = extract_transcript(hook_input[key])
            if nested:
                return nested

    return ""


def main():
    # Read hook input from stdin
    raw_input = ""
    try:
        raw_input = sys.stdin.read()
    except Exception:
        pass

    hook_input = {}
    if raw_input.strip():
        try:
            hook_input = json.loads(raw_input)
        except json.JSONDecodeError:
            log_debug(f"Failed to parse stdin as JSON: {raw_input[:200]}")

    event_type = hook_input.get("hook_event_name",
                                hook_input.get("event", "unknown"))
    session_id = hook_input.get("session_id", "unknown")
    log_debug(f"Hook fired: event={event_type}, session={session_id}")
    log_debug(f"Input keys: {list(hook_input.keys())}")

    _event_log.log_event(
        "context_load", f"session_hook_fired:{event_type}",
        "summarize-session", {"keys": list(hook_input.keys())}, session_id,
    )

    # --- Gather transcript ---
    transcript = ""
    transcript_path = hook_input.get("transcript_path", "")
    if transcript_path and os.path.isfile(transcript_path):
        try:
            with open(transcript_path, "r") as f:
                transcript = f.read()
            log_debug(f"Read transcript from file: {transcript_path} ({len(transcript)} chars)")
        except Exception as e:
            log_debug(f"Failed to read transcript file {transcript_path}: {e}")

    if not transcript:
        transcript = extract_transcript(hook_input)

    if transcript:
        log_debug(f"Transcript found: {len(transcript)} chars")

    # --- Write payload to temp file and spawn background worker ---
    payload = {
        "transcript": transcript,
        "event_type": event_type,
        "session_id": session_id,
    }

    try:
        fd, payload_path = tempfile.mkstemp(prefix="claude-hook-", suffix=".json")
        with os.fdopen(fd, "w") as f:
            json.dump(payload, f)

        # Launch detached background process
        subprocess.Popen(
            [sys.executable, __file__, "--background", payload_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        )
        log_debug(f"Spawned background worker: {payload_path}")
    except Exception as e:
        log_debug(f"Failed to spawn background worker: {e}")

    # --- Return immediately so the hook does not block ---
    print(json.dumps({"result": "continue"}))


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "--background":
        run_background(sys.argv[2])
    else:
        main()
