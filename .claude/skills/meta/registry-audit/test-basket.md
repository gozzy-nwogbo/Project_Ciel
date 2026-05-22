# Registry Audit — Test Basket

> Minimum 5 test cases with defined inputs and expected outputs.

---

## Test 1: Clean registry (no drift)

**Input:**
- Filesystem: 3 skills — `meta/skill-creator/`, `meta/skill-authoring/`, `writing/content-research/`
- Registry: 3 active rows matching those exact paths
- Registry header: "Total registered skills: 3"
- No struck-through rows

**Expected output:**
- Summary: 3 filesystem, 3 registry, 0 drift
- All sections report "None detected"
- Header drift: none
- Verdict: clean registry

---

## Test 2: Orphan skill detected

**Input:**
- Filesystem: 4 skills — the 3 from Test 1 plus `n8n/new-workflow-skill/`
- Registry: same 3 rows as Test 1
- Registry header: "Total registered skills: 3"

**Expected output:**
- Orphan skills section lists `n8n/new-workflow-skill/` with proposed registry row (category: n8n, DRAFT)
- Header drift: header says 3, actual 3 (header matches registry, not filesystem — header tracks registry rows)
- 1 drift issue total

---

## Test 3: Stale registry row

**Input:**
- Filesystem: 2 skills — `meta/skill-creator/`, `meta/skill-authoring/`
- Registry: 3 rows — the 2 matches plus `meta/deleted-skill/` (no filesystem match)
- Registry header: "Total registered skills: 3"

**Expected output:**
- Stale rows section lists `deleted-skill` with fix options (remove or rename)
- Header drift: none (header matches registry count)
- 1 drift issue total

---

## Test 4: Path mismatch

**Input:**
- Filesystem: `n8n/credential-pin/SKILL.md`
- Registry row: `credential-pin` at `.claude/skills/meta/credential-pin/` (wrong category)

**Expected output:**
- Path mismatch section: registry says `meta/credential-pin/`, filesystem says `n8n/credential-pin/`
- Proposed fix: update registry path to `.claude/skills/n8n/credential-pin/`
- 1 drift issue total

---

## Test 5: Struck-through row preservation

**Input:**
- Filesystem: `writing/content-research/SKILL.md` (exists)
- Registry: active row for `content-research`, struck-through row for ~~`content-research-writer`~~ with "Superseded by content-research" note
- No filesystem `content-research-writer/` folder

**Expected output:**
- Struck-through rows excluded: 1
- `content-research-writer` does NOT appear in stale rows (even though no filesystem match)
- `content-research-writer` does NOT appear in orphan skills
- Informational section notes struck-through row preserved
- 0 drift issues

---

## Test 6: Empty category

**Input:**
- Registry has a "Design" category section header with zero active rows beneath it
- All other categories have at least one active row

**Expected output:**
- Informational section: "Design category empty — consider folding into another category or removing the section header"
- This is NOT counted as drift
- 0 drift issues from this condition

---

## Test 7: Header count drift

**Input:**
- Registry has 52 active rows
- Registry header says "Total registered skills: 50"

**Expected output:**
- Header drift section: "Registry header says 50 skills, actual count is 52. Update header."
- 1 drift issue (header drift)

---

## Test 8: Multiple SKILL.md in one folder

**Input:**
- Filesystem: `meta/broken-skill/SKILL.md` and `meta/broken-skill/SKILL.md.bak` renamed to `SKILL.md` (two files)
- Registry: active row for `broken-skill`

**Expected output:**
- Structural error: "Multiple SKILL.md files in meta/broken-skill/. Manual inspection required."
- `broken-skill` excluded from orphan/stale/path-mismatch checks
- Do not produce duplicate flags
