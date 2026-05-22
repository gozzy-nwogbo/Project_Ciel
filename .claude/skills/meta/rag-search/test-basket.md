# Test Basket: rag-search

## Test 1: Standard search returns results with source labels

**Input:** Query "n8n workflow" in standard mode
**Expected output:**
- Results from both Supabase tables and vault folders
- Each result labeled with source (table name or folder), date, one-line excerpt
- Max 7 results
- retrieval_log entry created with mode="standard"
- Binary prompt "Useful? (y/n)" fires after results

---

## Test 2: Find pattern mode with error message

**Input:** Pasted error message: `ERROR: 23514: new row for relation "captures" violates check constraint "captures_status_check"`
**Expected output:**
- Agent extracts signal: check constraint violation on captures table, status field
- PATTERN SEARCH output format with past occurrences
- Confidence level stated (high/medium/low)
- retrieval_log entry with mode="find-pattern"
- Binary prompt fires

---

## Test 3: Find pattern mode with natural language

**Input:** "find pattern: my n8n webhooks keep timing out"
**Expected output:**
- Searches for webhook timeout patterns across all sources
- PATTERN SEARCH output format
- Does not reject input for not being an error message
- retrieval_log entry with mode="find-pattern"
- Binary prompt fires

---

## Test 4: Expand mode widens vault scope

**Input:** "search: expand — Telegram bot architecture"
**Expected output:**
- Supabase search runs identically to standard
- Vault Grep covers all of ~/second-brain/, not just 3 default folders
- retrieval_log entry with mode="expand"
- Result set may differ from standard mode for same query

---

## Test 5: Zero results handled gracefully

**Input:** "search for quantum computing applications in agriculture"
**Expected output:**
- "No results found." message
- retrieval_log entry with results_returned=0
- Binary prompt still fires
- No error or crash

---

## Test 6: Results capped at 7

**Input:** Broad query likely to match many entries (e.g., "n8n")
**Expected output:**
- Exactly 7 or fewer results displayed
- No pagination offered
- retrieval_log.results_returned <= 7

---

## Test 7: Pre-flight check failure produces stub report

**Input:** Run search when Supabase is unreachable (simulated)
**Expected output:**
- Stub report written to `.claude/skills/meta/rag-search/stub-report.md`
- Search does not execute
- No retrieval_log entry (table unreachable)
- Clear error message to user
