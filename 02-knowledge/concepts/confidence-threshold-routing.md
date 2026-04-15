---
title: Confidence Threshold Routing
type: concept
source_date: 2026-04-13
tags: [classification, data-pipeline, quality-control]
---

A classification strategy that routes captured data to high-confidence tables based on a confidence score threshold. Items meeting the threshold (0.6 or above) are written to dedicated tables for people, projects, and ideas, while all captures are simultaneously logged to an audit trail regardless of confidence level.
