# Skill: Changelog Generator

Automatically create user-facing changelogs from git commit history. Triggers on: "generate changelog", "write release notes", "summarize what changed", "CHANGELOG.md". Output artifact: `CHANGELOG.md` entry or standalone markdown block.

---

# Changelog Generator

Transforms git commits into human-readable release notes for customers and users.

## When to Use

- Before a release and you need a CHANGELOG entry
- When asked to "summarize what changed" or "write release notes"
- When generating a CHANGELOG.md from scratch or updating an existing one

## Process

### Step 1: Get the Commits

```bash
# Since last tag
git log $(git describe --tags --abbrev=0)..HEAD --oneline --no-merges

# Between two tags
git log v1.2.0..v1.3.0 --oneline --no-merges

# Last N commits
git log -20 --oneline --no-merges
```

### Step 2: Categorize

Map commits to changelog sections:

| Commit type | Changelog section |
|-------------|------------------|
| `feat:` / `add:` | New Features |
| `fix:` / `bug:` | Bug Fixes |
| `perf:` / `optim:` | Performance |
| `security:` | Security |
| `deprecated:` | Deprecations |
| `docs:` | Documentation |
| `chore:` / `build:` | Skip (internal) |
| `refactor:` | Skip (internal) unless user-visible |

### Step 3: Rewrite for Users

Technical -> Human-readable:

| Before | After |
|--------|-------|
| `fix: null check on user.profile` | Fixed a crash that occurred when viewing a profile without a profile picture |
| `feat: add bulk export endpoint` | You can now export multiple records at once from the dashboard |
| `perf: cache user sessions in Redis` | Login and navigation are now significantly faster |

Rules for good changelog entries:
- Write from the user's perspective ("You can now..." / "Fixed an issue where...")
- Explain the impact, not the implementation
- Be specific — avoid "various improvements"
- Group related commits into one entry if appropriate

### Step 4: Format

```markdown
## [1.3.0] - 2025-02-20

### New Features
- You can now export multiple records at once from the dashboard (#234)
- Added dark mode support to the settings panel

### Bug Fixes
- Fixed a crash when opening a profile without a photo
- Fixed incorrect totals in the weekly summary email

### Performance
- Login and navigation are noticeably faster

### Security
- Updated dependencies to address a security advisory
```

## Keep a Changelog Format

If the project uses [keepachangelog.com](https://keepachangelog.com) format, use these sections:
`Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`

## Output Options

Ask the user which format they want:
- Update `CHANGELOG.md` in the project
- Output as markdown for copy/paste
- Format for a specific platform (GitHub Release, Slack, email)
