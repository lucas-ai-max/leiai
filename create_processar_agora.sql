-- Tabela para o usuário clicar em "Iniciar processamento" e o worker processar a fila.
-- Execute no SQL Editor do Supabase.

CREATE TABLE IF NOT EXISTS public.processar_agora (
    id BIGSERIAL PRIMARY KEY,
    projeto_id UUID REFERENCES public.projeto(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_processar_agora_created ON public.processar_agora(created_at);

ALTER TABLE public.processar_agora DISABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Allow all on processar_agora" ON public.processar_agora;
CREATE POLICY "Allow all on processar_agora" ON public.processar_agora FOR ALL TO public USING (true) WITH CHECK (true);

COMMENT ON TABLE public.processar_agora IS 'Fila de disparo: frontend insere ao clicar em Iniciar processamento; worker processa e remove.';

SELECT 'Tabela processar_agora criada.' AS status;
