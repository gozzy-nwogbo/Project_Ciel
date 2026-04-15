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
| Send email | **NO** | Not wired. No send tool loaded. |
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

## What This Skill Does NOT Do

- Send emails (no tool available, no workaround attempted)
- Delete or archive messages
- Modify labels or stars
- Access spam/trash unless explicitly requested
- Create drafts without explicit user approval
- Auto-apply to jobs (deferred to Phase 5)
