# Test Basket: prd-generator

## Test 1: Multi-Phase Build

**Input:** "An n8n pattern memory system that logs recurring workflow errors and surfaces past solutions."

**Expected classification:** Multi-phase (3+ components: error logging pipeline, pattern matching engine, solution retrieval interface)

**Expected output:** Full PRD at `01-projects/n8n-pattern-memory/PRD.md` with all 8 sections:
1. What We Are Building
2. Core Architecture table
3. Explicit Scope (in + out)
4. Security Boundaries table
5. Build Phases (minimum 3)
6. Build Principles
7. Open Questions
8. Status header

**Expected side artifact:** `01-projects/n8n-pattern-memory/elicitation-[date].md`

---

## Test 2: Single-Scope Build

**Input:** "A skill that monitors Go High Level subscription status and flags inactive subscriptions."

**Expected classification:** Single-scope (one API integration, one check, one output)

**Expected output:** Spec contract at `01-projects/ghl-monitor/spec-contract.md` matching `.claude/templates/spec-contract.md` structure. All 8 template sections present:
1. Declared Goal
2. Explicit Inputs
3. Output Contract
4. Constraints
5. Out-of-Scope Declarations
6. Dependencies
7. Success Criteria
8. Change Log + Approval

**Expected side artifact:** `01-projects/ghl-monitor/elicitation-[date].md`

---

## Test 3: Exploratory Route

**Input:** "I have a vague idea about making my second brain talk to other people's second brains somehow."

**Expected classification:** Exploratory (no clear problem, no defined user, no measurable success state)

**Expected output:** No PRD or spec contract generated. No project folder created. Agent surfaces: "This idea needs more shaping before it can be specced. Run the elicitation skill with: 'interview me about [project idea]' — then come back to the PRD generator."

**Expected side artifact:** None.

---

## Test 4: Seed File Pre-Population

**Input:** Seed file exists at `01-projects/seeds/webhook-relay.md` with Q1, Q2, Q3 already answered.

**Expected behavior:** Agent reads seed file, skips Q1-Q3, asks Q4-Q6 only. Classification proceeds normally after Q6.

---

## Test 5: User Overrides Classification

**Input:** Agent classifies as multi-phase. User says "No, this is a single-scope build."

**Expected behavior:** Agent accepts user's classification. Produces spec contract, not full PRD.
