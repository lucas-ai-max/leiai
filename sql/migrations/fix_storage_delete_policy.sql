-- Habilitar DELETE no bucket 'docs' para todas as roles (ou service role)
-- Isso corrige o erro: "Erro ao remover do bucket (confira RLS DELETE em storage.objects)"

BEGIN;

-- Criar política de DELETE para bucket 'docs' se não existir
-- (Pode-se usar ON storage.objects)

DROP POLICY IF EXISTS "Permitir Delete Bucket Docs" ON storage.objects;

CREATE POLICY "Permitir Delete Bucket Docs"
ON storage.objects
FOR DELETE
USING ( bucket_id = 'docs' );

-- Garantir que policies públicas também permitam (se usar cliente anon)
-- Se estiver usando service_role, isso bypassa RLS, mas o erro sugere que RLS está ativo.

COMMIT;
