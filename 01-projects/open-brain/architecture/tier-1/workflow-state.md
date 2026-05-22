# Workflow State Model

**Primitive:** 4 (Workflow State)
**Phase:** 2 (Context Persistence)
**Status:** Design document. No implementation yet.
**Created:** 2026-04-09

---

## 1. Session State vs. Workflow State

These solve different problems. Conflating them is the fastest way to build a system that loses work.

**Session state** is the conversational context between a human and an agent within a single Claude Code session. It includes the transcript, loaded files, tool results, and the agent's working memory. Session state is ephemeral by nature. When a session ends, the transcript is gone unless a hook captures it. Session state lives in Claude Code's internal runtime and in the session JSON persisted by hooks.

**Workflow state** is the progress of a multi-step task that may span multiple sessions, run in the background, or execute without a human present. A flush process that extracts concepts from daily logs is a workflow. A heartbeat that gathers context from five APIs and sends a Slack digest is a workflow. These workflows have steps, and those steps can fail, pause, or need to resume.

The key differences:

| Dimension | Session State | Workflow State |
|---|---|---|
| Lifetime | Single session | Spans sessions, days, or indefinitely |
| Owner | Claude Code runtime | Vault file system |
| Trigger | Human opens a session | Cron, hook, or manual invocation |
| Failure mode | Session ends, context lost | Step fails, workflow pauses at checkpoint |
| Resume mechanism | `.continue-here.md` (manual) | Checkpoint file (automatic) |
| Persistence | Hook-written transcript summary | Explicit state file per workflow run |

**Why this matters for Open Brain:** Every automated process we build (flush, heartbeat, email pipeline, weekly review) needs to survive crashes gracefully. If the Anthropic API times out during a flush at log 3 of 7, the next run should pick up at log 4, not restart from log 1. Session state cannot provide this. Workflow state can.

---

## 2. Workflow Definitions

### 2.1 Flush Process

**Purpose:** Extract concepts and connections from daily logs into the knowledge wiki.
**Current status:** Built (`.claude/scripts/flush.py`). States are implicit. This section documents them explicitly.

```
               ┌─────────┐
               │  idle    │
               └────┬─────┘
                    │ cron fires or manual run
                    ▼
              ┌───────────┐
              │  scanning  │
              └────┬──────┘
                   │ unprocessed logs found
                   ▼
            ┌─────────────┐
            │  extracting  │◄── per-log loop
            └────┬────────┘
                 │ API returns, files written
                 ▼
            ┌──────────┐
            │  writing  │
            └────┬─────┘
                 │ concept + connection files saved, log marked
                 ▼
            ┌────────────┐
            │  indexing   │
            └────┬───────┘
                 │ index.md rebuilt
                 ▼
            ┌──────────┐
            │   done    │
            └──────────┘
```

| State | Trigger In | Trigger Out | On Crash |
|---|---|---|---|
| idle | Process not running | Cron fires or manual invocation | N/A |
| scanning | Entry point called | Unprocessed logs enumerated | Safe. No side effects yet. |
| extracting | Log file read, API called | API returns JSON | Safe. Log not yet marked. Re-run will re-extract this log. |
| writing | JSON parsed | Concept/connection files written to disk | Safe. Files use "skip if exists" guard. Partial writes are idempotent on next run. |
| indexing | All logs processed | index.md rebuilt from disk state | Safe. Index rebuild is a full scan, not incremental. |
| done | Index written | Process exits | N/A |

**Checkpoint mechanism (current):** The `flush_processed: true` frontmatter marker on each daily log. This is a per-item checkpoint, not a per-run checkpoint. This is correct for this workflow because each log is independent.

---

### 2.2 Heartbeat Process

**Purpose:** Gather context from all connected APIs, reason about priorities, and deliver a digest via Slack DM.
**Current status:** Not built. Scheduled for Phase 6.

```
              ┌─────────┐
              │  idle    │
              └────┬────┘
                   │ cron fires (morning or weekly)
                   ▼
             ┌───────────┐
             │  gathering │
             └────┬──────┘
                  │ all API responses collected
                  ▼
             ┌────────────┐
             │  reasoning  │
             └────┬───────┘
                  │ digest drafted
                  ▼
             ┌──────────────────┐
             │ awaiting_approval │
             └────┬─────────────┘
                  │ human approves or edits
                  ▼
             ┌────────────┐
             │  delivering │
             └────┬───────┘
                  │ Slack DM sent
                  ▼
             ┌──────────┐
             │   done    │
             └──────────┘
```

| State | Trigger In | Trigger Out | On Crash |
|---|---|---|---|
| idle | Not running | Cron fires | N/A |
| gathering | Entry point called | All API data collected and cached locally | Resume: skip APIs whose cache file exists for this run |
| reasoning | All data cached | LLM produces digest draft | Resume: re-run reasoning from cached data (cheap) |
| awaiting_approval | Draft written to staging file | Human approves via Slack reaction or CLI | Resume: draft persists in staging file, re-prompt for approval |
| delivering | Approval received | Slack API confirms delivery | Resume: check Slack for duplicate before re-sending |
| done | Delivery confirmed | Workflow run archived | N/A |

