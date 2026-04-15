# Skill Audit: file-organizer

**Date:** 2026-04-14
**Auditor:** Phase 5 Track A migration

---

## C1: Single-line description with trigger context + output artifact named
**PASS**
Description block covers what it does, trigger phrases, and names output artifact (`_review/` folder and reorganized directory).

## C2: Output contract (artifact name, path, structure, out-of-scope declared)
**FAIL**
Proposed structure template is shown but output path is dynamic (user's directory). No explicit out-of-scope declaration for outputs.

## C3: Input contract (all inputs named with purposes)
**FAIL**
Implicitly requires a target directory path but does not formally declare inputs with required/optional status.

## C4: Constraints as binary testable rules (no "should"/"ideally")
**PASS**
Safety rules are binary testable: "Never delete without review", "Always confirm before bulk operations". These are clear pass/fail checks.

## C5: Edge cases declared (>=3 with handling instructions)
**FAIL**
Safety rules cover some edge behavior (active files, duplicates) but no formal edge cases section. Missing: empty directory, permission-denied files, symlinks, files with special characters in names.

## C6: Worked example file exists in same folder
**FAIL**
No worked example file present.

## C7: Core file <=150 lines
**PASS**
SKILL.md is within the 150-line limit.

## C8: Handoff defined (specific artifact, location, condition)
**FAIL**
No explicit handoff section. The process ends at Step 5 but does not declare a completion condition or final artifact.

## C9: Test basket file with >=3 cases exists in folder
**FAIL**
No test basket file present.

---

## Verdict: DRAFT (3/9 PASS)
