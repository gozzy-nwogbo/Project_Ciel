# /today

Morning desk review. Prioritized plan from calendar, tasks, act_now, and captures. This command is read-only. No writes.

---

## Sources to Query

### 1. Google Calendar
Query today's events only, across all calendars.

### 2. Asana Tasks
Query Asana Open-Brain project for tasks due today or overdue.

### 3. ACT NOW Items
Run:
```bash
python3 01-projects/open-brain/scripts/write_act_now.py --query-open
```
Surface open items.

### 4. Supabase Captures
Query the Open Brain MCP server for recent captures: status = 'routed' with action_items, last 24 hours only. Use the `list_recent` MCP tool with appropriate filters.

### 5. Yesterday's Daily Log
Read yesterday's daily log from `06-daily/` if it exists. Extract any carry-forward items (open questions, unresolved items, items marked as next).

---

## Priority Ranking (strict order, matches morning digest v4)

1. Overdue Asana tasks (oldest first)
2. Asana tasks due today
3. ACT NOW items (high priority first)
4. Calendar events requiring prep
5. Captures with action items (last 24h)

---

## Output Format

Total output must be under 200 words. Use exactly this format:

```
TODAY — [YYYY-MM-DD]

Top 3:
1. [imperative verb] [thing] — [deadline or context]
2. [imperative verb] [thing] — [deadline or context]
3. [imperative verb] [thing] — [deadline or context]

Calendar:
[Time] — [event name]
[Time] — [event name]

Carry-forward from yesterday:
[Any unresolved items from yesterday's log, or "None"]
```

---

## Hard Constraints

- This command is read-only. No writes to any file or table.
- Under 200 words total output. No exceptions.
- Imperative actions only. "Finish X", not "You should finish X".
- No advice, no editorializing, no motivational language.
- If calendar or Asana is unavailable, note it and produce from available sources.
- If fewer than 3 items exist across all sources, show only what exists. Do not fabricate.
