# Skill: prd-generator

Generates a project planning document (full PRD, spec contract, or exploratory route) after a mandatory 6-question mini elicitation interview, producing the output at `01-projects/[project-name]/PRD.md` or `spec-contract.md` — invoke when starting any new project, building something new, or when the user says "I want to build" or "spec this out."

---

## Inputs

| Input | Required | Purpose |
|---|---|---|
| User answers to 6 mini elicitation questions | Yes | Raw project context for classification and document generation |
| `01-projects/seeds/[project-name].md` | No | Pre-populated answers from content-research or idea capture; skip answered questions |
| `04-reflections/elicitation-*.md` (within 7 days) | No | Recent elicitation summary; pre-populates answered questions to avoid re-interviewing |
| `.claude/templates/spec-contract.md` | Yes (spec path) | Template for single-scope builds |
| `01-projects/open-brain/PRD/PRD.md` | Yes (PRD path) | Structural reference for full PRD format |

---

## Output Contract

| Path | Format | When |
|---|---|---|
| `01-projects/[project-name]/PRD.md` | md | Multi-phase classification confirmed |
| `01-projects/[project-name]/spec-contract.md` | md | Single-scope classification confirmed |
| `01-projects/[project-name]/elicitation-[date].md` | md | Always (summary of interview answers) |

**Out of scope:** Implementation planning, phase execution, code generation, skill creation. This skill produces the planning document only.

---

## Process

### Step 1: Prior Elicitation Check
Scan `04-reflections/` for any `elicitation-*.md` file dated within the last 7 days. If found, read it and map its content against Q1-Q6. For each question with a clear answer in the summary, pre-populate that answer. Surface to user: "I found a recent elicitation summary from [date]. I've pre-populated [N] of 6 questions from it. Confirming: [list pre-populated answers as Q#: one-line summary]. Correct?" Wait for confirmation. If user corrects any answer, use the corrected version. Then proceed to only the unanswered questions. If all 6 are covered and user confirms, skip directly to Step 3 (classification).

### Step 2: Seed Check
Read `01-projects/seeds/` for a file matching the project name. If found, pre-populate any remaining unanswered questions and skip those in the interview.

### Step 3: Mini Elicitation (mandatory, never skip)
Ask one question at a time. Wait for response. Use follow-up if answer is thin (single sentence, vague, or abstract).

**Q1:** What problem does this solve, and for whom specifically?
- Follow-up: "Can you name a specific person or situation where this problem exists right now?"

**Q2:** What does success look like in 90 days — what's specifically true that isn't true today?
- Follow-up: "How would you measure that? What number or state changes?"

**Q3:** What do you already know how to build here, and what are you genuinely uncertain about?
- Follow-up: "What's the assumption underneath this project that, if wrong, kills it?"

**Q4:** What would you need to believe to commit to this — and can you test that cheaply before building?
- Follow-up: "What's the fastest version of this you could test in a week?"

**Q5:** What is this competing with for your time right now?
- Follow-up: "If you do this, what specifically doesn't get done?"

**Q6:** What would make you stop working on this — and is that kill condition clear enough that you'd actually stop?
- Follow-up: "Is there a version of this that fails but you keep going anyway?"

### Step 4: Classification (user confirms before output)
After all questions are answered (via pre-population, seed, or interview), classify and surface:

| Classification | Criteria | Output |
|---|---|---|
| **Multi-phase** | 3+ components, infrastructure-level, multiple systems, weeks-to-months | Full PRD |
| **Single-scope** | One workflow/agent/integration/tool, days to 1-2 weeks | Spec contract |
| **Exploratory** | Idea not formed enough to spec | Route to elicitation skill Mode 2 |

Surface: "Based on your answers, this looks like a [classification]. I'll produce a [full PRD / spec contract / elicitation brief]. Does that match your expectation?"

Wait for confirmation. Do not generate until confirmed.

### Step 5: Generate Output

**Full PRD path:** Create `01-projects/[project-name]/PRD.md` with all 8 required sections:
1. What We Are Building (one paragraph, specific, testable)
2. Core Architecture (concern/solution/source table)
3. Explicit Scope (in scope + explicitly out of scope)
4. Security Boundaries (integration permissions table, zero-trust defaults)
5. Build Phases (each: goal, primitives, deliverables, success criteria)
6. Build Principles (encoded, not rediscovered)
7. Open Questions (decisions needed before/during build)
8. Status header (current phase, last updated, execution environment)

**Spec contract path:** Create `01-projects/[project-name]/spec-contract.md` using `.claude/templates/spec-contract.md` exactly. All 8 template sections required. No simplified version.

**Exploratory path:** Surface: "This idea needs more shaping before it can be specced. Run the elicitation skill with: 'interview me about [project idea]' — then come back to the PRD generator." Do not generate a PRD or spec contract. Do not create a project folder.

### Step 6: Write Elicitation Summary
Write interview answers to `01-projects/[project-name]/elicitation-[date].md` (skip for exploratory path).

---

## Constraints

| # | Constraint | Verification |
|---|---|---|
| 1 | Mini elicitation runs before any output generation | Check: no PRD/spec file created before Q6 is answered |
| 2 | Classification confirmed by user before output | Check: explicit user confirmation exists in conversation |
| 3 | Full PRD contains all 8 sections | Check: count H2 headers in output file |
| 4 | Spec contract uses installed template structure | Check: diff output sections against template sections |
| 5 | Project folder created before any file is written | Check: folder exists at `01-projects/[project-name]/` |
| 6 | Elicitation summary always written (non-exploratory paths) | Check: file exists at stated path |
| 7 | Seed file checked before elicitation begins | Check: read attempted on `01-projects/seeds/` |
| 8 | Prior elicitation checked before interview starts | Check: scan attempted on `04-reflections/elicitation-*.md` within 7 days |

---

## Edge Cases

1. **User provides a wall of text instead of answering Q1:** Extract answers to as many questions as possible from the text. Ask remaining questions only. Do not re-ask what was already answered.
2. **User says "just give me the PRD, skip the questions":** Refuse. Surface: "The mini elicitation is mandatory. It takes 5 minutes and prevents building the wrong thing. Q1: [ask Q1]."
3. **User disagrees with classification:** Accept the user's classification. They know their project better. Proceed with their chosen output path.
4. **Seed file answers all 6 questions:** Summarize seed contents, confirm classification, skip to Step 4. Do not re-interview.
5. **Project folder already exists:** Use existing folder. Do not overwrite existing PRD.md or spec-contract.md without explicit confirmation.

---

## Handoff

After this skill completes, the next stage receives:
- **Artifact:** `PRD.md` or `spec-contract.md` at `01-projects/[project-name]/`
- **Condition:** Document is written and all required sections are present
- **Routing:** Full PRD routes to phase planning (GSD or manual). Spec contract routes to execution. Exploratory routes to elicitation skill Mode 2.
