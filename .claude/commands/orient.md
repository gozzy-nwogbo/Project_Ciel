# /orient

Load full orientation about current life and work state. This command is read-only. No writes, no Supabase mutations, no file changes.

---

## Sources to Read

Read all 8 sources below. If any source is unavailable (API down, file missing, tool error), note it in the output and continue with available sources.

### 1. User Profile
Read `.claude/user.md` — extract active tracks, operating rhythms, current status.

### 2. Memory
Read `.claude/memory.md` — extract key decisions and lessons.

### 3. Asana Tasks
Query Asana for the Open-Brain project. Get all open tasks. Group by:
- **Overdue** (due date before today)
- **Due today**
- **Due this week** (next 7 days)
- **Later** (everything else)

### 4. Google Calendar
Query Google Calendar for today's and tomorrow's events across all calendars.

### 5. ACT NOW Items
Run:
```bash
python3 01-projects/open-brain/scripts/write_act_now.py --query-open
```
Surface all open items with their priority and creation date.

### 6. Billing Alerts
Search Gmail for billing-related emails from the last 7 days:
```
Query: (billing OR subscription OR "payment due" OR invoice OR "you've been charged") newer_than:7d label:inbox
```
If results found: surface under a "Billing Alerts" section in the context summary.
If no results: omit the section entirely. No "No billing alerts" message needed.

### 7. Recent Daily Logs
Read the last 3 daily logs in `06-daily/` (by date, most recent first). Extract any items tagged as open questions, unresolved, or carry-forward.

### 8. Knowledge Index
Read `02-knowledge/index.md` for vault navigation reference.

---

## Output Format

Produce a structured context summary using exactly this format:

```
CONTEXT — [YYYY-MM-DD]

Active tracks:
- [From user.md — what's currently running in parallel]

Open commitments:
Overdue:
- [task] — due [date]
Due today:
- [task]
This week:
- [task] — due [date]
Later:
- [task] — due [date]

Today / Tomorrow:
[date, day]:
- [time] — [event name]
[date, day]:
- [time] — [event name]

Unresolved ACT NOW items:
- [priority] [item] — created [date]

Billing alerts (if any):
- [subject] — [sender], [date]

Recurring themes (last 3 sessions):
- [Patterns, repeated topics, or unresolved threads from daily logs]

Vault entry point:
[From index.md — top-level categories and where to start if research is needed]
```

---

## Hard Constraints

- This command is strictly read-only. No writes to any file or table.
- Surface only. Do not start executing tasks from the context output.
- If any source is unavailable, note it and continue with available sources.
- Do not load full file contents into output. Summarize and extract.
