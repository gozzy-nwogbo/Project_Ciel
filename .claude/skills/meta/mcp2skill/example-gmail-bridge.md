# Worked Example: Gmail MCP → Integration Skill

## Step 1: Pre-flight Check
Read `02-knowledge/mcp-tool-audit.md`. Found "Gmail" entry. Surface: "This server is already registered. Update existing entry or regenerate skill from scratch?"
User: "Regenerate from scratch."

## Step 2: Query MCP Server
Queried Gmail MCP. Found 7 tools:
- gmail_search_messages, gmail_read_message, gmail_read_thread, gmail_list_labels, gmail_list_drafts, gmail_get_profile, gmail_create_draft

Surface: "Found 7 tools on Gmail. Proceeding to classification."

## Step 3: Permission Proposal

| Tool | Proposed Tier | Reason | Allow / Block |
|---|---|---|---|
| gmail_search_messages | read-only | Searches inbox, no side effects | Allow |
| gmail_read_message | read-only | Reads single message content | Allow |
| gmail_read_thread | read-only | Reads thread content | Allow |
| gmail_list_labels | read-only | Lists label metadata | Allow |
| gmail_list_drafts | read-only | Lists existing drafts | Allow |
| gmail_get_profile | read-only | Returns account metadata | Allow |
| gmail_create_draft | mutating | Creates draft in Gmail, reversible | Allow (approval-first) |

Surface: "Review and confirm — type APPROVE to proceed, or specify changes."
User: "APPROVE"

## Step 4: Generated Output (abbreviated)
Created `.claude/skills/integrations/gmail/SKILL.md` matching the Gmail skill structure with:
- Permission Boundaries table
- 6 allowed read-only tools (no approval needed)
- 1 mutating tool (gmail_create_draft) with approval-first pattern
- 0 blocked tools
- Graceful degradation section
- Event logging section with 8-field format
- "What This Skill Does NOT Do" section

## Step 5: Audit
9-criterion audit run. Result: PASS (assuming worked example and test basket exist).

## Step 6: MCP Tool Audit Updated
Gmail entry in `02-knowledge/mcp-tool-audit.md` updated with: 7 tools, 6 allowed, 0 blocked, 1 mutating.
