# Skill: humanizer

Multi-pass AI pattern removal with voice profile alignment. Scans text against the 31-pattern AI writing catalog, calibrates flags to the target platform, rewrites flagged passages to match the writer's authentic voice, and verifies consistency end-to-end. Invoke when humanizing any writing for external use: "humanize this", "check for AI patterns", "does this sound like me", "voice check", "AI tells audit", "clean this up."

---

## When to use

- After drafting any writing that will be published or sent externally
- When reviewing AI-assisted writing for tells and pattern artifacts
- Before finalizing cover letters, LinkedIn posts, essays, questionnaire responses
- When something "reads like AI" but you can't pinpoint why

## When NOT to use

- Internal notes, session logs, or scratch documents
- Technical documentation where structured formatting is expected
- When the user says "don't humanize" or "raw is fine"

## Prerequisites

- `04-reflections/voice-profile.md` must exist. If missing, halt and report: "No voice profile found at 04-reflections/voice-profile.md. Cannot run humanizer without a voice target. Build one first using the elicitation skill or provide a voice profile."
- Reference knowledge at `02-knowledge/ai-patterns-and-tells.md` (31-pattern catalog)
- Platform rules at `02-knowledge/platform-humanizer-rules.md`
- Voice alignment checklist at `02-knowledge/voice-alignment-checklist.md`

## Input

The text to humanize, plus:
1. **Platform** (required): linkedin / essay / email / twitter / technical / case-study
2. **Intensity** (optional, default: standard): light (patterns 19-24 only) / standard (all 31) / aggressive (all 31 + voice rewrite)

## Process

### Pass 1 — Pattern scan

Read `02-knowledge/ai-patterns-and-tells.md`. Scan the input text against all 31 categories. Flag every match with:
- Pattern number and name
- The offending text (quoted)
- Severity: critical (immediate tell) / moderate (suspicious) / minor (stylistic)

### Pass 2 — Platform calibration

Read `02-knowledge/platform-humanizer-rules.md`. Cross-reference flagged patterns against the declared platform. Downgrade or remove flags where the pattern is platform-native (e.g., em dashes on LinkedIn, bold headers in technical docs).

### Pass 3 — Voice alignment

Read `04-reflections/voice-profile.md`. Read `02-knowledge/voice-alignment-checklist.md`. For each remaining flag:
- Rewrite the flagged text to match the voice profile's rhythm, register, and tone
- Preserve the original meaning
- Do not flatten voice-native constructions that happen to match a pattern

Run the 5-point voice alignment checklist from the reference doc.

### Pass 4 — Consistency check

Read the full rewritten piece end-to-end:
- Check for voice drift between sections (pattern 29)
- Check that rewrites didn't introduce new patterns
- Verify sentence rhythm variety matches the voice profile

### Pass 5 — Output

Present:
1. The rewritten text
2. Change log: list of patterns found and fixes applied
3. Pattern count: before vs. after
4. Voice alignment checklist results (pass/fail per item)
5. Summary of changes made (if non-trivial)

## Edge cases

1. **No voice profile found:** Halt. Report the missing file. Do not proceed with generic humanization.
2. **Voice profile conflicts with pattern rules:** Platform norms take precedence on structural patterns (13-17). Voice profile takes precedence on everything else, including vocabulary, register, and rhythm.
3. **User says "just fix the worst ones":** Run Pass 1 only, show critical flags, let user pick.
4. **Text is already clean:** Report "No significant AI patterns detected" with the scan results. Do not rewrite clean text.
5. **Mixed platform content:** Ask user to declare a primary platform. Do not guess.

## Allowed tools

- Read (voice profile, reference docs, input text)
- Write (output file if requested)
- Edit (in-place fixes if requested)
- Grep (pattern scanning across files)

## Quality criteria

A successful humanizer pass means:
- Zero critical-severity patterns remain
- Voice alignment checklist: 5/5 pass
- The piece sounds like the voice profile author, not like "a human" generically
- No new AI patterns introduced by the rewrite
- Original meaning preserved in every rewritten sentence

## References

- `02-knowledge/ai-patterns-and-tells.md` — 31-pattern catalog
- `02-knowledge/platform-humanizer-rules.md` — platform-specific rules
- `02-knowledge/voice-alignment-checklist.md` — post-pass alignment check
- `04-reflections/voice-profile.md` — the writer's voice target
