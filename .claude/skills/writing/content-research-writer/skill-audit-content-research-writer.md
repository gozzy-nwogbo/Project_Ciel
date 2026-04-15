# Skill Audit: content-research-writer

**Date:** 2026-04-14
**Auditor:** Phase 5 Track A migration

---

## C1: Single-line description with trigger context + output artifact named
**PASS**
Description block includes what it does, trigger phrases, and names the output artifact (`final.md`).

## C2: Output contract (artifact name, path, structure, out-of-scope declared)
**FAIL**
File organization section names `~/writing/article-name/final.md` as the output path and lists the folder structure. However, there is no explicit out-of-scope declaration for outputs.

## C3: Input contract (all inputs named with purposes)
**FAIL**
Step 1 asks clarifying questions (topic, audience, length, goal, style) but does not formally declare these as named inputs with explicit purposes and required/optional status.

## C4: Constraints as binary testable rules (no "should"/"ideally")
**FAIL**
Uses soft language: "Suggest, don't replace", "Ask periodically". These are guidelines, not binary testable rules.

## C5: Edge cases declared (>=3 with handling instructions)
**FAIL**
No edge cases section exists. No handling for: missing topic, conflicting style preferences, no sources found, content too long, etc.

## C6: Worked example file exists in same folder
**FAIL**
No worked example file present.

## C7: Core file <=150 lines
**PASS**
SKILL.md is within the 150-line limit after restructuring.

## C8: Handoff defined (specific artifact, location, condition)
**FAIL**
File organization implies output locations but no explicit handoff section defining what artifact, where, and under what condition the skill is done.

## C9: Test basket file with >=3 cases exists in folder
**FAIL**
No test basket file present.

---

## Verdict: DRAFT (2/9 PASS)
