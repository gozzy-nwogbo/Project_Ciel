# Atom Front-Matter Standard

**Version:** 2.0
**Status:** Active
**Created:** 2026-04-24
**Updated:** 2026-05-22

---

## Purpose

Defines the required structure for knowledge atoms in `02-knowledge/`. Every atom uses YAML frontmatter enclosed in `---` fences as its first content. The atom-promotion skill validates staging atoms against these rules before promotion.

---

## YAML Frontmatter

All atoms begin with a YAML frontmatter block. No other metadata format is accepted.

### Required fields (all atom types)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `title` | string | Human-readable name for concepts/frameworks/principles. Kebab-case slug for connections. | `title: CODE Method` |
| `type` | enum | One of: `concept`, `framework`, `principle`, `connection` | `type: concept` |
| `source_date` | string | ISO 8601 date (YYYY-MM-DD) | `source_date: 2026-05-13` |

### Required fields (non-connection atoms)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `tags` | list of strings | Retrieval tags. May be empty (`[]`). | `tags: [agent-memory, governance]` |

### Required fields (connection atoms)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `from` | string | Source concept name | `from: Pattern Escalation Rule` |
| `to` | string | Target concept name | `to: Structural Fixes Principle` |

Connections use `from`/`to` instead of `tags`.

### Optional fields

| Field | Type | Description | Typical presence |
|-------|------|-------------|-----------------|
| `source_session` | string | Session context suffix split from a date+context source_date value | YAML atoms with session provenance |
| `domain` | string | Knowledge domain (matches parent folder name) | NotebookLM-origin atoms |
| `origin` | string | Creator and approximate year | NotebookLM-origin atoms |
| `sources` | list of strings | Source books or materials | NotebookLM-origin atoms |
| `notebooklm_notebook` | string | Name of the NotebookLM notebook containing source material | NotebookLM-origin atoms |

Optional fields are omitted when not applicable. Do not populate with empty strings or placeholder values.

---

## Type Vocabulary

| Type | Definition | Population |
|------|-----------|------------|
| `concept` | A single durable claim, pattern, or mental model. The default type. | Majority of atoms |
| `framework` | A multi-dimensional model with named components that work together. More structured than a concept. | Manually assigned |
| `principle` | A prescriptive rule or guideline. States what should be done, not just what is. | Manually assigned |
| `connection` | A relationship between two existing atoms. Describes how one concept relates to another. | Produced by flush.py and deep-parse |

Default for new atoms of uncertain type: `concept`. Reclassification to `framework` or `principle` is a manual editorial decision.

---

## Body Section Patterns

Two body shapes are valid. Both follow the YAML frontmatter block. Body content should match the atom's depth: do not force structure onto a lightweight claim, and do not truncate a multi-dimensional model to fit a single-sentence shape.

### Lightweight atom

YAML frontmatter + 1-3 sentence body claim. No section headings required.

Used for: flush.py-produced concepts, derivation atoms, single-paragraph insights captured from operational work. Typical type: `concept`.

```
---
title: Scale Anomaly Halt Pattern
type: concept
source_date: 2026-05-15
tags: [operations, safety, data-preservation]
---

During bulk deletion operations, halt and surface unexpectedly large directories before dropping. Confirm via user that the size matches intent and that no unique content exists in the target.
```

### Structured atom

YAML frontmatter + 4 H2 body sections. Section order matters.

| Section | Purpose | Minimum content |
|---------|---------|-----------------|
| `## What it is` | One-paragraph definition | At least one sentence |
| `## When to use it` | Bulleted list of retrieval situations | At least 2 bullets |
| `## Core mechanism` | How it operates | At least one sentence |
| `## Related frameworks` | Related atoms or honest disclaimer | Body text below heading (may be "None") |

Used for: book-extracted claims, multi-dimensional models, deeply-developed concepts. Typical type: `framework`. Common in NotebookLM-origin atoms and manually-authored deep atoms.

#### `When to use it` — Situations Not Topics

Each bullet must describe a concrete situation, not a topic label.

Good: "You want to start a new daily habit but keep forgetting"
Bad: "Habit formation"

Connection atoms use a single-sentence relationship body with no required section headings.

---

## Example Atoms

### Concept (lightweight)

