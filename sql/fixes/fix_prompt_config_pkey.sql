-- Corrige duplicate key em prompt_config: id tinha DEFAULT 1, então novos projetos tentavam usar id=1.
-- Novos inserts devem usar uma sequência (id auto-incremento).
-- Execute no SQL Editor do Supabase.

-- Remover o default 1 da coluna id
ALTER TABLE public.prompt_config ALTER COLUMN id DROP DEFAULT;

-- Criar sequência e vincular ao id para novos inserts
CREATE SEQUENCE IF NOT EXISTS public.prompt_config_id_seq;

-- Ajustar sequência para o próximo valor após o maior id existente
SELECT setval(
  'public.prompt_config_id_seq',
  COALESCE((SELECT MAX(id) FROM public.prompt_config), 0) + 1
);

-- Novos inserts passam a usar a sequência
ALTER TABLE public.prompt_config
  ALTER COLUMN id SET DEFAULT nextval('public.prompt_config_id_seq');

SELECT 'Coluna id passou a usar sequência. Novos projetos não conflitam mais com id=1.' AS status;
