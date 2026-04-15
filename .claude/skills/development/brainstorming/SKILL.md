# Skill: Brainstorming

Transform rough ideas into fully-formed designs through Socratic questioning and structured alternative exploration. Triggers on: "I want to build...", "let's brainstorm", "help me design", "before we code". Output artifact: `design.md` saved to the project directory.

---

# Brainstorming

Activates before writing code. Refines rough ideas through questions, explores alternatives, and presents design in digestible sections for validation. Saves a design document when complete.

## When to Use

- A user says they want to build something new
- Before any implementation begins
- When requirements are vague or underspecified
- When exploring architectural options

## Process

1. **Don't jump to code** — ask clarifying questions first
2. **Tease out the real goal** — what problem is this actually solving?
3. **Explore alternatives** — present 2-3 different approaches with tradeoffs
4. **Present design in sections** — show the design incrementally, get confirmation on each part
5. **Save the design document** — write it to disk before moving to planning

## Questioning Approach (Socratic)

Ask one or two focused questions at a time. Good questions include:

- "What's the core problem you're trying to solve?"
- "Who uses this, and what's their main workflow?"
- "What does success look like in 6 months?"
- "What constraints do we have? (time, tech stack, team size)"
- "What have you already tried that didn't work?"

Avoid overwhelming with a list of 10 questions at once.

## Design Document Structure

```markdown
# Design: [Feature/Project Name]

## Problem Statement
[What problem are we solving and for whom]

## Goals
[What success looks like — measurable where possible]

## Non-Goals
[Explicitly out of scope]

## Proposed Solution
[The chosen approach with rationale]

## Alternatives Considered
[Other approaches evaluated and why they were rejected]

## Key Design Decisions
[Important choices and their tradeoffs]

## Open Questions
[Things still to be resolved]

## Implementation Notes
[Hints for the planning phase]
```

## Handoff

When the design is confirmed:
1. Save the design document to `design.md` (or similar) in the project
2. Signal readiness to move to the `writing-plans` skill
3. The plan should reference the design doc

## Philosophy

Design before code. A clear design doc prevents wasted implementation effort and gives future agents/sessions full context on what was decided and why.
