# Yzzog

**A second brain that thinks back.**

This is a personal AI infrastructure system built on top of Claude Code, Supabase (pgvector), n8n, and an Obsidian-style vault. It captures thoughts, compiles knowledge, searches semantically, and writes in a voice that's actually mine.

Personal infrastructure. Built once, maintained over time, and it gets more useful the longer it runs.

---

## What It Does

- A Telegram bot captures raw thoughts. Claude Haiku classifies each one and routes it to the right Supabase table.
- Daily logs and captures compile into a structured wiki: concepts, connections, and an auto-maintained index. The knowledge layer compounds on its own.
- Search is semantic. A custom MCP server runs pgvector across everything the system has stored, so you query by meaning instead of guessing at keywords.
- Writing goes through a voice profile built from real interviews and writing samples. Two paths: quick (LinkedIn, email, outreach) and deep (essays, narratives, briefs).
- Gmail, Google Calendar, and Asana connect via MCP. Read access on all three; write access only where deliberately approved.
- Skills are evaluated against a 9-criterion standard, and config changes run harness tests. The system audits itself so you don't carry that overhead.

## Architecture

```
Vault (files)          Supabase (database)         n8n (automation)
    |                       |                           |
    +--- CLAUDE.md          +--- captures               +--- Telegram capture
    +--- .claude/skills/    +--- people                 +--- Classification
    +--- 02-knowledge/      +--- projects               +--- Routing
    +--- 06-daily/          +--- ideas                  +--- Reply
    |                       |
    +----------- MCP Server (semantic_search, write, list_recent, stats)
```

Three layers, always:
1. **Directives:** SOPs, behavioral rules, decision criteria
2. **Orchestration:** agent coordination, routing, decisions
3. **Execution:** deterministic scripts, API calls, output formatting

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

- **Quick write:** short-form output (LinkedIn, email, cold outreach) produced directly in session
- **Deep write:** long-form output (articles, essays, narratives) routed through a writing brief pipeline

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

*Built by Gozzy. If it makes you think about building your own, good.*