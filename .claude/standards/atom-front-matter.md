# Atom Front-Matter Standard

**Version:** 1.0
**Status:** Active
**Created:** 2026-04-24

---

## Purpose

Defines the required structure for knowledge atoms. Every atom promoted to `02-knowledge/[domain]/` must conform to this standard. The atom-promotion skill validates staging atoms against these rules before promotion.

---

## Required Metadata Fields

Inline bold fields immediately after the H1 title, one per line.

| Field | Format | Example |
|-------|--------|---------|
| Title | H1 heading, first line of file | `# CODE Method` |
| Domain | `**Domain:** [value]` | `**Domain:** agent-architecture` |
| Origin | `**Origin:** [value]` | `**Origin:** Tiago Forte, 2022` |
| Source book(s) | `**Source book(s):** [value]` | `**Source book(s):** Building a Second Brain -- Tiago Forte` |

---

## Required Body Sections

Each section uses an H2 heading. Order matters.

| Section | Purpose | Minimum content |
|---------|---------|-----------------|
| `## What it is` | One-paragraph definition | At least one sentence |
| `## When to use it` | Bulleted list of retrieval situations | At least 2 bullets |
| `## Core mechanism` | How the framework operates | At least one sentence |
| `## Related frameworks` | Related atoms or honest disclaimer | Body text below heading (see D9) |
| `## NotebookLM pointer` | Notebook name for source tracing | Non-empty |

---

## `When to use it` — Situations Not Topics

Each bullet must describe a **concrete situation** the reader could find themselves in. Not a topic label.

**Good (situations):**
- "You want to start a new daily habit but keep forgetting"
- "Designing an information processing pipeline"
- "A cost structure seems inherited rather than justified"

**Bad (topics):**
- "Habit formation"
- "Behavior change"
- "Leadership"

A topic tells you the category. A situation tells you when to reach for the framework. Atoms exist to be retrieved in context. Situations make retrieval work.

This is guidance for authoring quality. It is not a disqualification rule because detecting topic-vs-situation programmatically requires judgment.

---

## Disqualification Rules

An atom that violates ANY rule below fails validation. Binary checks, no partial credit.

| # | Rule | Test |
|---|------|------|
| D1 | Has H1 title | First non-empty line starts with `# ` followed by non-whitespace |
| D2 | Has domain field | File contains `**Domain:**` with a non-empty value |
| D3 | Domain matches folder | `**Domain:**` value matches the parent folder name exactly |
| D4 | Has origin field | File contains `**Origin:**` with a non-empty value |
| D5 | Has source books field | File contains `**Source book(s):**` with a non-empty value |
| D6 | Has "What it is" section | File contains `## What it is` heading with body text below |
| D7 | Has "When to use it" section | File contains `## When to use it` heading with at least one `- ` bullet |
| D8 | Has "Core mechanism" section | File contains `## Core mechanism` heading with body text below |
| D9 | Has "Related frameworks" section | File contains `## Related frameworks` heading with body text below (may be "None" or similar honest disclaimer) |
| D10 | Has "NotebookLM pointer" section | File contains `## NotebookLM pointer` heading with non-empty text below |

---

## Promotion-Added Fields

The promotion skill adds these. Authors do not write them.

| Field | Set by | Values |
|-------|--------|--------|
| `status` | atom-promotion skill | `promoted` or `flagged` |
| `flag_reasons` | atom-promotion skill | List of D-rule violations (flagged atoms only) |

These are written as YAML front matter at the top of the file, enclosed in `---` fences.

---

## Version

Standard version: **1.0**

When this standard changes, version increments. Previously promoted atoms are not retroactively invalidated.
