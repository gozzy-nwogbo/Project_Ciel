# Memory

Promoted memories from daily logs. Updated by session hooks.

- **soul.md and user.md rebuilt** from structured elicitation interview on 2026-04-16. Previous versions were hand-written approximations. Elicitation summary at `04-reflections/elicitation-agent-provisioning-2026-04-16.md`.

SB Planner = Claude.ai web project (planning/strategy)
Second Brain = ~/second-brain/ local repo (execution + authoritative knowledge)
AI Domain = original local repo (legacy execution, scheduled for evaluation against Second Brain standards post-CSC)
Direction of authority: Second Brain is upstream. AI Domain mirrors from it.

Memory.md operational entries: not currently pruned. Reassess pruning policy when file exceeds ~50 entries or any individual entry passes 60 days unreferenced. Decision deferred until pattern emerges.

- Humanizer skill and AI patterns reference now in Second Brain (02-knowledge/ + .claude/skills/meta/humanizer/). Authoritative source for pattern library. AI Domain writing pipeline mirrors from here going forward.
- **Convention housekeeping complete (2026-04-29):** Karpathy principles confirmed in Coding Discipline (already present), skill architecture split documented in CLAUDE.md Section 9, content-research-writer supersession noted in registry, SB Planner template at .claude/templates/sb-planner-session-prompt.md, Claude Code session template at .claude/templates/session-prompt-template.md.
- **supersede-skill built (2026-04-29):** Atomic three-step supersession: registry strike-through + filesystem deletion + memory log. Closes operational gap surfaced by registry-audit's first run. Located at .claude/skills/meta/supersede-skill/.
- **CLAUDE.md Section 9 updated (2026-04-29):** registry-audit no longer marked as "queued, not yet built." Now documented as PASS with path reference.
- **Vault renumbered (2026-04-30):** Semantic reordering resolved duplicate 03-prefix. 03-skills/ stayed in place. 03-reflections/ -> 04-reflections/, 04-resources/ -> 05-resources/, 05-daily/ -> 06-daily/. New 07-portfolio/ created. 130+ references updated across 50+ files. CLAUDE.md vault structure tree now complete for the first time (was missing reflections since initial commit). AI Domain evaluation queued next.
- **AI Domain Pass 1 inventory complete (2026-05-01).** 37 items inventoried at 01-projects/ai-domain-evaluation/inventory.md. 9 active, 17 dormant, 3 finished. 8 promote, 5 archive, 9 extract, 4 drop, 4 unsure. Pass 2 (triage) is next. Precursor task before Pass 2: define the "good" rubric in SB Planner, determining what makes a project worth promoting vs. extracting vs. archiving vs. dropping.
- **STATUS.md is now active planning reference (2026-05-10).** PRD at 01-projects/open-brain/PRD/PRD.md is preserved as historical artifact, not maintained. Active plan lives at 01-projects/open-brain/STATUS.md. AI Domain Pass 3 outcomes will trigger Phase 7 re-scoping; definition of 'done' for initial Second Brain is deliberately undefined until Pass 3 completes.
- **AI Domain Pass 2a triage complete (2026-05-08).** 24 obvious items triaged at 01-projects/ai-domain-evaluation/triage.md. 3 promote, 6 archive, 6 extract, 5 drop, 2 archive+extract, 1 split (school), 1 selective-extract-then-drop (YoutubeTakeaways). 6 hard items deferred to Pass 2b. 7 idea files deferred to separate session. Pass 3 (execute) cannot start until both 2a and 2b are complete.
- **Phase 6.5 classifier model: claude-haiku-4-5.** 7-day evaluation window begins when classifier ships to production, not from scoping date. If accuracy below 85% on test set at threshold 0.7 after 7 days of live Telegram traffic, escalate to Sonnet 4.6.
- **People canonical contact-date column: last_contact_date** (date type, not timestamptz). The legacy last_contact column persists for read-compatibility but is deprecated. All writes to people from any system (n8n classifier, MCP, Claude Code sessions) must target last_contact_date. Slated for removal in schema-drift hygiene session.