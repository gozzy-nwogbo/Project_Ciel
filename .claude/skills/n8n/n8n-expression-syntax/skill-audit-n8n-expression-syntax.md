# Skill Audit: n8n-expression-syntax

**Date**: 2026-04-14
**Skill**: n8n-expression-syntax
**Source**: /path/to/n8n-skills/skills/n8n-expression-syntax/SKILL.md
**Lines**: 516

---

## Criteria Evaluation

### C1: Single-line description with trigger context + output artifact named
**PASS** - Description block includes what it does (validate n8n expression syntax and fix errors), trigger phrases (n8n expression, {{}} syntax, $json variable, expression error), and output artifact (corrected n8n expression string or expression pattern reference).

### C2: Output contract (artifact name, path, structure, out-of-scope declared)
**FAIL** - No formal output contract. Produces expression corrections inline but does not declare artifact structure, path, or out-of-scope boundaries explicitly.

### C3: Input contract (all inputs named with purposes)
**FAIL** - No formal input contract. Implicitly expects an expression to validate but does not enumerate inputs with purposes.

### C4: Constraints as binary testable rules (no "should"/"ideally")
**PASS** - Most rules are binary testable: "Expressions must be wrapped in double curly braces", "Node names must be in quotes", "Node names are case-sensitive", "No nested {{}}", "Don't use expressions in Code nodes". Minimal soft language.

### C5: Edge cases declared (>=3 with handling instructions)
**PASS** - Declares multiple edge cases: (1) webhook data not at root -> use .body, (2) expressions in Code nodes -> use direct JS access, (3) field names with spaces -> bracket notation, (4) case sensitivity in node names, (5) double-wrapped expressions.

### C6: Worked example file exists in same folder
**PASS** - EXAMPLES.md exists in the source folder and will be copied to target, providing real workflow examples.

### C7: Core file <=150 lines
**FAIL** - SKILL.md is 516 lines. Expected failure per task brief.

### C8: Handoff defined (specific artifact, location, condition)
**FAIL** - No explicit handoff section defining what is produced, where, or when complete.

### C9: Test basket file with >=3 cases exists in folder
**FAIL** - No dedicated test basket file. COMMON_MISTAKES.md functions as an error catalog but is not structured as a test basket with pass/fail cases.

---

## Summary

| Criterion | Result |
|-----------|--------|
| C1 | PASS |
| C2 | FAIL |
| C3 | FAIL |
| C4 | PASS |
| C5 | PASS |
| C6 | PASS |
| C7 | FAIL |
| C8 | FAIL |
| C9 | FAIL |

**Passing**: 4/9
**Verdict**: **DRAFT**
