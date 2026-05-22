# Worked Example: Standard Search

## Input
User query: "n8n workflow error handling"

## Pre-flight
```bash
python3 01-projects/open-brain/scripts/log_retrieval.py --check
# Output: OK: retrieval_log table accessible
```

## Search Execution

### Supabase (semantic_search)
Called: `mcp__open-brain__semantic_search(query="n8n workflow error handling", limit=7)`
Returned 4 results across captures and ideas tables.

### Vault (Grep)
Searched: `04-reflections/`, `06-daily/`, `02-knowledge/`
Pattern: "n8n.*error|error.*handl"
Returned 3 matching files.

## Merged Output (7 results, capped)
```
SEARCH: n8n workflow error handling
[1] captures | 2026-04-10 | Telegram capture about n8n webhook timeout in production workflow
[2] 02-knowledge/concepts/ | 2026-04-10 | Schema validation error debugging pattern for n8n nodes
[3] ideas | 2026-04-08 | Idea: centralized error handler node pattern for all n8n workflows
[4] 06-daily/ | 2026-04-09 | Session log noting error handle node added to email pipeline
[5] captures | 2026-04-07 | n8n IF node returning empty array on error branch
[6] 02-knowledge/concepts/ | 2026-04-10 | Six-node workflow structure includes error handle step
[7] 04-reflections/ | 2026-04-06 | Reflection on n8n error patterns across 483 workflows
```

## Log Entry
```bash
python3 01-projects/open-brain/scripts/log_retrieval.py \
  --query "n8n workflow error handling" --mode standard \
  --sources '["captures","people","projects","ideas","04-reflections/","06-daily/","02-knowledge/"]' \
  --results 7 --session-id "phase5-example"
```

## Binary Prompt
Agent: "Useful? (y/n)"
User: "y"

```bash
python3 01-projects/open-brain/scripts/log_retrieval.py \
  --update abc12345-... --useful true
```

## Final retrieval_log entry
```json
{
  "id": "abc12345-...",
  "query": "n8n workflow error handling",
  "mode": "standard",
  "sources_searched": ["captures","people","projects","ideas","04-reflections/","06-daily/","02-knowledge/"],
  "results_returned": 7,
  "useful": true,
  "timestamp": "2026-04-16T...",
  "session_id": "phase5-example"
}
```
