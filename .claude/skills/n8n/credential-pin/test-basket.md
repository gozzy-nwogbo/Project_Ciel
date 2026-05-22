# credential-pin — Test Basket

---

## T1 — Clean snapshot and restore (happy path)

**Input:**
- Mode: snapshot, then restore
- Workflow ID: `abc123` with 3 credentialed nodes
- Workflow state: all 3 nodes have credential bindings assigned

**Snapshot expected output:**
- File created at `02-knowledge/n8n-credential-snapshots/abc123-[timestamp].json`
- `snapshot_version: 1`
- `node_bindings` contains exactly 3 entries
- No credential secrets in output file

**Restore expected output (after simulated SDK wipe):**
- Diff shows 3 bindings missing
- Operator prompted with full diff before any write
- After approval: all 3 bindings applied via `n8n_update_partial_workflow`
- Verification read confirms 3/3 match

---

## T2 — Restore with mismatched node IDs

**Input:**
- Mode: restore
- Workflow ID: `abc123`
- Existing snapshot has nodes: "Gmail Send", "Slack Post", "HTTP Request"
- Current workflow has nodes: "Gmail Send", "Slack Notify", "HTTP Request"

**Expected output:**
- Skill halts before any write
- Reports: "Slack Post" exists in snapshot but not in current workflow; "Slack Notify" exists in current workflow but not in snapshot
- Asks operator for per-node approval before proceeding
- Does NOT silently restore the 2 matching nodes

---

## T3 — Snapshot with zero credentialed nodes

**Input:**
- Mode: snapshot
- Workflow ID: `empty456` with 5 nodes, none using credentials

**Expected output:**
- File created at `02-knowledge/n8n-credential-snapshots/empty456-[timestamp].json`
- `node_bindings` is an empty object `{}`
- Report: "5 nodes scanned, 0 with credentials. No bindings to pin."
- No error, no warning — clean exit

---

## T4 — Restore with deleted credential

**Input:**
- Mode: restore
- Workflow ID: `abc123`
- Snapshot has binding: "Gmail Send" → `{ "gmailOAuth2Api": "9" }`
- Credential ID 9 no longer exists in n8n

**Expected output:**
- Skill flags: "Credential ID 9 (gmailOAuth2Api for node 'Gmail Send') no longer exists in n8n"
- Presents remaining valid bindings separately
- Asks operator: skip the missing credential and apply the rest, or abort entirely
- Does NOT silently skip or silently apply

---

## T5 — Restore with no existing snapshot

**Input:**
- Mode: restore
- Workflow ID: `nosnap789`
- No snapshot file exists in `02-knowledge/n8n-credential-snapshots/`

**Expected output:**
- Skill halts immediately
- Reports: "No snapshot found for workflow nosnap789. Cannot restore without a prior snapshot."
- Does NOT attempt to read current workflow state
- Does NOT attempt to reconstruct bindings from memory or inference
