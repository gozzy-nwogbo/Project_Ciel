# Skill: gmail

Gmail integration for Open Brain Phase 4. Read inbox, search messages, read threads, create drafts (with explicit user approval). No send, delete, or label modification.
Trigger phrases: "check my email", "read my inbox", "draft a reply", "search gmail", "unread emails", "job alerts".
Output artifact: email summaries in conversation, draft objects in Gmail via `gmail_create_draft`.

---

# Gmail Integration Skill

> Open Brain Phase 4. Read inbox + create drafts. No send capability.

## Permission Boundaries (from PRD Security Table)

| Operation | Allowed | Tool |
|-----------|---------|------|
| Read inbox | Yes | `gmail_search_messages`, `gmail_read_message` |
| Read threads | Yes | `gmail_read_thread` |
| List labels | Yes | `gmail_list_labels` |
| List drafts | Yes | `gmail_list_drafts` |
| Get profile | Yes | `gmail_get_profile` |
| Create drafts | Yes | `gmail_create_draft` |
| Send email (self) | Yes | `gmail_send` — permitted ONLY when `to:` address is `nwogbo.gozzy@gmail.com` (self-send only). Any send to an external address remains blocked. Log every send to `system-events.jsonl`. |
| Send email (external) | **NO** | Sending to any address other than `nwogbo.gozzy@gmail.com` is blocked. No exceptions. |
| Delete messages | **NO** | No delete tool available. |
| Modify labels | **NO** | Not in scope for Phase 4. |

## Default Filtering

By default, inbox queries exclude newsletters and automated senders:

```
Default query prefix:
-category:promotions -category:social -from:noreply -from:no-reply -from:notifications -from:mailer-daemon
```

**Override flag:** When the user says `show:all`, drop all filters and return everything.

Apply the default filter to all `gmail_search_messages` calls unless `show:all` is specified.

## Available Operations

### 1. Surface Unread Threads

Search for recent unread messages, filtered by default.

```
Tool: gmail_search_messages
Query: "is:unread -category:promotions -category:social -from:noreply -from:no-reply -from:notifications"
maxResults: 10
```

With `show:all` override:
```
Query: "is:unread"
```

For each result, read the thread to get full context:
```
Tool: gmail_read_thread
threadId: <from search result>
```

Output format per thread:
```
- [sender] subject, one-line summary (date)
```

### 2. Search by Sender, Subject, or Date

Use Gmail query syntax:
- `from:name@example.com`
- `subject:keyword`
- `after:2026/04/01 before:2026/04/14`
- `has:attachment`
- Combine: `is:unread from:boss@company.com has:attachment`

Default filters still apply unless `show:all` is specified.

### 3. Read Full Thread

Given a thread ID from search results, retrieve the complete conversation.

```
Tool: gmail_read_thread
threadId: <id>
```

### 4. Create Draft Reply (Requires Explicit Approval)

**Workflow (mandatory):**
1. Read the thread to understand context
2. Compose proposed draft text
3. **Surface the full draft text to the user and wait for confirmation**
4. Only after user says "yes" / "approved" / "send it" / "save draft": call `gmail_create_draft`
5. If user edits the draft text, use the edited version

Never call `gmail_create_draft` without explicit user approval.

```
Tool: gmail_create_draft
threadId: <id from the thread>
body: <approved reply text>
contentType: "text/plain"
```

Subject is auto-derived from the thread when threadId is provided.

### 5. Create New Draft (Requires Explicit Approval)

Same approval workflow as draft replies:
1. Compose proposed draft
2. Surface to user for approval
3. Only create after confirmation

```
Tool: gmail_create_draft
to: "recipient@example.com"
subject: "Subject line"
body: <approved text>
contentType: "text/plain"
```

## Job Alert Scoring

Job alert emails (from LinkedIn, Jobright, Indeed, Glassdoor, and similar) are filtered from the default inbox view but processed separately through a job-fit scoring pass.

