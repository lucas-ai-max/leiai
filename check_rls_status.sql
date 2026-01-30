-- Script para verificar o status atual do RLS
-- Execute este script para diagnosticar o problema

-- 1. Verificar se RLS está habilitado
SELECT 
    tablename,
    rowsecurity as "RLS Habilitado"
FROM pg_tables 
WHERE tablename = 'documento_gerenciamento';

-- 2. Listar todas as políticas existentes
SELECT 
    schemaname,
    tablename,
    policyname as "Nome da Política",
    permissive as "Permissiva",
    roles as "Roles",
    cmd as "Comando",
    qual as "USING",
    with_check as "WITH CHECK"
FROM pg_policies 
WHERE tablename = 'documento_gerenciamento';

-- 3. Verificar estrutura da tabela
SELECT 
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'documento_gerenciamento'
ORDER BY ordinal_position;
