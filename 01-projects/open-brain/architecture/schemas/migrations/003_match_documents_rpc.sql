-- 003_match_documents_rpc.sql
-- Open Brain: RPC function for cross-table semantic search
-- Called by the MCP server's semantic_search tool
-- Created: 2026-04-10
--
-- Idempotent: CREATE OR REPLACE

CREATE OR REPLACE FUNCTION match_documents(
    query_embedding vector(1536),
    match_table text,
    match_limit int DEFAULT 10,
    match_threshold float DEFAULT 0.7
)
RETURNS TABLE (
    id uuid,
    similarity float,
    content jsonb
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    IF match_table = 'captures' THEN
        RETURN QUERY
        SELECT
            c.id,
            (1 - (c.embedding <=> query_embedding))::float AS similarity,
            jsonb_build_object(
                'source', c.source,
                'original_text', left(c.original_text, 500),
                'status', c.status,
                'confidence', c.confidence,
                'topics', c.topics,
                'created_at', c.created_at
            ) AS content
        FROM captures c
        WHERE c.deleted_at IS NULL
          AND c.embedding IS NOT NULL
          AND (1 - (c.embedding <=> query_embedding)) >= match_threshold
        ORDER BY c.embedding <=> query_embedding
        LIMIT match_limit;

    ELSIF match_table = 'people' THEN
        RETURN QUERY
        SELECT
            p.id,
            (1 - (p.embedding <=> query_embedding))::float AS similarity,
            jsonb_build_object(
                'name', p.name,
                'context', p.context,
                'company', p.company,
                'role', p.role,
                'health_score', p.health_score,
                'importance', p.importance,
                'last_contact', p.last_contact,
                'topics', p.topics
            ) AS content
        FROM people p
        WHERE p.deleted_at IS NULL
          AND p.embedding IS NOT NULL
          AND (1 - (p.embedding <=> query_embedding)) >= match_threshold
        ORDER BY p.embedding <=> query_embedding
        LIMIT match_limit;

    ELSIF match_table = 'projects' THEN
        RETURN QUERY
        SELECT
            pr.id,
            (1 - (pr.embedding <=> query_embedding))::float AS similarity,
            jsonb_build_object(
                'name', pr.name,
                'description', left(pr.description, 500),
                'status', pr.status,
                'category', pr.category,
                'next_action', pr.next_action,
                'vault_path', pr.vault_path,
                'topics', pr.topics
            ) AS content
        FROM projects pr
        WHERE pr.deleted_at IS NULL
          AND pr.embedding IS NOT NULL
          AND (1 - (pr.embedding <=> query_embedding)) >= match_threshold
        ORDER BY pr.embedding <=> query_embedding
        LIMIT match_limit;

    ELSIF match_table = 'ideas' THEN
        RETURN QUERY
        SELECT
            i.id,
            (1 - (i.embedding <=> query_embedding))::float AS similarity,
            jsonb_build_object(
                'title', i.title,
                'body', left(i.body, 500),
                'status', i.status,
                'source', i.source,
                'priority', i.priority,
                'topics', i.topics
            ) AS content
        FROM ideas i
        WHERE i.deleted_at IS NULL
          AND i.embedding IS NOT NULL
          AND (1 - (i.embedding <=> query_embedding)) >= match_threshold
        ORDER BY i.embedding <=> query_embedding
        LIMIT match_limit;

    ELSE
        RAISE EXCEPTION 'Invalid table: %. Must be captures, people, projects, or ideas.', match_table;
    END IF;
END;
$$;
