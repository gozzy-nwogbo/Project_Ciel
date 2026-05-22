# Test Basket: atom-promotion

## Test 1 — Valid atom promotes successfully

**Input:** A staging atom with all D1-D10 fields present and correct. Domain folder does not exist in `02-knowledge/`.

**Expected output:**
- Atom file appears at `02-knowledge/[domain]/[filename]`
- Source file removed from staging
- Domain folder created in `02-knowledge/`
- Report shows promoted: 1, flagged: 0

---

## Test 2 — Missing field triggers flag

**Input:** A staging atom with `## When to use it` section removed (violates D7).

**Expected output:**
- Atom stays in staging with YAML front matter added: `status: flagged`, `flag_reasons: ["D7: missing When to use it section"]`
- Atom does NOT appear in `02-knowledge/`
- Report shows promoted: 0, flagged: 1

---

## Test 3 — Domain mismatch triggers flag

**Input:** A staging atom in `agent-architecture/` folder but `**Domain:** mental-models` in the file.

**Expected output:**
- Atom flagged with `flag_reasons: ["D3: domain field does not match parent folder"]`
- Atom stays in staging
- Report shows promoted: 0, flagged: 1

---

## Test 4 — Collision halts entire run

**Input:** A valid staging atom whose filename already exists at the destination in `02-knowledge/[domain]/`.

**Expected output:**
- Entire skill run halts immediately
- No atoms promoted or flagged in this run
- Report states collision file path and halts

---

## Test 5 — Empty domain folder skipped

**Input:** A domain folder in staging that contains no `.md` files.

**Expected output:**
- Domain skipped silently
- Report notes "[domain]: 0 atoms staged"
- No errors, no flags

---

## Test 6 — Previously flagged atom re-validates clean

**Input:** A staging atom with existing YAML front matter `status: flagged` but all D1-D10 rules now pass.

**Expected output:**
- Atom promoted to `02-knowledge/[domain]/`
- Old YAML front matter removed or replaced
- Report shows promoted: 1