**Scoring workflow:**
1. Search: `from:linkedin OR from:jobright OR from:indeed OR from:glassdoor subject:(job OR role OR apply OR engineer OR consultant)`
2. For each role found, cross-reference against the user profile in `.claude/user.md`:
   - 2 years AI experience
   - Skills: Claude Code, n8n, Supabase, FastAPI, React, MCP, agent architecture
   - Goals: AI role, consulting role, startup, AI consulting for SMEs
   - Location: Toronto, ON (note remote preferences)
   - JD frames: Builder / Enterprise / Agentic / Sales-GTM / Product-Design / Regulated
3. Score each role: **high** / **medium** / **low** fit with one sentence reason
4. Surface only **high** fits in a weekly digest format
5. Log each scored lead to Supabase captures table:

```json
{
  "table": "captures",
  "content": "Job lead: [role] at [company]",
  "source": "gmail",
  "classification": {"type": "job-lead", "fit_score": "high|medium|low", "reason": "one sentence"},
  "status": "routed"
}
```

**Deferred to Phase 5:** Full application automation (resume tailoring, cover email drafting).

## Confidence Bouncer

Before any write operation (draft creation, Supabase logging):
- If classification confidence < 0.6, log as `needs-review` and surface to user
- All draft creation requires explicit user approval before calling the tool
- Log every permission decision: action, tool, reason, timestamp

## Event Logging

Every Gmail tool call must be logged to the system event log:

```json
{
  "timestamp": "ISO-8601",
  "category": "integration",
  "action": "gmail_read | gmail_draft_create | gmail_job_score",
  "tool": "tool name",
  "reason": "why this action was taken",
  "permission_tier": "read-only | mutating",
  "result": "success | failure | needs-review"
}
```

## Constraints

| # | Rule | Verification |
|---|------|-------------|
| 8 | Gmail queries use category:primary for draft automation and never query Promotions, Social, Updates, or Forums for draft targets | Verify every gmail_search_messages call for draft targets uses category:primary |
| 9 | Job alerts (LinkedIn, Indeed) are fetched separately from primary threads — scored for fit, never drafted | Job alert queries use label:updates from:(linkedin.com OR indeed.com) — separate node, separate payload field |

## What This Skill Does NOT Do

- Send emails (no tool available, no workaround attempted)
- Delete or archive messages
- Modify labels or stars
- Access spam/trash unless explicitly requested
- Create drafts without explicit user approval
- Auto-apply to jobs (deferred to Phase 5)

---

## Draft Generation Protocol (Phase 6.3)

> Full protocol for drafting email replies. Used by both the scheduled n8n workflow and the `/draft-email` on-demand command. Every draft follows all 5 steps in order.

### Step 1 — Read Thread

1. Call `gmail_read_thread` for the target thread
2. Extract: subject line, full thread history, what a reply needs to address (questions asked, actions requested, information needed)
3. **Parse the `from:` field** from the most recent message:
   - Raw format from Gmail API: `"Display Name" <email@domain.com>` or just `email@domain.com`
   - Extract `sender_email`: strip everything except the email address inside `< >`. If no angle brackets, the entire value is the email.
   - Extract `sender_name`: strip the email address and angle brackets, keep the display name only. If no display name exists, set to `null`.
   - Use `sender_email` to populate the `to:` field in `gmail_create_draft`
   - Use `sender_name` for salutation logic in Step 3. If null or unclear, use "Hi," and append `[Note: sender name unclear, verify recipient before sending]`
4. **Rejection detection** — before proceeding, check for rejection signals:
   - Subject contains: "application update", "position has been filled", "other candidates", "not moving forward", "decided to move forward with other", "not selected"
   - OR body contains: "we will be proceeding with other candidates", "we have decided to move forward with", "not selected for", "position has been filled"
   - If detected: do NOT auto-draft. Surface instead: `"This appears to be a rejection email from [sender]. Draft a reply anyway? (yes / skip) — Note: most rejections don't warrant replies unless you have a specific reason to maintain this relationship."`
   - Wait for explicit "yes" before drafting. If skipped, log as `dismissed: true` with reason `rejection_detected`.
5. **HTML/content check** — after extracting body text:
   - Strip all HTML tags from the message body
   - If remaining text is less than 50 meaningful words (excluding signatures, disclaimers, legal footers): skip thread, log as `"insufficient content to draft reply"`, move to next thread
   - Never draft a reply to a thread where the body content could not be read or parsed
