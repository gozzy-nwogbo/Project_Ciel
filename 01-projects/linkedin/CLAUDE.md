# CLAUDE.md — LinkedIn Engine

This file documents conventions for the LinkedIn content engine. The engine is
designed to function standalone when extracted from the second-brain vault.

## Purpose

On-demand engine that produces LinkedIn-ready post bundles (text + visual)
from the second-brain atom graph. See `docs/2026-05-24-linkedin-engine-design.md`
for full design.

## Project structure

- `src/` — Python implementation
  - `strategies/` — atom selection → PostBrief
  - `renderers/` — PostBrief → visual asset (Tier 1 only in v1.0)
  - `storage/` — bundle persistence (filesystem in v1.0)
  - `linter/` — voice rule enforcement
  - `usage/` — cooldown tracking + scoring
  - `cli/` — `/draft-post` and `/linkedin-status` entry points
- `tests/` — pytest suite
- `backlog/` — generated post bundles (one folder per post)
- `state/` — atom-usage.json, connection-usage.json, rejections.jsonl, approvals.jsonl
- `logs/` — state.jsonl, cost.jsonl, errors.jsonl
- `brand-spec.md` — visual brand tokens (placeholder in v1.0; replaced by brand revamp)

## Conventions

- All Python code is type-hinted. Pyright-strict where feasible.
- Voice rules enforced via `src/linter/rules.yml`. Edit YAML, not code.
- State transitions ALWAYS go through the storage adapter, never direct JSON writes.
- Atom source path is configurable: defaults to `../../02-knowledge/` relative to project root.
- When extracted from the vault, point the atom source config at any directory of atom markdown files.

## How to run

```
python -m linkedin_engine.cli.draft_post [args]
python -m linkedin_engine.cli.linkedin_status [args]
```

The slash commands at `.claude/commands/draft-post.md` and `.claude/commands/linkedin-status.md` wrap these.

## Testing

```
pytest tests/ -v
```

## Voice rules

See vault-level `CLAUDE.md` §3. Engine enforces a subset programmatically via the voice linter.
