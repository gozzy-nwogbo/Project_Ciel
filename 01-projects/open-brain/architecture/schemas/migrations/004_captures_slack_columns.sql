-- 004_captures_slack_columns.sql
-- Add Slack capture pipeline columns to captures table.
-- All nullable, no breaking changes. Idempotent.

ALTER TABLE captures ADD COLUMN IF NOT EXISTS source text;
ALTER TABLE captures ADD COLUMN IF NOT EXISTS classification jsonb;
ALTER TABLE captures ADD COLUMN IF NOT EXISTS status text DEFAULT 'routed';
ALTER TABLE captures ADD COLUMN IF NOT EXISTS slack_ts text;
ALTER TABLE captures ADD COLUMN IF NOT EXISTS slack_user text;
ALTER TABLE captures ADD COLUMN IF NOT EXISTS routed_to text;

-- Unique constraint on slack_ts for dedup (nulls are allowed, only non-null values are unique)
CREATE UNIQUE INDEX IF NOT EXISTS captures_slack_ts_unique ON captures (slack_ts) WHERE slack_ts IS NOT NULL;