6. Query Supabase `people` table for the sender (match on `sender_email`):
   - If found: load `relationship_type`, `last_contact_date`, any notes. This informs register selection in Step 2.
   - If not found: proceed with defaults. Do not create a people entry.

### Step 2 — Load Voice

1. Read `04-reflections/voice-profile.md` — this is mandatory for every draft, never skipped.
2. Read the relevant section from `02-knowledge/platform-rules.md` based on sender relationship:

| Sender type | Platform section | Register |
|---|---|---|
| Recruiter / professional contact | Cold Outreach / Email (Platform 3) | Direct, specific, warm. 100-200 words. |
| Warm contact / known person | Long-form (Platform 2) | Exploratory, personal. Up to 300 words if earned. |
| Unknown sender | Cold Outreach defaults | Direct, specific, warm. 100-200 words. |

### Step 3 — Write Draft

The reply must satisfy all of these:

1. **Salutation logic** (apply in priority order):
   - If sender exists in Supabase `people` table: use first name from people record. This overrides all other logic.
   - If sender has a display name with a clear first name (e.g., "Jane Smith"): use "Hi [first name],"
   - If sender display name exists but is a company name (e.g., "Acme Support"): use "Hi [company name],"
   - If sender display name is missing or is just an email address: use "Hi," and append to end of draft: "[Note: sender name unclear, verify recipient before sending]"
2. **Open with something specific to this thread** — never "Hope this finds you well", never "Thanks for reaching out", never any generic opener. Reference the actual content of their message.
3. **Address what the thread actually needs** — answer questions asked, confirm actions requested, provide information needed. Do not add tangents.
4. **Match register to relationship** — cold for unknown, warm for known, professional for recruiters. The people table context guides this.
5. **Stay under 200 words** unless thread complexity genuinely requires more (multi-question threads, detailed technical discussions). Maximum 300 words.
6. **Prohibited phrases** — never use any of these: "Happy to", "I just wanted to", "I hope this finds you", "reaching out to", "circling back", "touching base"
7. **Specificity requirement** — every draft must contain at least one detail specific to this thread or sender that could not appear in a reply to any other email. If no specific detail can be identified, flag: `"[Review: this draft lacks specificity — add one detail unique to this thread before sending]"`
8. **Rejection replies** (only if user explicitly approved in Step 1 rejection detection): acknowledge the decision in one sentence, then add one genuine specific sentence about the company or role. Under 75 words total.
9. **Pass voice calibration test** from `voice-profile.md`:
   - Does this sound like someone thinking, or someone presenting?
   - Is there at least one specific detail that couldn't have come from anyone else?
   - Would I be embarrassed if someone called this generic?

### Step 4 — Surface Proposal

Display the draft to the user in exactly this format:

```
Thread: [subject] — [sender]
Context: [one sentence on what this thread is about]

Draft:
[full draft text]

Save to Gmail drafts? (yes / edit / skip)
```

**Wait for the user's response. Never proceed without it.**

### Step 5 — On Response

| Response | Action |
|---|---|
| **yes** | Call `gmail_create_draft` with the draft text and thread ID. Write a `draft_log` entry: `approved: true`, `gmail_draft_id` from the response, `mode` set to current mode. |
| **edit** | Take the user's edit. Regenerate the draft incorporating their changes. Re-surface the proposal (return to Step 4). |
| **skip** | Write a `draft_log` entry: `dismissed: true`, `mode` set to current mode. Move to next thread or close. |

### Draft Generation Hard Constraints

1. **`gmail_send` is never called.** This tool does not exist in this skill and must never be added or simulated.
2. **Voice profile is loaded on every draft.** `04-reflections/voice-profile.md` is read before every draft generation. No caching across threads, no skipping.
3. **Approval gate fires before every `gmail_create_draft` call.** In on-demand mode, the user approves interactively. In scheduled mode, drafts are saved directly and the Telegram notification serves as the review surface.
4. **Every draft produces a `draft_log` entry** in Supabase, regardless of whether it was approved, edited, or skipped.
