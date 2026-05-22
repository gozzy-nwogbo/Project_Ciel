# Test Basket: meeting-debrief

_Minimum 3 test cases with defined inputs and expected outputs._

---

## Test 1 — Meeting Mode: Structured transcript with time signals

**Input:**
- Mode: meeting
- Transcript with speaker labels, 3 speakers, 2 action items with time signals, 1 without

**Expected Output:**
- `04-reflections/meeting-[date]-[title].md` created
- All 5 sections present (Context Summary, Decisions, Action Items, Open Questions, Speaker Notes)
- Time-signal items surface calendar approval prompts (not auto-booked)
- Non-time-signal item routed to Asana
- Speaker matching queries fired against Supabase people table
- Context summary written in first person, past tense, using voice profile

**Pass condition:** File contains all 5 sections. Calendar items show approval prompt. Asana item has meeting source in description. No raw transcript stored.

---

## Test 2 — Meeting Mode: Raw input without speaker labels

**Input:**
- Mode: meeting
- Plain text paragraph describing a meeting, no speaker labels

**Expected Output:**
- Skill prompts user: "No speaker labels detected. Please identify the speakers in this meeting."
- Processing pauses until speakers are identified
- After speaker identification, produces standard 5-section output

**Pass condition:** Skill does not proceed without speaker identification. No silent inference of speakers.

---

## Test 3 — Brain Dump Mode: Mixed item types

**Input:**
- Mode: brain-dump
- Text containing: 1 idea ("explore using Cursor for pair programming"), 1 task ("file Q1 taxes"), 1 person mention ("ask Dave about the n8n webhook issue"), 1 reference link ("https://example.com/useful-article")

**Expected Output:**
- Idea → Supabase ideas table (title, text, tags, source: brain-dump)
- Task → Asana Open-Brain project
- Person (Dave) → Supabase people table query, approval prompt if new
- Reference → Supabase captures table (classification: reference, source: brain-dump)
- Summary file at `04-reflections/brain-dump-[date].md` with counts per destination

**Pass condition:** Each item routed to correct destination. People write has approval prompt. Summary file has accurate counts. No raw dump stored in vault.

---

## Test 4 — Graceful degradation: Asana unreachable

**Input:**
- Mode: meeting
- Standard transcript with 2 action items (no time signals)
- Asana MCP returns error or timeout

**Expected Output:**
- Action items written to `00-inbox/staging/action-items-[date].md`
- Meeting file still created with all 5 sections
- Degradation logged: "Asana unavailable, action items staged to 00-inbox/staging/"

**Pass condition:** Skill completes without error. Items are not lost. Degradation is visible to user.
