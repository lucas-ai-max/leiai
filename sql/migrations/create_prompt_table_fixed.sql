-- Script corrigido para criar a tabela prompt_config no Supabase (Versão Multi-Projeto)
-- Execute este script no SQL Editor do Supabase se a tabela não existir ou estiver com erro.

-- 1. Remover tabela se existir
DROP TABLE IF EXISTS public.prompt_config CASCADE;

-- 2. Criar tabela com suporte a projeto_id
CREATE TABLE public.prompt_config (
    id SERIAL PRIMARY KEY,
    projeto_id UUID UNIQUE REFERENCES public.projeto(id) ON DELETE CASCADE,
    prompt_text TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Desabilitar RLS
ALTER TABLE public.prompt_config DISABLE ROW LEVEL SECURITY;

-- 4. Políticas (opcional, para garantia futura)
CREATE POLICY "Allow public all" ON public.prompt_config FOR ALL TO public USING (true) WITH CHECK (true);

-- 5. Comentário
COMMENT ON TABLE public.prompt_config IS 'Armazena o prompt customizado por projeto';

SELECT 'Tabela prompt_config recriada com sucesso!' as status;
