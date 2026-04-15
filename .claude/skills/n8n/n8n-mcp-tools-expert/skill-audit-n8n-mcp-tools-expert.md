# Skill Audit: n8n-mcp-tools-expert

**Date**: 2026-04-14
**Skill**: n8n-mcp-tools-expert
**Source**: /path/to/n8n-skills/skills/n8n-mcp-tools-expert/SKILL.md
**Lines**: 830

---

## Criteria Evaluation

### C1: Single-line description with trigger context + output artifact named
**PASS** - Description block includes what it does (expert guide for n8n-mcp MCP tools), trigger phrases (search nodes, validate config, template, workflow management, credentials, audit), and output artifact (tool call sequence with correct parameters).

### C2: Output contract (artifact name, path, structure, out-of-scope declared)
**FAIL** - No formal output contract declaring artifact name, path, or structure. Produces tool call sequences but does not define boundaries or out-of-scope items explicitly.

### C3: Input contract (all inputs named with purposes)
**FAIL** - No formal input contract. The skill responds to various tool usage questions but does not list required inputs with purposes.

### C4: Constraints as binary testable rules (no "should"/"ideally")
**PASS** - Most rules are binary: "Use SHORT prefix for search/validate tools", "Use FULL prefix for workflow tools", "nodeType formats differ", "Auto-sanitization runs on ALL nodes during updates". The Do/Don't lists are clearly binary.

### C5: Edge cases declared (>=3 with handling instructions)
**PASS** - Declares 6 common mistakes as edge cases with handling: (1) wrong nodeType format, (2) using detail="full" by default, (3) not using validation profiles, (4) ignoring auto-sanitization, (5) not using smart parameters, (6) not using intent parameter.

### C6: Worked example file exists in same folder
**FAIL** - No standalone worked example file. Examples are inline within SKILL.md and guide files.

### C7: Core file <=150 lines
**FAIL** - SKILL.md is 830 lines. Expected failure per task brief.

### C8: Handoff defined (specific artifact, location, condition)
**FAIL** - No explicit handoff section. The skill ends with summary and related skills but does not define completion artifacts or conditions.

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
