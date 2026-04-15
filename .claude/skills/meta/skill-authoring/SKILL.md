# Skill: skill-authoring

Evaluates any skill file against the V2 authoring standard and produces a structured pass/fail report — run this before any skill enters a pipeline, returns a binary verdict per criterion with an overall PASS or DRAFT classification.

---

## When to Trigger

- Before any new skill is added to a pipeline (design, writing, or any future system)
- When an existing skill is updated and needs revalidation
- When retroactively auditing skills that predate this standard

Do NOT skip this because the skill "looks fine." The standard exists precisely for cases where problems are invisible to casual reading.

---

## Inputs

| Input | Required | Description |
|---|---|---|
| The skill's `SKILL.md` file | Yes | The file being evaluated |
| The skill's folder contents | Yes | To verify worked examples, references, and test basket exist |
| This checklist | Yes | The evaluation criteria below |

---

## Constraints

- Every criterion evaluation must cite specific evidence from the skill file — never assert PASS or FAIL without quoting or pointing to the relevant section
- The audit report must be completable by an agent with no human input — the criteria are the criteria, not guidelines
- Do not add criteria beyond C1-C9 during an audit — scope changes go through the authoring standard update process
- A skill with 9/9 PASS is production-ready; 8/9 is a draft — there is no "close enough"

---

## Evaluation Criteria

Each criterion is binary: **PASS** or **FAIL**. There is no partial credit.

### C1 — Single-Line Description
The skill file contains exactly one description line immediately after the `# Skill:` header. This line is unbroken (no line breaks within it). It contains: what the skill does, when an agent should invoke it, and the name of the output artifact.
- **PASS:** One unbroken line with trigger context and output artifact named.
- **FAIL:** Description is missing, spans multiple lines, or omits trigger context or output name.

### C2 — Output Contract
The skill declares what it produces as a contract: artifact name, file path, and structure. It also declares what it does NOT produce (out-of-scope).
- **PASS:** Output section names the artifact, its path, its structure, and explicitly states what is out of scope.
- **FAIL:** Output is described in prose without a concrete artifact, path is missing, or out-of-scope is absent.

### C3 — Input Contract
The skill declares every input it requires before running. Each input is named and its purpose stated.
- **PASS:** All required inputs listed with names and purposes. No implicit dependencies.
- **FAIL:** Inputs are vague ("the relevant files"), unnamed, or incomplete.

### C4 — Constraints as Rules
Constraints are binary and testable. No qualitative language ("should be concise," "keep it clean").
- **PASS:** Every constraint can be evaluated as true or false by an agent with no subjective judgment.
- **FAIL:** Any constraint requires interpretation or subjective assessment.

### C5 — Edge Cases Declared
The skill explicitly addresses what happens in ambiguous or boundary situations. These are written out, not assumed.
- **PASS:** At least three edge cases documented with explicit handling instructions.
- **FAIL:** No edge cases section, or edge cases rely on "use your judgment."

### C6 — Worked Example Exists
At least one worked example exists alongside the skill file in the same folder. The example shows the skill being applied to a real or realistic input and producing the declared output.
- **PASS:** Example file exists, shows input and output, and matches the skill's declared contract.
- **FAIL:** No example, or example does not match the declared output format.

### C7 — Core File Under 150 Lines
The `SKILL.md` file is 150 lines or fewer.
- **PASS:** Line count <= 150.
- **FAIL:** Line count > 150.

### C8 — Handoff Defined
The skill declares what the next stage in the pipeline receives after this skill completes. This is a specific artifact or state, not a general description.
- **PASS:** Handoff section names the artifact, its location, and the condition under which handoff occurs.
- **FAIL:** Handoff is missing or vague ("pass to the next agent").

### C9 — Test Basket Exists
A test basket with minimum 3 inputs and expected outputs exists in or alongside the skill folder.
- **PASS:** Test basket file exists with >= 3 test cases, each with defined input and expected output.
- **FAIL:** No test basket, or fewer than 3 cases, or expected outputs missing.

---

## Output Contract

**Produces:** `skill-audit-[skill-name].md` in the same folder as the evaluated skill.

**Structure:**

```markdown
# Skill Audit: [skill-name]
_Evaluated: [date] | Standard: skill-authoring v1_

## Verdict: PASS / DRAFT

| # | Criterion | Result | Evidence |
|---|---|---|---|
| C1 | Single-Line Description | PASS/FAIL | [one-line justification] |
| C2 | Output Contract | PASS/FAIL | [one-line justification] |
| C3 | Input Contract | PASS/FAIL | [one-line justification] |
| C4 | Constraints as Rules | PASS/FAIL | [one-line justification] |
| C5 | Edge Cases Declared | PASS/FAIL | [one-line justification] |
| C6 | Worked Example Exists | PASS/FAIL | [one-line justification] |
| C7 | Core File Under 150 Lines | PASS/FAIL | [one-line justification] |
| C8 | Handoff Defined | PASS/FAIL | [one-line justification] |
| C9 | Test Basket Exists | PASS/FAIL | [one-line justification] |

## Failing Criteria — Required Fixes
[For each FAIL: what specifically must change to pass. If no failures: "None."]

## Classification
- **PASS (all 9 criteria):** Skill is production-ready. Eligible for promotion gate.
- **DRAFT (any failure):** Skill is not production-ready. Fix failing criteria and re-run.
```

**Does NOT produce:** Prose feedback, subjective quality assessments, or recommendations beyond the nine criteria. This is an audit, not a review.

---

## Edge Cases

1. **Skill under evaluation IS this skill (self-referential audit):** Run normally. Every criterion applies. If this skill fails its own standard, it is a draft.
2. **Skill has a `references/` folder but no worked example file:** FAIL on C6. References are not examples. A worked example shows the skill applied to input and producing output.
3. **Skill has a test section inline but no separate test basket file:** FAIL on C9. Test basket must be a separate file so it can be run independently of reading the skill.
4. **Description is one line but is vague ("does design stuff"):** FAIL on C1. The line must contain trigger context and output artifact name, not just a category.
5. **Constraints use "should" or "ideally":** FAIL on C4. Every constraint must be binary. "Should" is not binary.

---

## Handoff

After this skill completes, the next stage receives:
- **Artifact:** `skill-audit-[skill-name].md` at the evaluated skill's folder path
- **Condition:** The audit is complete when every criterion has a PASS or FAIL with evidence
- **Routing:** If verdict is PASS, skill is eligible for the promotion gate (Phase 3). If DRAFT, skill returns to the author for fixes.
