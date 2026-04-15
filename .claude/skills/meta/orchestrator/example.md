# Worked Example: orchestrator

Two scenarios — one design pipeline (mid-project) and one writing pipeline (fresh start).

---

## Scenario 1 — Design Pipeline: Mid-Project, System Built, No Review Yet

### Project State (files on disk)

- `ux-brief.md` — exists (produced by ux-research)
- `design-principles-portfolio.md` — exists (produced by design-principles)
- `.interface-design/system.md` — exists (produced by design-system)
- `src/components/Hero.tsx` — exists (builder completed hero section)
- `reviews/review-hero.md` — does NOT exist

### Orchestrator Execution

**Step 1 — Identify active pipelines:**
ux-brief.md and system.md exist → Design pipeline is active.
No content-brief.md or writing files → Writing pipeline is not active.

**Step 2 — Determine position:**
Walk design routing table:
- Stage 1: ux-brief.md exists → skip
- Stage 2: design-principles-portfolio.md exists → skip
- Stage 3: .interface-design/system.md exists → skip
- Stage 4: Hero section built → skip
- Stage 5: No reviews/review-hero.md → **current position**

**Step 3 — Gate on inputs:**
design-review requires: ux-brief.md (exists), .interface-design/system.md (exists), completed work (Hero.tsx exists). All inputs confirmed.

**Step 4 — Escalation check:**
No review files exist yet → no escalation signals.

**Step 5 — Status report:**

```
PIPELINE STATUS — 2026-04-04

Active pipelines: Design

## Design Pipeline
Position: Stage 5 — design-review
Next action: Invoke design-review
Required inputs: ux-brief.md ✓ | system.md ✓ | Hero.tsx ✓
Blockers: none
Escalations: none

## Routing Decision
→ design-review — Review hero section against brief, system, accessibility, and responsive criteria. Produces reviews/review-hero.md.
```

---

## Scenario 2 — Writing Pipeline: Fresh Start, Only WRITING.md Exists

### Project State (files on disk)

- `WRITING.md` — exists (content type: thought leadership, platform: LinkedIn, voice mode: personal)
- No content-brief.md, no outline.md, no voice-brief.md, no drafts, no reviews

### Orchestrator Execution

**Step 1 — Identify active pipelines:**
No content-brief.md or writing files → Writing pipeline is NOT yet active (no stage outputs exist).
However, WRITING.md exists with content type filled in → writing pipeline can be initiated.
No design files → Design pipeline not active.

**Step 2 — Determine position:**
Walk writing routing table:
- Stage 1: No content-brief.md → **current position**

**Step 3 — Gate on inputs:**
content-research requires: WRITING.md filled in (exists, content type and platform confirmed), voice mode identified (present in WRITING.md). All inputs confirmed.

**Step 4 — Escalation check:**
No review files exist → no escalation signals.

**Step 5 — Status report:**

```
PIPELINE STATUS — 2026-04-04

Active pipelines: Writing

## Writing Pipeline
Position: Stage 1 — content-research
Next action: Invoke content-research
Required inputs: WRITING.md ✓ | voice mode: personal ✓
Blockers: none
Escalations: none

## Routing Decision
→ content-research — Research topic, define angle, retrieve NotebookLM principles, check Reddit signal. Produces content-brief.md.
```
