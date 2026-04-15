---
title: Temporary File Handoff Pattern
type: concept
source_date: 2026-04-09
tags: [ipc, patterns, file-systems]
---

A data passing mechanism where a process writes intermediate results to a temporary file and hands off the file path to a background worker, which processes it independently and moves results to final storage. Decouples the initiating process from the worker.
