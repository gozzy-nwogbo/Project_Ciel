# LinkedIn Engine v1.0 — Execution Handoff

**Created:** 2026-05-25
**Reason:** Orchestrator context exhaustion. Brainstorm + spec + plan writing consumed the session; subagent dispatch loop needs a fresh orchestrator session to continue cleanly.
**Status:** Branch `feat/linkedin-engine-v1.0`. Baseline committed. Task A1 (scaffold) committed. 25 tasks remain.

---

## Quick state

- **Branch:** `feat/linkedin-engine-v1.0` (off `main`)
- **Latest commit:** `659ab4e` — A1 scaffold
- **Baseline commit:** `5d62193` — spec + plan + gitignore whitelist
- **Working tree:** clean for linkedin paths

```bash
git log --oneline feat/linkedin-engine-v1.0 ^main
# Expect 2 commits: 659ab4e (A1) + 5d62193 (baseline)
```

---

## What's done

- ✅ Brainstorm complete
- ✅ Design spec: `01-projects/linkedin/docs/2026-05-24-linkedin-engine-design.md`
- ✅ Implementation plan: `2026-05-24-v1-0-implementation-plan.md` (Part 1) + `-part2.md` (Part 2)
- ✅ Command reference: `command-reference.md`
- ✅ Library of Alexandria v2 prompt: `05-resources/prompts/library-of-alexandria-v2.md`
- ✅ Gitignore whitelist for `01-projects/linkedin/`
- ✅ Feature branch created
- ✅ Task A1 (scaffold) implemented + committed

---

## What's next (in order)

25 remaining tasks from the plan. Phase order:

| Phase | Tasks | Plan file |
|---|---|---|
| A (cont.) | A2, A3, A4, A5 | Part 1 |
| B | B1 | Part 1 |
| C | C1, C2, C3 | Part 1 |
| D | D1, D2 | Part 1 |
| E | E1, E2 | Part 1 |
| F | F1 | Part 1 |
| G | G1, G2, G3, G4 | Part 2 |
| H | H1 | Part 2 |
| I | I1 | Part 2 |
| J | J1 | Part 2 |
| K | K1 | Part 2 |
| L | L1, L2, L3 | Part 2 |
| M | M1 (test), M2 (manual smoke) | Part 2 |

---

## How to resume in a fresh Claude Code session

1. **Open Claude Code in `/Users/gozzynwogbo/second-brain/`.**
2. **Verify branch:**
   ```bash
   git branch --show-current
   # Expect: feat/linkedin-engine-v1.0
   ```
3. **Paste this prompt to Claude:**

   ```
   Continue execution of the LinkedIn engine v1.0 plan.

   Context:
   - Branch: feat/linkedin-engine-v1.0
   - Plan: 01-projects/linkedin/docs/2026-05-24-v1-0-implementation-plan.md (Part 1) and -part2.md (Part 2)
   - Execution mode: subagent-driven-development (already chosen)
   - Completed: Task A1 (scaffold) at commit 659ab4e
   - Next task: A2 — Project-level CLAUDE.md
   - Read EXECUTION-HANDOFF.md first for full state.

   Use the superpowers:subagent-driven-development skill and continue dispatching implementers for tasks A2 through M2 in plan order. Use cheap models (haiku) for scaffolding/docs tasks (A2, A3, A4, A5, B1, K1, L3), standard models (sonnet) for code-heavy tasks (C–L code), and most capable for end-to-end tests (M1).

   Follow the two-stage review per task: spec compliance review, then code quality review. Don't pause between tasks. Stop only for BLOCKED status or genuine ambiguity.
   ```

4. **The new Claude reads `EXECUTION-HANDOFF.md` and the plan files, then continues.**

---

## Key context for the next orchestrator

### Gitignore facts (already set up)

- `01-projects/linkedin/` is whitelisted for `src/`, `tests/`, `docs/`, `CLAUDE.md`, `brand-spec.md`, `pyproject.toml`, `requirements.txt`, `requirements-dev.txt`.
- `01-projects/linkedin/{backlog,state,logs}/` are gitignored — runtime data, never committed.
- No `git add -f` ever needed.

### Subagent dispatch pattern (per skill)

Per task:
1. **Implementer** (general-purpose, model-by-complexity): give full task text from plan, scene context, working dir, self-review checklist.
2. **Spec reviewer** (general-purpose, sonnet): verify code matches plan task. Read the implementation, don't trust the report.
3. **Code quality reviewer** (general-purpose, sonnet): check clarity, file boundaries, test quality, BASE_SHA to HEAD_SHA diff.
4. **Mark task completed in task list.**

Templates at: `~/.claude/plugins/cache/claude-plugins-official/superpowers/5.1.0/skills/subagent-driven-development/{implementer,spec-reviewer,code-quality-reviewer}-prompt.md`

### Model selection by task

| Task type | Suggested model | Rationale |
|---|---|---|
| Scaffold, docs, config (A2-A5, B1, K1, L3) | haiku | Mechanical |
| Single-file code with tests (C1-F1, H1, I1, J1, L2) | sonnet | Standard |
| Multi-file integration (G1-G4, L1) | sonnet | Strategy modules touch loader+graph+models |
| End-to-end test (M1) | sonnet | Spans full pipeline |
| Manual smoke (M2) | n/a | User runs commands themselves |

### Per-task commit convention

`feat(linkedin): <task-id> <one-line description>` with TDD-style intent (test first, implementation, verify, commit). Each task = 1 commit minimum.

### What NOT to do

- Don't ingest the entire plan into orchestrator context. Read only the current task's section.
- Don't dispatch parallel implementer subagents (file conflicts).
- Don't skip the two-stage review.
- Don't accept "close enough" — re-loop reviewer until ✅.
- Don't add Higgsfield, Remotion, Satori, Supabase, Telegram, scheduler integration — those are v1.1+ scope and explicitly out of v1.0.
- Don't add the angle-similarity check (deferred to v1.1).
- Don't add `--batch=N` loop implementation (deferred, arg parser accepts it but only `=1` wired).

### Tests pass criterion

Each task ends with `pytest tests/<test-file>.py -v` passing. The full suite must pass at the end of each phase boundary (A complete, B complete, etc).

### Final task M2 is manual

M2 requires the human user to run commands against real atoms in `02-knowledge/`. The orchestrator can prepare the commands and explain the smoke test, but the user runs them and reports the result.

---

## After all 26 tasks complete

1. Dispatch a final code reviewer for the entire implementation (per skill protocol).
2. Invoke `superpowers:finishing-a-development-branch` to handle merge/PR decision.
3. Update `03-skills/registry.md` if any skill rows are missing.
4. Surface the smoke test results to the user.

---

## Open questions deferred to planning (per spec §8.1)

If a subagent surfaces these during implementation, defer to user:
1. Higgsfield CLI auth model — irrelevant for v1.0 (tier 3 is v1.2).
2. Satori vs React-PDF — irrelevant for v1.0 (tier 2 is v1.1).
3. Connection-type retro-tagging — leave atoms untyped; default to `general`.
4. Voice training data persistence — `edit_delta` already captured via approval log.
5. Series strategy — emergent; no named series in v1.0.

---

*Handoff written by the brainstorm/plan/exec-bootstrap session. Continue execution in a fresh session.*
