# MCP Tool Audit

> Living document tracking every registered MCP tool. Updated when integrations change.
> Last audited: 2026-04-14

---

## Open Brain (Supabase + pgvector)

Source: `01-projects/open-brain/mcp-server/server.py`
MCP config: `.mcp.json` → `open-brain`

| Tool | Trust Tier | Last Used | Default Pool | Load on Demand |
|------|-----------|-----------|-------------|---------------|
| `semantic_search` | read-only | 2026-04-14 | yes | no |
| `list_recent` | read-only | 2026-04-14 | yes | no |
| `stats` | read-only | 2026-04-14 | yes | no |
| `write` | mutating | 2026-04-14 | yes | no |
| `get_tool_registry` | read-only | 2026-04-14 | yes | no |

---

## Gmail (Claude.ai Remote MCP)

Source: `claude.ai/Gmail`
Skill: `.claude/skills/gmail.md`

| Tool | Trust Tier | Last Used | Default Pool | Load on Demand |
|------|-----------|-----------|-------------|---------------|
| `gmail_search_messages` | read-only | 2026-04-14 | no | yes |
| `gmail_read_message` | read-only | 2026-04-14 | no | yes |
| `gmail_read_thread` | read-only | 2026-04-14 | no | yes |
| `gmail_list_labels` | read-only | 2026-04-14 | no | yes |
| `gmail_list_drafts` | read-only | 2026-04-14 | no | yes |
| `gmail_get_profile` | read-only | 2026-04-14 | no | yes |
| `gmail_create_draft` | mutating | 2026-04-14 | no | yes |

---

## Google Calendar (Claude.ai Remote MCP)

Source: `claude.ai/Google_Calendar`
Skill: `.claude/skills/google-calendar.md`

| Tool | Trust Tier | Last Used | Default Pool | Load on Demand |
|------|-----------|-----------|-------------|---------------|
| `list_calendars` | read-only | 2026-04-14 | no | yes |
| `list_events` | read-only | 2026-04-14 | no | yes |
| `get_event` | read-only | 2026-04-14 | no | yes |
| `suggest_time` | read-only | 2026-04-14 | no | yes |
| `create_event` | **BLOCKED** | never | no | no |
| `update_event` | **BLOCKED** | never | no | no |
| `delete_event` | **BLOCKED** | never | no | no |
| `respond_to_event` | **BLOCKED** | never | no | no |

---

## Asana (Claude.ai Remote MCP)

Source: `claude.ai/Asana`
Skill: `.claude/skills/asana.md`

### Read Tools (18)

| Tool | Trust Tier | Last Used | Default Pool | Load on Demand |
|------|-----------|-----------|-------------|---------------|
| `get_me` | read-only | 2026-04-14 | no | yes |
| `get_user` | read-only | 2026-04-14 | no | yes |
| `get_users` | read-only | 2026-04-14 | no | yes |
| `get_teams` | read-only | 2026-04-14 | no | yes |
| `get_projects` | read-only | 2026-04-14 | no | yes |
| `get_project` | read-only | 2026-04-14 | no | yes |
| `get_tasks` | read-only | 2026-04-14 | no | yes |
| `get_task` | read-only | 2026-04-14 | no | yes |
| `get_my_tasks` | read-only | 2026-04-14 | no | yes |
| `get_attachments` | read-only | 2026-04-14 | no | yes |
| `get_portfolios` | read-only | 2026-04-14 | no | yes |
| `get_portfolio` | read-only | 2026-04-14 | no | yes |
| `get_items_for_portfolio` | read-only | 2026-04-14 | no | yes |
| `get_status_overview` | read-only | 2026-04-14 | no | yes |
| `search_objects` | read-only | 2026-04-14 | no | yes |
| `search_tasks_preview` | read-only | 2026-04-14 | no | yes |
| `get_project_internal` | read-only | 2026-04-14 | no | yes |
| `search_objects_internal` | read-only | 2026-04-14 | no | yes |

### Write Tools (approved projects only)

