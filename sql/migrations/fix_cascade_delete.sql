-- Migration: Corrigir constraint de chave estrangeira
-- Adiciona ON DELETE CASCADE para permitir exclusão de projetos com casos vinculados

-- 1. Remover a constraint antiga
ALTER TABLE casos_processamento 
DROP CONSTRAINT IF EXISTS casos_processamento_projeto_id_fkey;

-- 2. Adicionar nova constraint com ON DELETE CASCADE
ALTER TABLE casos_processamento 
ADD CONSTRAINT casos_processamento_projeto_id_fkey 
FOREIGN KEY (projeto_id) 
REFERENCES projeto(id) 
ON DELETE CASCADE;

-- Comentário
COMMENT ON CONSTRAINT casos_processamento_projeto_id_fkey ON casos_processamento 
IS 'Quando um projeto é excluído, todos os casos vinculados também são excluídos automaticamente';

-- Verificar constraints
SELECT 
    conname AS constraint_name,
    conrelid::regclass AS table_name,
    confrelid::regclass AS referenced_table,
    pg_get_constraintdef(oid) AS constraint_definition
FROM pg_constraint
WHERE conname = 'casos_processamento_projeto_id_fkey';
