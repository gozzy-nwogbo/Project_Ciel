# Skill Audit: using-git-worktrees

**Date:** 2026-04-14

## Criteria Evaluation

### C1: Single-line description with trigger context + output artifact named
**PASS** — Description block includes what it does, trigger phrases, and names "Clean worktree directory with verified test baseline" as artifact.

### C2: Output contract (artifact name, path, structure, out-of-scope declared)
**FAIL** — Artifact named in header. Path convention described (../[repo-name]-[feature-slug]) but no formal out-of-scope declaration.

### C3: Input contract (all inputs named with purposes)
**FAIL** — Implicitly requires a git repo and feature name but no formal input contract listing all required inputs.

### C4: Constraints as binary testable rules (no "should"/"ideally")
**PASS** — Safety Rules are binary: "Never force-remove a worktree with uncommitted changes", "Check git worktree list before creating", "Keep worktree directories adjacent". No hedging.

### C5: Edge cases declared (>=3 with handling instructions)
**PASS** — Three safety rules with handling, plus "tests already failing" edge case with explicit stop-and-report instruction.

### C6: Worked example file exists in same folder
**FAIL** — No example file exists.

### C7: Core file <=150 lines
**PASS** — SKILL.md is 71 lines (well under 150).

### C8: Handoff defined (specific artifact, location, condition)
**PASS** — Integration section defines handoff: "Use writing-plans then executing-plans or subagent-driven-development" after worktree is ready.

### C9: Test basket file with >=3 cases exists in folder
**FAIL** — No test basket file exists.

## Verdict: DRAFT (5/9)
