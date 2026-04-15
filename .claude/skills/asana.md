# Asana Integration Skill

> Open Brain Phase 4. Read all tasks. Write to approved projects only. No project creation or deletion.

## Permission Boundaries (from PRD Security Table)

| Operation | Allowed | Tool |
|-----------|---------|------|
| Get current user | Yes | `get_me` |
| Get user details | Yes | `get_user` |
| List users | Yes | `get_users` |
| List teams | Yes | `get_teams` |
| List projects | Yes | `get_projects` |
| Get project details | Yes | `get_project` |
| List tasks | Yes | `get_tasks` |
| Get task details | Yes | `get_task` |
| Get my tasks | Yes | `get_my_tasks` |
| List attachments | Yes | `get_attachments` |
| List portfolios | Yes | `get_portfolios` |
| Get portfolio details | Yes | `get_portfolio` |
| Get portfolio items | Yes | `get_items_for_portfolio` |
| Get status overview | Yes | `get_status_overview` |
| Search objects | Yes | `search_objects` |
| Search tasks preview | Yes | `search_tasks_preview` |
| Create task | **Approved projects only** | `create_tasks`, `create_task_preview`, `create_task_confirm` |
| Update task | **Approved projects only** | `update_tasks` |
| Add comment | **Approved projects only** | `add_comment` |
| Post status update | **Approved projects only** | `create_project_status_update` |
| Create project | **NO** | Tool exists but must never be called. |
| Delete task | **NO** | Tool exists but must never be called. |

## Approved Projects (Explicit List)

Only these projects may receive writes. This list is the canonical source. Do not infer additional projects.

| Project | GID | Workspace GID |
|---------|-----|---------------|
| Open-Brain | `1214064555057948` | `1214044632574385` |

**Adding a project to this list requires explicit user instruction in the conversation. Never add projects by inference.**

## Workspace Restriction

Only workspace `1214044632574385` is accessible. Do not attempt to query or write to other workspaces.

## Write Gating (Approval-First Pattern)

Before any write operation (create task, update task, add comment, post status):

1. Verify the target project GID is in the Approved Projects table above
2. Surface what will be written: task name, project, assignee, due date, notes
3. Wait for explicit user approval ("yes", "approved", "do it", "create it")
4. Only after approval: call the write tool
5. Log the permission decision to system-events.jsonl

If the target project is NOT in the approved list: refuse the write and surface which project was requested.

## Available Operations

### 1. Surface Open Tasks

List incomplete tasks in a project or across all assigned tasks.

```
Tool: get_tasks
project: <project GID>
opt_fields: "name,assignee,due_on,completed,notes"
```

Or for personal task list:
```
Tool: get_my_tasks
completed_since: "now"
```

Output format:
```
- [ ] Task name (due: YYYY-MM-DD, assignee: name)
```

### 2. Get Task Details

```
Tool: get_task
task_id: <task GID>
```

Surface: name, description, assignee, due date, subtasks, comments, custom fields, dependencies.

### 3. Search Tasks

```
Tool: search_objects
resource_type: "task"
query: "<search term>"
```

### 4. Create Task (Approved Projects Only)

**Workflow (mandatory):**
1. Confirm target project is in the Approved Projects list
2. Compose task details: name, notes, assignee, due_on
3. Surface the proposed task to the user
4. Wait for explicit approval
5. Call `create_task_preview` for single tasks, `create_tasks` for multiple

```
Tool: create_task_preview
taskName: "Task name"
project_gid: "1214064555057948"
description: "Task description"
assignee: "me"
dueDate: "YYYY-MM-DD"
```

### 5. Update Task (Approved Projects Only)

Same approval workflow:
1. Verify task belongs to an approved project
2. Surface proposed changes
3. Wait for approval
4. Call `update_tasks`

```
Tool: update_tasks
tasks: [{"task": "<GID>", "name": "Updated name", "due_on": "YYYY-MM-DD"}]
```

### 6. Add Comment (Approved Projects Only)

```
Tool: add_comment
task_id: "<GID>"
text: "Comment text"
```

Same approval pattern: surface comment text, wait for confirmation.

### 7. Project Status Update (Approved Projects Only)

```
Tool: create_project_status_update
parent: "<project GID>"
title: "Status title"
color: "green|yellow|red|blue|complete"
text: "Status body"
```

## Event Logging

Every Asana tool call must be logged to `.claude/logs/system-events.jsonl`:

```json
{
  "timestamp": "ISO-8601",
  "category": "integration",
  "action": "asana_read | asana_task_create | asana_task_update | asana_comment | asana_status",
  "tool": "tool name",
  "reason": "why this action was taken",
  "permission_tier": "read-only | mutating",
  "project_gid": "if applicable",
  "approved_project": true | false,
  "result": "success | failure | blocked"
}
```

## What This Skill Does NOT Do

- Create new projects (tool exists but is never called)
- Delete tasks (tool exists but is never called)
- Write to projects not in the Approved Projects list
- Access workspaces beyond the single registered workspace
- Create tasks without explicit user approval
- Infer project approval from context
