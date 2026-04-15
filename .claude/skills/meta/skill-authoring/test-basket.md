# Test Basket: skill-authoring

Minimum 3 test cases. Each defines an input skill and expected audit outcome.

---

## Test Case 1 — Perfect Skill (Expected: PASS)

**Input:** A skill file with:
- Single-line description with trigger phrases and output artifact name
- Output contract section with artifact name, path, structure, and out-of-scope
- Input table with all dependencies named and described
- Three binary constraints with no qualitative language
- Three edge cases with explicit handling
- Worked example file in folder matching declared output format
- 80 lines total
- Handoff section naming artifact, location, condition, and routing
- Test basket file with 3 test cases in folder

**Expected Output:** Verdict: PASS. All 9 criteria PASS. Classification: production-ready.

---

## Test Case 2 — Skill with Qualitative Constraints (Expected: DRAFT)

**Input:** A skill file with:
- Single-line description (valid)
- Output contract (valid)
- Input table (valid)
- Constraints using "should," "ideally," and "try to" in 2 of 3 rules
- No edge cases section
- No worked example file in folder
- 90 lines
- Handoff says "pass results to the next agent" with no artifact named
- No test basket file

**Expected Output:** Verdict: DRAFT. Failures on C4 (qualitative constraints), C5 (no edge cases), C6 (no worked example), C8 (vague handoff), C9 (no test basket). 5 criteria fail.

---

## Test Case 3 — Skill That Is Over Line Limit (Expected: DRAFT)

**Input:** A skill file with:
- Single-line description (valid)
- Output contract (valid)
- Input table (valid)
- Binary constraints (valid)
- Four edge cases documented (valid)
- Worked example exists in folder (valid)
- 187 lines total
- Handoff defined with artifact, location, and routing (valid)
- Test basket with 3 cases exists (valid)

**Expected Output:** Verdict: DRAFT. Single failure on C7 (187 lines > 150 limit). 1 criterion fails. All others PASS. Classification: draft — reduce to 150 lines.

---

## Test Case 4 — Skill with Everything Except Description Format (Expected: DRAFT)

**Input:** A skill file with:
- Multi-paragraph "What This Skill Does" section instead of single-line description
- Output contract (valid)
- Input table (valid)
- Binary constraints (valid)
- Three edge cases (valid)
- Worked example (valid)
- 120 lines
- Handoff defined (valid)
- Test basket exists (valid)

**Expected Output:** Verdict: DRAFT. Single failure on C1 (description is multi-line, lacks trigger phrases in a single line). Classification: draft — rewrite description as one unbroken line with trigger context and output artifact name.
