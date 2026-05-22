# Worked Example: Trusted Creator Research

## Input
User: "Nate B. Jones posted a video about building a retrieval log for your second brain to track whether captures actually come back through search."

## Step 1: Classification
Read `02-knowledge/trusted-creators.md` → "Nate B. Jones" matches row 1.
**Declared:** "Research type: trusted-creator (Nate B. Jones matched in watchlist)"

## Step 2: Output 1 — Content Summary
Read `04-reflections/voice-profile.md` for voice reference.
Written in first person, past tense, matching voice profile:

> I watched Nate break down the retrieval log concept, which is essentially a two-door audit for your second brain. The core idea: it's not enough to capture information, you need to track whether it ever comes back out through search. He walked through adding a retrieval_log table to Supabase with fields for query, results count, and a binary useful flag. The useful flag is the key insight. Without it, you can't distinguish between "I searched and found something" and "I searched and found something that actually helped."

Saved to: `04-reflections/research-2026-04-16-retrieval-log-two-door-audit.md`

## Step 3: Output 2 — Key Insights
Written to Supabase ideas table via MCP write tool:
```json
{
  "title": "Two-door audit: track retrieval, not just capture",
  "body": "A second brain that only measures inputs (captures) without measuring outputs (retrievals) has no quality signal. The retrieval_log with a binary useful flag closes the loop.",
  "status": "active",
  "source": "Nate B. Jones",
  "topics": ["retrieval", "two-door-audit", "quality-signal"]
}
```

## Step 4: Output 3 — Opportunity Seeds
Read `.claude/user.md` → cross-reference against background.
Match found: user is building Open Brain with Supabase + pgvector, already has captures table.

> This content + your existing Supabase infrastructure and Phase 4 two-door audit requirement could become: a retrieval quality dashboard that scores the second brain's usefulness over time, feeding into the Phase 7 visual layer.

Saved to: `01-projects/seeds/opportunity-retrieval-log-two-door-audit-2026-04-16.md`

## Step 5: Output 4 — Floor-raising signals
Written to Supabase captures table:
```json
{
  "original_text": "Nate's framing of 'binary useful flag' as the minimum viable quality signal. Not a 1-5 rating, not a detailed review. Just: did this help? This pattern applies beyond retrieval to any feedback loop.",
  "source": "trusted-creator",
  "destination": "captures",
  "confidence": 0.9,
  "status": "processed",
  "topics": ["floor-raiser", "feedback-loops", "minimum-viable-signal"]
}
```

## Step 6: Output 5 — Gap Analysis
Compare against 4 sources:
- PRD.md: retrieval_log is listed in Phase 4 deliverables
- memory.md: no prior mention of two-door audit implementation
- Skill registry: rag-search skill exists, no retrieval quality tracking
- 01-projects/ scan: open-brain project has MCP server but no retrieval dashboard

```
### Gap Analysis

**Already have:**
- retrieval_log table exists in Supabase (created Phase 5 Track B)
- rag-search skill writes to retrieval_log after every search
- Binary useful flag is already in the schema

**Missing:**
- No dashboard or aggregate view of retrieval quality over time
- No automated scoring of retrieval effectiveness (% useful)
- Morning digest does not yet pull from retrieval_log

**Raises the floor:**
- The "minimum viable signal" pattern (binary yes/no instead of scaled rating) could apply to other feedback loops in the system: job application outcomes, meeting action item completion
```

Appended to: `04-reflections/research-2026-04-16-retrieval-log-two-door-audit.md`
