-- WARNING: This script will Re-Create the prompt_config table correctly for multi-project support.
-- It fixes the "single row" constraint issue and adds the 'projeto_id' column.

-- 1. Drop existing table (Data will be lost, but it's just config)
DROP TABLE IF EXISTS public.prompt_config CASCADE;

-- 2. Create table with correct schema
CREATE TABLE public.prompt_config (
    id SERIAL PRIMARY KEY,
    projeto_id UUID UNIQUE REFERENCES public.projeto(id) ON DELETE CASCADE,
    prompt_text TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Disable RLS for easy access (or configure policies if needed)
ALTER TABLE public.prompt_config DISABLE ROW LEVEL SECURITY;

-- 4. Create policies (just in case RLS is enabled later)
DROP POLICY IF EXISTS "Allow public select on prompt_config" ON public.prompt_config;
CREATE POLICY "Allow public select on prompt_config" ON public.prompt_config FOR SELECT TO public USING (true);

DROP POLICY IF EXISTS "Allow public insert on prompt_config" ON public.prompt_config;
CREATE POLICY "Allow public insert on prompt_config" ON public.prompt_config FOR INSERT TO public WITH CHECK (true);

DROP POLICY IF EXISTS "Allow public update on prompt_config" ON public.prompt_config;
CREATE POLICY "Allow public update on prompt_config" ON public.prompt_config FOR UPDATE TO public USING (true) WITH CHECK (true);

-- 5. Insert a legacy default if needed (linked to the first project found, or null)
-- We insert a default prompt for projects that don't have one yet? No, frontend handles defaults.
-- But we can insert one for the "default project" if it exists.

DO $$
DECLARE
    default_project_id UUID;
BEGIN
    SELECT id INTO default_project_id FROM public.projeto ORDER BY created_at ASC LIMIT 1;
    
    IF default_project_id IS NOT NULL THEN
        INSERT INTO public.prompt_config (projeto_id, prompt_text)
        VALUES (default_project_id, 'Analise o documento jurídico e extraia estas informações em formato JSON:

{
  "numero_processo": "Número do processo",
  "tipo_documento": "Tipo do documento",
  "partes": "Partes envolvidas",
  "juiz": "Nome do juiz",
  "data_decisao": "Data da decisão",
  "resultado": "Resultado da decisão",
  "resumo": "Resumo breve"
}

CHAVES OBRIGATÓRIAS:
numero_processo, tipo_documento, partes, juiz, data_decisao, resultado, resumo

Retorne APENAS o JSON válido.');
    END IF;
END $$;

SELECT 'Tabela prompt_config corrigida com sucesso (Suporte a múltiplos projetos)' as status;
