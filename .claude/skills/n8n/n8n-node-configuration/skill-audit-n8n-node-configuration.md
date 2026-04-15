# Skill Audit: n8n-node-configuration

**Date**: 2026-04-14
**Skill**: n8n-node-configuration
**Source**: /path/to/n8n-skills/skills/n8n-node-configuration/SKILL.md
**Lines**: 810

---

## Criteria Evaluation

### C1: Single-line description with trigger context + output artifact named
**PASS** - Description block includes what it does (operation-aware node configuration guidance), trigger phrases (configure n8n node, property dependencies, required fields, detail levels), and output artifact (node configuration JSON object with operation-specific required fields).

### C2: Output contract (artifact name, path, structure, out-of-scope declared)
**FAIL** - No formal output contract. Produces configuration JSON guidance but does not declare artifact name, path, structure schema, or out-of-scope boundaries as a formal section.

### C3: Input contract (all inputs named with purposes)
**FAIL** - No formal input contract. Implicitly expects node type and desired operation but does not enumerate required inputs with purposes.

### C4: Constraints as binary testable rules (no "should"/"ideally")
**PASS** - Rules are largely binary testable: "Resource + operation determine which fields are required", "displayOptions control field visibility", anti-patterns section uses clear Do/Don't framing. The configuration workflow is prescriptive with binary decision tree.

### C5: Edge cases declared (>=3 with handling instructions)
**PASS** - Declares edge cases: (1) conditional body requirement (sendBody + method), (2) IF node singleValue for unary operators, (3) operation switch changing required fields, (4) over-configuring upfront, (5) copying configs without understanding operation context.

### C6: Worked example file exists in same folder
**FAIL** - No standalone worked example file. The HTTP Request configuration walkthrough is inline. OPERATION_PATTERNS.md contains patterns but is not a worked example file.

### C7: Core file <=150 lines
**FAIL** - SKILL.md is 810 lines. Expected failure per task brief.

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
| C4 | PASS |
| C5 | PASS |
| C6 | FAIL |
| C7 | FAIL |
| C8 | FAIL |
| C9 | FAIL |

**Passing**: 3/9
**Verdict**: **DRAFT**