**Checkpoint data:** Run ID, gathered API responses (cached as JSON), draft text, approval status. All written to `.claude/state/heartbeat/<run-id>/`.

---

### 2.3 Email Draft Pipeline

**Purpose:** Read inbox, identify threads needing response, draft replies for human approval.
**Current status:** Not built. Scheduled for Phase 4 (read) and Phase 6 (draft).

```
              ┌─────────┐
              │  idle    │
              └────┬────┘
                   │ triggered by heartbeat or manual
                   ▼
             ┌───────────┐
             │  fetching  │
             └────┬──────┘
                  │ inbox threads retrieved
                  ▼
             ┌─────────────┐
             │  triaging    │
             └────┬────────┘
                  │ threads scored and filtered
                  ▼
             ┌────────────┐
             │  drafting   │◄── per-thread loop
             └────┬───────┘
                  │ draft written
                  ▼
             ┌──────────────────┐
             │ awaiting_approval │
             └────┬─────────────┘
                  │ human approves, edits, or rejects each draft
                  ▼
             ┌──────────┐
             │   done    │
             └──────────┘
```

| State | Trigger In | Trigger Out | On Crash |
|---|---|---|---|
| idle | Not running | Heartbeat or manual trigger | N/A |
| fetching | Entry point called | Thread list cached | Resume: re-fetch (Gmail reads are idempotent) |
| triaging | Threads cached | Scored list written | Resume: re-triage from cache |
| drafting | Per thread: triage complete | Draft saved to staging | Resume: skip threads with existing drafts |
| awaiting_approval | All drafts staged | Human acts on each draft | Resume: re-present unapproved drafts |
| done | All drafts resolved | Run archived | N/A |

**Checkpoint data:** Run ID, thread list, triage scores, per-thread draft status. All written to `.claude/state/email/<run-id>/`.

**Security constraint:** This pipeline never sends. It creates Gmail drafts only. The human sends manually. This is a non-negotiable boundary from the PRD security table.

---

### 2.4 Weekly Review

**Purpose:** Scan the past 7 days of daily logs, surface open loops, suggest next-week actions, identify recurring themes.
**Current status:** Not built. Scheduled for Phase 6.

```
              ┌─────────┐
              │  idle    │
              └────┬────┘
                   │ Sunday cron fires
                   ▼
             ┌────────────┐
             │  collecting │
             └────┬───────┘
                  │ 7 days of logs read
                  ▼
             ┌─────────────┐
             │  analyzing   │
             └────┬────────┘
                  │ LLM produces review
                  ▼
             ┌────────────┐
             │  writing    │
             └────┬───────┘
                  │ review saved to 06-daily/ and promoted to memory
                  ▼
             ┌──────────────────┐
             │ awaiting_approval │
             └────┬─────────────┘
                  │ human reviews (optional, can auto-complete)
                  ▼
             ┌──────────┐
             │   done    │
             └──────────┘
```

| State | Trigger In | Trigger Out | On Crash |
|---|---|---|---|
| idle | Not running | Sunday cron fires | N/A |
| collecting | Entry point called | Daily logs for the week read into memory | Safe. Read-only. |
| analyzing | Logs collected | LLM produces structured review | Resume: re-analyze from collected logs |
| writing | Review produced | Written to `06-daily/week-review-YYYY-WNN.md` | Resume: overwrite (single output file) |
| awaiting_approval | Review written | Human confirms or workflow auto-completes after timeout | Resume: re-present review |
| done | Approved or timed out | Run archived | N/A |

**Checkpoint data:** Run ID, collected log content, review draft. Written to `.claude/state/weekly-review/<run-id>/`.

---

### 2.5 Capture-to-Storage Pipeline

**Purpose:** Move raw input from `00-inbox/` through processing into `02-knowledge/`.
**Current status:** Partially built. The flush process handles daily-log-to-knowledge. This covers external captures (articles, transcripts, papers) dropped into `00-inbox/raw/`.

```
              ┌─────────┐
              │  idle    │
              └────┬────┘
                   │ new file detected in 00-inbox/raw/
                   ▼
             ┌─────────────┐
             │  converting  │
             └────┬────────┘
                  │ file converted to markdown
                  ▼
             ┌─────────────┐
             │  extracting  │
             └────┬────────┘
                  │ LLM extracts concepts, tags, connections
                  ▼
             ┌────────────┐
             │  filing     │
             └────┬───────┘
                  │ written to 02-knowledge/<topic>/
                  ▼
             ┌────────────┐
             │  indexing   │
             └────┬───────┘
                  │ index.md updated
                  ▼
             ┌──────────┐
             │   done    │
             └──────────┘
```

