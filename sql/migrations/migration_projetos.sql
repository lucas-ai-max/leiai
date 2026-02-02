-- Migração: Organização por Projeto (Pasta)
-- Execute no SQL Editor do Supabase. Cada projeto terá seu próprio prompt e documentos.

-- 1. Criar tabela de projetos
CREATE TABLE IF NOT EXISTS public.projeto (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índice para listagem
CREATE INDEX IF NOT EXISTS idx_projeto_created ON public.projeto(created_at DESC);

-- RLS
ALTER TABLE public.projeto DISABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow all on projeto" ON public.projeto;
CREATE POLICY "Allow all on projeto" ON public.projeto FOR ALL TO public USING (true) WITH CHECK (true);

COMMENT ON TABLE public.projeto IS 'Projetos (pastas). Cada projeto contém prompt e documentos.';

-- 2. Adicionar projeto_id em documento_gerenciamento
ALTER TABLE public.documento_gerenciamento 
ADD COLUMN IF NOT EXISTS projeto_id UUID REFERENCES public.projeto(id) ON DELETE CASCADE;

CREATE INDEX IF NOT EXISTS idx_doc_ger_projeto ON public.documento_gerenciamento(projeto_id);

-- 3. Alterar prompt_config para um registro por projeto
ALTER TABLE public.prompt_config 
ADD COLUMN IF NOT EXISTS projeto_id UUID REFERENCES public.projeto(id) ON DELETE CASCADE;

ALTER TABLE public.prompt_config DROP CONSTRAINT IF EXISTS single_row;

-- Constraint única em projeto_id (necessária para ON CONFLICT no upsert do frontend)
ALTER TABLE public.prompt_config DROP CONSTRAINT IF EXISTS prompt_config_projeto_id_key;
ALTER TABLE public.prompt_config ADD CONSTRAINT prompt_config_projeto_id_key UNIQUE (projeto_id);

-- 4. Adicionar projeto_id em resultados_analise
ALTER TABLE public.resultados_analise 
ADD COLUMN IF NOT EXISTS projeto_id UUID REFERENCES public.projeto(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_resultados_projeto ON public.resultados_analise(projeto_id);

-- 5. Inserir projeto padrão e migrar dados existentes (opcional)
INSERT INTO public.projeto (id, nome)
SELECT gen_random_uuid(), 'Projeto padrão'
WHERE NOT EXISTS (SELECT 1 FROM public.projeto LIMIT 1);

-- Atualizar documentos e resultados antigos para o primeiro projeto (se houver)
UPDATE public.documento_gerenciamento
SET projeto_id = (SELECT id FROM public.projeto ORDER BY created_at ASC LIMIT 1)
WHERE projeto_id IS NULL;

UPDATE public.resultados_analise
SET projeto_id = (SELECT id FROM public.projeto ORDER BY created_at ASC LIMIT 1)
WHERE projeto_id IS NULL;

-- Vincular prompt_config antigo (id=1) ao projeto padrão
UPDATE public.prompt_config
SET projeto_id = (SELECT id FROM public.projeto ORDER BY created_at ASC LIMIT 1)
WHERE id = 1 AND projeto_id IS NULL;

SELECT 'Migração por projeto concluída.' AS status;
