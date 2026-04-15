# Skill Registry

> Check here before building anything new. If a skill exists, invoke it.
> If a skill is missing, build it, then register it here before use.

**Total registered skills:** 42
**Last updated:** 2026-04-14
**Last audit run:** 2026-04-14 (Phase 5 Track A migration)

---

## How to Use This Registry

1. Identify the task category (development, design, writing, etc.)
2. Find a matching skill by name or trigger phrase
3. Invoke by referencing the skill file path
4. If nothing matches, go to `meta/skill-creator` first

**All skills now live in:** `.claude/skills/[category]/[skill-name]/SKILL.md`

---

## Development (15 skills)

| Skill | Trigger Phrases | Path | Audit | Last Eval |
|-------|----------------|------|-------|-----------|
| `brainstorming` | "brainstorm", "explore ideas", "what are my options" | .claude/skills/development/brainstorming/ | DRAFT | 2026-04-14 |
| `changelog-generator` | "generate changelog", "what changed", "release notes" | .claude/skills/development/changelog-generator/ | DRAFT | 2026-04-14 |
| `dispatching-parallel-agents` | "run in parallel", "split this across agents", "dispatch" | .claude/skills/development/dispatching-parallel-agents/ | DRAFT | 2026-04-14 |
| `executing-plans` | "execute this plan", "start implementation", "run the plan" | .claude/skills/development/executing-plans/ | DRAFT | 2026-04-14 |
| `finishing-a-development-branch` | "finish this branch", "wrap up", "ready to merge" | .claude/skills/development/finishing-a-development-branch/ | DRAFT | 2026-04-14 |
| `mcp-builder` | "build an MCP", "create MCP server", "MCP tool" | .claude/skills/development/mcp-builder/ | DRAFT | 2026-04-14 |
| `receiving-code-review` | "I got feedback", "review came back", "address comments" | .claude/skills/development/receiving-code-review/ | DRAFT | 2026-04-14 |
| `requesting-code-review` | "review my code", "check this PR", "audit this file" | .claude/skills/development/requesting-code-review/ | DRAFT | 2026-04-14 |
| `subagent-driven-development` | "use subagents", "delegate to agents", "agent-driven" | .claude/skills/development/subagent-driven-development/ | DRAFT | 2026-04-14 |
| `systematic-debugging` | "debug this", "fix this error", "something is broken" | .claude/skills/development/systematic-debugging/ | DRAFT | 2026-04-14 |
| `test-driven-development` | "write tests first", "TDD", "test before code" | .claude/skills/development/test-driven-development/ | DRAFT | 2026-04-14 |
| `using-git-worktrees` | "worktree", "parallel branches", "git worktree" | .claude/skills/development/using-git-worktrees/ | DRAFT | 2026-04-14 |
| `verification-before-completion` | "verify this works", "check before done", "final check" | .claude/skills/development/verification-before-completion/ | DRAFT | 2026-04-14 |
| `webapp-testing` | "test the app", "QA this", "end-to-end test" | .claude/skills/development/webapp-testing/ | DRAFT | 2026-04-14 |
| `writing-plans` | "write a plan", "plan this out", "create a PRD" | .claude/skills/development/writing-plans/ | DRAFT | 2026-04-14 |

---

## Design (1 skill)

| Skill | Trigger Phrases | Path | Audit | Last Eval |
|-------|----------------|------|-------|-----------|
| `interface-design` | "design this UI", "build a component", "design system" | .claude/skills/design/interface-design/ | DRAFT | 2026-04-14 |

---

## Writing (3 skills)

| Skill | Trigger Phrases | Path | Audit | Last Eval |
|-------|----------------|------|-------|-----------|
| `writing-gateway` | "write", "draft", "LinkedIn post", "email draft", "article", "essay", "copy", "letter", "cold outreach" | .claude/skills/writing/writing-gateway/ | DRAFT | 2026-04-14 |
| `content-research-writer` | "write an article", "research and write", "content piece" | .claude/skills/writing/content-research-writer/ | DRAFT | 2026-04-14 |
| `internal-comms` | "write a slack message", "internal announcement", "team update" | .claude/skills/writing/internal-comms/ | DRAFT | 2026-04-14 |

---

## Productivity (3 skills)

| Skill | Trigger Phrases | Path | Audit | Last Eval |
|-------|----------------|------|-------|-----------|
| `file-organizer` | "organize these files", "sort this folder", "clean up structure" | .claude/skills/productivity/file-organizer/ | DRAFT | 2026-04-14 |
| `invoice-organizer` | "organize invoices", "sort receipts", "expense tracking" | .claude/skills/productivity/invoice-organizer/ | DRAFT | 2026-04-14 |
| `meeting-insights-analyzer` | "analyze this meeting", "extract insights", "meeting notes" | .claude/skills/productivity/meeting-insights-analyzer/ | DRAFT | 2026-04-14 |

---

## Meta (5 skills)

