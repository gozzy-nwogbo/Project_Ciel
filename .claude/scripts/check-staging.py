#!/usr/bin/env python3
"""
Check 00-inbox/staging/ and write a reminder file when deep parse is due.

Trigger conditions (either fires):
  - Any staging file is older than STALE_DAYS days
  - Staging contains FILE_THRESHOLD or more files

Run via cron. The reminder file is surfaced on session-start by
session-start.py and removed by the /deep-parse-staging slash command
after it finishes.
"""

import os
from datetime import datetime, timedelta

VAULT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
STAGING_DIR = os.path.join(VAULT_DIR, "00-inbox", "staging")
REMINDERS_DIR = os.path.join(VAULT_DIR, ".claude", "reminders")
REMINDER_FILE = os.path.join(REMINDERS_DIR, "deep-parse-due.md")

STALE_DAYS = 7
FILE_THRESHOLD = 5


def list_staging() -> list[tuple[str, float]]:
    """Return list of (filename, mtime) for .md files in staging."""
    if not os.path.isdir(STAGING_DIR):
        return []
    files = []
    for fname in os.listdir(STAGING_DIR):
        if fname.startswith("."):
            continue
        if not fname.endswith(".md"):
            continue
        path = os.path.join(STAGING_DIR, fname)
        if os.path.isfile(path):
            files.append((fname, os.path.getmtime(path)))
    return sorted(files, key=lambda x: x[1])


def main():
    files = list_staging()

    if not files:
        # Empty staging: clear any existing reminder
        if os.path.exists(REMINDER_FILE):
            os.unlink(REMINDER_FILE)
        return

    now = datetime.now()
    oldest_mtime = files[0][1]
    oldest_age_days = (now.timestamp() - oldest_mtime) / 86400

    fires_age = oldest_age_days >= STALE_DAYS
    fires_count = len(files) >= FILE_THRESHOLD

    if not (fires_age or fires_count):
        # Below threshold: clear any stale reminder
        if os.path.exists(REMINDER_FILE):
            os.unlink(REMINDER_FILE)
        return

    # Write the reminder
    os.makedirs(REMINDERS_DIR, exist_ok=True)

    reasons = []
    if fires_count:
        reasons.append(f"{len(files)} files in staging (threshold {FILE_THRESHOLD})")
    if fires_age:
        reasons.append(f"oldest is {oldest_age_days:.1f} days old (threshold {STALE_DAYS})")

    lines = [
        "# Deep-parse due",
        "",
        f"*Generated {now.strftime('%Y-%m-%d %H:%M')} by check-staging.py*",
        "",
        f"**Why:** {', '.join(reasons)}.",
        "",
        "**Action:** run `/deep-parse-staging` when ready. The slash command bundles the full Pass 2 protocol and clears this reminder when done.",
        "",
        "## Files awaiting deep parse",
        "",
    ]
    for fname, mtime in files:
        age = (now.timestamp() - mtime) / 86400
        date_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
        lines.append(f"- `{fname}` (staged {date_str}, {age:.1f}d old)")
    lines.append("")

    with open(REMINDER_FILE, "w") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    main()
