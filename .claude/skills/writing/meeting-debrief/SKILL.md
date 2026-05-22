# Skill: meeting-debrief

Processes meeting transcripts or brain dumps into structured, routed outputs (meeting file, action items to Asana/Calendar, speaker records to Supabase people table, ideas to Supabase ideas table) — invoke when a user says "debrief", "meeting notes", "process transcript", "brain dump", or "log this meeting", produces `04-reflections/meeting-[date]-[title].md` or `04-reflections/brain-dump-[date].md`.

---

## Modes

Mode is declared at invocation. Never inferred silently. Ask if not stated.

- **Meeting Mode** — input is a meeting transcript (Granola, Jamie, Fireflies, or raw text)
- **Brain Dump Mode** — input is unstructured ideas, scattered notes, or raw thinking

---

## Inputs

| Input | Required | Purpose |
|---|---|---|
| User-declared mode | Yes | Determines processing pipeline (meeting or brain-dump) |
| Transcript or raw text | Yes | The content to process |
| `04-reflections/voice-profile.md` | Yes | Voice for first-person context summary |
| Supabase people table (via Open Brain MCP) | Yes | Speaker matching for existing records |
| Supabase ideas table (via Open Brain MCP) | Brain Dump only | Destination for classified ideas |
| Asana Open-Brain project (GID: 1214064555057948) | Yes | Destination for action items without time signals |
| Google Calendar MCP | Meeting only | Destination for time-bound action items (mutating, approval required) |
| Granola MCP | Optional | Source for meeting notes if Granola is the transcript source |

---

## Meeting Mode

### Input Detection

1. **Structured input** (Granola MCP output, or markdown with `Speaker:` labels from Jamie/Fireflies) — use speaker labels directly
2. **Granola MCP path:** query `get_meetings` or `query_granola_meetings` for the relevant meeting, extract enhanced notes. Note: full transcript access requires Granola Business plan. Basic plan provides enhanced notes only within a 30-day window.
3. **Raw input** (plain text, no speaker labels) — prompt user to identify speakers before processing

### Processing

Read transcript, extract 5 output types, discard raw content after extraction. Never store full transcript in vault or Supabase.

### Output 1 — Context Summary

- One paragraph, first person, past tense
- Written using voice from `04-reflections/voice-profile.md`
- Saved to `04-reflections/meeting-[YYYY-MM-DD]-[title-slug].md`

### Output 2 — Decisions Log

- Each decision: what was decided, who decided it, conditions or dependencies
- Saved to same meeting file under `## Decisions`

### Output 3 — Action Items (Routed)

- **Time signal detected** (specific date, day name, "by X", "next week") — flag for calendar approval. Surface: `Proposed calendar event: [title], [date/time]. Approve to create?` Wait for confirmation. On approval: create via Google Calendar MCP (mutating tier, approval required per PRD security boundaries).
- **No time signal** — route to Asana Open-Brain project as task. Include source meeting and date in task description.
- Approval-first on all calendar writes. Never auto-book.

### Output 4 — Open Questions

- Unresolved questions from the meeting
- Saved to meeting file under `## Open Questions`
- Flagged to surface at next session start

### Output 5 — Speaker-Specific Notes

- For each identified speaker: name, role (if known), quoted statements (verbatim), commitments made
- **Speaker matching:** query Supabase people table by name via `semantic_search`
  - Match found — append meeting date, quotes, and commitments to existing record. Requires user approval before Supabase write.
  - No match — surface: `New person detected: [name]. Create people record?` Wait for confirmation before any write.
  - After appending notes to an existing people record, always update last_contact_date to the meeting date. This is mandatory, not optional. A meeting debrief is always a contact event. The meeting date is the source_date from the transcript header, or today if no date is present in the transcript.

All 5 sections present in every meeting file. Empty state: `None identified.`

---

## Brain Dump Mode

### Input

Any unstructured text: voice memo transcription, Apple Notes export, free-form thinking, scattered ideas.

