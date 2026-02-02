-- Corrige ON CONFLICT no upsert do prompt por projeto.
-- Postgres exige UNIQUE CONSTRAINT (não só UNIQUE INDEX) para ON CONFLICT (projeto_id).
-- Execute no SQL Editor do Supabase.

-- Remover índice único parcial (não é usado pelo ON CONFLICT)
DROP INDEX IF EXISTS public.idx_prompt_config_projeto;

-- Garantir constraint única em projeto_id (permite upsert por projeto_id)
ALTER TABLE public.prompt_config
  DROP CONSTRAINT IF EXISTS prompt_config_projeto_id_key;

ALTER TABLE public.prompt_config
  ADD CONSTRAINT prompt_config_projeto_id_key UNIQUE (projeto_id);

SELECT 'Constraint prompt_config_projeto_id_key criada. Upsert por projeto_id deve funcionar.' AS status;
