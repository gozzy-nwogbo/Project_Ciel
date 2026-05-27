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
  - `renderers/` — PostBrief → visual asset. As of v1.2, three Tier 1 renderers behind a registry:
    - `atom_card.py` — source_spotlight, 1:1 canvas
    - `bridge_card.py` — two_atom_bridge, 4:5 canvas, pillars + mechanism band
    - `convergence_card.py` — convergence_finder, 4:5 canvas, funnel + convergence panel
    - `registry.py` — `for_strategy(strategy_name, **kwargs)` dispatches to the right class
    - `templates/_card_frame.css.j2` — shared CSS partial for bridge + convergence (atom_card still inlines its own CSS)
  - `storage/` — bundle persistence (filesystem in v1.0)
  - `linter/` — voice rule enforcement
    - `tagged.py` — generic `<TAG>...</TAG>` extractor (v1.2)
    - `thesis.py` — thin wrapper over `tagged.extract_tagged(body, "THESIS")`
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
- Per-strategy visual aspect ratios (v1.2): source_spotlight = 1:1; two_atom_bridge = 4:5; convergence_finder = 4:5. Strategies set `aspect_ratio` on the brief; renderers validate it.
- Voice prompt v3 (v1.2) requires `<THESIS>...</THESIS>` universally and `<CLAIM>...</CLAIM>` for two_atom_bridge + convergence_finder only. The text generator strips both tag pairs from the saved `post.md`.
- State transitions ALWAYS go through the storage adapter, never direct JSON writes.
- Atom source path is configurable: defaults to `../../02-knowledge/` relative to project root.
- When extracted from the vault, point the atom source config at any directory of atom markdown files.
- `convergence_finder` (v1.3+) selects atom triples by semantic coherence using OpenAI `text-embedding-3-small`. Requires `OPENAI_API_KEY` in env. Embeddings cached at `.cache/atom-embeddings.json` (gitignored, SHA-256 body-hash invalidated). Default coherence threshold is `0.35` min pairwise cosine; override via `LINKEDIN_CONVERGENCE_MIN_SIM` env var or per-call `min_sim` param. When no candidate triple clears the threshold, the strategy raises `ValueError` with a diagnostic payload (best min_sim, top 3 candidate slug triples). Graph-connectivity is no longer a selection signal for this strategy.

## How to run

**Inside Claude Code (preferred):**

```
/draft-post --strategy=convergence_finder --topic=feedback
/draft-post --advance <slug>
/linkedin-status
```

The slash commands at `.claude/commands/draft-post.md` and `.claude/commands/linkedin-status.md` set env vars internally. No manual `PYTHONPATH=` or `LINKEDIN_*` exports needed.

**Terminal (anywhere on disk):**

```
./bin/draft-post --strategy=convergence_finder --topic=feedback
./bin/draft-post --advance <slug>
```

The wrapper at `01-projects/linkedin/bin/draft-post` bundles `PYTHONPATH=src`, `LINKEDIN_ATOM_SOURCE`, `LINKEDIN_PROJECT_ROOT`, `LINKEDIN_BRAND_SPEC` and forwards args to `python3 -m cli.draft_post`.

**Raw invocation (only when debugging the wrapper itself):**

```
cd 01-projects/linkedin
PYTHONPATH=src python -m cli.draft_post [args]
```

Avoid this form in daily use. If you find yourself pasting env-var prefixes, you're doing it wrong: use the slash command or the wrapper.

## One-time install

After `pip install -r requirements.txt`, install the Chromium binary
Playwright uses for the Tier 1 renderer:

    python -m playwright install chromium

## Testing

```
pytest tests/ -v
```

## Voice rules

See vault-level `CLAUDE.md` §3. Engine enforces a subset programmatically via the voice linter.
