# Skill: credential-pin

Prevents n8n credential bindings from being wiped during SDK workflow updates by capturing node-to-credential mappings before push and re-applying them after. Invoke on "pin credentials", "snapshot n8n credentials", "restore credential bindings", "credential pin before push", "save credential bindings." Output: snapshot JSON at `02-knowledge/n8n-credential-snapshots/[workflow-id]-[timestamp].json` and inline restore diff report.

---

## When to use

- Before any n8n SDK workflow push (`n8n_update_full_workflow`, `n8n_update_partial_workflow`, `n8n_create_workflow`)
- After an SDK push when credential bindings need restoration
- When you suspect credential bindings were lost and need to verify against a prior snapshot

## When NOT to use

- When editing workflows through the n8n UI (credentials persist through UI edits)
- When modifying credentials themselves (this skill handles bindings, not credential definitions)
- When working across multiple n8n instances (single-instance scope only)

## Input

| Input | Required | Description |
|---|---|---|
| Workflow ID | Yes | The n8n workflow ID to snapshot or restore |
| Operation mode | Yes | `snapshot`, `restore`, or `pin` |
| Snapshot timestamp | No | For `restore`: use a specific older snapshot instead of most recent |

## Process

### Mode: snapshot

1. Read the current workflow via `n8n_get_workflow` or `n8n_get_workflow_details`
2. Extract every node's `credentials` field: map node name to credential type to credential ID
3. Write the mapping to `02-knowledge/n8n-credential-snapshots/[workflow-id]-[timestamp].json`
4. Report: number of nodes scanned, number with credentials, snapshot file path

### Mode: restore

1. Locate the most recent snapshot for the given workflow ID (or use the specified timestamp)
2. Read the current workflow state via `n8n_get_workflow`
3. Diff: for each node in the snapshot, compare credential bindings against current state
4. Present the full diff to the operator: which bindings are missing, which match, which are new
5. Wait for explicit operator approval before applying any changes
6. Apply approved bindings via `n8n_update_partial_workflow`
7. Verify: re-read workflow, confirm bindings match the approved set

### Mode: pin

1. Run **snapshot** (steps from snapshot mode)
2. Report: "Snapshot complete at [path]. After your SDK push, run credential-pin in restore mode for this workflow ID."
3. End.

## Output Contract

**Produces:**
- **Snapshot:** `02-knowledge/n8n-credential-snapshots/[workflow-id]-[timestamp].json` with structure `{ snapshot_version: 1, workflow_id, workflow_name, timestamp, node_bindings: { [nodeName]: { [credentialType]: credentialId } } }`
- **Restore:** Inline diff report and applied confirmation (no file output)
- **Pin:** Snapshot file + guidance to run restore after SDK push

**Does NOT produce:** credential secrets or tokens (bindings only), workflow JSON modifications beyond credential fields, cross-instance mappings, automatic SDK push wrapping.

## Constraints

1. Snapshot captures node-to-credential ID mappings ONLY. Never capture credential secrets, auth keys, tokens, or any credential definition data.
2. Snapshots are saved to `02-knowledge/n8n-credential-snapshots/[workflow-id]-[timestamp].json`. Never inline in workflow JSON. Never in the project folder being pushed.
3. Restore presents the full binding diff before any write. Wait for explicit operator approval. No auto-restore.
4. If no snapshot exists for a workflow being restored, halt and report. Do not reconstruct from memory or inference.
5. If snapshot and current workflow have different node sets (nodes added, removed, or renamed), halt and report mismatched nodes. Do not partial-restore without explicit operator approval per node.
6. Each operation mode is independent: snapshot runs without restore, restore runs without a preceding snapshot (if a prior file exists), pin runs both sequentially but each terminates cleanly.

## Edge Cases

1. **Workflow has zero credentialed nodes.** Snapshot writes an empty `node_bindings` object, logs "no bindings to pin." Not a failure.
2. **Multiple snapshots exist for one workflow ID.** Restore uses the most recent by default. Operator can specify a snapshot timestamp to override.
3. **Workflow ID changed between snapshot and restore** (workflow recreated). Halt, report the mismatch, ask operator whether to apply the snapshot to the new ID or abort.
4. **Credential ID in snapshot no longer exists in n8n** (credential deleted). Flag the specific binding, propose remaining valid bindings, ask operator whether to skip or abort.

## Allowed Tools

- `n8n_get_workflow` / `n8n_get_workflow_details` (read workflow state)
- `n8n_update_partial_workflow` (restore credential bindings)
- Read / Write (snapshot files in `02-knowledge/n8n-credential-snapshots/`)
- Glob (find existing snapshots for a workflow ID)

## Handoff

After this skill completes:
- **Artifact:** Snapshot JSON file (snapshot/pin) and/or inline confirmation that bindings are restored (restore)
- **Condition:** Handoff when operation completes: snapshot written, bindings confirmed applied, or both
- **Routing:** Operator proceeds with normal workflow development. Unresolved mismatches require manual resolution before continuing.
