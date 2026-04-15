# Skill Audit: n8n-validation-expert

**Date**: 2026-04-14
**Skill**: n8n-validation-expert
**Source**: /path/to/n8n-skills/skills/n8n-validation-expert/SKILL.md
**Lines**: 761

---

## Criteria Evaluation

### C1: Single-line description with trigger context + output artifact named
**PASS** - Description block includes what it does (interpret validation errors and guide fixing), trigger phrases (validation error, warning, false positive, operator structure, validation profile), and output artifact (diagnosis with fix instructions or corrected configuration JSON).

### C2: Output contract (artifact name, path, structure, out-of-scope declared)
**FAIL** - No formal output contract. Produces error diagnoses and fix guidance but does not declare artifact name, path, structure, or out-of-scope boundaries.

### C3: Input contract (all inputs named with purposes)
**FAIL** - No formal input contract. Implicitly expects validation result output but does not enumerate required inputs with purposes.

### C4: Constraints as binary testable rules (no "should"/"ideally")
**FAIL** - Contains "Should Fix" as a severity level header. Uses "When acceptable" framing for false positives which is judgment-based rather than binary. Some rules are binary ("Errors must be fixed") but the false positive handling is inherently non-binary.

### C5: Edge cases declared (>=3 with handling instructions)
**PASS** - Declares multiple edge cases: (1) false positive "missing error handling" with when-acceptable criteria, (2) patchNodeField find string not found, (3) ambiguous match multiple occurrences, (4) paradoxical corrupt states requiring DB intervention, (5) circular dependencies in workflow validation.

### C6: Worked example file exists in same folder
**FAIL** - No standalone worked example file. The validation loop example is inline. ERROR_CATALOG.md and FALSE_POSITIVES.md are reference files, not worked examples.

### C7: Core file <=150 lines
**FAIL** - SKILL.md is 761 lines. Expected failure per task brief.

### C8: Handoff defined (specific artifact, location, condition)
**FAIL** - No explicit handoff section defining artifact, location, or completion condition.

### C9: Test basket file with >=3 cases exists in folder
**FAIL** - No test basket file exists in the folder.

---

## Summary

| Criterion | Result |
|-----------|--------|
| C1 | PASS |
| C2 | FAIL |
| C3 | FAIL |
| C4 | FAIL |
| C5 | PASS |
| C6 | FAIL |
| C7 | FAIL |
| C8 | FAIL |
| C9 | FAIL |

**Passing**: 2/9
**Verdict**: **DRAFT**
