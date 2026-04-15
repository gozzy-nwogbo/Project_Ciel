# Capture Pipeline: Telegram → n8n → Supabase

**Status:** Design complete. Ready to build.
**Phase:** 4 (Core Integrations)
**Last updated:** 2026-04-13

---

## Overview

This is the first always-on integration for Open Brain. A Telegram bot (Open Brain bot) acts as the single capture surface. Every message sent to the bot triggers an n8n workflow that classifies the content, routes it to the correct Supabase table, and confirms with a Telegram reply.

The pipeline uses cloud n8n (non-sensitive captures only until self-hosted migration in Phase 7).

**Design principle:** Reduce the human's job to ONE reliable behavior: throw a thought into the capture channel.

**Why Telegram over Slack:** Slack's n8n trigger requires production URL registration which breaks test mode. The production/test URL conflict prevents node-by-node testing, and signing secret issues caused repeated failures. Telegram trigger supports both test and production modes natively, providing identical capture UX with full n8n development parity.

---

## 1. Capture Flow

```
User sends message to Open Brain bot (Telegram)
        |
        v
n8n Telegram Trigger receives the message
        |
        v
Claude API (Haiku) classifies the message
   -> destination table, confidence, metadata
        |
        +-- confidence >= 0.6
        |       |
        |       v
        |   Route to destination table (people/projects/ideas)
        |       |
        |       v
        |   Also log to captures table (audit trail)
        |       |
        |       v
        |   Reply in Telegram: "Captured as [type]: [summary]"
        |
        +-- confidence < 0.6
                |
                v
            Log to captures table with status=needs_review
                |
                v
            Reply in Telegram: "Not sure where this belongs.
            [summary]. Can you clarify?"
```

### Step-by-step

1. **User sends message** to the Open Brain Telegram bot. Any format: text, link, brain dump, contact info, project idea.

2. **Telegram fires update** to n8n via the Telegram Bot API (long polling or webhook, configurable in n8n).

3. **n8n extracts message content** from the Telegram update payload: `message.text`, `message.from.id`, `message.message_id`, `message.chat.id`.

4. **Claude API classifies** the raw text. Model: `claude-haiku-4-5-20251001`. Stateless call, no conversation history. Returns structured JSON with destination table, confidence score, summary, and extracted metadata.

5. **Confidence check:**
   - **>= 0.6:** Route to the destination table (`people`, `projects`, or `ideas`) with extracted metadata. Always also write to `captures` as an audit record with `status=routed`.
   - **< 0.6:** Write to `captures` only with `status=needs_review`. Do not route to any other table.

6. **Telegram reply:** Always reply to the original message in the bot chat confirming what was done. Use `reply_to_message_id` to thread the response to the original capture.

7. **Audit trail:** Every capture writes to the `captures` table regardless of routing outcome. This is the single source of truth for what entered the system.

---

## 2. Classification Prompt

This is the exact prompt sent to `claude-haiku-4-5-20251001` for every capture:

```
You are a classification agent for a personal knowledge management system.

Given a raw capture from the user, classify it into the correct destination and extract metadata.

Destination tables:
- "people": contacts, relationship notes, meeting notes about specific people
- "projects": project updates, decisions, tasks, milestones, work-related captures
- "ideas": standalone ideas, shower thoughts, future plans, things to explore
- "captures": default fallback when the content does not clearly fit another table

Rules:
- Set confidence between 0.0 and 1.0 based on how clearly the content maps to a single destination
- If the content could belong to multiple tables equally, set confidence below 0.6
- If the content is a vague thought or ambiguous fragment, set confidence below 0.6
- Extract all named people, projects, and topics mentioned
- Identify any action items (things the user needs to do)
- Write a one-sentence summary that captures the core intent
- No em-dashes in the summary. Active voice.

Return valid JSON only. No markdown fencing. No explanation.

{
  "destination": "people|projects|ideas|captures",
  "confidence": 0.0-1.0,
  "summary": "one sentence summarizing the capture",
  "metadata": {
    "topics": ["topic1", "topic2"],
    "entities": ["person or project name"],
    "action_items": ["action if any"]
  }
}

Raw capture:
{raw_text}
```

### Prompt design rationale

- **Haiku model:** Cheapest model sufficient for classification. No reasoning required, just pattern matching and JSON output.
- **No conversation history:** Stateless by design. Each capture is classified independently. No context window growth.
- **Confidence as routing signal:** The 0.6 threshold matches the zero-trust default from the PRD. Below 0.6 means "log and ask, never guess-and-pollute."
- **Metadata extraction in the same call:** Avoids a second API call. Topics, entities, and action items are extracted alongside classification.

---

## 3. n8n Workflow Structure

Six nodes, following the standard automation workflow pattern from CLAUDE.md.

```
[1] Telegram Trigger → [2] Classify       → [3] Parse JSON
                                                  |
                                      +-----------+
                                      |           |
                                [4a] Route     [4b] Needs Review
                                      |           |
                                      +-----+-----+
                                            |
                                      [5] Write to Supabase
                                            |
                                      [6] Reply in Telegram
```

### Node details

**[1] Telegram Trigger**
- Type: Telegram Trigger node
- Listens for incoming messages to the Open Brain bot
- Extracts: `message.text`, `message.from.id`, `message.message_id`, `message.chat.id`
- Filters: ignores non-text messages (photos, stickers, etc. unless text caption present)

**[2] Classify (HTTP Request / AI Agent)**
- Type: HTTP Request node calling Anthropic Messages API
- Model: `claude-haiku-4-5-20251001`
- Max tokens: 512
- Sends the classification prompt with `message.text` interpolated
- Returns raw JSON string in response body

