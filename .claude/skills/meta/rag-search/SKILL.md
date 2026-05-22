# Skill: rag-search

Searches Supabase (captures, people, projects, ideas) and vault files (04-reflections/, 06-daily/, 02-knowledge/) simultaneously, returns max 7 ranked results with source labels, logs every query to retrieval_log, and prompts for usefulness feedback. Invoke when user asks to search, find, recall, or surface knowledge from the second brain.

---

## Modes

**Standard** (default) — natural language query. Trigger: "search", "find", "what do I know about", "recall", "surface".
**Find pattern** — error diagnosis or recurring problem lookup. Trigger: "find pattern", pasted error message, "have I seen this before".
**Expand** — full vault search. Trigger: "search: expand" flag appended to any query.

---

## Pre-flight (every search)

1. Run: `python3 01-projects/open-brain/scripts/log_retrieval.py --check`
2. FAIL → write stub report to `.claude/skills/meta/rag-search/stub-report.md` and STOP
3. PASS → proceed

---

## Inputs

| Input | Required | Purpose |
|---|---|---|
| Query (natural language or error message) | Yes | The search target |
| Mode | No | Auto-detected from trigger phrase; defaults to standard |

---

## Execution

### 1. Parse
- Standard/Expand: use query as-is
- Find pattern + error message: extract core signal (error type, node name, trigger condition) before searching. Never search raw error string.
- Find pattern + natural language: use with light reformulation

### 2. Search (run in parallel)
**a) Supabase:** call `mcp__open-brain__semantic_search` with query, all 4 tables, limit=7
**b) Vault:** Grep query terms across scoped folders
- Default: `04-reflections/`, `06-daily/`, `02-knowledge/`
- Expand: all of `~/second-brain/`

### 3. Merge and rank
- Combine results. Supabase results have similarity scores; vault results ranked by match density.
- Deduplicate by content overlap.
- **Cap at 7 total.** Truncate, never paginate.
- Label each: source (table name or folder path), date, one-line excerpt.

### 4. Present

**Standard/Expand output:**
```
SEARCH: [query]
[1] [source] | [date] | [excerpt]
...
```

**Find pattern output:**
```
PATTERN SEARCH: [extracted problem summary]

Past occurrences:
- [date]: [what happened] → [how resolved]

Confidence: [high/medium/low]
  high = 3+ occurrences with clear resolution
  medium = 1-2 occurrences or resolution unclear
  low = 0 occurrences — new pattern
```

### 5. Log (mandatory)
```bash
python3 01-projects/open-brain/scripts/log_retrieval.py \
  --query "[query]" --mode "[standard|find-pattern|expand]" \
  --sources '[...]' --results [N] --session-id "[session]"
```

### 6. Binary prompt (mandatory)
Ask: **"Useful? (y/n)"** — wait for response — then:
```bash
python3 01-projects/open-brain/scripts/log_retrieval.py \
  --update [id] --useful [true|false]
```

---

## Output Contract

**Produces:** Ranked search results (conversation) + retrieval_log entry (Supabase)
**Path:** Supabase `retrieval_log` table
**Structure:** Each entry has: query, mode, sources_searched, results_returned, useful, timestamp, session_id
**Out of scope:** Does not modify vault files. Does not write to captures/people/projects/ideas tables. Does not generate embeddings.

---

## Constraints

| # | Constraint | Verification |
|---|---|---|
| 1 | Max 7 results per search | Count output items |
| 2 | Binary prompt fires after every search, never skipped | Check conversation flow |
| 3 | Default vault scope is exactly 3 folders, not ~/second-brain/ | Check Grep paths |
| 4 | Every search writes a retrieval_log entry | Query table after search |
| 5 | Pre-flight runs before first search in session | Check tool call order |
| 6 | Error messages: signal extracted before searching | Compare search query to raw input |

---

## Edge Cases

1. **Zero results from both sources:** Report "No results found." Log with results_returned=0. Binary prompt still fires.
2. **Supabase MCP down, vault accessible:** Search vault only. Log sources as vault folders only. Note degraded mode.
3. **"find pattern" with non-error input:** Accept as natural language pattern search. Never reject input type.
4. **User ignores binary prompt:** Log with useful=null. Do not re-ask.
5. **Expand mode returns identical results to standard:** Present normally. Log mode as "expand" regardless.

---

## Handoff

**Artifact:** retrieval_log entry in Supabase (useful field may be null)
**Location:** Supabase `retrieval_log` table
**Condition:** Binary prompt answered or skipped
**Next stage:** Phase 6 morning digest reads retrieval_log for quality signal. Two-door audit uses it for capture-to-retrieval loop metrics.