| Tool | Trust Tier | Last Used | Default Pool | Load on Demand |
|------|-----------|-----------|-------------|---------------|
| `create_tasks` | mutating | 2026-04-14 | no | yes |
| `create_task_preview` | mutating | 2026-04-14 | no | yes |
| `create_task_confirm` | mutating | 2026-04-14 | no | yes |
| `update_tasks` | mutating | 2026-04-14 | no | yes |
| `add_comment` | mutating | 2026-04-14 | no | yes |
| `create_project_status_update` | mutating | 2026-04-14 | no | yes |

### Blocked Tools

| Tool | Trust Tier | Last Used | Default Pool | Load on Demand |
|------|-----------|-----------|-------------|---------------|
| `create_project_preview` | **BLOCKED** | never | no | no |
| `create_project_confirm` | **BLOCKED** | never | no | no |
| `create_project_confirm_populate` | **BLOCKED** | never | no | no |
| `delete_task` | **BLOCKED** | never | no | no |

---

## n8n (Local MCP via n8n-mcp)

Source: `.mcp.json` → `n8n-mcp`
Config: n8n cloud API

| Tool | Trust Tier | Last Used | Default Pool | Load on Demand |
|------|-----------|-----------|-------------|---------------|
| `n8n_list_workflows` | read-only | 2026-04-13 | no | yes |
| `n8n_get_workflow` | read-only | 2026-04-13 | no | yes |
| `n8n_create_workflow` | mutating | 2026-04-13 | no | yes |
| `n8n_update_full_workflow` | mutating | never | no | yes |
| `n8n_update_partial_workflow` | mutating | never | no | yes |
| `n8n_delete_workflow` | destructive | never | no | yes |
| `n8n_validate_workflow` | read-only | 2026-04-13 | no | yes |
| `n8n_autofix_workflow` | mutating | never | no | yes |
| `n8n_test_workflow` | mutating | never | no | yes |
| `n8n_health_check` | read-only | 2026-04-13 | no | yes |
| `n8n_workflow_versions` | read-only | never | no | yes |
| `n8n_executions` | read-only | never | no | yes |
| `n8n_deploy_template` | mutating | never | no | yes |
| `n8n_audit_instance` | read-only | never | no | yes |
| `n8n_generate_workflow` | mutating | never | no | yes |
| `n8n_manage_credentials` | mutating | never | no | yes |
| `n8n_manage_datatable` | mutating | never | no | yes |
| `search_nodes` | read-only | 2026-04-13 | no | yes |
| `search_templates` | read-only | never | no | yes |
| `get_node` | read-only | never | no | yes |
| `get_template` | read-only | never | no | yes |
| `validate_node` | read-only | never | no | yes |
| `validate_workflow` | read-only | never | no | yes |
| `tools_documentation` | read-only | never | no | yes |

---

## Telegram (via n8n workflow, not MCP)

Source: n8n cloud workflow (Telegram Trigger node)
Note: Not a direct MCP tool. Runs as always-on n8n workflow.

| Capability | Trust Tier | Last Used | Notes |
|-----------|-----------|-----------|-------|
| Receive bot messages | read-only | 2026-04-13 | Trigger node, always-on |
| Reply in bot chat | mutating | 2026-04-13 | Via n8n Telegram node |
| Classify + route to Supabase | mutating | 2026-04-13 | Haiku classification |

---

## Supabase (via Open Brain MCP, not direct)

Source: Accessed through Open Brain MCP server, not a standalone MCP integration.
Tables: captures, people, projects, ideas

Direct Supabase access is scoped through the Open Brain server only. No standalone Supabase MCP is registered.

---

## Audit Notes

- **Total MCP tools registered:** ~62 (across Open Brain, Gmail, Calendar, Asana, n8n)
- **Blocked tools:** 8 (Calendar write tools + Asana project creation/deletion)
- **Default pool:** Only Open Brain tools (5) load by default. All others load on demand.
- **Gap:** No tool pool assembly mechanism exists yet (P9). All integration tools are available in every session regardless of task context.
- **Gap:** No retrieval_log table exists to track whether stored captures are actually retrieved (two-door audit).
- **Next audit:** After Phase 5 skill restructure adds metadata.json to each skill.
