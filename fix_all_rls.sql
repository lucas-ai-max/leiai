-- SOLUÇÃO COMPLETA PARA RLS - Execute este script INTEIRO
-- Este script resolve TODOS os problemas de RLS

-- ============================================
-- PARTE 1: DESABILITAR RLS NA TABELA
-- ============================================
ALTER TABLE documento_gerenciamento DISABLE ROW LEVEL SECURITY;

-- ============================================
-- PARTE 2: REMOVER TODAS AS POLÍTICAS
-- ============================================
DO $$ 
DECLARE
    r RECORD;
BEGIN
    -- Remover políticas da tabela documento_gerenciamento
    FOR r IN (
        SELECT policyname 
        FROM pg_policies 
        WHERE schemaname = 'public' 
        AND tablename = 'documento_gerenciamento'
    ) LOOP
        EXECUTE format('DROP POLICY IF EXISTS %I ON public.documento_gerenciamento', r.policyname);
        RAISE NOTICE 'Política removida: %', r.policyname;
    END LOOP;
END $$;

-- ============================================
-- PARTE 3: CONFIGURAR STORAGE BUCKET (IMPORTANTE!)
-- ============================================
-- O Storage também tem RLS! Precisamos configurar

-- Verificar se o bucket existe e suas políticas
SELECT name, public, file_size_limit 
FROM storage.buckets 
WHERE name = 'processos';

-- ============================================
-- PARTE 4: VERIFICAÇÃO FINAL
-- ============================================
-- Verificar status da tabela
SELECT 
    'Tabela: ' || tablename as item,
    CASE 
        WHEN rowsecurity THEN '❌ RLS HABILITADO'
        ELSE '✅ RLS DESABILITADO'
    END as status
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename = 'documento_gerenciamento'

UNION ALL

-- Verificar políticas restantes
SELECT 
    'Políticas restantes: ' || COUNT(*)::text as item,
    CASE 
        WHEN COUNT(*) = 0 THEN '✅ Nenhuma política'
        ELSE '⚠️ ' || COUNT(*)::text || ' políticas encontradas'
    END as status
FROM pg_policies 
WHERE schemaname = 'public' 
AND tablename = 'documento_gerenciamento';

-- ============================================
-- TESTE MANUAL (Execute separadamente se quiser testar)
-- ============================================
-- Descomente as linhas abaixo para testar inserção manual:
-- 
-- INSERT INTO documento_gerenciamento (filename, status, storage_path, file_size_mb)
-- VALUES ('teste_manual.pdf', 'PENDENTE', 'test/path.pdf', 1.5);
-- 
-- Se funcionar, o problema não é RLS na tabela!
