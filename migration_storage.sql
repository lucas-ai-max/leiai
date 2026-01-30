-- Script de migração para nova arquitetura com Supabase Storage
-- Execute este script no SQL Editor do Supabase

-- Adicionar coluna para armazenar o caminho do arquivo no Storage
ALTER TABLE documento_gerenciamento 
ADD COLUMN IF NOT EXISTS storage_path TEXT;

-- Adicionar índice para busca rápida por storage_path
CREATE INDEX IF NOT EXISTS idx_storage_path ON documento_gerenciamento(storage_path);

-- Comentário explicativo
COMMENT ON COLUMN documento_gerenciamento.storage_path IS 'Caminho do arquivo no Supabase Storage (bucket: processos)';
