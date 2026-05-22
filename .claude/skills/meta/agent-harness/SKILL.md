# Agent Harness Skill
**Category:** meta
**Variant:** anthropic (Claude Code)
**Source:** Derived from Nate B. Jones / OB1 `n-agentic-harnesses`, adapted for this vault

---

## Description (loaded first — minimal context)

A routing skill for designing, auditing, and improving the harness layer around agentic products. Use this when the real problem involves tool boundaries, permission policy, approval flow, workflow state, crash durability, context assembly, memory, evals, or operator visibility. Returns a buildable plan or a findings-first review, not vague architecture advice.

**Triggers:**
- "evaluate my agent harness"
- "audit this CLAUDE.md"
- "audit my skill against the 12 primitives"
- "what's missing from this agent"
- "help me design a new agent"
- "harness review"
- "is my agent production-ready"
- "design the harness for [X]"
- "what primitives should I build first"
- "run a retrospective on [phase/build]"

**Opinionated defaults:**
- Single-agent unless the request gives a strong documented reason for multi-agent
- Tier 1 primitives must be stable before Tier 2 is discussed
- Simplicity is maintainable, push back on premature complexity

---

## Full Skill (loaded on trigger)

### What This Skill Does

This skill helps you reason about the non-glamorous 80% of agentic system engineering: the harness that makes an agent reliable, safe, and auditable over time. It routes to one of three modes based on your request, and returns structured output you can act on immediately.

**Modes:**
1. **Design Mode** — You describe what you're building. The skill produces an architecture with rationale before any code is written.
2. **Evaluation Mode** — Point it at an existing codebase, CLAUDE.md, or architecture doc. The skill returns findings ordered by severity and a prioritized upgrade path.
3. **Retrospective Mode** — After completing a build phase, run this to confirm the phase's primitives are actually stable before advancing. This is the runtime enforcement mechanism for the PRD's phase gating.

---

### The 12 Primitives Reference

Before routing to a mode, internalize this reference. Every output from this skill should be grounded in these primitives, presented in the order they should be built.

#### TIER 1 — Day-One Non-Negotiables

**P1: Tool Registry with Metadata-First Design**
- Pattern: Define capabilities as a data structure before writing implementation. The registry answers "what exists and what does it do" without executing anything.
- Production signal: Two parallel registries, commands (user-facing) and tools (model-facing). Every entry has a name, source hint, and responsibility description. Implementations load on demand.
- Your system signal: Can you call `list_tools()` and get metadata for all capabilities without triggering any of them? Can you filter by context? If no: this is missing.
- Failure mode without it: Can't filter tools by context. Every new tool requires orchestration changes. System is opaque to introspection.

**P2: Permission System with Tiered Trust**
- Pattern: Categorize every tool by risk tier (read-only / mutating / destructive). Apply different approval requirements per tier. Pre-classify, don't improvise.
- Production signal: Three trust tiers (built-in always-available / plugin medium-trust / user-defined lowest-trust). Shell execution alone has an 18-module security stack: pre-approved patterns, destructive command warnings, domain-specific checks, sandbox termination.
- Your system signal: Is every tool classified by what it can do to the world? Do you have pre-approved patterns for safe actions? Do you log every permission decision with action + reason + timestamp?
- Failure mode without it: You have a demo. Not a product. An agent that can execute code or modify files without a permission layer is not deployable.

**P3: Session Persistence That Survives Crashes**
- Pattern: A session is not conversation history. It is a recoverable state object: conversation + usage metrics + permission decisions + configuration. All together, as a unit.
- Production signal: Sessions persisted as JSON. Captures session ID, messages, token counts in/out. A `resume_session()` function can reconstruct the full engine from the stored file, load, reconstruct transcript, restore counters, return functional agent.
- Your system signal: If the process dies mid-run, can you resume with the same tools, permissions, and token state? Or does every crash restart from zero?
- Failure mode without it: Every interruption is a restart. Every restart is a degraded experience.

**P4: Workflow State (Separate From Session State)**
- Pattern: Chat transcript = what was said. Workflow state = what step are we in, what side effects have happened, is this safe to retry, what happens after restart. These are different problems with different solutions.
- Production signal: Explicit workflow states distinct from conversation state. Named states like `planned`, `awaiting_approval`, `executing`, `waiting_on_external`. Checkpoints persisted continuously.
- Your system signal: If the agent crashes mid-tool-execution, will it duplicate a write or re-run an expensive operation? Do you have explicit named states for long-running work?
- Failure mode without it: Agent can be reinstated to conversation position but not workflow position. Silent double-sends and duplicate writes.

**P5: Token Budget Management**
- Pattern: Hard limits on token usage enforced at the engine level. Per-session ceilings. Pre-turn projection that stops execution before the API call if the budget is exceeded. Structured stop reason returned, not a hard crash.
- Production signal: Max turns, max token budget, compaction threshold, all configured. Every turn calculates projected usage before proceeding. If projection exceeds budget, execution stops with a structured stop reason.
- Your system signal: Can your agent run away and burn unlimited tokens? If yes, this is missing. Budget tracking is non-negotiable responsible engineering.
- Failure mode without it: Runaway loops, unexpected spend, customer trust damage.

