# Skill Audit: google-calendar

**Date:** 2026-04-14
**Auditor:** Phase 5 Track A migration

---

## C1: Single-line description with trigger context + output artifact named
**PASS**
Description block covers what it does, trigger phrases, and names output artifacts (event listings, conflict reports).

## C2: Output contract (artifact name, path, structure, out-of-scope declared)
**PASS**
Output formats defined per operation (event listings, conflict format, availability slots). "What This Skill Does NOT Do" explicitly declares out-of-scope.

## C3: Input contract (all inputs named with purposes)
**PASS**
Each operation specifies exact tool parameters (startTime, endTime, timeZone, orderBy, eventId, attendeeEmails, durationMinutes) with purposes.

## C4: Constraints as binary testable rules (no "should"/"ideally")
**PASS**
Permission boundaries are binary (Yes/NO). "Tool exists but must never be called" is binary testable. Defaults section provides exact values (timezone, calendar, sort order).

## C5: Edge cases declared (>=3 with handling instructions)
**PASS**
Edge cases handled: (1) no events returns "No events today", (2) user asks to move a meeting triggers read-only explanation, (3) non-primary calendar requires explicit user specification, (4) write tools exist but must never be called.

## C6: Worked example file exists in same folder
**FAIL**
No worked example file present.

## C7: Core file <=150 lines
**PASS**
SKILL.md is within the 150-line limit (132 lines source plus description block).

## C8: Handoff defined (specific artifact, location, condition)
**PASS**
Each operation defines completion: listings are surfaced in conversation, conflicts are flagged, availability slots are presented. Approval pattern section defines the read-only boundary explicitly.

## C9: Test basket file with >=3 cases exists in folder
**FAIL**
No test basket file present.

---

## Verdict: DRAFT (7/9 PASS)
