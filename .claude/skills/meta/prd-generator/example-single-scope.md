# Worked Example: Single-Scope Build (Subscription Monitor)

## Input: User answers to mini elicitation

**Q1:** "I need a skill that checks my Go High Level subscription and flags if it's inactive. I'm paying for it but haven't used it in weeks."
**Q2:** "In 90 days, I either know GHL is actively used in my workflows or I've cancelled it. The number that changes is monthly spend — either justified or eliminated."
**Q3:** "I know how to hit the GHL API. Uncertain about what 'active usage' actually means — logins? Workflow triggers? Contact updates?"
**Q4:** "I'd need to believe GHL has an API endpoint that exposes usage metrics. I can check their docs in 30 minutes."
**Q5:** "This competes with the n8n lead gen rebuild. But it's a 2-hour build, not a week."
**Q6:** "If GHL doesn't expose usage data via API, this is dead. That's clear enough."

## Classification

Surface: "Based on your answers, this looks like a **single-scope build** — one integration, one check, days not weeks. I'll produce a spec contract. Does that match your expectation?"

User confirms.

## Output: spec-contract.md (abbreviated)

```markdown
# Spec Contract: GHL Subscription Monitor
_Version: v1 | Author: Gozzy | Date: 2026-04-16 | Status: Draft | Pipeline Stage: Phase 5 skill build_

## Declared Goal
> The system checks Go High Level API weekly for usage activity and surfaces a flag in the morning digest when no meaningful usage is detected in the trailing 14 days.

## Explicit Inputs
| Input File | Path | Purpose | Required |
|---|---|---|---|
| GHL API credentials | .env | Authentication for API calls | Yes |
| Usage definition doc | 01-projects/ghl-monitor/usage-criteria.md | Defines what counts as "active usage" | Yes |

## Output Contract
| Output Artifact | Path | Format | Properties | Consumed By |
|---|---|---|---|---|
| Usage check result | Supabase captures table | JSON | status (active/inactive), last_activity_date, metric_source | Morning digest heartbeat |

[... remaining 5 sections follow template exactly ...]
```

## Elicitation Summary Written To
`01-projects/ghl-monitor/elicitation-2026-04-16.md`
