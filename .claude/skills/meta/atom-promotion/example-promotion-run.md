# Worked Example: atom-promotion on agent-architecture

## Input State

Staging directory: `00-inbox/staging/framework-atoms/agent-architecture/` with 3 atoms:
- `code-method.md` (valid)
- `para.md` (valid)
- `broken-atom.md` (missing `## Core mechanism` section)

Target directory: `02-knowledge/agent-architecture/` (does not exist yet)

## Pre-flight Output

```
Pre-flight scan complete.

Domains: 1 (agent-architecture)
Total atoms: 3
  - Pass: 2
  - Flag: 1 (broken-atom.md: D8 missing "Core mechanism" section)
  - Errors: 0
  - Collisions: 0

About to promote 2 atoms across 1 domain. 1 will be flagged. 0 errors. Proceed?
```

User responds: "yes"

## Post-run State

### Promoted
- `02-knowledge/agent-architecture/code-method.md` (created, body unchanged)
- `02-knowledge/agent-architecture/para.md` (created, body unchanged)
- `00-inbox/staging/framework-atoms/agent-architecture/code-method.md` (removed)
- `00-inbox/staging/framework-atoms/agent-architecture/para.md` (removed)

### Flagged
`00-inbox/staging/framework-atoms/agent-architecture/broken-atom.md` now has:
```yaml
---
status: flagged
flag_reasons:
  - "D8: missing Core mechanism section"
---
```

### New domain folders created
- `02-knowledge/agent-architecture/`

### Report excerpt
```markdown
## Summary
- Total staged: 3
- Promoted: 2
- Flagged: 1
- Errors: 0
- Reconciliation: PASS (2 + 1 + 0 = 3)
```