| State | Trigger In | Trigger Out | On Crash |
|---|---|---|---|
| idle | No new files | File detected in `00-inbox/raw/` | N/A |
| converting | Raw file read | Markdown version written to `00-inbox/processed/` | Resume: re-convert (source file unchanged) |
| extracting | Markdown available | LLM returns structured extraction | Resume: re-extract from markdown |
| filing | Extraction complete | Knowledge files written | Resume: skip-if-exists guard on each file |
| indexing | All files written | index.md rebuilt | Resume: full rebuild (same as flush) |
| done | Index updated | Source file moved to `00-inbox/archived/` | N/A |

**Checkpoint mechanism:** File location is the checkpoint. A file in `raw/` has not been touched. A file in `processed/` has been converted but not extracted. A file in `archived/` is complete. No separate state file needed.

---

## 3. Checkpoint Persistence Pattern

Every workflow that runs outside a Claude Code session needs crash-safe state. The pattern is the same across all workflows.

### 3.1 State Directory Structure

```
.claude/state/
├── flush/           # flush process (currently uses frontmatter markers instead)
├── heartbeat/
│   └── <run-id>/
│       ├── state.json
│       ├── gathered/       # cached API responses
│       └── draft.md
├── email/
│   └── <run-id>/
│       ├── state.json
│       ├── threads.json
│       └── drafts/
│           └── <thread-id>.md
├── weekly-review/
│   └── <run-id>/
│       ├── state.json
│       └── review.md
└── capture/
    # uses file location as implicit state (no state.json needed)
```

### 3.2 state.json Schema

Every workflow run that uses explicit checkpointing writes a `state.json`:

```json
{
  "workflow": "heartbeat",
  "run_id": "2026-04-09T08:00:00",
  "current_state": "gathering",
  "started_at": "2026-04-09T08:00:00Z",
  "updated_at": "2026-04-09T08:00:12Z",
  "completed_items": ["gmail", "calendar"],
  "pending_items": ["slack", "asana"],
  "error": null
}
```

Fields:
- **workflow**: The workflow name (matches directory name)
- **run_id**: Unique per invocation. Use ISO timestamp of trigger time.
- **current_state**: One of the named states from that workflow's state machine
- **started_at / updated_at**: ISO timestamps
- **completed_items**: Items processed so far in the current state (for per-item loops)
- **pending_items**: Items remaining
- **error**: Null if healthy. String describing last error if the workflow stopped unexpectedly.

### 3.3 Rules

1. **Write state.json before starting work in a new state.** If the process crashes, the state file tells the next run where to resume.
2. **Update completed_items after each item, not after the full batch.** This gives per-item resume granularity.
3. **Never delete state.json until the workflow reaches `done`.** A missing state file means "idle."
4. **Old run directories are archived, not deleted.** Move completed runs to `.claude/state/<workflow>/archive/` after 7 days. This provides audit trail.
5. **The flush process is an exception.** Its per-file frontmatter marker is simpler and sufficient because each daily log is fully independent. Do not retrofit state.json onto flush unless it gains cross-file dependencies.

---

## 4. Standard State Machine Format

All future workflows in this system follow this format. Copy this template when designing a new workflow.

### Template

```
Workflow: <name>
Trigger: <what starts it>
Frequency: <cron schedule or event-driven>
Security: <permission boundaries from PRD>

States:
  idle        → <first_state>     [trigger: <what causes transition>]
  <state_1>   → <state_2>         [trigger: <what causes transition>]
  <state_N>   → done              [trigger: <what causes transition>]

Crash behavior:
  <state>: <what happens on resume>

Checkpoint:
  location: .claude/state/<workflow>/<run-id>/
  schema: state.json with completed_items/pending_items

Approval required: yes | no | optional
  If yes: workflow pauses at awaiting_approval until human acts
```

### Conventions

- **State names are lowercase, single words.** Use underscores only when a compound is unavoidable (e.g., `awaiting_approval`).
- **Every workflow with external side effects must have an `awaiting_approval` state.** The PRD principle is "agent surfaces, human decides, agent executes." No autonomous sends, posts, or mutations.
- **The `done` state is always terminal.** A workflow that needs to repeat goes back to `idle` via cron, not via a `done → idle` transition.
- **Error is not a state.** An error is a property on the current state. The workflow stays in whatever state it was in when the error occurred. The next run reads the state file, sees the error, and retries or skips that item.
- **Run IDs use ISO timestamps.** No UUIDs. Timestamps are sortable, human-readable, and unique at the granularity these workflows run (minutes, not milliseconds).

---

*This document defines the workflow state model for Open Brain. Implementation happens per-workflow as each is built. The flush process already conforms to these patterns implicitly. Future workflows should conform explicitly by writing state.json at each transition.*
