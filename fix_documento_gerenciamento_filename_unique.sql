-- Permite vários registros com o mesmo nome de arquivo (ex.: vários "Contrato.pdf" ou reenvios).
-- Remove a constraint UNIQUE em filename na tabela documento_gerenciamento.
-- Execute no SQL Editor do Supabase.

ALTER TABLE public.documento_gerenciamento
  DROP CONSTRAINT IF EXISTS documento_gerenciamento_filename_key;

SELECT 'Constraint documento_gerenciamento_filename_key removida. Nomes de arquivo podem se repetir.' AS status;
