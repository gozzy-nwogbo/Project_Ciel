# Skill: skill-creator

Guide for creating effective Claude skills from scratch or improving existing ones, covering intent capture, reusable content planning, SKILL.md authoring, and packaging.
Trigger phrases: "create a new skill", "build a skill", "improve this skill", "write a skill description", "package a skill".
Output artifact: complete skill folder with `SKILL.md` at `.claude/skills/[category]/[skill-name]/SKILL.md`.

---

# Skill Creator

Guidance for creating effective Claude skills from scratch or improving existing ones.

## When to Use

- Creating a new skill
- Updating or improving an existing skill
- Improving a skill's description to trigger more reliably
- Packaging a skill for sharing

## Process Overview

1. Understand the skill with concrete examples
2. Plan reusable contents (scripts, references, assets)
3. Initialize the skill folder
4. Write SKILL.md
5. Package for distribution
6. Iterate based on testing

---

## Step 1: Understand with Concrete Examples

Before writing anything, collect real examples of how the skill will be used. Good questions:
- "What exactly should this skill enable Claude to do?"
- "Can you give 3 examples of user prompts that should trigger this skill?"
- "What would a successful output look like?"

Conclude when you have 3-5 concrete example interactions.

## Step 2: Plan Reusable Contents

For each example, ask:
- Is there code that would need to be rewritten each time? -> `scripts/`
- Is there reference material Claude would need to look up? -> `references/`
- Are there templates or assets used in the output? -> `assets/`

## Step 3: Folder Structure

```
skill-name/
├── SKILL.md          <- Required
├── scripts/          <- Executable Python/Bash
├── references/       <- Docs loaded into context as needed
└── assets/           <- Templates, images, fonts used in output
```

## Step 4: Write SKILL.md

### Frontmatter (required)

```yaml
---
name: skill-name           # snake-case identifier
description: [When to use and what it does -- this is how Claude decides to trigger the skill]
---
```

**Description writing tips:**
- Include both WHAT it does and WHEN to use it
- Be specific about trigger conditions
- Make it slightly "pushy" to avoid under-triggering
- Example: "Use this skill whenever the user mentions X, Y, or Z, even if they don't explicitly ask for [skill name]"

### Body

Write in **imperative/infinitive form** (verb-first, not "you should"):
- "To accomplish X, do Y"
- Not: "You should do X"

Include:
1. **Purpose** -- what the skill does in 2-3 sentences
2. **When to use** -- specific trigger contexts
3. **How to use** -- step-by-step instructions for Claude
4. **References** to bundled resources (scripts, references, assets)

### Size Guidelines

- SKILL.md body: keep under 500 lines
- Reference files: move detailed content here to keep SKILL.md lean
- If SKILL.md approaches 500 lines, add a `references/` file and link to it

## Step 5: Progressive Disclosure

Skills load in 3 stages:
1. **Metadata** (name + description) -- always in context
2. **SKILL.md body** -- loaded when skill triggers
3. **Bundled resources** -- loaded only as needed

Keep SKILL.md focused on essential workflow. Put detailed schemas, API docs, and examples in `references/`.

## Step 6: Package

```bash
# Zip for sharing
zip -r skill-name.zip skill-name/

# Or using the ComposioHQ packaging script (if available)
python scripts/package_skill.py path/to/skill-folder
```

## Description Quality Checklist

- [ ] Clearly states what the skill does
- [ ] Specifies when to trigger (not just what it does)
- [ ] Includes specific keywords/contexts that should trigger it
- [ ] Is not so broad it triggers on everything
- [ ] Is not so narrow it never triggers

## Common Mistakes

- **Too vague**: "Helps with data" -- Claude won't know when to use it
- **Too long**: Descriptions over ~100 words become hard to parse
- **Missing triggers**: Saying what it does without saying when to use it
- **Passive voice**: "This skill can be used..." -> "Use this skill when..."
