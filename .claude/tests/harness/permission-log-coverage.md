# Harness Test: Permission Log Coverage

**Name:** permission-log-coverage
**Primitive:** P7 (System Event Log), P8 (Two-Level Verification)
**Trigger:** After any new integration is added or permission config changes

---

## Purpose

Verify that every MCP tool call produces a compliant system-events.jsonl entry. No tool call should execute without a log entry. This is the audit trail guarantee.

---

## Test Procedure

1. Select one read tool and one write tool from any active integration:
   - Read example: `gmail_search_messages` (search for recent unread)
   - Write example: `create_task_preview` in Asana Open-Brain project (test task, delete after)

2. Execute each tool call.

3. After each call, verify a new entry exists in `.claude/logs/system-events.jsonl` with all required fields:

   ```json
   {
     "timestamp": "[ISO-8601]",          // required — when the call happened
     "session_id": "[string]",            // required — current session identifier
     "action": "[tool name]",             // required — exact tool name called
     "integration": "[source]",           // required — gmail / calendar / asana / telegram / supabase / n8n
     "permission_tier": "[tier]",         // required — read-only / mutating / destructive
     "inputs_summary": "[one line]",      // required — what was passed
     "result": "[outcome]",               // required — success / blocked / error
     "reason": "[why]"                    // required — why this call was made
   }
   ```

4. Verify completeness:
   - All 8 fields present
   - `reason` field is not empty or generic ("test" is acceptable for test runs, but production calls must have a real reason)
   - `permission_tier` matches the tool's classification in `02-knowledge/mcp-tool-audit.md`

5. Clean up any test artifacts (delete test Asana task if created).

---

## Pass Criteria

- 100% of tool calls in the test run produce a compliant log entry.
- All 8 required fields are present in every entry.
- `reason` field contains a non-empty explanation.
- `permission_tier` is accurate per the MCP tool audit.

## Fail Criteria

- Any tool call produces no log entry.
- Any log entry is missing a required field.
- `reason` field is empty or missing.
- `permission_tier` does not match the tool audit classification.

---

## Verification Command

After running the test, check the last N entries:

```bash
tail -5 .claude/logs/system-events.jsonl | python3 -m json.tool
```

Confirm the test entries are present and complete.
