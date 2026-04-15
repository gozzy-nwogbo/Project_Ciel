---
title: hook-blocking-root-cause
type: connection
from: Anthropic API calls
to: asynchronous-hook-processing
source_date: 2026-04-09
---

**Anthropic API calls** -> **asynchronous-hook-processing**

Synchronous API calls in the webhook handler cause blocking and timeouts, motivating adoption of asynchronous hook processing to execute API calls in background.
