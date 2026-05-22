# Claude Code Session Prompt Template

_For Claude Code sessions in ~/second-brain/ (or any working directory with a CLAUDE.md)._

**Used for:** execution, building, convention housekeeping, skill building, integration work.

**NOT used for:** strategic planning (use SB Planner), capture (use Telegram), atom queries (use NotebookLM).

---

## Session Header

Session type: [capture / reflect / research / execute]
Working directory: [~/second-brain/ or project-specific path]

Write-allowed folders:
- [list every folder this session may create or modify files in]
- [e.g., .claude/templates/, 03-skills/, 06-daily/]
- [any write outside these folders requires explicit approval]

---

## Pre-reads

Read in this order before starting any task:

1. [file path] — [why: e.g., "behavioral identity"]
2. [file path] — [why: e.g., "recent handoff context"]
3. [file path] — [why: e.g., "registry to check for existing skills"]

---

## Tasks

### Task N — [short name]

[Goal in 1-2 sentences. State the verifiable outcome, not the activity.]

[Scope: what to touch, what not to touch, what "done" looks like.]

[Any task-specific constraints or halt conditions.]

---

_(Repeat Task block for each task. Number sequentially. Do not batch.)_

---

## Halt Conditions

Stop and ask (do not proceed) when:
- [e.g., "expected file does not exist"]
- [e.g., "content already present — would duplicate"]
- [e.g., "task expands beyond housekeeping scope"]
- [e.g., "ambiguous supersession or merge conflict"]

---

## Hard Session Rules

- Approval-first on every file edit and create. Cycle: propose diff/text, wait for approval, write, confirm.
- One task at a time in sequence. Do not begin Task N+1 until Task N is confirmed complete.
- No writes outside the folders listed in Session Header without explicit approval.
- [session-specific rules, e.g., "no new skills built this session"]
- [session-specific rules, e.g., "templates and conventions only"]

---

## Handoff

After all tasks complete:

- Update memory.md if any durable facts were produced (one-line entries only).
- Write or append to `06-daily/[date].md` with: what was done, decisions made, open questions.
- Update `.continue-here.md` in any active project folder touched.
