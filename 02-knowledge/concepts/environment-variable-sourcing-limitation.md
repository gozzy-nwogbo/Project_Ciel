---
title: Environment Variable Sourcing Limitation in JSON Config
type: concept
source_date: 2026-04-10
tags: [configuration, environment, shell, json]
---

Shell source commands like `source .env` do not work in JSON configuration files because JSON lacks shell syntax interpretation. Explicit parsing methods like bash with grep/xargs/export must be used instead to load environment variables before passing them to subprocesses.
