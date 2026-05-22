# Humanizer — Test Basket

Three test cases covering different platforms and pattern densities.
Run these after any skill modification to verify behavior.

---

## Test 1: Heavy pattern density (essay)

**Platform:** essay
**Intensity:** standard
**Expected behavior:** Multiple critical flags, full rewrite

**Input:**
> The landscape of AI development is rapidly evolving, showcasing the
> interplay between innovation and responsibility. It's not just about
> building models. It's about building trust. Additionally, this
> paradigm shift highlights the crucial role of alignment research in
> fostering a more robust ecosystem. The implications are profound —
> not merely technical, but deeply human.

**Expected flags:**
- P1: significance inflation ("rapidly evolving", "paradigm shift", "profound")
- P7: AI vocabulary ("landscape", "showcasing", "interplay", "crucial", "fostering", "robust ecosystem")
- P9: negative parallelism ("not just about... It's about")
- P13: em dash (essay platform, flag it)
- P25: contrastive reframing ("not merely technical, but deeply human")
- P3: superficial -ing analysis ("showcasing", "fostering")

**Expected outcome:** Full rewrite. Zero critical patterns. Voice-aligned.

---

## Test 2: Platform-native patterns (LinkedIn)

**Platform:** linkedin
**Intensity:** standard
**Expected behavior:** Some flags downgraded due to platform norms

**Input:**
> I spent 3 months building an AI agent that automates lead research.
>
> Here's what I learned:
>
> **The tool matters less than the workflow.** Most people obsess over
> which model to use. The real leverage is in how you chain the steps.
>
> **Specificity beats sophistication.** A simple prompt that names the
> exact output format outperforms a complex chain 9 times out of 10.
>
> **Ship before you're ready.** My first version was embarrassing. It's
> also the one that got me my first paying client.

**Expected flags:**
- P15: inline-header vertical lists — DOWNGRADE (LinkedIn-native)
- P14: boldface — DOWNGRADE (LinkedIn-native)
- P9: negative parallelism ("matters less than") — minor, not the
  "isn't just / it's" construction
- Possible P10: rule of three — minor (three sections, but each has
  genuine distinct content)

**Expected outcome:** Minimal changes. Most patterns are platform-native.
Voice check should confirm specificity and rhythm are already strong.

---

## Test 3: Clean text (email)

**Platform:** email
**Intensity:** standard
**Expected behavior:** No significant patterns, no rewrite

**Input:**
> Hey Marcus, wanted to follow up on the Supabase migration. I ran
> the schema diff yesterday and found three columns in the leads table
> that don't exist in the new schema. Looks like they were added during
> the December sprint and never documented. Can you check whether
> anything in the n8n workflows references them before I drop them?
> Don't want to break a pipeline nobody remembers building.

**Expected flags:**
- None critical. Text is specific, conversational, purposeful.

**Expected outcome:** "No significant AI patterns detected." No rewrite.

**Clean-text validation note:** Test passes when humanizer correctly
declines to rewrite. Validation specifically checks against false-positive
rewrites (over-aggressive humanization), not just absence of flags. If the
humanizer rewrites clean text, that is a test failure even if the rewrite
introduces no new patterns.

---

## Validation criteria

A test passes when:
1. All expected flags are identified (no false negatives on critical patterns)
2. Platform downgrades are applied correctly (no false positives after calibration)
3. Clean text is not unnecessarily rewritten (see Test 3 clean-text validation note)
4. Voice alignment checklist scores match expected outcome
5. No new patterns introduced by rewrites
6. For clean-text tests specifically: humanizer must decline to rewrite rather than
   declaring clean to avoid work. The distinction matters because an over-aggressive
   humanizer and a lazy humanizer both produce zero flags but for opposite reasons.
