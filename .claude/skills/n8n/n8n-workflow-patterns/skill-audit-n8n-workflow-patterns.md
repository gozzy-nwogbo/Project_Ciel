# Skill Audit: n8n-workflow-patterns

**Date**: 2026-04-14
**Skill**: n8n-workflow-patterns
**Source**: /path/to/n8n-skills/skills/n8n-workflow-patterns/SKILL.md
**Lines**: 412

---

## Criteria Evaluation

### C1: Single-line description with trigger context + output artifact named
**PASS** - Description block includes what it does (proven workflow architectural patterns), trigger phrases (workflow pattern, build workflow, workflow architecture, webhook processing, AI agent, scheduled task), and output artifact (workflow pattern specification with node list, connection map, and configuration checklist).

### C2: Output contract (artifact name, path, structure, out-of-scope declared)
**FAIL** - No formal output contract section. Produces pattern guidance and checklists but does not declare artifact structure, path, or out-of-scope boundaries.

### C3: Input contract (all inputs named with purposes)
**FAIL** - No formal input contract. Implicitly expects a use case description but does not enumerate required inputs with purposes.

### C4: Constraints as binary testable rules (no "should"/"ideally")
**PASS** - Rules are mostly binary: "5 core patterns cover 90%+ of use cases", clear "Use when" / pattern selection criteria, workflow creation checklist with binary checkboxes. Do/Don't section is binary. Minimal soft language.

### C5: Edge cases declared (>=3 with handling instructions)
**PASS** - Declares gotchas as edge cases: (1) webhook data structure -> use $json.body, (2) multiple input items -> Execute Once mode, (3) authentication issues -> credential configuration, (4) node execution order -> v0 vs v1, (5) expression errors -> use {{}}.

### C6: Worked example file exists in same folder
**PASS** - Multiple pattern files serve as worked examples: webhook_processing.md, http_api_integration.md, database_operations.md, ai_agent_workflow.md, scheduled_tasks.md.

### C7: Core file <=150 lines
**FAIL** - SKILL.md is 412 lines. Expected failure per task brief.

### C8: Handoff defined (specific artifact, location, condition)
**FAIL** - No explicit handoff section. The "Next Steps" section provides guidance but does not define a completion artifact, location, or condition.

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
| C6 | PASS |
| C7 | FAIL |
| C8 | FAIL |
| C9 | FAIL |

**Passing**: 4/9
**Verdict**: **DRAFT**
