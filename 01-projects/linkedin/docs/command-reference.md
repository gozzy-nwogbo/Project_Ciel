# LinkedIn Engine — Command Reference

**Companion to:** `01-projects/linkedin/docs/2026-05-24-linkedin-engine-design.md`
**Audience:** Power users / scripting / when conversational interface is unavailable

Two slash commands. The conversation interface inside Claude Code handles daily flow; commands exist for explicit/reproducible operations.

---

## `/draft-post` — generation + state transitions

### Bare invocation

```
/draft-post
```
One draft. Auto-picks strategy + atoms based on cooldowns and scoring.

### Generation flags (v1.0)

| Flag | What it does | Example |
|---|---|---|
| `--batch=N` | Generate N drafts in one run (anti-repeat respected within batch) | `/draft-post --batch=3` |
| `--scan` | Exhaustive scan, top-10 candidates by score | `/draft-post --scan` |
| `--strategy=<name>` | Force a strategy. Names: `source_spotlight`, `two_atom_bridge`, `cluster_reveal`, `convergence_finder` | `/draft-post --strategy=convergence_finder` |
| `--source=<name>` | For `source_spotlight`: pick this source | `/draft-post --strategy=source_spotlight --source="Nate B. Jones"` |
| `--atom-a=<slug> --atom-b=<slug>` | For `two_atom_bridge`: specify the pair | `/draft-post --strategy=two_atom_bridge --atom-a=feedback-loops --atom-b=trust-substitution` |
| `--topic=<string>` | For `convergence_finder`: the topic to converge on | `/draft-post --strategy=convergence_finder --topic="naming things"` |
| `--cluster-anchor=<tag>` | For `cluster_reveal`: anchor tag | `/draft-post --strategy=cluster_reveal --cluster-anchor=agent-design` |
| `--since=<date>` | For `cluster_reveal`: timeframe lower bound | `/draft-post --strategy=cluster_reveal --since=2026-04-01` |
| `--tier=<1\|2\|3>` | Force visual tier (default: strategy decides) | `/draft-post --tier=2` |
| `--dry-run` | Show what would be generated without writing files | `/draft-post --batch=5 --dry-run` |

### State transition flags (v1.0)

| Flag | What it does | Example |
|---|---|---|
| `--advance <slug>` | Pass draft through Gate 1 → renderer fires → Gate 2 | `/draft-post --advance 2026-05-24-feedback-loops/` |
| `--kill <slug>` | Move draft to rejections.jsonl | `/draft-post --kill 2026-05-24-trust/ --reason "angle too abstract"` |
| `--reason "..."` | Companion to `--kill` (engine prompts if missing) | (see above) |
| `--render <slug>` | Re-render visual for an existing draft (after brief edit) | `/draft-post --render 2026-05-24-feedback-loops/` |
| `--mark-posted <slug>` | Mark as published; record permalink | `/draft-post --mark-posted 2026-05-24-feedback-loops/ --url=https://linkedin.com/...` |
| `--force` | Bypass voice linter failures | `/draft-post --advance <slug> --force` |

### v2.0 additions (when scheduler ships)

| Flag | What it does |
|---|---|
| `--schedule <slug> --at "<iso8601>"` | Push approved draft to scheduler at specific time |
| `--schedule <slug> --window "tue 9-11"` | Push to scheduler with time window |
| `--unschedule <slug>` | Pull from scheduler queue |

---

## `/linkedin-status` — read-only state surface

### Bare invocation

```
/linkedin-status
```
Full state report: backlog count, pending reviews, recent activity, cooldown picture, next suggested action.

### Filter flags (v1.0)

| Flag | What it shows |
|---|---|
| `--backlog` | Unreviewed drafts only (status: `text_ready` or `gate2_pending`) |
| `--ready` | Drafts approved and waiting to post |
| `--cooldown` | Atom + connection cooldown picture |
| `--rejections [--last=N]` | Recent N rejections (default 10) with reasons |
| `--approvals [--last=N]` | Recent N approvals with edit_delta summary |
| `--cost [--month\|--week]` | Higgsfield + LLM API burn for window |
| `--strategy-mix [--last=N]` | Distribution of last N strategies used (helps diversity check) |
| `--errors [--last=N]` | Recent render/lint errors |

### v2.5 additions (when analytics ships)

| Flag | What it shows |
|---|---|
| `--stats` | Per-post performance: impressions, saves, comments |
| `--stats --by-strategy` | Performance averaged by strategy |
| `--stats --by-tier` | Performance averaged by visual tier |
| `--stats --quadrant` | The four-quadrant approval-vs-performance matrix |
| `--gaps` | Topics where `convergence_finder` failed (signals corpus gaps) |

---

## Conversational equivalents (no command needed)

Every state transition also works through chat inside Claude Code. Examples:

| Spoken | Engine action |
|---|---|
| *"Generate three drafts"* | `/draft-post --batch=3` |
| *"Kill the trust one, angle was too abstract"* | `/draft-post --kill ... --reason "..."` |
| *"Advance the feedback-loops draft but rewrite the second paragraph"* | Edit `approved_text`, log edit_delta, then `--advance` |
| *"What's in the backlog?"* | `/linkedin-status --backlog` |
| *"Why did you pick those atoms?"* | Show the score breakdown from the last run |
| *"Show me my recent rejections"* | `/linkedin-status --rejections` |

The CLI surface exists for: scripting, cron jobs, sessions outside Claude Code, and explicit/reproducible operations. The conversation is the daily interface.

---

## Quick reference card

```
Generation:     /draft-post                    (one)
                /draft-post --batch=3          (small backlog)
                /draft-post --scan             (launch day / wide options)

Force strategy: /draft-post --strategy=convergence_finder --topic="trust"

Approve:        /draft-post --advance <slug>
                (or: "advance the X draft" in chat)

Kill:           /draft-post --kill <slug> --reason "..."
                (or: "kill X because..." in chat)

Re-render:      /draft-post --render <slug>

Mark posted:    /draft-post --mark-posted <slug> --url=...

Check state:    /linkedin-status
                /linkedin-status --backlog
                /linkedin-status --cooldown
                /linkedin-status --rejections
```

---

*Last updated: 2026-05-24*
