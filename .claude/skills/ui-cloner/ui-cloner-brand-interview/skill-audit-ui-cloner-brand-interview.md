# Skill Audit: ui-cloner-brand-interview

**Date:** 2026-04-14

---

## C1: Single-line description with trigger context + output artifact named
**PASS** — Description block includes trigger phrases ("brand interview", "run phase 2", "collect brand info"), output artifact (`plans/02-brand-interview.md`), and pipeline step number (Step 2 of 6).

## C2: Output contract (artifact name, path, structure, out-of-scope declared)
**PASS** — Output artifact is `plans/02-brand-interview.md` containing all 12 answers with question labels. Structure is defined (12 labeled Q&A pairs). Scope is clear: collect answers only, do not synthesize.

## C3: Input contract (all inputs named with purposes)
**PASS** — Input: completed Phase 1 (Site DNA must exist). The 12 questions define exactly what information is collected from the user and why each shapes the output.

## C4: Constraints as binary testable rules (no "should"/"ideally")
**PASS** — "Ask all 12 questions at once. Do not drip them one at a time." "Do not proceed to synthesis until you have their answers to all 12." Binary, testable.

## C5: Edge cases declared (3+ with handling instructions)
**FAIL** — Only one edge case addressed: missing/vague answers (ask for clarification on those specific questions). Does not cover: user declining to answer questions, partial answers, user wanting to skip the interview, conflicting answers between questions.

## C6: Worked example file exists in same folder
**FAIL** — No worked example file exists in the skill folder.

## C7: Core file 150 lines or fewer
**PASS** — Source is 80 lines, well under the 150-line limit.

## C8: Handoff defined (specific artifact, location, condition)
**PASS** — "When complete: Invoke ui-cloner-synthesis to begin Phase 3." Artifact and save location defined.

## C9: Test basket file with 3+ cases exists in folder
**FAIL** — No test basket file exists in the skill folder.

---

## Verdict: DRAFT (6/9 — fails C5, C6, C9)
