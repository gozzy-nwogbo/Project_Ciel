# Skill Audit: n8n-code-javascript

**Date**: 2026-04-14
**Skill**: n8n-code-javascript
**Source**: /path/to/n8n-skills/skills/n8n-code-javascript/SKILL.md
**Lines**: 699

---

## Criteria Evaluation

### C1: Single-line description with trigger context + output artifact named
**PASS** - Description block includes what it does (write JavaScript in n8n Code nodes), trigger phrases (writing JavaScript in n8n, $input/$json/$node syntax, etc.), and output artifact (JavaScript code block for n8n Code node configuration).

### C2: Output contract (artifact name, path, structure, out-of-scope declared)
**FAIL** - Returns JavaScript code blocks but does not formally declare artifact name, output path, structure schema, or out-of-scope boundaries. The skill produces code guidance inline rather than a named deliverable with defined structure.

### C3: Input contract (all inputs named with purposes)
**FAIL** - No formal input contract. The skill implicitly expects a coding task description but does not enumerate required inputs (e.g., task description, data shape, mode preference) with their purposes.

### C4: Constraints as binary testable rules (no "should"/"ideally")
**FAIL** - Contains soft language: "recommended for most use cases", "Prefer Array Methods Over Loops" (preference, not binary). Rules like "CRITICAL: Must return [{json: {...}}]" are testable, but several best practices use non-binary framing.

### C5: Edge cases declared (>=3 with handling instructions)
**PASS** - Declares multiple edge cases with handling: (1) empty input data -> return [], (2) webhook body nesting -> access via .body, (3) null/undefined fields -> optional chaining, (4) expression syntax confusion in code nodes, (5) missing return statement.

### C6: Worked example file exists in same folder
**FAIL** - No standalone worked example file. Examples are inline within SKILL.md. Supporting files (COMMON_PATTERNS.md, ERROR_PATTERNS.md) contain patterns but not a single end-to-end worked example file.

### C7: Core file <=150 lines
**FAIL** - SKILL.md is 699 lines. Expected failure per task brief.

### C8: Handoff defined (specific artifact, location, condition)
**FAIL** - No explicit handoff section. The skill ends with a checklist and resource links but does not define what artifact is produced, where it goes, or under what condition the skill is "done."

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
