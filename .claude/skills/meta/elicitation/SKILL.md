# Knowledge Elicitation Skill
**Category:** meta  
**Vault reference:** `01-soul/user.md`, `01-soul/soul.md`, `00-inbox/staging/`  
**Source:** Nate B. Jones "The Real Problem With AI Agents Nobody's Talking About"

---

## Description (loaded first — minimal context)

A structured interview skill that extracts tacit operational knowledge — the expertise you carry but cannot easily articulate. Use this before provisioning any new agent, starting any new project, or when you notice an agent producing generic output because it doesn't have enough of your actual context. Also use this to explore and pressure-test new ideas before committing to building them.

**Triggers:**
- "interview me about [topic/project/role]"
- "elicitation"
- "help me figure out what I actually want"
- "I want to provision a new agent"
- "my agent feels generic"
- "extract my knowledge about [X]"
- "I have a new project idea, interview me"
- "explore my idea log"
- "help me think through [X]"
- "I don't know how to describe what I need"
- "run the elicitation"
- "what do I actually know about [X]"

**Three modes:**
1. **Agent Provisioning** — Full 5-layer interview to produce soul.md / user.md config output for a new or updated agent
2. **Project Elicitation** — Structured interview to surface what you actually know, want, and need before starting a new project
3. **Idea Pressure Test** — Lighter interview that explores an idea in your idea log and surfaces whether it's worth building, what the real shape of it is, and what tacit assumptions are baked into it

---

## Full Skill (loaded on trigger)

### Why This Skill Exists

The root cause of most agent failures is not the agent — it's the quality of context the agent has to work from. Expertise compresses into automatic behavior over time. The more senior and capable you become, the less visible your own operating system is to you. You have the source code, but it's been compiled into machine code and you can no longer read it directly.

This skill is the decompiler. It asks the questions in the order and with the follow-up depth needed to surface knowledge you genuinely have but cannot access unprompted.

**This is not onboarding. This is not "describe yourself." This is a structured professional interview.**

The output is always written to the vault. The conversation itself is more valuable than the config files it produces.

---

### Before Starting Any Mode

Ask the user one question to route correctly:

> "What are we trying to surface today? Options:
> 1. Provisioning a new agent or updating an existing one (full 5-layer interview → config output)
> 2. Exploring a new project before committing to it (project elicitation → structured brief)
> 3. Pressure-testing an idea from your idea log (idea interview → go/no-go + shape definition)"

Wait for a response before proceeding.

---

### MODE 1: Agent Provisioning Interview

**When to use:** Before provisioning any new agent. Before updating soul.md or user.md after a significant life or work change. When an existing agent feels generic.

**Time investment:** 45–90 minutes. Do not rush this. The depth is the point.

**Process:** Work through the five layers in order. Each layer has primary questions and follow-up probes. Do not move to the next layer until the current one feels genuinely complete — not when the user gives a first answer, but when the follow-ups have surfaced things they didn't say initially.

---

#### LAYER 1: Operating Rhythms

*Goal: Understand the actual texture of the user's days, weeks, and months — not the calendar version, the real one.*

**Primary questions:**
- Walk me through a typical Tuesday. Not the scheduled version — what actually happens, what you actually touch, in what order.
- What does a good week look like vs. a chaotic one? What's the difference?
- What do you do first thing in the morning before anything else? What do you always do last?
- What time of day do you do your best thinking? When do you do mechanical work?
- What recurring work happens weekly that nobody would know about unless you told them?
- What's the work you always push to the next day and why?

**Follow-up probes (use when first answers are thin):**
- "What would break if you didn't do that?"
- "How long has that rhythm been in place? Did you design it or did it emerge?"
- "What does that look like on a bad week — what slips first?"
- "Who else's rhythm is yours dependent on?"

**Output to capture:** A narrative description of actual operating rhythms, not job title abstractions. Specific enough that an agent could recognize when a task fits vs. doesn't fit the real schedule.

---

#### LAYER 2: Recurring Decisions

*Goal: Surface the judgment calls that happen constantly, including the ones that feel automatic.*

**Primary questions:**
- What decisions do you make every day without thinking about them?
- What are the hard calls — the ones where you genuinely have to stop and think?
- When you're deciding whether to take on a new project or opportunity, what are you actually weighing?
- What information do you need before you can make a good decision about [relevant domain]?
- What does "good enough" look like for [key work type]? What would you reject?
- When do you escalate vs. handle something yourself? What's the real rule you use?

