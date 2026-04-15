-- 001_initial_schema.sql
-- Open Brain: initial database schema
-- Phase 3 (Memory Search & RAG)
-- Created: 2026-04-10
--
-- Idempotent: safe to run multiple times.
-- Run against Supabase PostgreSQL with pgvector enabled.

-- ============================================================
-- Extensions
-- ============================================================

CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================
-- Helper: updated_at trigger function
-- ============================================================

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- 1. captures
-- ============================================================

CREATE TABLE IF NOT EXISTS captures (
    id              uuid            PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at      timestamptz     NOT NULL DEFAULT now(),
    updated_at      timestamptz     NOT NULL DEFAULT now(),
    deleted_at      timestamptz,
    embedding       vector(1536),

    source          text            NOT NULL,
    original_text   text            NOT NULL,
    destination     text,
    destination_id  uuid,
    confidence      numeric(3,2)    NOT NULL DEFAULT 0.00,
    status          text            NOT NULL DEFAULT 'pending',
    topics          text[],
    entities        jsonb,
    action_items    jsonb,
    processed_at    timestamptz
);

DROP TRIGGER IF EXISTS captures_updated_at ON captures;
CREATE TRIGGER captures_updated_at
    BEFORE UPDATE ON captures
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE INDEX IF NOT EXISTS idx_captures_status
    ON captures (status) WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_captures_source
    ON captures (source, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_captures_confidence
    ON captures (confidence) WHERE status = 'needs_review';

-- ============================================================
-- 2. people
-- ============================================================

CREATE TABLE IF NOT EXISTS people (
    id              uuid            PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at      timestamptz     NOT NULL DEFAULT now(),
    updated_at      timestamptz     NOT NULL DEFAULT now(),
    deleted_at      timestamptz,
    embedding       vector(1536),

    name            text            NOT NULL,
    context         text,
    company         text,
    role            text,
    email           text,
    last_contact    timestamptz,
    contact_method  text,
    health_score    integer         NOT NULL DEFAULT 50,
    importance      text            NOT NULL DEFAULT 'medium',
    notes           text,
    topics          text[],
    next_action     text,
    next_action_due date
);

DROP TRIGGER IF EXISTS people_updated_at ON people;
CREATE TRIGGER people_updated_at
    BEFORE UPDATE ON people
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE INDEX IF NOT EXISTS idx_people_health
    ON people (health_score ASC) WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_people_last_contact
    ON people (last_contact ASC NULLS FIRST) WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_people_importance
    ON people (importance, health_score ASC);

-- ============================================================
-- 3. projects
-- ============================================================

CREATE TABLE IF NOT EXISTS projects (
    id              uuid            PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at      timestamptz     NOT NULL DEFAULT now(),
    updated_at      timestamptz     NOT NULL DEFAULT now(),
    deleted_at      timestamptz,
    embedding       vector(1536),

    name            text            NOT NULL,
    description     text,
    status          text            NOT NULL DEFAULT 'active',
    category        text,
    next_action     text,
    next_action_due date,
    last_activity   timestamptz,
    related_people  uuid[],
    vault_path      text,
    notes           text,
    topics          text[]
);

DROP TRIGGER IF EXISTS projects_updated_at ON projects;
CREATE TRIGGER projects_updated_at
    BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE INDEX IF NOT EXISTS idx_projects_status
    ON projects (status) WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_projects_activity
    ON projects (last_activity DESC NULLS LAST) WHERE status = 'active';

-- ============================================================
-- 4. ideas
-- ============================================================

CREATE TABLE IF NOT EXISTS ideas (
    id                uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at        timestamptz NOT NULL DEFAULT now(),
    updated_at        timestamptz NOT NULL DEFAULT now(),
    deleted_at        timestamptz,
    embedding         vector(1536),

    title             text        NOT NULL,
    body              text        NOT NULL,
    status            text        NOT NULL DEFAULT 'raw',
    source            text,
    source_capture_id uuid        REFERENCES captures(id),
    related_projects  uuid[],
    related_ideas     uuid[],
    topics            text[],
    priority          text
);

DROP TRIGGER IF EXISTS ideas_updated_at ON ideas;
CREATE TRIGGER ideas_updated_at
    BEFORE UPDATE ON ideas
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE INDEX IF NOT EXISTS idx_ideas_status
    ON ideas (status) WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_ideas_source
    ON ideas (source, created_at DESC);

-- ============================================================
-- Vector indexes (IVFFlat)
--
-- IVFFlat requires data in the table to build the index.
-- On an empty table, CREATE INDEX succeeds but the index
-- will be rebuilt on first query. This is expected.
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_captures_embedding
    ON captures USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_people_embedding
    ON people USING ivfflat (embedding vector_cosine_ops) WITH (lists = 50);

CREATE INDEX IF NOT EXISTS idx_projects_embedding
    ON projects USING ivfflat (embedding vector_cosine_ops) WITH (lists = 50);

CREATE INDEX IF NOT EXISTS idx_ideas_embedding
    ON ideas USING ivfflat (embedding vector_cosine_ops) WITH (lists = 50);

-- ============================================================
-- Row-Level Security
--
-- Enable RLS on all tables. Policies restrict access to
-- the service role used by the MCP server.
-- No anon or authenticated access permitted.
-- ============================================================

ALTER TABLE captures ENABLE ROW LEVEL SECURITY;
ALTER TABLE people   ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE ideas    ENABLE ROW LEVEL SECURITY;

-- Service role bypass: Supabase service_role key bypasses RLS
-- by default. These policies apply to non-service-role access
-- (anon, authenticated) and block everything.

DO $$ BEGIN
    -- captures
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'captures_deny_anon' AND tablename = 'captures') THEN
        CREATE POLICY captures_deny_anon ON captures FOR ALL TO anon USING (false);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'captures_deny_authenticated' AND tablename = 'captures') THEN
        CREATE POLICY captures_deny_authenticated ON captures FOR ALL TO authenticated USING (false);
    END IF;

    -- people
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'people_deny_anon' AND tablename = 'people') THEN
        CREATE POLICY people_deny_anon ON people FOR ALL TO anon USING (false);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'people_deny_authenticated' AND tablename = 'people') THEN
        CREATE POLICY people_deny_authenticated ON people FOR ALL TO authenticated USING (false);
    END IF;

    -- projects
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'projects_deny_anon' AND tablename = 'projects') THEN
        CREATE POLICY projects_deny_anon ON projects FOR ALL TO anon USING (false);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'projects_deny_authenticated' AND tablename = 'projects') THEN
        CREATE POLICY projects_deny_authenticated ON projects FOR ALL TO authenticated USING (false);
    END IF;

    -- ideas
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'ideas_deny_anon' AND tablename = 'ideas') THEN
        CREATE POLICY ideas_deny_anon ON ideas FOR ALL TO anon USING (false);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'ideas_deny_authenticated' AND tablename = 'ideas') THEN
        CREATE POLICY ideas_deny_authenticated ON ideas FOR ALL TO authenticated USING (false);
    END IF;
END $$;

-- ============================================================
-- Done
-- ============================================================
-- To run: paste into Supabase SQL Editor or use supabase db push
-- Next: wire MCP server write tools to these tables