| Skill | Trigger Phrases | Path | Audit | Last Eval |
|-------|----------------|------|-------|-----------|
| `skill-creator` | "create a new skill", "build a skill", "I need a skill for" | .claude/skills/meta/skill-creator/ | DRAFT | 2026-04-14 |
| `skill-authoring` | "audit this skill", "validate skill", "skill ready for production?" | .claude/skills/meta/skill-authoring/ | **PASS** | 2026-04-14 |
| `orchestrator` | "what's next in the pipeline", "pipeline status", "which stage" | .claude/skills/meta/orchestrator/ | **PASS** | 2026-04-14 |
| `agent-harness` | "evaluate my agent harness", "audit this CLAUDE.md", "design the harness for" | .claude/skills/meta/agent-harness/ | DRAFT | 2026-04-14 |
| `spec-contract` | "write a spec contract", "create spec for", "lock the spec" | .claude/skills/meta/spec-contract/ | DRAFT | 2026-04-14 |

> **Always use `skill-creator` when adding to this registry.** It ensures consistent structure, evaluation criteria, and metadata.
> **Run `skill-authoring` before any skill enters a pipeline.** It produces a binary PASS/DRAFT verdict against the V2 standard.

---

## Integrations (3 skills)

| Skill | Trigger Phrases | Path | Audit | Last Eval |
|-------|----------------|------|-------|-----------|
| `gmail` | "check email", "read inbox", "draft reply", "gmail", "email" | .claude/skills/integrations/gmail/ | DRAFT | 2026-04-14 |
| `google-calendar` | "calendar", "schedule", "meetings", "free time", "conflicts" | .claude/skills/integrations/google-calendar/ | DRAFT | 2026-04-14 |
| `asana` | "tasks", "asana", "project tasks", "create task", "open brain tasks" | .claude/skills/integrations/asana/ | DRAFT | 2026-04-14 |

---

## n8n (7 skills)

| Skill | Trigger Phrases | Path | Audit | Last Eval |
|-------|----------------|------|-------|-----------|
| `n8n-code-javascript` | "write JS in n8n", "code node javascript", "n8n JS" | .claude/skills/n8n/n8n-code-javascript/ | DRAFT | 2026-04-14 |
| `n8n-code-python` | "write Python in n8n", "code node python", "n8n Python" | .claude/skills/n8n/n8n-code-python/ | DRAFT | 2026-04-14 |
| `n8n-expression-syntax` | "n8n expression", "reference data in n8n", "{{ syntax }}" | .claude/skills/n8n/n8n-expression-syntax/ | DRAFT | 2026-04-14 |
| `n8n-mcp-tools-expert` | "n8n MCP", "connect MCP to n8n", "MCP tool in workflow" | .claude/skills/n8n/n8n-mcp-tools-expert/ | DRAFT | 2026-04-14 |
| `n8n-node-configuration` | "configure this node", "set up n8n node", "node settings" | .claude/skills/n8n/n8n-node-configuration/ | DRAFT | 2026-04-14 |
| `n8n-validation-expert` | "validate workflow", "check n8n logic", "workflow QA" | .claude/skills/n8n/n8n-validation-expert/ | DRAFT | 2026-04-14 |
| `n8n-workflow-patterns` | "build a workflow", "new n8n workflow", "automation pattern" | .claude/skills/n8n/n8n-workflow-patterns/ | DRAFT | 2026-04-14 |

> **n8n standard patterns** (from CLAUDE.md):
> - Agent workflow: `Trigger → Prepare Input → AI Agent → Chat Model → Output Parser → Format Output`
> - Automation workflow: `Webhook → Validate → Execute Agent → Error Handle → Format → Respond`
> Always reference these patterns before invoking any n8n skill.

---

## UI Cloner Pipeline (6 skills)

> This is a sequential pipeline, not a menu of options. Run in order.
> Entry point for any brand audit or website replication task.

| Step | Skill | Purpose | Path | Audit | Last Eval |
|------|-------|---------|------|-------|-----------|
| 1 | `ui-cloner-forensic-audit` | Deep analysis of target site | .claude/skills/ui-cloner/ui-cloner-forensic-audit/ | DRAFT | 2026-04-14 |
| 2 | `ui-cloner-brand-interview` | Extract brand identity | .claude/skills/ui-cloner/ui-cloner-brand-interview/ | DRAFT | 2026-04-14 |
| 3 | `ui-cloner-synthesis` | Synthesize audit + interview into design brief | .claude/skills/ui-cloner/ui-cloner-synthesis/ | DRAFT | 2026-04-14 |
| 4 | `ui-cloner` | Generate the cloned/adapted UI | .claude/skills/ui-cloner/ui-cloner/ | DRAFT | 2026-04-14 |
| 5 | `ui-cloner-iterator` | Refine and iterate on output | .claude/skills/ui-cloner/ui-cloner-iterator/ | DRAFT | 2026-04-14 |
| 6 | `ui-cloner-quality-check` | Final QA pass | .claude/skills/ui-cloner/ui-cloner-quality-check/ | DRAFT | 2026-04-14 |

> **Locked brand decisions** (never override without explicit instruction):
> Teal accent, Geist font, 5% amber, Semantic tokens only

---

## Registry Maintenance

**When adding a new skill:**
1. Build it using `skill-creator`
2. Place in `.claude/skills/[category]/[skill-name]/SKILL.md`
3. Run `skill-authoring` audit, produce audit report and metadata.json
4. Add a row to the correct table above with: name, trigger phrases, path, audit status, last eval date
5. Update the total count at the top of this file

**When a skill is superseded:**
- Strike through the old row, add a note pointing to the replacement
- Do not delete the row

**Audit status key:**
- **PASS** (9/9 criteria): Production-ready, eligible for pipeline promotion
- **DRAFT** (any failure): Not production-ready, needs fixes per audit report
