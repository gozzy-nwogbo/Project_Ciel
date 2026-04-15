# Test Basket: orchestrator

Minimum 3 test cases. Each defines project state and expected routing output.

---

## Test Case 1 — Happy Path: Fresh Design Project

**Input (files on disk):**
- `CLAUDE.md` — exists, configured for portfolio project
- `ux-brief.md` — does NOT exist
- No other pipeline state files

**Expected Output:**
- Active pipelines: Design (initiated by CLAUDE.md project config)
- Position: Stage 1 — ux-research
- Required inputs checked: Project brief or WRITING.md (must exist — if missing, BLOCKED)
- If project brief exists: Route to ux-research
- If project brief does NOT exist: BLOCKED — "No project brief or WRITING.md. Provide project inputs to begin."
- No escalation signals (no review files)
- Status report produced with routing decision
- Verdict: PASS — deterministic routing to Stage 1

---

## Test Case 2 — Partial Failure: Missing Required Input Mid-Pipeline

**Input (files on disk):**
- `ux-brief.md` — exists
- `design-principles-portfolio.md` — does NOT exist (design-principles was skipped or failed)
- `.interface-design/system.md` — does NOT exist

**Expected Output:**
- Active pipelines: Design
- Position: Stage 2 — design-principles
- Required inputs checked: ux-brief.md (exists), notebook-ids.json (check disk — if missing: BLOCKED), references/query-patterns.md (check disk — if missing: BLOCKED)
- If notebook-ids.json is missing: BLOCKED — "Pipeline blocked — notebook-ids.json does not exist. Required by design-principles. Ensure NotebookLM notebook IDs are configured."
- If all inputs present: Route to design-principles
- Orchestrator does NOT skip to design-system even though ux-brief.md exists — stages are sequential, Stage 2 must complete first
- Verdict: PASS — gates correctly on missing inputs, does not skip stages

---

## Test Case 3 — Edge Condition: Review File Triggers Escalation

**Input (files on disk):**
- Full design pipeline complete through 2 sections:
  - `reviews/review-hero.md` — exists, Handoff Status: "Ready with logged issues." Contains 1 Warning under "Design System Consistency"
  - `reviews/review-about.md` — exists, Handoff Status: "Ready with logged issues." Contains 1 Warning under "Design System Consistency"
  - Third section (Portfolio) built but not yet reviewed

**Expected Output:**
- Active pipelines: Design
- Position: Stage 5 — design-review (for Portfolio section)
- Escalation detected: "Design System Consistency" warnings appear in 2 review files (hero and about)
- Status report includes escalation flag: "Escalation required — Design System Consistency issues found in 2 review files. This is a system fix, not a component fix. Update .interface-design/system.md before next build stage."
- Routing decision: BLOCKED on escalation — "Resolve system-level Design System Consistency issue in .interface-design/system.md before reviewing Portfolio section. Revalidate hero and about sections after system update."
- Orchestrator does NOT route to design-review for Portfolio until escalation is acknowledged
- Verdict: PASS — escalation detection works, blocks routing correctly

---

## Test Case 4 — Edge Condition: Both Pipelines Active

**Input (files on disk):**
- Design pipeline: ux-brief.md exists, design-principles exists, system.md exists, hero section built, reviews/review-hero.md exists with "Ready"
- Writing pipeline: content-brief.md exists, outline.md exists, no voice-brief.md

**Expected Output:**
- Active pipelines: Both
- Design pipeline position: Stage 4 — builder (next section to build). Routing: "Next: builder stage. No skill file — human-executed. Confirm .interface-design/system.md is present."
- Writing pipeline position: Stage 3 — voice-style. Routing: Route to voice-style. Required inputs: WRITING.md, outline.md, content-brief.md.
- Both pipelines reported independently — no interleaving
- Human decides which to advance first
- Verdict: PASS — dual pipeline routing works independently
