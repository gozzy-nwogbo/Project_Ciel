# Skill Audit: rag-search
_Evaluated: 2026-04-16 | Standard: skill-authoring v1_

## Verdict: PASS

| # | Criterion | Result | Evidence |
|---|---|---|---|
| C1 | Single-Line Description | PASS | Line 3: single unbroken line naming trigger context ("invoke when user asks to search, find, recall, or surface") and output artifact ("retrieval_log entry") |
| C2 | Output Contract | PASS | Lines 89-94: names artifact (retrieval_log entry + conversation results), path (Supabase retrieval_log table), structure (7 fields listed), and out-of-scope (no vault writes, no captures/people/projects/ideas writes, no embeddings) |
| C3 | Input Contract | PASS | Lines 25-28: two inputs named with purposes. Query (required, "the search target") and Mode (optional, "auto-detected from trigger phrase") |
| C4 | Constraints as Rules | PASS | Lines 100-107: all 6 constraints are binary and testable with explicit verification methods (count items, check paths, query table, check tool call order) |
| C5 | Edge Cases Declared | PASS | Lines 113-117: 5 edge cases documented with explicit handling (zero results, MCP down, non-error find-pattern, ignored prompt, identical expand results) |
| C6 | Worked Example Exists | PASS | `example-standard-search.md` exists in folder, shows full input-to-output flow matching declared contract (query, parallel search, merged results, log entry, binary prompt) |
| C7 | Core File Under 150 Lines | PASS | 126 lines (verified via wc -l) |
| C8 | Handoff Defined | PASS | Lines 123-126: names artifact (retrieval_log entry), location (Supabase table), condition (binary prompt answered or skipped), next stage (Phase 6 morning digest, two-door audit) |
| C9 | Test Basket Exists | PASS | `test-basket.md` exists with 7 test cases, each with defined input and expected output |

## Failing Criteria — Required Fixes
None.

## Classification
- **PASS (9/9 criteria):** Skill is production-ready. Eligible for promotion gate.
