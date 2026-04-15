# Skill Audit: Finishing a Development Branch

**Date:** 2026-04-14
**Auditor:** Phase 5 Track A migration

## Criteria Evaluation

### C1: Single-line description with trigger context + output artifact named
**PASS** — Description names trigger phrases ("finish branch", "merge this", "open a PR") and output artifacts (merged main or open PR URL, cleaned worktree).

### C2: Output contract (artifact name, path, structure, out-of-scope)
**FAIL** — Four possible outcomes are described (merge, PR, keep, discard) but no single named output artifact with defined structure. PR description template exists but is not a standalone artifact contract.

### C3: Input contract (all inputs named with purposes)
**FAIL** — No formal input contract. Implicit inputs: branch name, plan.md status, test status. None are enumerated with required/optional status.

### C4: Constraints as binary testable rules (no "should"/"ideally")
**PASS** — Pre-flight checks are all binary (plan tasks complete, tests pass, no debug code, verification run). "If any check fails, stop and fix before proceeding" is binary.

### C5: Edge cases declared (>=3 with handling instructions)
**FAIL** — No edge cases declared. No handling for: merge conflicts, remote branch already deleted, worktree doesn't exist, upstream main has diverged, PR already open.

### C6: Worked example file exists in same folder
**FAIL** — No example file exists.

### C7: Core file <=150 lines
**PASS** — SKILL.md is 85 lines.

### C8: Handoff defined (specific artifact, location, condition)
**PASS** — After Merging section defines post-completion steps. Each option has a clear terminal state. Pre-flight check defines entry condition.

### C9: Test basket file with >=3 cases exists in folder
**FAIL** — No test basket file exists.

## Verdict: DRAFT (4/9 PASS)
