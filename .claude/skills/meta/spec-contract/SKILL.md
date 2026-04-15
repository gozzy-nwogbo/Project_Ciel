# Spec Contract: [Project or Feature Name]
_Version: [v1, v2...] | Author: [name] | Date: [YYYY-MM-DD] | Status: Draft / Approved | Pipeline Stage: [name of the stage that executes this spec]_

---

## Declared Goal

> [One sentence. Specific and testable. This is the outcome, not the task.]

**Good:** "The homepage loads in under 2 seconds on mobile, presents the value proposition within the first viewport, and provides exactly one primary CTA leading to the portfolio section."
**Bad:** "Build a good homepage." (Not testable. "Good" is not a measurement.)

**Test:** Can an agent read this goal and determine, after the work is done, whether it was achieved? If no, rewrite.

---

## Explicit Inputs

Every file the agent will read to do this work. Named, located, and purpose-stated.

| Input File | Path | Purpose | Required |
|---|---|---|---|
| [file name] | [exact path from project root] | [what the agent learns from this file] | Yes / No |

**Rules:**
- Every file must exist at the stated path before work begins. If it does not exist, the spec is not ready.
- "The relevant files" is not an input declaration. Name each file.
- If an input is produced by a prior pipeline stage, state which stage produces it.

**Good example row:** `ux-brief.md | /ux-brief.md | User archetypes, journey map, and constraints that bound all design decisions | Yes`
**Bad example row:** `Research docs | /docs/ | Background reading | No` (Which docs? What do they contain? Why are they optional?)

---

## Output Contract

What does "done" look like? What files exist when this spec is fulfilled?

| Output Artifact | Path | Format | Properties | Consumed By |
|---|---|---|---|---|
| [artifact name] | [exact path] | [md / json / tsx / etc.] | [key properties the artifact must have] | [next stage + what it requires from this output specifically] |

**Rules:**
- Every output must have a path. An artifact that exists "in chat" does not exist.
- Properties are specific. Not "a complete design system" but "semantic color tokens for primary, secondary, background, surface, text-primary, text-secondary, error, and success; a spacing scale with at least 6 steps; typography scale with heading and body variants."
- If the output is consumed by a downstream stage, state what that stage requires from this output specifically, not just its name.
- If the output feeds into another pipeline stage, name that stage.

**Test:** Could an agent verify, by reading the output file, that every stated property is present? If no, the properties are too vague.

---

## Constraints

Binary rules. Every constraint must be evaluable as TRUE or FALSE with no subjective judgment.

| # | Constraint | Verification Method |
|---|---|---|
| 1 | [Rule statement] | [How to check: file inspection / line count / token search / etc.] |

**Good:** "Amber (#D97706) appears in a maximum of 2 component instances across the entire build. Count by searching for the hex value and the semantic token name."
**Bad:** "Amber should be used sparingly." (What is sparingly? 3? 5? 10?)

**Good:** "Every image has an alt attribute. Verify by searching for `<img` tags without `alt=`."
**Bad:** "Images should be accessible." (Which accessibility property? How verified?)

**Rules:**
- No "should," "ideally," "try to," or "where possible." These are not constraints.
- Every constraint must include its verification method. A rule without a check is aspirational.
- Constraints that conflict with each other must be resolved in this document, not at build time.

---

## Out-of-Scope Declarations

What this spec explicitly does NOT cover. An agent given an incomplete spec will fill the gaps with its own judgment, usually wrong.

| # | Excluded Item | Why Excluded | Where It Lives Instead |
|---|---|---|---|
| 1 | [thing not covered] | [reason] | [which spec or phase owns it, or "not planned"] |

**Rules:**
- If you can imagine an agent attempting this work and going beyond the boundary, that boundary must be declared here.
- "Out of scope" means the agent must not attempt it. Not "it would be nice but isn't required."
- Every exclusion must state where the excluded work lives instead. If nowhere, state "not planned."

**Good:** "Responsive behavior below 320px is out of scope. Owned by: not planned, 320px is the minimum supported width."
**Bad:** "Don't worry about edge cases." (Which edge cases? All of them?)

---

## Dependencies

What must be true before this spec can be executed?

| # | Dependency | Status | Blocking? |
|---|---|---|---|
| 1 | [prior stage / file / decision] | [Done / In Progress / Not Started] | [Yes / No] |

**Rules:**
- A spec with unresolved blocking dependencies is not ready for execution.
- If a dependency is "in progress," state the expected completion condition, not a date.

---

## Success Criteria

How will the approver determine that the output contract has been fulfilled?

| # | Criterion | Test |
|---|---|---|
| 1 | [what success looks like] | [specific, repeatable check] |

**Rules:**
- Success criteria are not a restatement of the goal. They are the specific checks run against the output.
- Every criterion must be runnable by an agent or a human following instructions, no "looks good" or "feels right."
- If any criterion requires human judgment (e.g., brand tone), state that explicitly: "Human review required for: [specific aspect]."

---

## Change Log

| Version | Date | Changed By | What Changed |
|---|---|---|---|
| v1 | [date] | [name] | Initial spec |

---

## Approval

| Field | Value |
|---|---|
| Reviewed by | [name or "pending"] |
| Approved | Yes / No / Pending |
| Approved date | [YYYY-MM-DD or blank] |
| Notes | [any conditions on approval] |

**A spec that has not been approved is a draft. No pipeline runs against a draft spec.**
