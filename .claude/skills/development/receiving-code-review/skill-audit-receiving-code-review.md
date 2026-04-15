# Skill Audit: Receiving Code Review

**Date:** 2026-04-14
**Auditor:** Phase 5 Track A migration

## Criteria Evaluation

### C1: Single-line description with trigger context + output artifact named
**PASS** — Description names trigger phrases ("address review comments", "fix review feedback") and output artifact (updated branch with comments addressed and summary comment).

### C2: Output contract (artifact name, path, structure, out-of-scope)
**FAIL** — Output is described as "updated branch" and "summary comment" but no specific artifact file, path, or structure is defined. No out-of-scope declaration.

### C3: Input contract (all inputs named with purposes)
**FAIL** — No formal input contract. Implicit inputs: PR URL or review comments, branch name. None are enumerated.

### C4: Constraints as binary testable rules (no "should"/"ideally")
**FAIL** — "Should fix" is used as a category label (acceptable as a label, not as a rule). "Don't take feedback personally" is not binary testable. "Every comment deserves a response" is binary testable.

### C5: Edge cases declared (>=3 with handling instructions)
**FAIL** — One edge case is partially handled ("Disagree" items have a 3-step resolution process). No handling for: reviewer is wrong, conflicting reviewer feedback, review on deleted code, stale review on rebased branch.

### C6: Worked example file exists in same folder
**FAIL** — No example file exists.

### C7: Core file <=150 lines
**PASS** — SKILL.md is 56 lines.

### C8: Handoff defined (specific artifact, location, condition)
**FAIL** — Step 4 says "push the changes" and "add a comment summarizing what was changed" but does not define a next skill or terminal condition beyond re-requesting review.

### C9: Test basket file with >=3 cases exists in folder
**FAIL** — No test basket file exists.

## Verdict: DRAFT (2/9 PASS)
