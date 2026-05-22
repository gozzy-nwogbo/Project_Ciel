# Skill Audit: meeting-debrief
_Evaluated: 2026-04-16 | Standard: skill-authoring v1_

## Verdict: PASS

| # | Criterion | Result | Evidence |
|---|---|---|---|
| C1 | Single-Line Description | PASS | Single unbroken line after header: names trigger phrases ("debrief", "meeting notes", etc.), output artifacts (`meeting-[date]-[title].md`, `brain-dump-[date].md`), and when to invoke. |
| C2 | Output Contract | PASS | Handoff section names both artifacts, their paths (`04-reflections/`), structure (5 sections for meeting, summary for brain-dump), and condition for completion. Out-of-scope table with 5 exclusions. |
| C3 | Input Contract | PASS | Inputs table lists 8 named inputs with Required/Optional and purpose. Includes mode declaration, transcript, voice-profile, Supabase tables, Asana project GID, Calendar MCP, Granola MCP. |
| C4 | Constraints as Rules | PASS | 7 constraints, all binary and testable. Each has a verification method column. No "should" or "ideally" language. |
| C5 | Edge Cases Declared | PASS | 7 edge cases documented with explicit handling: Granola unreachable, Asana unreachable, Calendar unreachable, multiple people matches, ambiguous brain-dump items, empty input, mixed input. |
| C6 | Worked Example Exists | PASS | `example-meeting-debrief.md` in skill folder. Shows structured transcript input, full 5-section output, routing actions, and approval prompts matching the declared contract. |
| C7 | Core File Under 150 Lines | PASS | SKILL.md is 145 lines (verified via `wc -l`). |
| C8 | Handoff Defined | PASS | Handoff section names both artifacts, location (`04-reflections/`), completion condition (all sections populated or summary written, routed items confirmed or staged), and downstream consumers (session hook, Asana, Calendar). |
| C9 | Test Basket Exists | PASS | `test-basket.md` in skill folder with 4 test cases: structured meeting transcript, raw input without labels, mixed brain-dump items, graceful degradation. Each has input, expected output, and pass condition. |

## Failing Criteria — Required Fixes

None.

## Classification

- **PASS (9/9 criteria):** Skill is production-ready. Eligible for promotion gate.
