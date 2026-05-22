# credential-pin — Worked Example

_Constructed example based on n8n SDK behavior observed during CSC AI Reel Generator build (2026-04-25 to 2026-04-28). No real snapshot data used._

---

## Scenario

Workflow `wbZlNmM5LBrzhz6s` ("AI Reel Generator") has 4 credentialed nodes. The operator
needs to push an SDK update that will wipe credential bindings.

## Step 1 — Snapshot (pin mode)

**Invoke:** credential-pin, mode: pin, workflow ID: wbZlNmM5LBrzhz6s

**Skill reads workflow and extracts:**

```json
{
  "snapshot_version": 1,
  "workflow_id": "wbZlNmM5LBrzhz6s",
  "workflow_name": "AI Reel Generator",
  "timestamp": "2026-04-26T14:30:00Z",
  "node_bindings": {
    "Telegram Trigger": {
      "telegramApi": "4"
    },
    "Google Gemini Chat Model": {
      "googlePalmApi": "12"
    },
    "ElevenLabs": {
      "elevenLabsApi": "7"
    },
    "Telegram - Send Video": {
      "telegramApi": "4"
    }
  }
}
```

**Skill reports:** "Snapshot complete at `02-knowledge/n8n-credential-snapshots/wbZlNmM5LBrzhz6s-2026-04-26T143000Z.json`. After your SDK push, run credential-pin in restore mode for this workflow ID."

## Step 2 — Operator pushes SDK update

Operator runs `n8n_update_full_workflow` with new workflow JSON. All credential
bindings are wiped by the SDK (known behavior).

## Step 3 — Restore

**Invoke:** credential-pin, mode: restore, workflow ID: wbZlNmM5LBrzhz6s

**Skill reads current workflow, finds all 4 bindings missing. Presents diff:**

| Node | Credential Type | Snapshot ID | Current | Action |
|------|----------------|-------------|---------|--------|
| Telegram Trigger | telegramApi | 4 | (none) | RESTORE |
| Google Gemini Chat Model | googlePalmApi | 12 | (none) | RESTORE |
| ElevenLabs | elevenLabsApi | 7 | (none) | RESTORE |
| Telegram - Send Video | telegramApi | 4 | (none) | RESTORE |

**Operator approves.** Skill applies all 4 bindings via `n8n_update_partial_workflow`.
Skill re-reads workflow and confirms all 4 bindings match snapshot.

**Report:** "4/4 bindings restored. Workflow credential state matches snapshot."
