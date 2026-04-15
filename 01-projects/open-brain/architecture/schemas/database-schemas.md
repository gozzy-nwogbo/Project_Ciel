# Database Schemas

**Phase:** 3 (Memory Search & RAG)
**Database:** Supabase (PostgreSQL + pgvector)
**Status:** Live. Schema deployed to Supabase on 2026-04-10.
**Created:** 2026-04-10

---

## Design Principles

1. **Every table gets an embedding column.** pgvector `vector(1536)` for semantic search across all content. Embedding model: `text-embedding-3-small` (OpenAI) or equivalent.
2. **Every capture gets metadata extraction.** Topics, entities, and action items are extracted by LLM at write time and stored as structured fields, not computed at query time.
3. **Soft deletes only.** No row is ever physically deleted. `deleted_at` timestamp marks removal. The PRD security table prohibits `DROP TABLE` and schema changes from agent access.
4. **Timestamps are UTC.** Display layer converts to user timezone (America/New_York).
5. **MCP tools are the only write path.** No direct SQL inserts from agents. Every write goes through a named MCP tool that logs the operation.

---

## Shared Columns

Every table includes these columns. They are listed once here and not repeated in each schema.

| Column | Type | Notes |
|---|---|---|
| `id` | `uuid` | Primary key. Default: `gen_random_uuid()` |
| `created_at` | `timestamptz` | Default: `now()` |
| `updated_at` | `timestamptz` | Default: `now()`, auto-updated via trigger |
| `deleted_at` | `timestamptz` | Null if active. Set on soft delete. |
| `embedding` | `vector(1536)` | pgvector column. Generated at write time. |

---

## 1. captures

The inbox log. Every piece of raw input that enters the system lands here first, before routing to its destination.

**MCP tools:** `write` (table: captures), `list_recent`, `semantic_search`

| Column | Type | Nullable | Notes |
|---|---|---|---|
| `source` | `text` | no | Where the capture came from: `slack`, `obsidian`, `email`, `manual`, `web_clipper` |
| `original_text` | `text` | no | The raw input, unmodified |
| `destination` | `text` | yes | Where the system routed it: `projects`, `people`, `ideas`, `knowledge`, or null if unrouted |
| `destination_id` | `uuid` | yes | FK to the target table row, if routed |
| `confidence` | `numeric(3,2)` | no | Routing confidence score (0.00 to 1.00). Below 0.60 = `needs_review` status. |
| `status` | `text` | no | One of: `pending`, `routed`, `needs_review`, `archived`. Default: `pending` |
| `topics` | `text[]` | yes | Extracted topic tags (e.g., `{'recruiting', 'frontend'}`) |
| `entities` | `jsonb` | yes | Extracted named entities: `{"people": [], "projects": [], "tools": []}` |
| `action_items` | `jsonb` | yes | Extracted actions: `[{"action": "...", "due": null, "priority": "normal"}]` |
| `processed_at` | `timestamptz` | yes | When metadata extraction ran |

**Indexes:**
- `idx_captures_status` on `(status)` where `deleted_at IS NULL`
- `idx_captures_source` on `(source, created_at DESC)`
- `idx_captures_confidence` on `(confidence)` where `status = 'needs_review'`
- `idx_captures_embedding` using `ivfflat (embedding vector_cosine_ops)` with `lists = 100`

**Confidence bouncer rule:** If `confidence < 0.60`, status is set to `needs_review` and the capture is never auto-routed. A human must approve the routing or discard.

---

## 2. people

Relationship tracking. Every person the system knows about, with health scoring for relationship maintenance.

**MCP tools:** `write` (table: people), `list_recent`, `semantic_search`, `stats`

| Column | Type | Nullable | Notes |
|---|---|---|---|
| `name` | `text` | no | Full name |
| `context` | `text` | yes | How you know them: `work`, `conference`, `friend`, `recruiter`, `mentor`, etc. |
| `company` | `text` | yes | Current company/org |
| `role` | `text` | yes | Their role/title |
| `email` | `text` | yes | Primary email |
| `last_contact` | `timestamptz` | yes | Most recent meaningful interaction |
| `contact_method` | `text` | yes | How last contact happened: `email`, `slack`, `in_person`, `linkedin` |
| `health_score` | `integer` | no | 1-100. Computed from recency, frequency, and relationship importance. Default: 50. |
| `importance` | `text` | no | One of: `high`, `medium`, `low`. Affects nudge frequency. Default: `medium`. |
| `notes` | `text` | yes | Free-form notes about the relationship |
| `topics` | `text[]` | yes | What you typically discuss: `{'ai', 'recruiting', 'design'}` |
| `next_action` | `text` | yes | Suggested next outreach action |
| `next_action_due` | `date` | yes | When the next action should happen |

**Indexes:**
- `idx_people_health` on `(health_score ASC)` where `deleted_at IS NULL` (surfaces neglected contacts first)
- `idx_people_last_contact` on `(last_contact ASC NULLS FIRST)` where `deleted_at IS NULL`
- `idx_people_importance` on `(importance, health_score ASC)`
- `idx_people_embedding` using `ivfflat (embedding vector_cosine_ops)` with `lists = 50`

**Health score decay:** A background process (heartbeat or cron) decays `health_score` over time based on `importance` tier:
- `high`: loses 2 points/week without contact
- `medium`: loses 1 point/week
- `low`: loses 1 point/2 weeks

The heartbeat nudge system (Phase 6) reads from this table to surface neglected contacts.

---

## 3. projects

