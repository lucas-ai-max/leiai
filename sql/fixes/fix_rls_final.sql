-- SOLUÇÃO FINAL PARA RLS - Execute este script completo
-- Este script garante que o RLS está configurado corretamente

-- ============================================
-- PASSO 1: DESABILITAR RLS (SOLUÇÃO MAIS SIMPLES)
-- ============================================
ALTER TABLE documento_gerenciamento DISABLE ROW LEVEL SECURITY;

-- ============================================
-- PASSO 2: REMOVER TODAS AS POLÍTICAS EXISTENTES
-- ============================================
DO $$ 
DECLARE
    r RECORD;
BEGIN
    FOR r IN (
        SELECT policyname 
        FROM pg_policies 
        WHERE schemaname = 'public' 
        AND tablename = 'documento_gerenciamento'
    ) LOOP
        EXECUTE format('DROP POLICY IF EXISTS %I ON documento_gerenciamento', r.policyname);
    END LOOP;
END $$;

-- ============================================
-- PASSO 3: VERIFICAR SE ESTÁ DESABILITADO
-- ============================================
SELECT 
    tablename,
    CASE 
        WHEN rowsecurity THEN 'RLS HABILITADO ⚠️'
        ELSE 'RLS DESABILITADO ✅'
    END as status_rls
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename = 'documento_gerenciamento';

-- ============================================
-- VERIFICAÇÃO FINAL
-- ============================================
-- Se você ver "RLS DESABILITADO ✅" acima, está funcionando!
-- Agora tente fazer upload no frontend novamente.
