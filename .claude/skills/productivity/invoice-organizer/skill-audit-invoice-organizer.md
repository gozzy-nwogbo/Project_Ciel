# Skill Audit: invoice-organizer

**Date:** 2026-04-14
**Auditor:** Phase 5 Track A migration

---

## C1: Single-line description with trigger context + output artifact named
**PASS**
Description block names what it does, trigger phrases, and output artifacts (`invoice-log.csv` and summary markdown).

## C2: Output contract (artifact name, path, structure, out-of-scope declared)
**FAIL**
Output artifacts are described (CSV log, summary markdown, folder structure) but no explicit out-of-scope declaration. Path is dynamic.

## C3: Input contract (all inputs named with purposes)
**FAIL**
Implicitly requires a target directory and file types, but no formal input contract with named inputs and required/optional status.

## C4: Constraints as binary testable rules (no "should"/"ideally")
**FAIL**
Tips section uses soft guidance: "When a vendor name is unclear, use the domain from the email." Not framed as binary testable rules.

## C5: Edge cases declared (>=3 with handling instructions)
**FAIL**
Tips section handles two edge cases (unclear vendor name, unclear amount) but does not reach the minimum of 3. Missing: duplicate invoices, non-PDF formats, foreign currency, corrupted files.

## C6: Worked example file exists in same folder
**FAIL**
No worked example file present.

## C7: Core file <=150 lines
**PASS**
SKILL.md is within the 150-line limit.

## C8: Handoff defined (specific artifact, location, condition)
**FAIL**
Process ends at Step 5 (Generate Summary) but no explicit handoff defining completion condition or final deliverable.

## C9: Test basket file with >=3 cases exists in folder
**FAIL**
No test basket file present.

---

## Verdict: DRAFT (2/9 PASS)