### Processing

Classify each item before routing. Classification is binary per item:

| Item Type | Destination |
|---|---|
| Idea (explore or build) | Supabase ideas table — title, raw text, tags, source: brain-dump, date |
| Project seed (idea with enough shape to become a project) | `01-projects/[project-name]/stub.md` — title, one-line description, source date, status: seed |
| Person mentioned | Supabase people table — same approval-first pattern as meeting mode |
| Task (clear next action) | Asana Open-Brain project |
| Reference material (link, resource, fact to keep) | Supabase captures table — classification: reference, source: brain-dump |

### Output

`04-reflections/brain-dump-[YYYY-MM-DD].md` with: total items processed, count per destination, any unclassifiable items flagged for human review.

---

## Constraints

| # | Constraint | Verification |
|---|---|---|
| 1 | Full transcript or raw input is never stored in vault or Supabase | Grep meeting file and Supabase write payloads for raw transcript content |
| 2 | All Supabase people writes require explicit human approval before execution | Check that every `write` call to people table is preceded by user confirmation |
| 3 | All Google Calendar writes require explicit human approval before execution | Check that every `create_event` call is preceded by user confirmation |
| 4 | Mode (meeting or brain-dump) is declared at invocation, never inferred | First action is mode confirmation if not stated |
| 5 | Every meeting file contains all 5 output sections even if empty | Grep output file for all 5 section headers |
| 6 | Speaker-specific notes use verbatim quotes only, no paraphrasing | Quotes in output match source transcript exactly |
| 7 | Granola Basic plan: use enhanced notes only, do not attempt transcript access | No calls to `get_meeting_transcript` unless user confirms Business plan |
| 8 | Every matched speaker has their last_contact_date updated to the meeting date, never left unchanged | After debrief, query people table for each matched speaker, verify last_contact_date reflects meeting date |

---

## Edge Cases

1. **Granola MCP is unreachable:** Fall back to manual transcript paste. Log: "Granola unavailable, using manual input." Do not fail the skill.
2. **Asana MCP is unreachable:** Write action items to `00-inbox/staging/action-items-[date].md` and flag for manual routing. Log the degradation.
3. **Google Calendar MCP is unreachable:** Write time-bound items to `00-inbox/staging/calendar-items-[date].md` and flag for manual routing.
4. **Speaker name matches multiple people records:** Surface all matches with context. Ask user to disambiguate before writing.
5. **Brain dump item is ambiguous (could be idea or task):** Flag the item: `Could not classify: [item]. Idea or task?` Wait for user input.
6. **Empty transcript or dump:** Return early with: `No content to process. Provide transcript or text.` Do not create empty files.
7. **Mixed input (transcript + unstructured notes in one paste):** Ask user to separate, or declare which mode applies to the full input. Do not silently split.

---

## Out of Scope

| # | Excluded | Why | Where Instead |
|---|---|---|---|
| 1 | Sending emails based on meeting content | Security boundary: Gmail is read + draft only | Manual or Phase 6 heartbeat |
| 2 | Auto-booking calendar events without approval | PRD security boundary | Never planned |
| 3 | Recording or joining meetings | This skill processes transcripts, not live meetings | Granola app handles recording |
| 4 | Modifying or deleting Granola notes | PRD security boundary: read-only | Not planned |
| 5 | Full transcript storage | Extract-and-discard pattern per CLAUDE.md | Not planned |

---

## Handoff

After this skill completes, the next stage receives:
- **Artifact:** `04-reflections/meeting-[date]-[title].md` or `04-reflections/brain-dump-[date].md`
- **Location:** `04-reflections/` directory
- **Condition:** All 5 output sections populated (meeting mode) or summary file written (brain-dump mode), all routed items confirmed delivered or staged for manual routing
- **Downstream:** Session end hook picks up open questions for next session. Asana tasks appear in Open-Brain project. Calendar events appear after approval.
