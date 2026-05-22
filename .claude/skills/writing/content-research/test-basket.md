# Test Basket: content-research

## Test 1: Trusted creator classification and all 5 outputs

**Input:** "Cole Medin posted about using progressive disclosure in skill files to reduce token load"
**Expected:**
- Classification declared as "trusted-creator" before any output
- Creator matched from `02-knowledge/trusted-creators.md`, not hardcoded
- 5 outputs produced: summary (04-reflections/), insights (Supabase ideas), opportunity seeds (01-projects/seeds/), floor-raisers (Supabase captures), gap analysis (appended to same reflection file)
- Summary written in first person, past tense, voice from voice-profile.md

---

## Test 2: Gap analysis references all 4 sources

**Input:** Trusted creator research from Test 1
**Expected:**
- Gap analysis explicitly references: PRD.md, memory.md, skill registry, 01-projects/ directory
- Three sections present: Already have, Missing, Raises the floor
- No additional sources consulted beyond the 4 declared

---

## Test 3: Opportunity seed cross-references user.md

**Input:** Trusted creator research with content about agent architecture
**Expected:**
- Opportunity seed output references specific elements from `.claude/user.md` (e.g., "your n8n workflow experience", "your VAPI cold outreach agent")
- If no genuine connection: "No opportunity seeds detected" stated explicitly
- Seed file saved to `01-projects/seeds/` with status=seed

---

## Test 4: Writing project produces brief, no draft

**Input:** "writing project: LinkedIn post about why I build AI systems as personal infrastructure instead of SaaS products"
**Expected:**
- Classification declared as "writing-project"
- Brief produced at `00-inbox/staging/research-brief-[title]-[date].md`
- Brief contains: declared goal, platform (LinkedIn), content type (post), obvious version, non-obvious angle, key sources, existing vault knowledge, voice mode
- No draft content produced beyond the brief

---

## Test 5: General curiosity produces no gap analysis

**Input:** "I read an article about how solo developers are using AI to replace entire teams"
**Expected:**
- Classification declared as "general-curiosity" (no creator match, no writing/technical signal)
- Summary filed to `04-reflections/research-*.md`
- Insights to Supabase ideas table with source=general
- Opportunity seeds if genuine connection to user.md detected
- NO gap analysis section in output

---

## Test 6: Technical research invokes rag-search first

**Input:** "My n8n webhook keeps returning 502 after the IF node"
**Expected:**
- Classification declared as "technical"
- rag-search skill invoked in find-pattern mode before any other research
- If rag-search returns high confidence: pattern surfaced, research stops
- If low/medium: further research conducted, pattern note written to Supabase captures

---

## Test 7: Ambiguous input triggers classification question

**Input:** "I saw something interesting about workflow automation"
**Expected:**
- Could be trusted-creator (if about Nate/Cole), technical (workflow/automation), or general
- Skill asks for clarification before proceeding
- Does not assume a type and start producing output
