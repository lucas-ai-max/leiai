-- Extensão pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Tabela de chunks
CREATE TABLE documento_chunks (
    id BIGSERIAL PRIMARY KEY,
    document_id TEXT NOT NULL,
    filename TEXT NOT NULL,
    page_number INTEGER NOT NULL,
    chunk_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(1536),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_doc_id ON documento_chunks(document_id);
CREATE INDEX idx_filename ON documento_chunks(filename);
CREATE INDEX ON documento_chunks USING hnsw (embedding vector_cosine_ops);

-- Tabela de respostas
CREATE TABLE documento_respostas (
    id BIGSERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    document_id TEXT NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    "references" JSONB,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_resp_filename ON documento_respostas(filename);

-- Função de busca
CREATE OR REPLACE FUNCTION match_chunks(
    query_embedding VECTOR(1536),
    match_count INT DEFAULT 8,
    filter_document_id TEXT DEFAULT NULL
)
RETURNS TABLE (
    id BIGINT,
    document_id TEXT,
    filename TEXT,
    page_number INTEGER,
    content TEXT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        c.document_id,
        c.filename,
        c.page_number,
        c.content,
        1 - (c.embedding <=> query_embedding) AS similarity
    FROM documento_chunks c
    WHERE 
        (filter_document_id IS NULL OR c.document_id = filter_document_id)
    ORDER BY c.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;
