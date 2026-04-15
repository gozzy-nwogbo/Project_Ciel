# Skill: Writing Plans

Breaks approved designs into bite-sized executable implementation tasks (2-5 min each).
Trigger: "write a plan", "break this down", "implementation plan", "plan the work"
Output artifact: plan.md in project root

---

# Writing Plans

Activates with an approved design document. Breaks work into bite-sized tasks (2-5 minutes each). Every task has exact file paths, complete code, and verification steps.

## When to Use

- After a design is approved (from `brainstorming`)
- Before beginning implementation
- When a task is large enough to need structure

## Plan Quality Standards

A good plan is clear enough for an enthusiastic junior engineer with no project context to follow. That means:

- **Specific file paths** — not "add to the auth module", but `src/auth/middleware.ts`
- **Complete code** — not "write a function", but the actual function
- **Verification steps** — how to know the task succeeded (test command, expected output, etc.)
- **Small tasks** — 2-5 minutes each, not hour-long monsters
- **Sequenced correctly** — dependencies come before dependents

## Plan Format

```markdown
# Implementation Plan: [Feature Name]

## Overview
[One paragraph summary of what this plan accomplishes]

## Prerequisites
- [ ] [Anything that must be true before starting]

## Tasks

### Task 1: [Short descriptive name]
**File**: `path/to/file.ts`
**What**: [One sentence description]

\`\`\`typescript
// Complete code to add/change
\`\`\`

**Verify**: `npm test src/auth` should show X passing

---

### Task 2: [Short descriptive name]
...
```

## Key Principles

- **YAGNI** — You Aren't Gonna Need It. Only build what the design specifies.
- **DRY** — Don't Repeat Yourself. Identify shared logic and factor it out.
- **TDD** — Every task that adds logic should have a test task before it.
- **Reversible** — prefer changes that are easy to undo over clever solutions

## Handoff

When the plan is ready:
1. Save to `plan.md` in the project root
2. Review with the user before executing
3. Hand off to `executing-plans` or `subagent-driven-development`
