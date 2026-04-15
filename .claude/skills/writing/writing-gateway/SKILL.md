# Skill: writing-gateway

Routes any writing request to the correct execution path (quick write or deep write), loads voice profile and platform rules, and produces either a finished draft (quick) or a writing brief at `00-inbox/staging/writing-brief-[title]-[date].md` (deep).

---

## When to Trigger

- User asks to write, draft, or produce any text output (LinkedIn post, email, article, essay, cold outreach, letter, copy, case study, narrative, script)
- User says "write", "draft", "post", "email", "article", "essay", "copy", "letter", "cold outreach"

---

## Inputs

| Input | Required | Purpose |
|---|---|---|
| `03-reflections/voice-profile.md` | Yes | Authoritative voice reference for tone, rhythm, register, and calibration test |
| `02-knowledge/platform-rules.md` | Yes | Platform-specific constraints: length, hooks, CTAs, credibility killers |
| User request | Yes | The writing task: what to write, for whom, on which platform |

---

## Classification Logic

**Binary decision. No ambiguous middle state.**

**Quick write** when ALL three conditions are true:
1. Output is short-form: LinkedIn post, email draft, cold outreach, short copy, letter, single tweet, or any piece under 700 words
2. No research is required beyond what the user provides in the request
3. The request can be fulfilled in one pass without revision cycles

**Deep write** when ANY one condition is true:
1. Output is long-form: article, essay, narrative, project copy, script, case study, thread (5+ tweets)
2. Research is needed from vault, web, or external sources before drafting
3. Multiple revision passes are expected or the user explicitly requests a pipeline

**Default:** If a request could go either way, classify as quick write and state: "Classified as quick write. If this needs research or multiple passes, say 'deep write' and I'll produce a brief instead."

---

## Path A: Quick Write

**Steps:**
1. Read `03-reflections/voice-profile.md`
2. Read `02-knowledge/platform-rules.md`
3. Identify platform from request (LinkedIn, email, creative, essay, case study, Twitter/X)
4. Extract relevant platform constraints from platform-rules.md for that platform
5. Produce output directly in session using voice profile + platform constraints
6. Run the 5-question voice calibration test from voice-profile.md against the draft
7. Deliver final output

**Does NOT reference:** outline.md, content-brief.md, or any upstream pipeline file.

**Output:** Finished draft delivered in session.

---

## Path B: Deep Write

**Steps:**
1. Read `03-reflections/voice-profile.md`
2. Read `02-knowledge/platform-rules.md`
3. Identify platform from request
4. Search vault (02-knowledge/, 00-inbox/, Open Brain semantic search) for relevant existing context
5. Produce a writing brief at `00-inbox/staging/writing-brief-[title]-[date].md`

**Writing brief fields:**
```markdown
# Writing Brief: [Title]
_Created: [date]_

## Declared Goal
[One sentence: what this piece must accomplish]

## Platform
[Which platform from platform-rules.md]

## Content Type
[Article / essay / narrative / case study / script / thread]

## Voice Mode
Personal

## Vault Context Summary
[Any relevant captures, knowledge entries, or prior writing already in the system]

## Reference Material Paths
[Exact paths to vault files that should be loaded when drafting]

## Classification Reason
[Why this was routed to deep write instead of quick write]
```

6. Stop at brief creation. Do not draft.
7. State: "Take this brief into a dedicated writing pipeline session."

**Output:** Writing brief file at declared path. No draft produced.

---

## Constraints

1. Voice mode is always Personal. No client voice logic exists in this skill.
2. Voice profile and platform rules are referenced by path, never embedded inline in output.
3. Every quick write output must pass the 5-question voice calibration test from voice-profile.md before delivery.
4. Platform must be identified from the request. If the user does not specify a platform, ask before proceeding.
5. No output may contain em-dashes, contrastive framing ("Not as X, but as Y"), or more than 1 exclamation point per 150 words.
6. Deep write path produces a brief file only. It does not produce a draft.
7. Quick write path produces output in session only. It does not create files unless the user asks to save.

---

## Edge Cases

1. **User says "write an article" but provides all content and no research is needed:** Classify as quick write. State the assumption. The word "article" alone does not force deep write if all three quick-write conditions are met.
2. **User says "draft a LinkedIn post" but the topic requires vault research:** Classify as deep write. Research requirement overrides short-form format.
3. **User provides a platform not in platform-rules.md:** Ask the user for platform constraints before proceeding. Do not guess. State: "That platform isn't in my reference file. Tell me the length, hook, and CTA norms and I'll proceed."
4. **User says "write something" with no platform or format specified:** Ask: "What platform is this for, and what format? (e.g., LinkedIn post, email, article)" Do not default to a platform.
5. **User asks to revise a previous quick write into something longer:** Reclassify as deep write. Produce a brief referencing the original quick write as input material.

---

## Handoff

**Quick write path:** Handoff is delivery in session. The user receives a finished draft that has passed the voice calibration test. No downstream stage.

**Deep write path:** Handoff is the writing brief file at `00-inbox/staging/writing-brief-[title]-[date].md`. The next stage is a dedicated writing pipeline session that loads the brief as its spec. The brief must contain all 7 fields (declared goal, platform, content type, voice mode, vault context summary, reference material paths, classification reason) for the downstream session to proceed without re-gathering context.

---

## Output Contract

**Quick write produces:** A finished draft in session, matching voice profile and platform constraints. Does not produce a file unless requested.

**Deep write produces:** `00-inbox/staging/writing-brief-[title]-[date].md` with all 7 required fields populated.

**Does NOT produce:** Outlines, content briefs using other naming conventions, or drafts during the deep write path. Does not produce client-voice output. Does not produce output for platforms not in platform-rules.md without explicit user-provided constraints.