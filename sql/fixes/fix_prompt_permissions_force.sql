
-- 1. Check if RLS is enabled and disable for now (for development)
ALTER TABLE public.prompt_config DISABLE ROW LEVEL SECURITY;

-- 2. Grant ALL permissions to all roles (anon, authenticated, service_role)
GRANT ALL ON TABLE public.prompt_config TO anon, authenticated, service_role;
GRANT USAGE, SELECT ON SEQUENCE prompt_config_id_seq TO anon, authenticated, service_role;

-- 3. Verify Constraints (Optional: Drop if causing issues, but UNIQUE is needed)
-- ALTER TABLE public.prompt_config DROP CONSTRAINT IF EXISTS prompt_config_projeto_id_key;
-- ALTER TABLE public.prompt_config ADD CONSTRAINT prompt_config_projeto_id_key UNIQUE (projeto_id);

-- 4. Test Insert (This will fail if project doesn't exist, so create a dummy project first if needed)
-- INSERT INTO public.projeto (id, nome) VALUES ('00000000-0000-0000-0000-000000000000', 'Test Project') ON CONFLICT DO NOTHING;
-- INSERT INTO public.prompt_config (projeto_id, prompt_text) VALUES ('00000000-0000-0000-0000-000000000000', 'Test Prompt') 
-- ON CONFLICT (projeto_id) DO UPDATE SET prompt_text = EXCLUDED.prompt_text;

-- 5. Check if data exists
SELECT count(*) as total_prompts FROM public.prompt_config;
