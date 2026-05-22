# Worked Example: Meeting Debrief (Meeting Mode)

_Demonstrates the skill applied to a realistic meeting transcript input._

---

## Input

**Mode declared:** Meeting

**Transcript (structured, with speaker labels):**

```
Alex Chen: So we're agreeing to move the API deadline to April 25th?
Gozzy: Yes, the extra week gives us time to finish the auth middleware rewrite.
Alex Chen: Works for me. I'll update the sprint board.
Gozzy: I also want to flag that we still don't have a testing strategy for the webhook endpoints.
Alex Chen: Good point. Let's revisit that Thursday.
Gozzy: Sounds good. Oh, and I talked to Sarah Kim from the DevRel team yesterday. She might be able to help us with the docs sprint.
Alex Chen: Nice. Can you loop her in?
Gozzy: Will do by end of week.
```

---

## Expected Output

**File created:** `04-reflections/meeting-2026-04-16-api-deadline-sync.md`

```markdown
# Meeting Debrief: API Deadline Sync
_Date: 2026-04-16 | Processed by: meeting-debrief skill_

## Context Summary

I met with Alex to realign on the API deadline. We pushed it to April 25th to accommodate the auth middleware rewrite. We also flagged a gap in our webhook testing strategy and agreed to revisit it Thursday. Sarah Kim from DevRel came up as a potential resource for the docs sprint.

## Decisions

- **API deadline moved to April 25th.** Decided by: Gozzy and Alex Chen. Condition: extra week needed for auth middleware rewrite.

## Action Items

- [ ] Update sprint board (Alex Chen) — no time signal, routed to Asana
- [ ] Revisit webhook testing strategy (Gozzy + Alex) — time signal: Thursday → **Proposed calendar event: "Webhook testing strategy review", 2026-04-17. Approve to create?**
- [ ] Loop Sarah Kim into docs sprint (Gozzy) — time signal: "by end of week" → **Proposed calendar event: "Intro Sarah Kim to docs sprint", by 2026-04-18. Approve to create?**

## Open Questions

- What is the testing strategy for webhook endpoints?

## Speaker Notes

### Alex Chen
- Role: Engineering collaborator
- Quotes: "I'll update the sprint board." / "Can you loop her in?"
- Commitments: Update sprint board

### Gozzy
- Quotes: "The extra week gives us time to finish the auth middleware rewrite." / "Will do by end of week."
- Commitments: Loop Sarah Kim into docs sprint, revisit webhook testing Thursday

### Sarah Kim
- Role: DevRel team
- Quotes: None (mentioned, not present)
- Commitments: None identified
- **New person detected: Sarah Kim. Create people record?** [Awaiting confirmation]
```

**Routing actions taken:**
1. "Update sprint board" → Asana Open-Brain project (no time signal)
2. "Revisit webhook testing" → Calendar approval surfaced (time signal: Thursday)
3. "Loop Sarah Kim" → Calendar approval surfaced (time signal: end of week)
4. Sarah Kim → People table write pending user approval
5. Alex Chen → Supabase people table queried, match check performed
