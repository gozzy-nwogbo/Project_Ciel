# Worked Example — FAIL (DRAFT)

This example shows the skill-authoring meta-skill evaluating the existing `design-review` skill from the design pipeline. It demonstrates how a well-written, useful skill can still be classified as DRAFT under the authoring standard.

---

## The Skill Being Evaluated

**File:** `/design/skills/design-review/SKILL.md` (150 lines)
**Folder contents:** `SKILL.md`, `references/review-checklist.md`

---

## The Audit Report

```markdown
# Skill Audit: design-review
_Evaluated: 2026-03-31 | Standard: skill-authoring v1_

## Verdict: DRAFT

| # | Criterion | Result | Evidence |
|---|---|---|---|
| C1 | Single-Line Description | FAIL | No single-line description exists. Lines 3-4 are a multi-line "What This Skill Does" paragraph. The paragraph does describe the skill's function but is not a single unbroken line with trigger phrases and output artifact name. |
| C2 | Output Contract | PASS | Output Format section (line 47+) names the artifact (review-[component].md), path (/reviews/), and structure (severity-classified table). Soft Gate Rules section clarifies what the skill does not decide (promotion). |
| C3 | Input Contract | PASS | Prerequisites section (line 17) lists three required inputs by name with checkboxes: ux-brief.md, system.md, and completed work. |
| C4 | Constraints as Rules | FAIL | Soft Gate Rules contain "should be resolved before final handoff" (line 119) — "should" is not binary. Pattern Recognition section (line 128+) uses qualitative terms like "too small to evaluate quality" without a size threshold. |
| C5 | Edge Cases Declared | FAIL | No edge cases section exists. The Pattern Recognition section lists common issues but does not address ambiguous situations (e.g., what if system.md doesn't cover the component being reviewed? What if the builder disputes all findings?). |
| C6 | Worked Example Exists | FAIL | Folder contains only SKILL.md and references/review-checklist.md. No worked example showing the skill applied to a real component with the resulting review output. |
| C7 | Core File Under 150 Lines | PASS | 150 lines — at the boundary but within limit. |
| C8 | Handoff Defined | FAIL | Handoff Status section (line 103) describes three possible statuses but does not name the specific artifact the next stage receives, or state which pipeline stage receives it. "Ready for handoff" does not say handoff to what. |
| C9 | Test Basket Exists | FAIL | No test basket file in the skill folder. No test cases with defined inputs and expected outputs. |

## Failing Criteria — Required Fixes

| # | Criterion | Required Fix |
|---|---|---|
| C1 | Single-Line Description | Replace "What This Skill Does" section with a single unbroken description line after the header. Must include trigger phrases ("after a section is complete," "before handoff") and output artifact name ("review-[section].md"). |
| C4 | Constraints as Rules | Replace "should be resolved" with a binary statement. Replace "too small to evaluate quality" with a pixel or viewport-percentage threshold. Every constraint must be testable as true/false. |
| C5 | Edge Cases Declared | Add an Edge Cases section with minimum 3 cases. Suggested: (1) system.md doesn't cover the component, (2) builder disputes all findings, (3) review is requested for work-in-progress rather than complete work. |
| C6 | Worked Example Exists | Create an example file showing the skill applied to a sample component. Input: a component with 2 intentional issues. Output: the review report in the declared format with those issues classified. |
| C8 | Handoff Defined | Add explicit handoff: name the artifact (review-[section].md), its location (/reviews/), and which stage receives it (the builder for rework, or the orchestrator for routing to the next section). |
| C9 | Test Basket Exists | Create a test basket with minimum 3 test cases. Suggested: (1) component with no issues, (2) component with one critical accessibility failure, (3) component with mixed severity issues across all four categories. |

## Classification
DRAFT — 6 of 9 criteria fail. Skill is functional but does not meet the production authoring standard. Fix all failing criteria and re-run this audit.
```

---
