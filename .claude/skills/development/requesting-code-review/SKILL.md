# Skill: Requesting Code Review

Run a pre-review checklist before submitting code for review. Triggers on: "review my code", "pre-review check", "ready for review", "self-review", "before I open a PR". Output artifact: review request markdown block with changes summary, plan reference, testing notes, and open questions.

---

# Requesting Code Review

Pre-review checklist that activates between tasks. Reviews against the plan, reports issues by severity. Critical issues block progress.

## When to Use

- Before opening a pull request
- Between batches of tasks during `executing-plans`
- When you want a structured self-review before involving others

## Pre-Review Checklist

### Against the Plan
- [ ] Every task in the plan is either complete or explicitly deferred
- [ ] No scope creep — changes match what the plan specifies
- [ ] Design document constraints were respected

### Code Quality
- [ ] No debug code left in (console.log, TODO comments that are not meant to ship)
- [ ] Functions do one thing
- [ ] Names are clear and consistent with the codebase
- [ ] Error handling is present at I/O boundaries

### Tests
- [ ] Tests exist for all new logic
- [ ] Tests are meaningful (would catch a real regression)
- [ ] All tests pass

### Security (if applicable)
- [ ] User input is validated/sanitized
- [ ] Authentication checks are present
- [ ] No secrets in code

## Severity Levels

| Severity | Description | Action |
|----------|-------------|--------|
| **Critical** | Bug, security issue, or spec violation | Stop. Fix before proceeding. |
| **Major** | Poor error handling, missing edge case | Fix in current session |
| **Minor** | Style, naming, minor refactor | Note for follow-up |

## Review Request Format

When requesting review from a human:

```markdown
## Changes Summary
[What was built and why]

## Plan Reference
[Link to or summary of the relevant plan tasks]

## Testing
[What was tested and how]

## Concerns / Open Questions
[Anything the reviewer should pay special attention to]
```