**P6: Structured Streaming Events**
- Pattern: Streaming isn't about showing text. Every event is an opportunity to communicate system state: what tools the agent is considering, token consumption, whether it's wrapping up. Typed events, not raw chain-of-thought. Plan for a typed crash event as the last message in a failed stream.
- Production signal: Typed events emitted throughout the stream, `message_start`, `command_match`, `tool_match`, and others. Failed streams emit a typed crash event with a reason. This is the stream's black box recorder.
- Your system signal: Can a human watching the stream understand what the agent is doing and intervene? Does a crashed stream emit a typed reason, or just go silent?
- Failure mode without it: Black box agent. No intervention surface. Silent failures look like hangs.

**P7: System Event Log**
- Pattern: Separate from conversation transcript and streaming events, a persistent log of what the agent DID, not just what it said. Source of truth for any agentic run: context loaded, tool call, permission decision logged.
- Production signal: History log of system events, each with category and structured details. Full run reconstructable from the log alone.
- Your system signal: When something goes wrong, can you reconstruct what the agent actually did? Or can you only see what it said?
- Failure mode without it: Unauditable system. No provable record of actions. Not deployable for anything consequential.

**P8: Two-Level Verification**
- Pattern: Level 1, the agent verifies its own work before completing a run. Level 2, when you change the harness, you verify the change doesn't break guarantees that used to hold.
- Production signal: Explicit verification step in the harness. Plus a suite of harness-level regression tests: "do destructive tools still require approval after this change?", "when tokens run out does the agent stop gracefully or crash?"
- Your system signal: Do you have a harness test suite that runs after any change to CLAUDE.md or skill config? Or do you evolve the harness blind?
- Failure mode without it: Silent regressions. Every architectural change is a gamble. The system degrades invisibly over time.

---

#### TIER 2 — Operational Maturity

**P9: Tool Pool Assembly**
- Pattern: General-purpose agents don't load all tools on every run. They assemble a session-specific tool pool based on mode flags, permission context, and deny lists.
- Production signal: With 184 tools in the registry, Claude assembles a context-appropriate subset per session. Hard-coded full tool lists are a smell.
- Your system signal: Are all available tools loaded on every run? If yes, this is premature optimization debt waiting to hit you.

**P10: Transcript Compaction**
- Pattern: Automatic management of conversation history to stay within token budgets over long-running sessions. Keep recent entries, discard older ones. Preserve the original goal instruction always. Track persistence status to avoid data loss.
- Production signal: Compaction after a configurable number of turns. Configurable threshold. Persistence tracking on the transcript store.
- Your system signal: For sessions over ~20 turns, what happens to context? Does it just grow unbounded? Do you lose the original instruction?

**P11: Permission Audit Trail**
- Pattern: Permissions are not a boolean gate. They are a first-class queryable state object. Three handler types for three contexts: interactive (human-in-loop), coordinator (multi-agent orchestrator distributing permissions), swarm worker (autonomous execution managed by orchestrator).
- Production signal: Three separate permission handlers, each with appropriate behavior for its context. Permission state is queryable, not just checked.
- Your system signal: If you move to multi-agent setups, does your permission model know who granted what, in what context, at what level of the hierarchy?

**P12: Agent Type System**
- Pattern: Named taxonomy of agent types, each with its own prompt, allowed tools, and behavioral constraints. Explore agents can't edit files. Plan agents don't execute code. Types are the mechanism for managing an agent population.
- Production signal: Six built-in types, Explore, Plan, Verify, Guide, General Purpose, Status Line Setup. Each fully constrained.
- Your system signal: When you spawn sub-agents, are they clones of a generic agent with no constraints? Or do they have named roles with scoped tool access?

---

### Mode 1: Design Mode

**When to use:** You're starting a new agent build and want an architecture before writing code.

**Process:**
1. Ask what type of agent is being built. Examples: chat assistant, workflow orchestrator, code agent, capture agent, research agent, notification agent.
2. Ask what the agent will be able to do in the world (read-only? write? execute? send messages?). This determines which primitives are load-bearing from day one.
3. Ask if this is a solo agent or if multi-agent coordination is planned. Default assumption: solo until given a strong documented reason otherwise.
4. Identify which Tier 1 primitives are in scope given the agent's capabilities. An agent that can only read needs fewer Tier 1 items than one that can write and execute.
5. Sequence implementation into phases. Tier 1 always comes before Tier 2. Within Tier 1, P1 (registry) and P2 (permissions) come before P3 (session) and P4 (workflow).
6. Define verification criteria for each phase before any code is written.

**Output format:**
```
AGENT TYPE: [name]
CAPABILITIES: [list what it can do to the world]
SOLO/MULTI: [single agent / multi-agent, with rationale]

PHASE 1 — MINIMUM VIABLE HARNESS
Primitives: [list]
What to build: [specific items]
Verification criteria: [what must be true before advancing]

PHASE 2 — [name]
Primitives: [list]
What to build: [specific items]
Verification criteria: [what must be true before advancing]

COMPLEXITY WARNINGS (if any):
[Things the request is pushing toward that aren't justified yet]
```

