# Skill: Using Git Worktrees

Creates isolated git worktrees for parallel development branches with safety verification.
Trigger: "create worktree", "git worktree", "parallel branch", "isolated workspace"
Output artifact: Clean worktree directory with verified test baseline

---

# Using Git Worktrees

Creates isolated workspaces on new branches. Smart directory selection and safety verification.

## When to Use

- After a design is approved, before implementation starts
- When working on multiple features in parallel
- When you want to keep main clean while experimenting

## Setup Flow

### 1. Create the Worktree

```bash
# From the main repo directory
git worktree add ../project-feature-name feature/feature-name

# Navigate to the worktree
cd ../project-feature-name
```

Naming convention: `../[repo-name]-[feature-slug]`

### 2. Run Project Setup

In the new worktree, run whatever setup the project needs:
```bash
npm install    # or pip install, bundle install, etc.
```

### 3. Verify Clean Baseline

**Before making any changes**, confirm tests pass:
```bash
npm test    # or equivalent
```

If tests are already failing, stop and report this to the user before proceeding. Do not start implementation on a broken baseline.

### 4. Implement

Now the worktree is ready. Use `writing-plans` → `executing-plans` or `subagent-driven-development`.

## Listing and Managing Worktrees

```bash
# See all worktrees
git worktree list

# Remove a worktree after merging
git worktree remove ../project-feature-name
git branch -d feature/feature-name
```

## Safety Rules

- Never force-remove a worktree with uncommitted changes
- Check `git worktree list` before creating a new one to avoid collisions
- Keep worktree directories adjacent to the main repo (not inside it)

## Integration

- Use after `brainstorming` and before implementation
- Use `finishing-a-development-branch` to cleanly close out a worktree
