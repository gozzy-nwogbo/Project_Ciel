# Skill Audit: meeting-insights-analyzer

**Date:** 2026-04-14
**Auditor:** Phase 5 Track A migration

---

## C1: Single-line description with trigger context + output artifact named
**PASS**
Description block covers what it does, trigger phrases, and names the output artifact with path.

## C2: Output contract (artifact name, path, structure, out-of-scope declared)
**PASS**
Output format section provides a complete structured template. Limitations section declares what is out of scope (tone, non-verbals, relationship history).

## C3: Input contract (all inputs named with purposes)
**FAIL**
Implicitly requires a meeting transcript but does not formally declare inputs (transcript text, meeting title, participant list, expected contributors) with required/optional status.

## C4: Constraints as binary testable rules (no "should"/"ideally")
**FAIL**
Uses observational guidance rather than binary testable rules. "Look for immediate topic changes after disagreement" is not a pass/fail check.

## C5: Edge cases declared (>=3 with handling instructions)
**PASS**
Limitations section declares 3 edge conditions with handling: text-only analysis (flag uncertainty), approximate speaking times (note approximation), missing relationship context (flag when interpretation is uncertain).

## C6: Worked example file exists in same folder
**FAIL**
No worked example file present.

## C7: Core file <=150 lines
**PASS**
SKILL.md is within the 150-line limit.

## C8: Handoff defined (specific artifact, location, condition)
**FAIL**
Output format is well-defined but no explicit handoff section declaring when the skill is complete and where the artifact is delivered.

## C9: Test basket file with >=3 cases exists in folder
**FAIL**
No test basket file present.

---

## Verdict: DRAFT (4/9 PASS)
