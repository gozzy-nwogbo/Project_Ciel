# SB Planner Session Prompt Template

_For new conversations in the SB Planner Claude.ai project._

**Used for:** strategic planning, prompt drafting, architectural pushback, multi-session work coordination.

**NOT used for:** execution (use Claude Code), capture (use Telegram), atom queries (use NotebookLM).

---

## Session Declaration

| Field | Value |
|-------|-------|
| Mode | [plan / review / capture / reflect] |
| Goal (one sentence) | [what this session needs to produce] |
| Expected output | [a Claude Code prompt / an architectural decision / a written reflection / a draft document] |

**Test:** Can you read the goal after the session and determine whether it was achieved? If no, rewrite.

**Good:** "Produce a 5-task Claude Code session prompt that ports the humanizer skill from ai_domain into second-brain, with approval gates per task."
**Bad:** "Work on the humanizer." (No output artifact. No success criteria.)

---

## Context to Load

| Source | What to Load | Why |
|--------|-------------|-----|
| Vault state | [point to relevant files in second-brain: PRD, project specs, memory.md updates, recent handoffs] | [what the session needs from each file] |
| External materials | [transcripts, GitHub repos, articles added to project knowledge] | [what role they play in the session] |
| Prior session continuity | [link or summary of last related conversation, if applicable] | [what carried over and what changed since then] |

**Rule:** Name each file. "The relevant project docs" is not a context declaration. If you cannot name the file, the session is not ready.

---

## What I Want From You

Specifically: [push back / draft / review / synthesize / reflect with me]

**Good:** "Push back on whether the three-layer architecture (directives, orchestration, execution) is the right decomposition for this project, or whether two layers would be simpler."
**Bad:** "Help me think about this." (Think about what? In what direction? Against what criteria?)

---

## Constraints

- [If pushback is the goal: state what you're testing the position against]
- [If draft is the goal: state who consumes the output and in what tool]
- [If review is the goal: state what "good" looks like for this review]
- [If multi-session: state what this session must finish vs. what can carry over]

---

## Worked Examples

### Example 1: New project bootstrap (CSC AI Solutions Engineer)

```
Mode: plan
Goal: Produce planning documents to execute the CSC AI Solutions Engineer assessment within a 3-4 day window.
Expected output: project-brief.md, deliverable-checklist.md, architecture sketch.

Context loaded:
- Vault: CLAUDE.md (architecture preferences, n8n patterns), 02-knowledge/business-strategy/
- External: CSC assessment packet (3 build options, questionnaire, video walkthrough requirement)
- Prior session: none (cold start)

What I want: Help me decide which of the three build options to submit, then draft the planning documents for the chosen option.

Constraints:
- Testing the option choice against: CSC's stated evaluation criteria (working automation, error handling, scalability, AI tool usage), the role's marketing focus across 13 brands, and what demonstrates architectural judgment vs. just builder-for-hire.
- Output is consumed by Claude Code as a session prompt for Day 1 execution.
- "Good" means: locked tool stack, per-day schedule, deliverable checklist that doubles as definition-of-done.

How it unfolded:
- Evaluated all three options. Option 3 (Reel Generator) selected because it mapped directly to CSC's marketing need across 13 brands, unlike the scraper (Option 2) or scheduler (Option 1).
- Pushed back on building all three options to show range. Decision: one project deep outperforms three projects shallow. Mention adjacent extensions in video walkthrough instead.
- Tool stack locked early: 9-cog architecture with specific tools per cog. No further tool research after Day 1.
- Produced project-brief.md and deliverable-checklist.md. Both handed to Claude Code for execution.
```

### Example 2: Mid-project architectural pushback (humanizer port)

```
Mode: review
Goal: Stress-test the decision to port the humanizer skill from ai_domain into second-brain.
Expected output: Confirmation or revision of the port decision, with binding constraints for execution.

Context loaded:
- Vault: .claude/memory.md (direction-of-authority entry), 02-knowledge/ai-patterns-and-tells.md (already written by aborted Task 1 in prior session)
- External: Original humanizer skill and reference docs from ~/ai_domain/personalplayground/notebooklm/writing/skills/humanizer/
- Prior session: CSC questionnaire polish session, where humanizer was used manually to audit AI tells

What I want: Push back on whether second-brain is the right home for the humanizer. Test the port against maintenance burden, single-source-of-truth principle, and skill discovery.

Constraints:
- Testing against: does the port create a second copy that drifts, or does it establish a clear upstream?
- Decision must resolve where reference docs live (inside skill folder vs. 02-knowledge/) and who mirrors from whom.
- "Good" means: a clear direction-of-authority statement and a Claude Code session prompt with approval gates per task.

How it unfolded:
- Confirmed port rationale: second-brain is upstream, ai_domain mirrors from it going forward. No bidirectional sync.
- Pushed back on putting reference docs inside the skill folder. Decision: reference docs live in 02-knowledge/ (they're durable knowledge, not skill-specific), skill references them by vault path.
- Skill format matched existing meta skill conventions after a frontmatter format check across .claude/skills/meta/.
- Example.md uses verbatim shipped CSC Q8 text, not invented prose.
- Output: 5-task Claude Code session prompt with approval gates per task.
```

### Example 3: Post-execution reflection (CSC project debrief)

```
Mode: reflect
Goal: Extract reusable lessons from the CSC build for second-brain infrastructure and future time-boxed projects.
Expected output: Debrief document and memory.md update candidates.

Context loaded:
- Vault: 01-projects/csc-ai-engineer/specs/ (project-brief.md, deliverable-checklist.md, architecture-validated.md), 06-daily/2026-04-28.md
- External: none
- Prior session: final CSC build and questionnaire polish session

What I want: Reflect with me on what worked, what broke, and what patterns are worth promoting into second-brain infrastructure.

Constraints:
- Reflection must distinguish reusable patterns (promote to 02-knowledge/ or skill registry) from one-off project artifacts (stay in 01-projects/).
- Memory.md candidates must be durable facts, not ephemeral project state.
- "Good" means: each promoted pattern has a clear application beyond CSC.

How it unfolded:
- Identified three reusable patterns: validate-then-build cadence (Day 1 tool validation caught Pixabay and Higgsfield blockers before any workflow nodes existed), deliverable checklist as spec contract (written Day 1, used as literal definition-of-done every session), n8n MCP partial updates (removeNode/addNode/addConnection pattern for node swaps without touching the UI).
- Surfaced two feedback memories: API budget sequencing (metered APIs render cheapest first), n8n SDK credential wipe (workflow updates wipe auth bindings, require manual re-assignment).
- Documented what didn't work: Veo 2 credit depletion, narration-video duration mismatch, Higgsfield fallback never demonstrated.
- Debrief written to 04-reflections/csc-project-debrief.md.
```
