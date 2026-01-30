-- SOLUÇÃO RÁPIDA: Desabilitar RLS completamente
-- Execute este script no SQL Editor do Supabase se o script anterior não funcionar

-- Desabilitar RLS na tabela
ALTER TABLE documento_gerenciamento DISABLE ROW LEVEL SECURITY;

-- Verificar se foi desabilitado
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE tablename = 'documento_gerenciamento';

-- Se retornar rowsecurity = false, está desabilitado e funcionando!
