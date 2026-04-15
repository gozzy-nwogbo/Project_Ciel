# Skill: Subagent-Driven Development

Dispatches fresh subagents per task with two-stage review (spec compliance, then code quality).
Trigger: "execute plan with subagents", "parallel implementation", "subagent driven"
Output artifact: Committed code per task with review logs

---

# Subagent-Driven Development

Dispatches fresh subagents per task with two-stage review (spec compliance, then code quality). Faster iteration with built-in quality gates.

## When to Use

- A plan is ready and you want automated execution with review gates
- When tasks are independent enough to be parallelized
- As a higher-quality alternative to `executing-plans`

## How It Works

### For Each Task in the Plan

**Stage 1 — Execution**
Dispatch a fresh subagent with:
- The full plan context
- The specific task to implement
- Any relevant existing code (file contents, not summaries)
- Instruction to write a failing test first (TDD)

**Stage 2 — Spec Review**
A reviewer subagent checks:
- Does the implementation match what the plan specifies?
- Are all edge cases from the spec handled?
- Does the test actually test what was asked?

**Stage 3 — Code Quality Review**
A second reviewer checks:
- Is the code clean and readable?
- Are there obvious bugs or security issues?
- Does it follow existing patterns in the codebase?

### Review Outcomes

| Result | Action |
|--------|--------|
| Both reviews pass | Commit and move to next task |
| Spec review fails | Re-dispatch execution with reviewer feedback |
| Quality review fails | Fix inline and re-review |
| Both fail | Surface to user before proceeding |

### Dispatch Format

Each subagent should receive:
```
Task: [task name and description from plan]
Context: [relevant existing files]
Requirements:
1. Write a failing test first
2. Implement the minimum code to pass
3. Do not change other files
4. Verify: [verification command from plan]
```

## Principles

- **Fresh context per task** — subagents don't share state; give them everything they need
- **Two-stage review is non-negotiable** — spec compliance first, quality second
- **Critical findings block progress** — a subagent finding a critical issue stops the pipeline
- **Commit after each passing task** — preserve work and maintain a clean history

## When to Fall Back to Executing-Plans

- If subagents are unavailable
- If tasks have tight interdependencies that require shared state
- If the plan has fewer than 3 tasks
