-- Verificar se prompt_config existe e está pronta para uso por projeto
-- Execute no SQL Editor do Supabase

-- 1. Colunas da tabela (deve ter projeto_id)
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = 'prompt_config'
ORDER BY ordinal_position;

-- 2. Quantidade de registros e se têm projeto_id
SELECT COUNT(*) AS total,
       COUNT(projeto_id) AS com_projeto_id
FROM public.prompt_config;

-- 3. Amostra (id, projeto_id, início do prompt)
SELECT id, projeto_id, LEFT(prompt_text, 60) AS prompt_preview
FROM public.prompt_config
LIMIT 10;

-- Se a tabela não existir ou não tiver projeto_id, execute migration_projetos.sql
