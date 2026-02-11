-- Adiciona a coluna tamanho_bytes que o frontend está tentando enviar
-- Execute este script no SQL Editor do Supabase

ALTER TABLE public.documento_gerenciamento
ADD COLUMN IF NOT EXISTS tamanho_bytes BIGINT;

COMMENT ON COLUMN public.documento_gerenciamento.tamanho_bytes IS 'Tamanho do arquivo em bytes';

SELECT 'Coluna tamanho_bytes adicionada com sucesso.' AS status;
