-- Permissions Fix Script
-- Run this in Supabase SQL Editor if frontend still has access issues

-- 1. Ensure RLS is disabled (Open Access)
ALTER TABLE public.prompt_config DISABLE ROW LEVEL SECURITY;

-- 2. Explicitly Grant Permissions to API roles
GRANT ALL ON TABLE public.prompt_config TO anon, authenticated, service_role;
GRANT ALL ON SEQUENCE public.prompt_config_id_seq TO anon, authenticated, service_role;

-- 3. Verify Grants
SELECT grantee, privilege_type 
FROM information_schema.role_table_grants 
WHERE table_name = 'prompt_config';

-- 4. Re-create constraint to avoid duplicate prompts per project
ALTER TABLE public.prompt_config DROP CONSTRAINT IF EXISTS prompt_config_projeto_id_key;
ALTER TABLE public.prompt_config ADD CONSTRAINT prompt_config_projeto_id_key UNIQUE (projeto_id);

SELECT 'Permissions fixed for prompt_config' as status;
