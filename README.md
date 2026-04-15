# Yzzog

**A second brain that thinks back.**

This is a personal AI infrastructure system built on top of Claude Code, Supabase (pgvector), n8n, and an Obsidian-style vault. It captures thoughts, compiles knowledge, searches semantically, and writes in a voice that's actually mine.

Not a product. Not a template. Personal infrastructure, built once, maintained incrementally, compounding in value over time.

---

## What It Does

- **Captures** raw thoughts via Telegram bot, classifies them with Claude Haiku, routes them to the right table in Supabase
- **Compiles** daily logs and raw captures into a structured wiki with concepts, connections, and an auto-maintained index
- **Searches** by meaning, not keywords, using pgvector semantic search via a custom MCP server
- **Writes** in a calibrated personal voice using a voice profile built from real interviews and writing samples
- **Integrates** with Gmail (read + draft), Google Calendar (read), and Asana (read + scoped write) through MCP tools
- **Audits itself** with a 9-criterion skill evaluation standard and harness tests for every configuration change

## Architecture

```
Vault (files)          Supabase (database)         n8n (automation)
    |                       |                           |
    +--- CLAUDE.md          +--- captures               +--- Telegram capture
    +--- .claude/skills/    +--- people                 +--- Classification
    +--- 02-knowledge/      +--- projects               +--- Routing
    +--- 05-daily/          +--- ideas                  +--- Reply
    |                       |
    +----------- MCP Server (semantic_search, write, list_recent, stats)
```

Three layers, always:
1. **Directives** — SOPs, behavioral rules, decision criteria
2. **Orchestration** — agent coordination, routing, decisions
3. **Execution** — deterministic scripts, API calls, output formatting

## Design Philosophy

**Agent surfaces, human decides, agent executes.**

Every new integration starts read-only. Write access is added deliberately. Every permission decision is logged. Confidence below threshold gets flagged, never auto-filed.

## Build Phases

| Phase | Status | What It Built |
|-------|--------|--------------|
| 1. Memory Foundation | Done | soul.md, user.md, memory.md, session hooks |
| 2. Context Persistence | Done | Knowledge pipeline, daily flush, wiki index |
| 3. Memory Search & RAG | Done | pgvector, MCP server, semantic search, system event log |
| 4. Core Integrations | Done | Telegram capture, Gmail, Calendar, Asana, permission logging |
| 5. Skills & Capabilities | In Progress | Skill migration, writing gateway, voice system |
| 6. Heartbeat & Proactive | Planned | Morning digest, weekly review, auto-drafts |
| 7. Visual Layer | Planned | Vercel web app over Supabase |
| 8. Advanced Extensions | Planned | Cross-table reasoning, warm intro engine |

## Voice System

The writing system uses a voice profile built from real interviews and writing samples. It has two paths:

- **Quick write** — short-form output (LinkedIn, email, cold outreach) produced directly in session
- **Deep write** — long-form output (articles, essays, narratives) routed through a writing brief pipeline

Platform rules for 6 platforms. Personal voice only. No generic AI output.

## Skill System

42 registered skills across 8 categories: development, design, writing, productivity, meta, integrations, n8n, and UI cloner. Every skill is evaluated against a 9-criterion standard before entering any pipeline.

## Stack

- **Agent runtime:** Claude Code (terminal-first)
- **Database:** Supabase + pgvector
- **Automation:** n8n (cloud)
- **Knowledge format:** Markdown (Obsidian-compatible)
- **Capture:** Telegram bot
- **Integrations:** Gmail, Google Calendar, Asana (via MCP)

---

*Built by Gozzy. Not a template, but if it makes you think about building your own, that was the point.*