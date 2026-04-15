# Skill Audit: n8n-code-python

**Date**: 2026-04-14
**Skill**: n8n-code-python
**Source**: /path/to/n8n-skills/skills/n8n-code-python/SKILL.md
**Lines**: 748

---

## Criteria Evaluation

### C1: Single-line description with trigger context + output artifact named
**PASS** - Description block includes what it does (write Python in n8n Code nodes), trigger phrases (writing Python in n8n, _input/_json/_node syntax), and output artifact (Python code block for n8n Code node configuration).

### C2: Output contract (artifact name, path, structure, out-of-scope declared)
**FAIL** - No formal output contract. Produces Python code guidance inline but does not declare artifact name, output path, structure schema, or out-of-scope boundaries.

### C3: Input contract (all inputs named with purposes)
**FAIL** - No formal input contract listing required inputs with purposes.

### C4: Constraints as binary testable rules (no "should"/"ideally")
**FAIL** - Contains soft language: "Consider JavaScript first" (recommendation), "significantly more comfortable with Python syntax" (subjective). Some rules are testable ("Must return [{'json': {...}}]") but many are not binary.

### C5: Edge cases declared (>=3 with handling instructions)
**PASS** - Declares multiple edge cases: (1) external library imports -> ModuleNotFoundError, use HTTP Request node instead, (2) webhook body nesting -> access via ["body"], (3) KeyError on dict access -> use .get(), (4) missing return statement -> always return data, (5) None/null values -> explicit handling.

### C6: Worked example file exists in same folder
**FAIL** - No standalone worked example file. Examples are inline. Supporting files contain patterns but not a dedicated worked example.

### C7: Core file <=150 lines
**FAIL** - SKILL.md is 748 lines. Expected failure per task brief.

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
