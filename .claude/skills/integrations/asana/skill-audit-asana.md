# Skill Audit: asana

**Date:** 2026-04-14
**Auditor:** Phase 5 Track A migration

---

## C1: Single-line description with trigger context + output artifact named
**PASS**
Description block covers what it does, trigger phrases, and names output artifacts (task listings, Asana objects).

## C2: Output contract (artifact name, path, structure, out-of-scope declared)
**PASS**
Output formats defined per operation (task listings, task details, search results). "What This Skill Does NOT Do" explicitly declares out-of-scope. Write operations gated to approved projects only.

## C3: Input contract (all inputs named with purposes)
**PASS**
Each operation specifies exact tool parameters (project GID, task_id, opt_fields, taskName, description, assignee, dueDate) with purposes.

## C4: Constraints as binary testable rules (no "should"/"ideally")
**PASS**
Permission boundaries are binary (Yes/NO/Approved projects only). "Never add projects by inference" is binary. Write gating has 5 sequential binary checks. Workspace restriction is a single hard value.

## C5: Edge cases declared (>=3 with handling instructions)
**PASS**
Edge cases handled: (1) target project not in approved list triggers refusal with surface of requested project, (2) workspace restriction prevents cross-workspace queries, (3) project approval requires explicit user instruction, never inference, (4) write tools exist for create/delete project but must never be called, (5) approved_project field logged as true/false in events.

## C6: Worked example file exists in same folder
**FAIL**
No worked example file present.

## C7: Core file <=150 lines
**FAIL**
SKILL.md is 174 lines (source) plus description block, exceeding the 150-line limit.

## C8: Handoff defined (specific artifact, location, condition)
**PASS**
Each operation defines completion. Write gating defines the approval-first pattern with explicit completion condition (user approval before tool call). Event logging defines post-action artifact (system-events.jsonl entry).

## C9: Test basket file with >=3 cases exists in folder
**FAIL**
No test basket file present.

---

## Verdict: DRAFT (6/9 PASS)
