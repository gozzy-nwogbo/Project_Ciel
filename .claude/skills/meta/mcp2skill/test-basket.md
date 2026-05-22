# Test Basket: mcp2skill

## Test 1: New Server (Not Registered)

**Input:** MCP server "Indeed" not in mcp-tool-audit.md.
**Expected behavior:** Pre-flight finds no entry, proceeds to query. All tools listed, permission proposal produced, user approves, skill generated, audit run, mcp-tool-audit.md updated.
**Expected output:** `.claude/skills/integrations/indeed/SKILL.md` + metadata.json + skill-audit + mcp-tool-audit entry.

---

## Test 2: Already Registered Server

**Input:** MCP server "Gmail" already in mcp-tool-audit.md.
**Expected behavior:** Pre-flight finds existing entry. Surfaces: "This server is already registered. Update existing entry or regenerate skill from scratch?" Waits for response before proceeding.
**Expected output:** Depends on user choice. No files created until user responds.

---

## Test 3: Server With All Destructive Tools

**Input:** Hypothetical MCP server where all 5 tools are delete/send operations.
**Expected behavior:** All classified as destructive, all proposed as Block. Warning surfaced: "All 5 tools are destructive. Recommend blocking all and reconsidering this integration." Proposal still presented for review.
**Expected output:** Skill generated with all tools in Blocked section if user approves.

---

## Test 4: Server With Zero Tools

**Input:** MCP server that returns 0 tools.
**Expected behavior:** Surface: "Server [name] returned 0 tools. Either the server is not connected or has no exposed tools. Aborting." No files created.
**Expected output:** None.

---

## Test 5: User Rejects Proposal

**Input:** User types "No, change search_jobs to mutating."
**Expected behavior:** Regenerate proposal with the specified change. Surface updated table. Wait for new approval. Do not generate files until a version is approved.
**Expected output:** Updated proposal table, then files after approval.
