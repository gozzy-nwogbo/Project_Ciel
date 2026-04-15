# Build Principles — Decision Log

Decisions that changed the architecture or tooling. Logged with rationale to prevent rediscovery.

---

## 2026-04-13 — Replaced Slack with Telegram as capture channel

**Decision:** Telegram bot (Open Brain bot) replaces Slack private channel as the primary always-on capture surface.

**Reason:** Slack n8n trigger requires production URL registration which breaks test mode. The production/test URL conflict prevents node-by-node testing, and signing secret validation caused repeated integration failures. The overall developer experience was unworkable for iterative workflow development.

**Telegram advantage:** Telegram trigger supports both test and production modes natively. No URL registration conflict. Identical capture UX (send a message, get a confirmation reply). Full n8n development parity.

**Scope of change:**
- Phase 4 capture pipeline: Telegram → n8n → Supabase (was Slack → n8n → Supabase)
- Slack deferred to Phase 6 for notifications only, not capture
- Supabase schema: `slack_ts`/`slack_user` columns replaced with `telegram_message_id`/`telegram_user_id`
- Security boundaries updated: bot reads from Open Brain bot conversation only
