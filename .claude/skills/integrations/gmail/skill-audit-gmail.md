# Skill Audit: gmail

**Date:** 2026-04-14
**Auditor:** Phase 5 Track A migration

---

## C1: Single-line description with trigger context + output artifact named
**PASS**
Description block covers what it does, trigger phrases, and names output artifacts (email summaries, draft objects).

## C2: Output contract (artifact name, path, structure, out-of-scope declared)
**PASS**
Output formats defined per operation (thread summaries, draft creation). "What This Skill Does NOT Do" section explicitly declares out-of-scope operations.

## C3: Input contract (all inputs named with purposes)
**PASS**
Each operation specifies exact tool parameters (Query, threadId, body, contentType, maxResults) with their purposes.

## C4: Constraints as binary testable rules (no "should"/"ideally")
**PASS**
"Never call `gmail_create_draft` without explicit user approval" is binary testable. Permission boundaries table is binary (Yes/NO). Default filtering rule is binary (apply unless `show:all`).

## C5: Edge cases declared (>=3 with handling instructions)
**PASS**
Edge cases handled: (1) `show:all` override for filtered queries, (2) confidence < 0.6 triggers `needs-review`, (3) user edits draft text before approval, (4) job alerts filtered from default view but processed separately, (5) spam/trash access only on explicit request.

## C6: Worked example file exists in same folder
**FAIL**
No worked example file present.

## C7: Core file <=150 lines
**FAIL**
SKILL.md is 173 lines (source) plus description block, exceeding the 150-line limit.

## C8: Handoff defined (specific artifact, location, condition)
**PASS**
Each operation defines its completion: search returns formatted summaries, draft creation requires approval then calls tool, job scoring logs to Supabase captures table.

## C9: Test basket file with >=3 cases exists in folder
**FAIL**
No test basket file present.

---

## Verdict: DRAFT (6/9 PASS)