---

### Mode 2: Evaluation Mode

**When to use:** You have an existing agent, CLAUDE.md, skill registry, or architecture doc and want to know what's missing or broken.

**Process:**
1. Read the target. Ask the user to provide: CLAUDE.md, skill registry, architecture docs, or a path to the codebase.
2. Score each primitive: PRESENT / PARTIAL / MISSING.
3. For PARTIAL and MISSING, determine severity using this rubric:
   - CRITICAL: Any Tier 1 primitive that is missing in an agent that has write or execute capability
   - HIGH: Any Tier 1 primitive that is partial
   - MEDIUM: Any Tier 2 primitive that is missing
   - LOW: Any Tier 2 primitive that is partial
4. Return findings ordered by severity.
5. For each finding, provide: what's missing, why it matters, and a specific build action.
6. Provide a prioritized upgrade path ordered by dependency chain, not by severity alone (you can't build P4 before P3).

**Output format:**
```
EVALUATION TARGET: [what was read]
DATE: [today]

PRIMITIVE SCORES:
P1 Tool Registry: [PRESENT/PARTIAL/MISSING]
P2 Permission Tiers: [PRESENT/PARTIAL/MISSING]
P3 Session Persistence: [PRESENT/PARTIAL/MISSING]
P4 Workflow State: [PRESENT/PARTIAL/MISSING]
P5 Token Budgets: [PRESENT/PARTIAL/MISSING]
P6 Structured Streaming: [PRESENT/PARTIAL/MISSING]
P7 System Event Log: [PRESENT/PARTIAL/MISSING]
P8 Two-Level Verification: [PRESENT/PARTIAL/MISSING]
P9 Tool Pool Assembly: [PRESENT/PARTIAL/MISSING]
P10 Transcript Compaction: [PRESENT/PARTIAL/MISSING]
P11 Permission Audit Trail: [PRESENT/PARTIAL/MISSING]
P12 Agent Type System: [PRESENT/PARTIAL/MISSING]

FINDINGS (ordered by severity):
[CRITICAL] P_: [what's missing] → [why it matters] → [build action]
...

UPGRADE PATH (ordered by dependency chain):
Step 1: [primitive] — [what to build] — [verification test]
Step 2: ...

COMPLEXITY WARNINGS:
[Anything in the codebase that's more complex than current primitive coverage justifies]
```

---

### Mode 3: Retrospective Mode

**When to use:** You have just completed a build phase (as defined in the PRD) and want to confirm all primitives for that phase are actually stable before advancing to the next phase.

**This is the gate.** The PRD defines phases. This mode enforces them at runtime.

**Process:**
1. Identify which phase just completed. Retrieve the phase's primitives from the PRD phase table.
2. For each primitive in scope for that phase, ask: is there a passing verification test for this? Is it tested against real conditions or just assumed working?
3. Surface any primitive that is claimed complete but has no verification test.
4. Return a go/no-go verdict with specific outstanding items.

**Output format:**
```
PHASE: [name]
STATUS: [GO / NO-GO / CONDITIONAL GO]

PRIMITIVE GATE CHECK:
P_: [primitive] — [VERIFIED / ASSUMED / UNTESTED]
...

BLOCKERS (if NO-GO or CONDITIONAL GO):
[specific items that must be true before advancing]

RECOMMENDED NEXT SESSION:
[First thing to do in the next Claude Code session to close any gaps]
```

---

### Opinionated Defaults (Non-Negotiable)

These apply regardless of what the user asks for:

1. **Single-agent default.** Multi-agent is only recommended when the request makes a clear case for it, different trust boundaries, parallelizable independent work, or an explicit requirement for scoped role isolation. "It might be faster" is not sufficient.

2. **Tier 1 gates Tier 2.** Do not recommend any Tier 2 primitive to an agent that hasn't addressed all relevant Tier 1 items. An agent with P10 (compaction) but no P3 (session persistence) has its priorities backwards.

3. **Complexity is a cost, not a feature.** The most common failure mode in agentic systems is overengineering, building a multi-agent coordination layer before having a working permission system, or implementing a plugin marketplace before sessions can survive crashes. Push back explicitly and log the pushback in the output.

4. **Verification must be specific.** "It seems to work" is not a verification criterion. Every phase gate must have a named test with a specific expected behavior. Examples: "destructive tools always require approval," "when token budget is exceeded, agent stops with structured reason before API call."

5. **Log findings to the vault.** When Evaluation Mode or Retrospective Mode produces findings, offer to write the output to `04-reflections/harness-audit-[date].md` in the vault. Architectural findings that aren't captured compound into invisible debt.

---

### Vault Integration

This skill is most powerful when findings are written back to the vault.

**After Design Mode:** Write the architecture plan to `00-inbox/staging/agent-design-[name]-[date].md`

**After Evaluation Mode:** Write findings to `04-reflections/harness-audit-[date].md`

**After Retrospective Mode:** Write the gate check to `04-reflections/phase-[N]-retrospective-[date].md` and update the PRD phase status.
