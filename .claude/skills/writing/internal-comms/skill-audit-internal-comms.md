# Skill Audit: internal-comms

**Date:** 2026-04-14
**Auditor:** Phase 5 Track A migration

---

## C1: Single-line description with trigger context + output artifact named
**PASS**
Description block includes what it does, trigger phrases, and output artifact path.

## C2: Output contract (artifact name, path, structure, out-of-scope declared)
**FAIL**
Multiple template formats shown but no explicit out-of-scope declaration. Output path is named in the description block but not reinforced in the body.

## C3: Input contract (all inputs named with purposes)
**FAIL**
No formal input contract. The skill implicitly requires audience, format type, and project context, but these are not declared as named inputs.

## C4: Constraints as binary testable rules (no "should"/"ideally")
**FAIL**
Writing principles use imperative form ("Lead with the most important thing") which is better than soft language, but "don't bury the headline" is not binary testable. No explicit constraint list.

## C5: Edge cases declared (>=3 with handling instructions)
**FAIL**
No edge cases section. Missing handling for: unknown audience, mixed format request, missing project context, confidential content.

## C6: Worked example file exists in same folder
**FAIL**
No worked example file present.

## C7: Core file <=150 lines
**PASS**
SKILL.md is within the 150-line limit.

## C8: Handoff defined (specific artifact, location, condition)
**FAIL**
No explicit handoff section. The description block names an output path but does not define completion conditions.

## C9: Test basket file with >=3 cases exists in folder
**FAIL**
No test basket file present.

---

## Verdict: DRAFT (2/9 PASS)
