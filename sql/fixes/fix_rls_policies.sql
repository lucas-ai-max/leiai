-- Script para corrigir políticas RLS (Row Level Security) do Supabase
-- Execute este script no SQL Editor do Supabase

-- ============================================
-- OPÇÃO 1: DESABILITAR RLS (MAIS SIMPLES)
-- ============================================
-- Descomente a linha abaixo se quiser desabilitar RLS completamente
-- ALTER TABLE documento_gerenciamento DISABLE ROW LEVEL SECURITY;

-- ============================================
-- OPÇÃO 2: CRIAR POLÍTICAS PERMISSIVAS (RECOMENDADO)
-- ============================================

-- 1. Remover TODAS as políticas existentes primeiro
DO $$ 
DECLARE
    r RECORD;
BEGIN
    FOR r IN (SELECT policyname FROM pg_policies WHERE tablename = 'documento_gerenciamento') LOOP
        EXECUTE 'DROP POLICY IF EXISTS ' || quote_ident(r.policyname) || ' ON documento_gerenciamento';
    END LOOP;
END $$;

-- 2. Habilitar RLS (se não estiver)
ALTER TABLE documento_gerenciamento ENABLE ROW LEVEL SECURITY;

-- 3. Criar políticas permissivas para operações públicas
-- Política para INSERT (permitir qualquer um inserir)
CREATE POLICY "Allow public insert on documento_gerenciamento"
ON documento_gerenciamento
FOR INSERT
TO public
WITH CHECK (true);

-- Política para SELECT (permitir qualquer um ler)
CREATE POLICY "Allow public select on documento_gerenciamento"
ON documento_gerenciamento
FOR SELECT
TO public
USING (true);

-- Política para UPDATE (permitir qualquer um atualizar)
CREATE POLICY "Allow public update on documento_gerenciamento"
ON documento_gerenciamento
FOR UPDATE
TO public
USING (true)
WITH CHECK (true);

-- Política para DELETE (opcional - permitir deletar)
CREATE POLICY "Allow public delete on documento_gerenciamento"
ON documento_gerenciamento
FOR DELETE
TO public
USING (true);

-- 4. Verificar se a coluna storage_path existe (se não, criar)
ALTER TABLE documento_gerenciamento 
ADD COLUMN IF NOT EXISTS storage_path TEXT;

-- 5. Verificar se a coluna file_size_mb existe (se não, criar)
ALTER TABLE documento_gerenciamento 
ADD COLUMN IF NOT EXISTS file_size_mb NUMERIC(10, 2);

-- 6. Verificar se a coluna error_message existe (se não, criar)
ALTER TABLE documento_gerenciamento 
ADD COLUMN IF NOT EXISTS error_message TEXT;

-- Comentários explicativos
COMMENT ON POLICY "Allow public insert on documento_gerenciamento" ON documento_gerenciamento IS 
'Permite que qualquer usuário (incluindo anônimos) insira registros na tabela';

COMMENT ON POLICY "Allow public select on documento_gerenciamento" ON documento_gerenciamento IS 
'Permite que qualquer usuário (incluindo anônimos) leia registros da tabela';

COMMENT ON POLICY "Allow public update on documento_gerenciamento" ON documento_gerenciamento IS 
'Permite que qualquer usuário (incluindo anônimos) atualize registros da tabela';
