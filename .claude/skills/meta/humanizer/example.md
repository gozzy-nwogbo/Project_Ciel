# Humanizer — Worked Example

Source: CSC AI Solutions Engineer questionnaire, Q8 polish session (2026-04-28).
Platform: essay (questionnaire long-form responses)
Intensity: standard

---

## Input (Q8 v1, pre-humanizer)

> **The real threat isn't hallucinations. It's silent failures.**
>
> Hallucinations are visible — wrong output is still output, and a human
> reviewing the result catches it. What actually breaks production workflows
> is the edge case that produces no output and no error. A node receives an
> unexpected format, doesn't know what to do with it, and the execution just
> stops. No failure notification fires because technically nothing failed —
> it just didn't continue. By the time anyone notices, the downstream effects
> have already compounded.
>
> **How I prevent this:**
>
> Structured outputs with schema enforcement. Every AI generation call in my
> workflows specifies exact JSON output format. If the response doesn't
> parse, that's a caught error — not a silent one. Claude gets explicit
> instructions on structure, not just content.
>
> Explicit error routing on every consequential node. In the reel generator,
> Shotstack submission and render polling both have failure paths wired to
> Telegram notifications with error context. The goal is to make every
> failure loud, not graceful.
>
> Approval gates before irreversible actions. My Second Brain infrastructure
> uses an approval-first pattern — no writes to persistent storage, no
> external API calls with side effects, without explicit confirmation. This
> isn't just good security practice. It's the checkpoint that catches silent
> failures before they become production incidents.
>
> Monitoring at the ops layer. Telegram notifications on success and failure
> mean the system is reporting its own health in real time. You don't find
> out something broke when you check the queue on Monday. You find out when
> it breaks.
>
> **On rollback:** For content workflows, the human approval gate is the
> rollback strategy. Nothing irreversible happens without sign-off. For data
> workflows, I keep a log of every mutating action with inputs and outputs
> so any state can be reconstructed.

## Pass 1 — Pattern scan

| # | Pattern | Flagged text | Severity |
|---|---------|-------------|----------|
| 9 | Negative parallelism | "The real threat isn't hallucinations. It's silent failures." | critical |
| 9 | Negative parallelism | "This isn't just good security practice. It's the checkpoint..." | critical |
| 25 | Contrastive reframing | Same as above P9 instance 2 (overlapping) | critical |
| 15 | Inline-header vertical list | "**How I prevent this:**" and "**On rollback:**" bold headers | moderate |
| 13 | Em dash overuse | 4 em dashes across the passage | moderate |

2 critical, 2 moderate flags.

## Pass 2 — Platform calibration

Platform: essay. No downgrades. Bold headers and em dashes are not
platform-native for essay-length questionnaire responses. All flags stand.

## Pass 3 — Voice alignment

Voice profile says: vary sentence length, short sentence lands the point,
never let rhythm become uniform. Two inversions in one response creates
rhythmic repetition. Voice profile also flags "over-qualification" as a
recurring weakness, and the "isn't just" construction qualifies without
adding information.

Decision: retain one P9 instance ("The real threat isn't hallucinations.
It's silent failures.") because the concrete detail in the following
paragraph earns the rhetorical weight. Remove the second instance where
the content stands without the device. Replace bold headers with inline
transitions. Remove em dashes per CLAUDE.md hard rule.

## Pass 4 — Shipped output (Q8 final, verbatim)

> **The real threat isn't hallucinations. It's silent failures.**
>
> Hallucinations are visible. Wrong output is still output, and a human
> reviewing the result catches it. What actually breaks production workflows
> is the edge case that produces no output and no error. A node receives an
> unexpected format, doesn't know what to do with it, and the execution just
> stops. No failure notification fires because technically nothing failed,
> it just didn't continue. By the time anyone notices, the downstream
> effects have already compounded.
>
> I prevent this at four layers:
>
> Structured outputs with schema enforcement. Every AI generation call in my
> workflows specifies exact JSON output format. If the response doesn't
> parse, that's a caught error, not a silent one. Claude gets explicit
> instructions on structure, not just content.
>
> Explicit error routing on every consequential node. In the reel generator,
> Shotstack submission and render polling both have failure paths wired to
> Telegram notifications with error context. The goal is to make every
> failure loud, not graceful.
>
> Approval gates before irreversible actions. My Second Brain infrastructure
> uses an approval-first pattern. No writes to persistent storage, no
> external API calls with side effects, without explicit confirmation.
> That's the checkpoint that catches silent failures before they become
> production incidents.
>
> Monitoring at the ops layer. Telegram notifications on success and failure
> mean the system is reporting its own health in real time. You don't find
> out something broke when you check the queue on Monday. You find out when
> it breaks.
>
> For content workflows, human sign-off is the rollback strategy. Nothing
> irreversible happens without sign-off. For data workflows, I keep a log
> of every mutating action with inputs and outputs so any state can be
> reconstructed.

## Results

- Patterns before: 5 flags (2 critical P9/P25, 2 moderate P15, 1 moderate P13)
- Patterns after: 0
- Voice checklist: 5/5
- Changes applied:
  - P9/P25: One inversion retained (earned by concrete detail). One removed,
    rewritten as direct statement ("That's the checkpoint...").
  - P15: "**How I prevent this:**" replaced with "I prevent this at four layers:".
    "**On rollback:**" removed, content integrated as closing paragraph.
  - P13: Em dashes replaced with commas and periods throughout.
