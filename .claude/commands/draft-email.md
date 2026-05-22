# /draft-email

Draft Gmail replies on-demand, one thread at a time, with approval required before saving.

---

## Step 1 — Identify Target Thread

Check if a specific thread was named in the command arguments (e.g., `/draft-email reply to Sarah's email about the interview`).

**If a thread was specified:**
- Search Gmail using `gmail_search_messages` with the relevant keywords from the user's description
- Find the matching thread and proceed directly to Step 3

**If no thread was specified:**
- Fetch unread threads needing a reply using the same filters as scheduled mode:
  ```
  Query: is:unread -category:promotions -category:social -from:noreply -from:no-reply -from:notifications -from:mailer-daemon older_than:1d
  ```
- Surface a numbered list:
  ```
  Unread threads that may need a reply:
  1. [sender] — [subject] (received [date])
  2. [sender] — [subject] (received [date])
  3. [sender] — [subject] (received [date])

  Which thread would you like to draft a reply for? (enter number)
  ```
- Wait for the user to select a thread before proceeding

---

## Step 2 — Run Draft Generation Protocol

For the selected thread, execute the full Draft Generation Protocol from the Gmail skill (`.claude/skills/integrations/gmail/SKILL.md`, Phase 6.3 section):

1. **Read thread** — call `gmail_read_thread` for the target thread. Extract sender, subject, thread history, what a reply needs to address. Check Supabase `people` table for sender context.

2. **Load voice** — read `04-reflections/voice-profile.md` and the relevant section from `02-knowledge/platform-rules.md`:
   - Recruiter / professional contact: Cold Outreach / Email section
   - Warm contact / known person: Long-form / personal register
   - Unknown sender: Cold Outreach defaults

3. **Write draft** — generate a reply that:
   - Opens with something specific to this thread (never generic)
   - Addresses what the thread actually needs
   - Matches register to relationship
   - Stays under 200 words (300 max for complex threads)
   - Passes voice calibration test

4. **Surface proposal** — display in this exact format:
   ```
   Thread: [subject] — [sender]
   Context: [one sentence on what this thread is about]

   Draft:
   [full draft text]

   Save to Gmail drafts? (yes / edit / skip)
   ```
   Wait for the user's response. Never proceed without it.

5. **On response:**
   - **yes** — call `gmail_create_draft` with the draft text and thread ID. Write a `draft_log` entry to Supabase: `approved: true`, `gmail_draft_id` from the response, `mode: on-demand`.
   - **edit** — take the user's edit, regenerate the draft incorporating changes, re-surface the proposal.
   - **skip** — write a `draft_log` entry: `dismissed: true`, `mode: on-demand`. Move to Step 3.

---

## Step 3 — Continue or Close

After approval or skip, ask:

```
Draft another reply? (yes / no)
```

- **yes** — return to Step 1 with remaining unread threads (if listing mode) or ask for a new thread specification
- **no** — close cleanly with summary

---

## Step 4 — Close Summary

At close, surface:

```
Drafted [N] replies. [M] saved to Gmail drafts. [K] skipped.
```

---

## Hard Constraints

1. **One thread at a time.** Never batch drafts without explicit user permission.
2. **Full Draft Generation Protocol runs for every thread.** No shortcuts. Voice profile loaded fresh each time.
3. **Approval gate on every draft.** `gmail_create_draft` never fires without explicit "yes" from the user.
4. **`gmail_send` is never called.** Does not exist in this skill. Must not be added or simulated.
5. **Every draft produces a `draft_log` entry** in Supabase, regardless of outcome.
6. **Voice profile (`04-reflections/voice-profile.md`) is read before every draft.** Never skipped.

---

## Draft Log Entry Format

Write to Supabase `draft_log` table using `01-projects/open-brain/scripts/write_act_now.py` pattern or direct Supabase MCP:

```json
{
  "thread_id": "[Gmail thread ID]",
  "subject": "[thread subject]",
  "sender": "[sender email]",
  "approved": true/false,
  "dismissed": true/false,
  "gmail_draft_id": "[from gmail_create_draft response, or null if skipped]",
  "word_count": "[draft word count]",
  "mode": "on-demand"
}
```