**Follow-up probes:**
- "What would a wrong answer look like? How would you know?"
- "Has that decision rule changed in the last year? What changed it?"
- "What's the thing you wish you could delegate but can't explain well enough to?"
- "What judgment do you apply that you've never written down?"

**Output to capture:** Named decision rules, escalation criteria, quality thresholds. Specific enough to give an agent a real framework, not just "use good judgment."

---

#### LAYER 3: Dependencies

*Goal: Map who and what the user needs to get work done — the inputs that have to arrive before outputs can happen.*

**Primary questions:**
- Who do you need things from regularly? What do you need from each of them?
- When those things are late or wrong, what breaks downstream?
- What external information do you check before starting any significant piece of work?
- What tools or systems do you depend on that would be hard to replace?
- Who are the people whose opinion you check before finalizing something?
- What's the one dependency that causes the most friction in your work?

**Follow-up probes:**
- "What's your backup if that dependency fails?"
- "How much of your work is blocked on other people at any given time?"
- "What would an agent need to know to manage those dependencies on your behalf?"

**Output to capture:** A dependency map — people, tools, information sources, timing requirements. An agent operating without this will constantly run into invisible blockers.

---

#### LAYER 4: Friction

*Goal: Surface the recurring annoyances and time sinks that the user has stopped noticing because they've accepted them.*

**Primary questions:**
- What do you do repeatedly that feels like it shouldn't be your job?
- What takes longer than it should every single time?
- What do you context-switch into multiple times a day that breaks your flow?
- What administrative work eats the most time?
- What do you always forget that costs you time to reconstruct?
- If you could make one thing disappear from your week, what would it be?

**Follow-up probes:**
- "How long has that been friction? Have you tried to fix it before?"
- "What would removing that friction be worth to you in actual time per week?"
- "What's the reason it hasn't been fixed? Is it technical, social, or just not prioritized?"

**Output to capture:** A friction inventory — specific, named recurring time sinks that are candidates for agent automation or elimination. These are the highest-ROI targets for agent deployment.

---

#### LAYER 5: Standards and Judgment Criteria

*Goal: Extract the quality thresholds, trusted sources, and operating principles that define what "right" looks like.*

**Primary questions:**
- What does excellent output look like in your most important work type? How would you recognize it?
- Which data sources or inputs do you trust? Which are you skeptical of?
- What are your non-negotiables — things you won't compromise on regardless of time pressure?
- How do you communicate differently with different audiences?
- What's your bar for sending something vs. holding it for another pass?
- What would make you stop trusting an agent's output immediately?

**Follow-up probes:**
- "Is that standard written down anywhere? If not, where did it come from?"
- "Has that standard shifted? What changed it?"
- "How would you explain that standard to someone starting in your role tomorrow?"

**Output to capture:** Named quality standards, trusted source lists, communication style rules, non-negotiables. This is what makes an agent's output feel like yours vs. generic.

---

#### Producing the Output

After all five layers are complete, produce three things:

**1. soul.md draft** — Role definition, job description, tone, boundaries, decision framework, escalation rules, non-negotiables. Format: ready to drop into `.claude/soul.md` with minimal editing.

**2. user.md draft** — Personal profile: preferences, schedule patterns, communication style, dependency map, friction inventory, quality standards. Format: ready to drop into `.claude/user.md`.

**3. Interview summary** — A 3–5 paragraph narrative of what was surfaced, what surprised you, and what the key leverage points are. This is the output to write to the vault at `04-reflections/elicitation-[date].md`.

**Vault write:** Offer to write the interview summary to `04-reflections/elicitation-[topic]-[date].md` and the config drafts to `00-inbox/staging/` for review before overwriting live files. Never overwrite soul.md or user.md directly from this skill — always route through staging.

---

### MODE 2: Project Elicitation Interview

**When to use:** Before starting any new project. When a project brief feels vague or the scope keeps shifting. When you're not sure if you actually want to build something or just think you do.

**Time investment:** 20–40 minutes.

**Process:** Six questions. Each one probes a different dimension of the project. Follow-ups are used aggressively — first answers are rarely the real answers.

---

