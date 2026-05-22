# Skill: mcp2skill

Generates a complete integration skill from any connected MCP server by querying its tools, classifying permissions against the PRD security framework, and producing a SKILL.md with allowed/mutating/blocked sections, producing output at `.claude/skills/integrations/[server-name]/SKILL.md` — invoke when a new MCP server is connected, when wrapping an existing server as a skill, or when the user says "build integration skill" or "mcp2skill."

---

## Inputs

| Input | Required | Purpose |
|---|---|---|
| Target MCP server name or identifier | Yes | Which server to query for tools |
| `02-knowledge/mcp-tool-audit.md` | Yes | Check if server already registered; update after generation |
| `01-projects/open-brain/PRD/PRD.md` | Yes | Security boundaries framework for permission classification |
| `.claude/skills/integrations/gmail/SKILL.md` | Yes | Reference pattern for generated skill structure |

---

## Output Contract

| Path | Format | When |
|---|---|---|
| `.claude/skills/integrations/[server-name]/SKILL.md` | md | Permission proposal approved |
| `.claude/skills/integrations/[server-name]/metadata.json` | json | Always alongside SKILL.md |
| `.claude/skills/integrations/[server-name]/skill-audit-[server-name].md` | md | After audit runs |
| Updated `02-knowledge/mcp-tool-audit.md` | md | After skill generation |

**Out of scope:** Building MCP servers, modifying MCP server code, configuring MCP connections, creating n8n workflows for integrations.

---

## Process

### Step 1: Pre-flight Check
Read `02-knowledge/mcp-tool-audit.md`. Search for the target server name.
- **If found:** Surface existing entry and ask: "This server is already registered. Update existing entry or regenerate skill from scratch?" Wait for response.
- **If not found:** Proceed to Step 2.

### Step 2: Query MCP Server
List all available tools from the target MCP server. For each tool extract: name, description, what it reads or writes, what it can affect. Surface: "Found [N] tools on [server name]. Proceeding to classification."

### Step 3: Permission Proposal (approval gate)
Classify every tool using the PRD security boundaries framework:
- **Read-only:** retrieves data, no side effects, no writes
- **Mutating:** creates or modifies data, reversible
- **Destructive:** deletes, sends, or permanently affects external state

Produce a proposal table:

| Tool | Proposed Tier | Reason | Allow / Block |
|---|---|---|---|
| [tool name] | [tier] | [one line] | [Allow / Block] |

Default stance: when uncertain between tiers, classify higher (more restrictive). Flag uncertainty.

Surface: "Here is the proposed permission classification for [server name]. Review and confirm — type APPROVE to proceed, or specify changes." **Wait for explicit approval. Never proceed without it.**

### Step 4: Generate Skill Files
After approval, create `.claude/skills/integrations/[server-name]/` folder. Generate:

**SKILL.md** (match Gmail skill structure):
- Description block (5 lines max): what integration does, trigger phrases, output artifact
- Permission Boundaries table (from approved proposal)
- Allowed Tools section: read-only tools, callable without approval
- Mutating Tools section: each requires approval-first pattern before execution
- Blocked Tools section: never call, document why
- Graceful Degradation: if server unreachable, log to `00-inbox/staging/[server]-unavailable-[date].md` and surface to user
- Event Logging: every tool call writes to `.claude/logs/system-events.jsonl` with: timestamp, session_id, action, integration, permission_tier, inputs_summary, result, reason
- "What This Skill Does NOT Do" section

**metadata.json:** name, category (integrations), trigger_phrases, vault_paths, primitives_required [P2, P7], last_eval_date, audit_status (pending).

### Step 5: Run Skill-Authoring Audit
Run 9-criterion audit against generated SKILL.md. Produce `skill-audit-[server-name].md`. Update metadata.json audit_status with result.

### Step 6: Update MCP Tool Audit Doc
Add new entry to `02-knowledge/mcp-tool-audit.md`: name, source, trust tier (overall), default pool, load-on-demand, tools count, allowed count, blocked count, date added.

---

## Constraints

| # | Constraint | Verification |
|---|---|---|
| 1 | Permission proposal fires before any skill file is written | Check: no files in integrations/[server]/ before approval |
| 2 | Every tool classified — none skipped or left unclassified | Check: tool count in proposal matches tool count from query |
| 3 | Approval-first pattern present for all mutating/destructive tools in generated skill | Check: grep for "approval" or "wait for" near each mutating tool section |
| 4 | Graceful degradation present in generated skill | Check: section exists with fallback logging path |
| 5 | Permission logging present matching system-events.jsonl format | Check: Event Logging section with 8 required fields |
| 6 | No hardcoded server URLs in generated skill | Check: grep for http:// or https:// in SKILL.md returns zero |
| 7 | Audit runs before session closes | Check: skill-audit file exists alongside SKILL.md |
| 8 | MCP tool audit doc updated after generation | Check: server name appears in mcp-tool-audit.md |

---

## Edge Cases

1. **Server has zero tools:** Surface: "Server [name] returned 0 tools. Either the server is not connected or has no exposed tools. Aborting." Do not create any files.
2. **All tools classified as destructive:** Surface warning: "All [N] tools are destructive. Recommend blocking all and reconsidering this integration." Still produce the proposal for review.
3. **User rejects the permission proposal entirely:** Ask what changes are needed. Regenerate the proposal with changes. Do not proceed until a version is approved.
4. **Server already has a skill but user wants regeneration:** Delete existing skill folder contents, regenerate from scratch. Preserve any manually-added sections the user flags.
5. **Tool description is missing or vague:** Classify as mutating (conservative default). Flag: "Tool [name] has no description. Classified as mutating by default. Verify manually."

---

## Handoff

After this skill completes, the next stage receives:
- **Artifact:** Integration skill at `.claude/skills/integrations/[server-name]/SKILL.md` + updated `mcp-tool-audit.md`
- **Condition:** Skill audit complete, metadata.json written, MCP audit doc updated
- **Routing:** New skill is registered in `03-skills/registry.md` under Integrations. Skill is ready for use in sessions matching the integration's session type scope.