Project tracking. Active and archived projects with next-action surfacing.

**MCP tools:** `write` (table: projects), `list_recent`, `semantic_search`, `stats`

| Column | Type | Nullable | Notes |
|---|---|---|---|
| `name` | `text` | no | Project name |
| `description` | `text` | yes | What the project is and why it exists |
| `status` | `text` | no | One of: `active`, `paused`, `completed`, `archived`. Default: `active` |
| `category` | `text` | yes | Grouping: `personal`, `work`, `learning`, `infrastructure` |
| `next_action` | `text` | yes | The single most important next step |
| `next_action_due` | `date` | yes | When the next action is due |
| `last_activity` | `timestamptz` | yes | Most recent capture or update linked to this project |
| `related_people` | `uuid[]` | yes | FK references to `people.id` |
| `vault_path` | `text` | yes | Path to the project folder in the vault (e.g., `01-projects/open-brain/`) |
| `notes` | `text` | yes | Free-form project notes |
| `topics` | `text[]` | yes | Extracted topic tags |

**Indexes:**
- `idx_projects_status` on `(status)` where `deleted_at IS NULL`
- `idx_projects_activity` on `(last_activity DESC NULLS LAST)` where `status = 'active'`
- `idx_projects_embedding` using `ivfflat (embedding vector_cosine_ops)` with `lists = 50`

**Vault linkage:** `vault_path` connects the Supabase row to the file-based vault. The vault is the human-readable canvas; the database is the agent-queryable store. Both exist. Neither replaces the other.

---

## 4. ideas

Idea storage. Raw ideas captured and optionally linked to projects.

**MCP tools:** `write` (table: ideas), `list_recent`, `semantic_search`

| Column | Type | Nullable | Notes |
|---|---|---|---|
| `title` | `text` | no | Short descriptive title |
| `body` | `text` | no | Full idea description |
| `status` | `text` | no | One of: `raw`, `developing`, `ready`, `implemented`, `discarded`. Default: `raw` |
| `source` | `text` | yes | Where the idea came from: `session`, `capture`, `heartbeat`, `emerge`, `manual` |
| `source_capture_id` | `uuid` | yes | FK to `captures.id` if the idea originated from a capture |
| `related_projects` | `uuid[]` | yes | FK references to `projects.id` |
| `related_ideas` | `uuid[]` | yes | FK references to other `ideas.id` (idea clusters) |
| `topics` | `text[]` | yes | Extracted topic tags |
| `priority` | `text` | yes | One of: `high`, `medium`, `low`. Null = unranked. |

**Indexes:**
- `idx_ideas_status` on `(status)` where `deleted_at IS NULL`
- `idx_ideas_source` on `(source, created_at DESC)`
- `idx_ideas_embedding` using `ivfflat (embedding vector_cosine_ops)` with `lists = 50`

**Idea lifecycle:** `raw` (just captured) -> `developing` (being explored) -> `ready` (actionable) -> `implemented` (done) or `discarded` (dropped). The `/emerge` slash command (Phase 5+) queries `raw` and `developing` ideas via semantic search to surface connections the human never stated explicitly.

---

## 5. Metadata Extraction Pipeline

Every row written to `captures` triggers a metadata extraction step before the row is considered complete. This runs at write time, not as a background job.

**Extraction flow:**
1. `write` MCP tool (table: captures) receives raw text
2. LLM call (Haiku) extracts: `topics`, `entities`, `action_items`
3. Embedding generated from `original_text`
4. Row written with all fields populated
5. If `confidence >= 0.60`, auto-route to destination table
6. If `confidence < 0.60`, set `status = 'needs_review'`

**Extraction prompt contract:**
```
Input: raw capture text
Output: JSON with topics (string[]), entities (object), action_items (array)
Model: claude-haiku-4-5-20251001
Max tokens: 512
```

The extraction result is stored on the capture row. It is not re-computed unless the capture is manually edited.

---

## 6. Embedding Strategy

**Model:** `text-embedding-3-small` (1536 dimensions)
**Index type:** IVFFlat (good enough for <100k rows, simpler than HNSW)
**Distance metric:** Cosine similarity (`vector_cosine_ops`)

**What gets embedded:**
- `captures.original_text`
- `people.name || ' ' || coalesce(context, '') || ' ' || coalesce(notes, '')`
- `projects.name || ' ' || coalesce(description, '') || ' ' || coalesce(notes, '')`
- `ideas.title || ' ' || body`

**When embeddings are generated:**
- On insert (via MCP write tool)
- On update to any text field (via MCP write tool)
- Never recomputed in bulk unless the embedding model changes

**MCP `semantic_search` behavior:**
1. Accepts a query string and optional table filter
2. Generates embedding for query
3. Runs cosine similarity search across specified tables (or all four)
4. Returns top N results with similarity score, ranked cross-table

---

## 7. Row-Level Security

Supabase RLS policies will restrict access to the MCP server's service role key. No public access.

| Policy | Rule |
|---|---|
| Select | Service role only. No anon access. |
| Insert | Service role only. `deleted_at` must be null on insert. |
| Update | Service role only. Cannot modify `id` or `created_at`. |
| Delete | Blocked. All deletes go through soft-delete (set `deleted_at`). |

The MCP server authenticates with a service role key stored in `.env`. The key never appears in vault files, hook scripts, or agent context.

---

*This document defines the database schemas for Open Brain. Implementation (Supabase table creation, RLS policies, MCP tool wiring) happens as Phase 3 progresses. Schema changes require updating this document first.*
