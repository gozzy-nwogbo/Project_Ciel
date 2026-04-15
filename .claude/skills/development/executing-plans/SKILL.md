# Skill: Executing Plans

Execute an implementation plan in batches with human checkpoints. Triggers on: "execute the plan", "start implementation", "go", "run the plan". Output artifact: updated `plan.md` with tasks marked `[x]` and per-batch commit history.

---

# Executing Plans

Activates when a plan is ready and the user says to start. Executes tasks in batches and pauses for human review at checkpoints.

## When to Use

- A `plan.md` exists and the user is ready to implement
- As an alternative to `subagent-driven-development` when single-agent execution is preferred
- When the user wants manual review checkpoints between batches

## Execution Flow

### Before Starting
1. Read `plan.md` in full
2. Confirm the first batch of tasks with the user (default: 3-5 tasks per batch)
3. Check that tests pass before making any changes (clean baseline)

### During Execution
For each task:
1. Read the task description and verify file path exists (or create it)
2. Make the change
3. Run verification step from the plan
4. Mark task as complete in `plan.md` with `[x]`
5. Commit if tests pass

### Checkpoint Behavior
After each batch:
- Report what was completed
- Report any issues or deviations
- Show test results
- Ask: "Continue to next batch?" before proceeding

### On Failure
If a verification step fails:
1. Do not mark the task complete
2. Attempt to fix (max 2 tries)
3. If still failing, stop and report to user with full context
4. Do not proceed to the next task until this one passes

## Principles

- **Never skip verification** — if a task has a verify step, run it
- **Commit often** — after each passing task, commit with a clear message
- **No improvisation** — stick to the plan; if you think something needs to change, ask first
- **Test baseline first** — if tests are already failing before you start, surface that immediately

## Integration

- Works after `writing-plans`
- Calls `test-driven-development` for tasks that involve new logic
- Calls `requesting-code-review` between batches (optional)
