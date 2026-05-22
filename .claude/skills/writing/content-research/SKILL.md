# Skill: content-research

Classifies input into one of 4 research types (trusted-creator, writing-project, technical, general-curiosity), routes to the matching research pipeline, and produces structured outputs to vault files, Supabase tables, and opportunity seeds. Invoke when user shares content, asks for research, mentions a trusted creator, or starts a writing project.

---

## Classification (runs first, always declared)

| Input Signal | Research Type |
|---|---|
| Creator name matches `02-knowledge/trusted-creators.md` | trusted-creator |
| User states "writing project" or provides topic for a piece they're writing | writing-project |
| Input contains n8n, workflow, automation, or technical error | technical |
| Everything else | general-curiosity |

Surface the classified type to user before any output. If ambiguous, ask. Never assume.

---

## Inputs

| Input | Required | Purpose |
|---|---|---|
| URL, content summary, error message, or topic | Yes | The research target |
| `02-knowledge/trusted-creators.md` | Yes | Creator matching for classification |
| `04-reflections/voice-profile.md` | Trusted-creator only | Voice for summary writing |
| `.claude/user.md` | Trusted-creator + general | Opportunity seed cross-reference |

---

## Route: Trusted Creator

Produces 5 outputs in order:

**1. Content summary** — one paragraph, first person, past tense, voice from `04-reflections/voice-profile.md`. Save to `04-reflections/research-[YYYY-MM-DD]-[title-slug].md`.

**2. Key insights** — each: title, one-sentence insight, why it matters for your work. Write to Supabase ideas table via MCP: type=insight, source=[creator name], date, tags.

**3. Opportunity seeds** — cross-reference content against `.claude/user.md` (background, active tracks, interests). Format: "This content + your [specific background/skill] could become [specific opportunity]." If no genuine connection: "No opportunity seeds detected." Save to `01-projects/seeds/opportunity-[title-slug]-[date].md` with status=seed.

**4. Floor-raising signals** — content that raises work quality without plugging into current projects. Write to Supabase captures table: classification=floor-raiser, source=[creator], date. Always separate from insights. Never merged into same entry.

**5. Gap analysis** — compare content against exactly 4 sources: PRD.md, memory.md, skill registry, `01-projects/` directory scan. Three sections: Already have, Missing, Raises the floor. Append to same `04-reflections/research-[YYYY-MM-DD]-[title-slug].md`.

## Route: Writing Project

Inputs: topic + platform + content type.
Processing: surface the obvious angle, then name a non-obvious angle fitting voice profile. Identify 3-5 sources. Check Supabase via rag-search skill for existing knowledge.

Output: `00-inbox/staging/research-brief-[title]-[date].md` with fields: declared goal, platform/type, obvious version, non-obvious angle, key sources, existing vault knowledge, voice mode=Personal.

**Stops at brief. Does not draft.**

## Route: Technical

Inputs: error message or problem description.
Processing: invoke rag-search skill in find-pattern mode first. If high confidence: surface pattern and stop. If medium/low: research problem, surface resolution steps.

Output: pattern note to Supabase captures table (classification=pattern, source=technical-research, date) + resolution steps inline.

## Route: General Curiosity

Inputs: URL, article, topic from non-watchlist source.
Processing: summarize, extract insights, detect opportunity seeds (same user.md cross-ref).

Output: summary to `04-reflections/research-[YYYY-MM-DD]-[title-slug].md`, insights to Supabase ideas table (type=insight, source=general), seeds to `01-projects/seeds/` if detected. **No gap analysis.**

---

## Output Contract

**Produces:** Vault files (04-reflections/, 01-projects/seeds/, 00-inbox/staging/) + Supabase entries (ideas, captures tables)
**Path:** varies by route (see each route above)
**Structure:** Each route has declared outputs above
**Out of scope:** Does not draft written content. Does not publish. Does not modify existing vault files beyond appending gap analysis. Does not create NotebookLM entries (deferred enhancement).

---

## Constraints

| # | Constraint | Verification |
|---|---|---|
| 1 | Research type declared before any output | Check first message after input |
| 2 | Trusted creator detection reads watchlist file, not hardcoded names | Grep SKILL.md for creator names |
| 3 | Gap analysis runs only for trusted-creator type | Check output of other types |
| 4 | Opportunity seeds always cross-reference user.md | Check seed output references user background |
| 5 | Floor-raisers and insights are separate Supabase entries | Check write calls |
| 6 | Writing research terminates at brief, no draft | Check output for draft content |
| 7 | Technical research invokes rag-search first | Check tool call order |

---

## Edge Cases

1. **Creator not in watchlist but user says "treat as trusted":** Ask user to add creator to watchlist first. Do not bypass.
2. **Input matches multiple types (e.g., Cole Medin video about n8n):** Trusted-creator takes priority when creator is in watchlist.
3. **No opportunity seeds detected:** Output "No opportunity seeds detected" explicitly. Do not force connections.
4. **rag-search returns high confidence for technical:** Surface pattern and stop. Do not duplicate research.
5. **Video URL provided but no transcript tool available:** Ask user for content summary or key points. Do not fail silently.

---

## Handoff

**Artifact:** Research files in vault + Supabase entries (ideas/captures)
**Location:** `04-reflections/research-*.md`, `01-projects/seeds/`, Supabase ideas/captures tables
**Condition:** All outputs for the classified route have been produced
**Next stage:** Writing-gateway skill consumes research briefs. Phase 6 morning digest surfaces new insights. Gap analysis informs PRD updates.