```
---
title: Agent Memory Self-Poisoning
type: concept
source_date: 2026-05-13
tags: [agent-memory, failure-modes, memory-hygiene, governance]
---

When an agent writes inaccurate or context-collapsed summaries to its own memory layer, subsequent sessions inherit the distortion. The error compounds because later retrievals treat the corrupted memory as ground truth, producing increasingly divergent outputs.
```

### Connection

```
---
title: escalation-rule-triggers-structural-fixes
type: connection
from: Pattern Escalation Rule
to: Structural Fixes Principle
source_date: 2026-05-17
---

Pattern Escalation Rule -> Structural Fixes Principle: when a pattern repeats three times, escalation shifts the response from instance-level fix to structural intervention.
```

### Converted NotebookLM-origin atom (structured)

```
---
title: CODE Method
type: concept
source_date: 2026-04-24
tags: []
domain: habits-systems
origin: Tiago Forte, 2022
sources:
  - "Building a Second Brain -- Tiago Forte"
notebooklm_notebook: Habits & Systems
---

## What it is
A four-step workflow for managing knowledge: Capture, Organize, Distill, Express. Each step reduces raw input into progressively more actionable material.

## When to use it
- You have a growing collection of notes and articles but cannot find anything when you need it
- You are preparing a deliverable and need to synthesize across multiple sources quickly

## Core mechanism
Capture externally valuable information. Organize it by actionability, not category. Distill each note to its essential claim. Express the knowledge by producing output that uses it. The cycle compounds: each expression pass surfaces gaps that feed the next capture round.

## Related frameworks
PARA Method, Progressive Summarization
```

---

## Disqualification Rules

An atom that violates ANY rule below fails validation and is not promoted. Binary checks, no partial credit.

| # | Rule | Test |
|---|------|------|
| D1 | Valid YAML frontmatter | File starts with `---`, contains a closing `---`, and the block parses as valid YAML |
| D2 | Has title | `title` field is present and non-empty |
| D3 | Valid type | `type` field is present and value is one of: `concept`, `framework`, `principle`, `connection` |
| D4 | Has source_date | `source_date` field is present and matches `YYYY-MM-DD` format |
| D5 | Has tags (non-connection) | `tags` field is present (may be `[]`). Exempt for `type: connection`. |
| D6 | Connection has from/to | If `type: connection`, both `from` and `to` fields are present and non-empty |
| D7 | Domain matches folder | If `domain` field is present, its value matches the parent folder name |

---

## Flagging Fields

The atom-promotion skill writes these fields to atoms during validation. Atoms may be hard-failed (disqualified) or soft-flagged (advisory warnings that do not block promotion).

### Hard-fail fields (disqualified atoms only)

Disqualified atoms remain in staging with this frontmatter added. They are not promoted.

| Field | Set by | Description |
|-------|--------|-------------|
| `status` | atom-promotion skill | Set to `flagged` on atoms that fail one or more D-rules |
| `flag_reasons` | atom-promotion skill | List of D-rule violations |

### Soft-flag fields (advisory)

Atoms with quality flags are still promoted to `02-knowledge/`. These flags are advisory only, surfaced in the promotion report for optional manual review.

| Field | Set by | Description |
|-------|--------|-------------|
| `quality_flags` | atom-promotion skill | List of soft warnings. Does not block promotion. |

Example soft flags:
- `missing-when-to-use` — structured atom missing `## When to use it` section
- `body-shorter-than-frontmatter` — body content is shorter than the frontmatter block
- `structured-shell-thin-content` — has section headings but sections contain minimal content

Task 3a will implement the soft-flag logic in the atom-promotion skill rewrite.

---

## Out of Scope (This Version)

Derivation fields (`derived_from`, `perspective`, `derivation_type`, `warrant`, `provenance`) are not part of this standard version. They will be defined in a separate additive extension.

---

## Version History

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-04-24 | Initial standard. Inline-bold metadata format. |
| 2.0 | 2026-05-22 | YAML frontmatter as sole canonical format. Inline-bold retired. D-rules rewritten for YAML (D1-D7). Body section enforcement removed; two body patterns documented (lightweight + structured). Soft-flag mechanism added. Optional fields added for NotebookLM-origin provenance. |
