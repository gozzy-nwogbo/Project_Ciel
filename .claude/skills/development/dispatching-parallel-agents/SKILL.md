# Skill: Dispatching Parallel Agents

Coordinate concurrent subagent workflows for independent tasks. Triggers on: "parallelize", "dispatch agents", "run these in parallel", "independent tasks". Output artifact: aggregated results with conflict-check report.

---

# Dispatching Parallel Agents

Concurrent subagent workflows for independent tasks.

## When to Use

- Multiple tasks exist that don't depend on each other
- You want to parallelize work to save time
- Tasks are well-defined and self-contained

## Task Independence Check

Before dispatching, verify tasks are truly independent:
- Task B does not read files that Task A writes
- Tasks don't modify the same files
- Tasks don't share mutable state

If tasks are dependent, sequence them — don't parallelize.

## Dispatch Format

Each agent dispatch must include everything the agent needs:

```
Task: [Clear task name]

Context:
- Current file: [file path and full contents]
- Related files: [any other files the agent needs]
- Project conventions: [relevant style/pattern notes]

Instructions:
1. [Step 1]
2. [Step 2]
...

Constraints:
- Only modify [specific files]
- Do not change [things to preserve]
- Follow [specific pattern]

Verify:
- [How to confirm the task succeeded]
```

## Aggregating Results

When agents return:
1. Collect all outputs
2. Check for conflicts (do any agents modify the same file?)
3. If conflicts: resolve manually before committing
4. If clean: commit all changes together
5. Run full test suite after aggregation

## Result Review

For each completed task:
- [ ] Verification step passed?
- [ ] Only touched allowed files?
- [ ] Follows project conventions?
- [ ] Tests pass?

Reject and re-dispatch any task that fails review.

## Limits

- Dispatch at most 5-10 agents at a time
- Prefer smaller batches over large ones (easier to review)
- Don't dispatch more than one agent per file
