---
description: Read-only state surface for the LinkedIn content engine
allowed-tools: Bash, Read
---

# /linkedin-status

Read-only view of the LinkedIn engine state. See `01-projects/linkedin/docs/command-reference.md` for flags.

## Behavior

When the user types `/linkedin-status [args]`:

```bash
cd /Users/gozzynwogbo/second-brain/01-projects/linkedin && \
LINKEDIN_PROJECT_ROOT=/Users/gozzynwogbo/second-brain/01-projects/linkedin \
python -m cli.linkedin_status $ARGS
```

## Defaults

- Bare invocation: full state report (all bundles + their statuses).
- `--backlog`: only unreviewed drafts.
- `--cooldown`: atom cooldown picture.
- `--rejections [--last=N]`: recent rejections.
- `--approvals [--last=N]`: recent approvals with edit_delta magnitude.

## Read-only

This command does not write state. No permission_log entries required.
