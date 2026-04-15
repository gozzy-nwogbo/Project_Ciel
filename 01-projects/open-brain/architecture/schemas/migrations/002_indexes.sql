-- 002_indexes.sql
-- Open Brain: HNSW vector indexes (replaces IVFFlat from 001)
-- Phase 3 (Memory Search & RAG)
-- Created: 2026-04-10
--
-- HNSW is preferred over IVFFlat because:
-- 1. Works on empty tables (IVFFlat needs data to build)
-- 2. Better recall at our scale (<100k rows)
-- 3. No need to tune lists parameter
--
-- Idempotent: safe to run multiple times.
-- If 001 was already run, the IVFFlat indexes are dropped first.

-- ============================================================
-- Drop old IVFFlat indexes if they exist
-- ============================================================

DROP INDEX IF EXISTS idx_captures_embedding;
DROP INDEX IF EXISTS idx_people_embedding;
DROP INDEX IF EXISTS idx_projects_embedding;
DROP INDEX IF EXISTS idx_ideas_embedding;

-- ============================================================
-- Create HNSW vector indexes
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_captures_embedding
    ON captures USING hnsw (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_people_embedding
    ON people USING hnsw (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_projects_embedding
    ON projects USING hnsw (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_ideas_embedding
    ON ideas USING hnsw (embedding vector_cosine_ops);