**Q1: What problem does this project solve, and for whom?**
- Follow-up: "Who specifically has that problem right now? Can you name them?"
- Follow-up: "What are they doing instead of your solution? Is that good enough for them?"

**Q2: What does success look like in 90 days?**
- Follow-up: "What's the specific thing that would be true that isn't true today?"
- Follow-up: "How would you measure that? What number changes?"

**Q3: What do you already know how to do here, and what are you actually uncertain about?**
- Follow-up: "What's the assumption underneath this project that, if wrong, kills it?"
- Follow-up: "What's the thing you're most nervous about?"

**Q4: What would you need to believe to commit to this?**
- Follow-up: "Can you find out if that's true before spending significant time?"
- Follow-up: "What's the cheapest way to test the core assumption?"

**Q5: What is this project actually competing with for your time?**
- Follow-up: "If you do this, what doesn't get done?"
- Follow-up: "Is the trade-off worth it?"

**Q6: What would make you stop working on this?**
- Follow-up: "Is that kill condition clear enough that you'd actually stop, or would you find a reason to continue?"

**Output:** A structured project brief written to `00-inbox/staging/project-brief-[name]-[date].md`. Includes: problem definition, success criteria, known unknowns, core assumption, time trade-offs, and kill condition. Ready to use as the foundation for a PRD or to hand off to an agent for research.

---

### MODE 3: Idea Pressure Test

**When to use:** When something in your idea log feels interesting but you haven't committed to it. When you want to understand whether an idea is real before spending time on it. When exploring ideas generatively in a session.

**Time investment:** 10–20 minutes.

**Process:** Five fast questions designed to stress-test the idea, not validate it. The goal is to either sharpen it into something buildable or surface why it isn't ready yet.

---

**Q1: Say the idea in one sentence as if explaining it to someone who has never heard of it.**
- Follow-up: "Now say why it matters in one sentence."
- Note: If the user can't do either of these, the idea is not yet formed enough to act on.

**Q2: What's the fastest version of this you could test in a week?**
- Follow-up: "What would a passing result look like vs. a failing result?"

**Q3: What part of this is genuinely new, and what part is something that already exists?**
- Follow-up: "If something similar exists, why would yours be different or better for you specifically?"

**Q4: What would you need to be true about the world for this to be a bad idea?**
- Follow-up: "Is any of that true right now?"

**Q5: Does this excite you because it's genuinely valuable, or because it's interesting to think about?**
- Follow-up: "If it were boring to build but delivered the outcome, would you still want it?"

**Output:** One of three verdicts:
- **Shape it** — The idea is real. Write it to `00-inbox/staging/idea-[name]-[date].md` as a shaped brief with the answers captured.
- **Park it** — The idea has potential but a key unknown needs to be resolved first. Write the key question to the idea log.
- **Drop it** — The idea doesn't hold up under pressure. Note why in the idea log so you don't revisit it unnecessarily.

---

### Operating Rules for All Modes

**Never accept thin first answers.** The point of this skill is to get past the surface. If someone says "I make decisions based on the data," that is not a useful answer. Follow up: "Which data? In what order? What does a bad data signal look like to you?"

**Follow the energy.** If the user lights up answering a question, go deeper. That's where the real knowledge is. If a question produces a flat answer, probe once and move on — it may not be a rich vein.

**Name the abstractions.** When the user uses abstract language ("I handle the strategy," "I manage the relationship"), slow down and name the concrete behavior behind it. "Walk me through the last time you 'handled the strategy' — what did you actually do?"

**Surface the unsaid.** The most valuable knowledge is what the user doesn't think to mention because it feels obvious. The landmark-based directions problem: they tell you "turn left at the big tree" and don't realize you don't know what the big tree is. Ask for the things that feel too obvious to mention.

**Write everything to the vault.** Every output from this skill goes to the vault — not just the config files. The conversation transcript, the summary, the brief. The conversation itself is the asset. Config files can be regenerated. The surfaced knowledge compounds over time.

**Never overwrite live files.** All output routes through `00-inbox/staging/` for review. soul.md and user.md are only updated after the user has reviewed the staging drafts.

---

### Installation

```bash
mkdir -p ~/.claude/skills/elicitation
cp SKILL.md ~/.claude/skills/elicitation/SKILL.md
```

Test with:
> "Interview me about how I actually make decisions in my recruiting work."

Or:
> "I have a new project idea — interview me about it before I start building."
