# Skill: orchestrator

Reads project state by checking for key pipeline files on disk, determines which pipeline stage is next, gates on required inputs, and produces a status report with a deterministic routing decision — trigger at the start of any pipeline run, after any skill completes, or when project state is unclear — produces a status report (inline or saved to `pipeline-status.md`).

---

## Inputs

| Input | Required | Description |
|---|---|---|
| Project directory | Yes | The root directory containing all pipeline state files — orchestrator checks disk, never assumes |
| `references/routing-tables.md` | Yes | Design pipeline, writing pipeline, supporting skill routing tables, and state file registry |
| CLAUDE.md | Yes | Project configuration — pipeline structure and hard rules |

---

## Routing Protocol

### Step 1 — Identify active pipelines
Check for the existence of pipeline-initiating files:
- If `ux-brief.md` OR `.interface-design/system.md` OR `reviews/review-*.md` exists → **Design pipeline is active**
- If `content-brief.md` OR `outline.md` OR `.writing/drafts/*.md` → **Writing pipeline is active**
- If neither → **No pipeline active.** Surface: "No brief exists. Provide a project brief or spec contract to begin. Ideation pipeline not yet available."

Both pipelines can be active simultaneously.

### Step 2 — Determine pipeline position
For each active pipeline, walk the routing table in `references/routing-tables.md` from Stage 1 forward. The first stage whose output file does NOT exist is the current position. If all stage outputs exist, check the most recent review file's Handoff Status.

### Step 3 — Gate on required inputs
Before routing, verify every required input for the target skill exists on disk. For each missing file:
- Name the missing file
- Name the skill that produces it
- State: "Pipeline blocked — [file] does not exist. Run [skill] first."

**Never route to a skill whose required inputs are missing.**

### Step 4 — Check for escalation signals
Read all existing `reviews/review-*.md` files. If the same issue category (Brief Alignment, Design System, Accessibility, Responsive, Voice Consistency, Platform Fit, Humanizer) appears with Warning or Critical severity in 2 or more review files:
- Flag: "Escalation required — [category] issues found in [N] review files. This is a system fix, not a component fix. Update [system artifact] before next build stage."
- Block routing to the next build stage until the escalation is acknowledged.

### Step 5 — Produce status report
Output the status report using the format below. This is the orchestrator's only output.

---

## Status Report Format

```
PIPELINE STATUS — [date]

Active pipelines: [Design / Writing / Both / None]

## [Pipeline Name] Pipeline
Position: Stage [N] — [stage name]
Next action: Invoke [skill name]
Required inputs: [list — all confirmed present / blocked on [file]]
Blockers: [none / list]
Escalations: [none / list]

## Routing Decision
→ [skill name] — [one sentence: what it will do and what it will produce]
  OR
→ BLOCKED — [reason]
  OR
→ COMPLETE — [pipeline finished, all stages done, no unresolved reviews]
```

---

## Output Contract

**Produces:** A status report containing a deterministic routing decision for the next pipeline action. The report names the skill to invoke, confirms its inputs exist, and surfaces any blockers or escalations.

**Does NOT produce:** skill outputs, file modifications, design decisions, written content, or review reports. The orchestrator reads and routes — it never builds, writes, or fixes.

---

## Constraints

- Routing is deterministic — given identical project state (same files on disk), the orchestrator must produce the identical routing decision every time
- The orchestrator checks file existence on disk — it never assumes a file exists from conversation context or prior runs
- The builder stage in the design pipeline has no SKILL.md — the routing decision must state: "Next: builder stage. No skill file — human-executed. Confirm .interface-design/system.md is present."
- A review file with "Needs rework" in its Handoff Status routes back to the builder/writer — it does not advance to the next stage
- Escalation detection runs on every orchestrator invocation, not only when advancing to a new stage
- The orchestrator never skips a stage — if Stage 2's output is missing, it routes to Stage 2 even if Stage 3's inputs happen to exist from a prior run

---

## Edge Cases

1. **Both pipelines are active and both need routing:** Produce a status report for each pipeline independently. Do not interleave them. If both are blocked, report both blockers. The human decides which pipeline to advance first — the orchestrator does not prioritize between pipelines.

2. **A state file exists but is incomplete or marked as draft:** If the file exists on disk, the orchestrator treats it as present — it does not evaluate file content quality. Quality evaluation is the responsibility of the skill that produced the file (via its Quality Gate) and the review skill. The orchestrator gates on existence, not correctness.

3. **Review file exists but has no Handoff Status section:** Treat as incomplete. Route to the review skill to re-run: "Review file for [section] exists but has no Handoff Status. Re-run [design-review / writing-review] to complete the review." Do not advance past an incomplete review.

---

## Handoff

- **Artifact:** Status report (inline or `pipeline-status.md`)
- **Location:** Inline in the conversation or saved to project root
- **Condition:** All active pipelines have been evaluated, all routing decisions are stated, all blockers and escalations are surfaced
- **Routing:** The status report is consumed by the **human operator** who invokes the recommended skill. The orchestrator does not invoke skills directly. After the invoked skill completes, the orchestrator is re-run to determine the next action.
