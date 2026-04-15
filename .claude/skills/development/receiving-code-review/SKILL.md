# Skill: Receiving Code Review

Process and respond to code review feedback constructively. Triggers on: "address review comments", "fix review feedback", "respond to PR comments", "code review received". Output artifact: updated branch with all review comments addressed and summary comment posted.

---

# Receiving Code Review

How to process and respond to code review feedback without dropping anything.

## When to Use

- After receiving PR review comments
- When a reviewer has flagged issues to fix
- When deciding which review feedback to act on

## Processing Feedback

### Step 1: Categorize All Comments

Go through every comment and label it:

| Category | Description |
|----------|-------------|
| **Must fix** | Bug, spec violation, or the reviewer explicitly requires change |
| **Should fix** | Valid improvement the reviewer recommends |
| **Consider** | Suggestion or question, may or may not apply |
| **Disagree** | You believe the current approach is correct |

### Step 2: Respond to Everything

Every comment deserves a response, even if just "Done" or "I'll address this in a follow-up."

Do not silently ignore comments — that creates uncertainty about whether they were seen.

### Step 3: For "Disagree" Items

Don't just dismiss. Engage:
1. Understand what problem the reviewer is trying to solve
2. Explain your reasoning clearly
3. If they still disagree after discussion, default to their preference unless there's a strong technical reason not to

### Step 4: Fix and Re-Request

After addressing all must-fix and should-fix items:
1. Run the full test suite
2. Run `verification-before-completion`
3. Push the changes
4. Add a comment summarizing what was changed

## Principles

- **Reviews are about the code, not you** — don't take feedback personally
- **Reviewer intent matters** — understand what they're trying to achieve before responding
- **"It works" is not a response to a quality concern**
- **Agree where you agree** — acknowledging good feedback builds trust