**[3] Parse JSON (Code node)**
- Parses Claude API response into structured object
- Validates required fields: `destination`, `confidence`, `summary`, `metadata`
- If JSON parse fails: set `destination=captures`, `confidence=0`, `summary="Classification failed"`, trigger retry flag

**[4a] Route (IF node, confidence >= 0.6)**
- Condition: `confidence >= 0.6` AND `destination` is one of `people`, `projects`, `ideas`
- True branch: proceeds to write to destination table + captures
- False branch: proceeds to needs_review path

**[4b] Needs Review (Set node)**
- Sets `status = "needs_review"` on the capture record
- Sets `destination = "captures"` (override any classification)

**[5] Write to Supabase (HTTP Request nodes)**
- **Audit record (always):** POST to Supabase REST API, `captures` table
  - Fields: `content` (raw text), `source` ("telegram"), `classification` (full JSON from step 3), `status` ("routed" or "needs_review"), `telegram_message_id` (message ID), `telegram_user_id` (user ID)
- **Destination record (confidence >= 0.6 only):** POST to the classified destination table
  - Maps metadata fields to table columns based on destination
  - For `people`: `name` from entities, `notes` from raw text
  - For `projects`: `name` from entities, `notes` from raw text
  - For `ideas`: `content` from raw text, `topics` from metadata

**[6] Reply in Telegram (Telegram node)**
- Uses Telegram Bot API `sendMessage` with `reply_to_message_id` = original message ID
- **Routed message:** "Captured as [destination]: [summary]"
- **Needs review message:** "Not sure where this belongs. [summary]. Can you clarify?"
- **Error message:** "Capture logged but routing failed. Saved for manual review."

---

## 4. Security Boundaries

These are the Phase 4 permissions for this pipeline. No expansion without an explicit decision logged in the system event log.

| Component | Allowed | Not Allowed |
|---|---|---|
| Telegram | Read messages from Open Brain bot conversation only, reply in bot chat | Access other bots, groups, or channels |
| n8n | Receive trigger, call Claude API, call Supabase API, call Telegram API | Access vault files, read local filesystem, execute arbitrary code |
| Supabase | Write to `captures` table (always), write to `people`/`projects`/`ideas` (confidence >= 0.6 only) | Schema changes, delete records, drop tables |
| Claude API | Stateless classification only, single prompt per capture | Conversation memory, tool use, multi-turn context |

### Credential scoping

- **Telegram Bot Token:** Created via @BotFather. Scoped to the Open Brain bot only. No group permissions enabled.
- **Anthropic API Key:** Used in n8n HTTP Request node. No persistent storage of prompts or responses beyond the workflow execution.
- **Supabase Service Key:** Used in n8n for table writes. Stored in n8n credential store, not in workflow JSON.

### Data sensitivity

Cloud n8n is acceptable for this pipeline because:
- Captures are user-initiated (the user chose to send them to the bot)
- No sensitive credentials pass through the classification prompt
- No vault files are accessed
- Self-hosted migration planned for Phase 7

---

## 5. Error Handling

| Failure | Detection | Response | Recovery |
|---|---|---|---|
| Claude API returns malformed JSON | JSON.parse throws in Parse node | Retry classification once with same input | If retry fails: log to `captures` with `status=needs_review`, reply in Telegram with "Classification failed, saved for manual review" |
| Claude API timeout / 5xx | HTTP Request node error handler | Log error, skip classification | Write raw capture to `captures` with `status=unclassified`, reply in Telegram with failure notice |
| Supabase write fails | HTTP response status != 201 | Log error with full payload to n8n execution log | Reply in Telegram: "Capture failed to save. Error: [code]. Please re-send or check manually." |
| Telegram reply fails | Telegram API error response | Log to n8n execution log | Capture is still saved in Supabase. Telegram confirmation is best-effort, not critical path. |
| Duplicate message (Telegram retry) | Check `telegram_message_id` against existing captures | Skip if `telegram_message_id` already exists in captures table | Supabase unique constraint on `telegram_message_id` field prevents duplicates |

### Retry policy

- Claude API: 1 retry with 2-second delay. After that, fail gracefully.
- Supabase: No retry. Log and notify. Human reviews failed captures.
- Telegram: No retry. Confirmation is best-effort.

---

## 6. Data Schema: Captures Table Extension

The existing `captures` table needs these additional columns for the Telegram pipeline:

| Column | Type | Purpose |
|---|---|---|
| `source` | text | Origin of the capture ("telegram", "obsidian", "manual") |
| `classification` | jsonb | Full classification JSON from Claude API |
| `status` | text | "routed", "needs_review", "unclassified" |
| `telegram_message_id` | text | Telegram message ID (unique identifier for dedup) |
| `telegram_user_id` | text | Telegram user ID who sent the message |
| `routed_to` | text | Destination table name if routed, null otherwise |

These columns should be added before the n8n workflow goes live. The existing `content` column stores the raw capture text. The existing `embedding` column continues to be auto-generated on write.

---

## 7. Testing Plan

Before going live:

1. **Classification accuracy:** Send 20 test messages covering all 4 destination types + ambiguous cases. Verify confidence scores align with expected routing.
2. **Confidence threshold:** Confirm that genuinely ambiguous messages score below 0.6 and route to needs_review.
3. **Telegram replies:** Verify all replies thread correctly to the original message via reply_to_message_id.
4. **Dedup:** Send the same message twice, verify only one capture is created.
5. **Error paths:** Simulate Claude API failure, Supabase write failure. Verify graceful degradation.
6. **Audit completeness:** After 20 test messages, verify `captures` table has exactly 20 records regardless of routing decisions.

---

*This document defines the capture pipeline architecture. No n8n building begins until this design is reviewed and approved.*
