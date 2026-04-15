# Skill: Finishing a Development Branch

Complete a development branch by choosing the right next step: merge, open a PR, keep for later, or discard. Triggers on: "finish branch", "merge this", "open a PR", "done with this branch", "clean up branch". Output artifact: merged main or open PR URL, plus cleaned worktree.

---

# Finishing a Development Branch

Guides completion of development work. Presents clear options and handles the chosen workflow cleanly.

## When to Use

- All tasks in the plan are marked complete
- Tests pass
- Code review is done (or not required)
- Ready to decide what happens next with this branch

## Pre-Flight Check

Before presenting options, verify:
- [ ] All plan tasks are complete (`[x]` in plan.md)
- [ ] All tests pass
- [ ] No debug/temporary code is committed
- [ ] `verification-before-completion` has been run

If any check fails, stop and fix before proceeding.

## Options to Present

Present these options clearly to the user:

### Option A: Merge to Main
```bash
git checkout main
git merge feature/feature-name --no-ff -m "feat: [description]"
git push origin main
git worktree remove ../project-feature-name
git branch -d feature/feature-name
```
*Use when: small change, solo project, or team has approved*

### Option B: Open a Pull Request
```bash
git push origin feature/feature-name
# Then open PR via gh CLI or web
gh pr create --title "feat: [description]" --body "[summary]"
```
*Use when: team review required, want CI to run first*

### Option C: Keep Branch, Close Worktree
```bash
git push origin feature/feature-name
git worktree remove ../project-feature-name
# Branch stays, worktree is removed
```
*Use when: work is done but merge decision is deferred*

### Option D: Discard
```bash
git worktree remove ../project-feature-name
git branch -D feature/feature-name
```
*Use when: the experiment didn't work out*

## After Merging

1. Delete the worktree directory
2. Delete the local branch
3. Pull latest main to confirm the merge is visible
4. Archive `plan.md` and `design.md` if desired

## PR Description Template

```markdown
## What
[One paragraph: what does this change do]

## Why
[Why was this change needed]

## How
[Brief description of implementation approach]

## Testing
[How was this tested]

## Related
[Links to design doc, issue, etc.]
```
