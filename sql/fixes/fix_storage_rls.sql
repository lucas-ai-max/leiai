-- CONFIGURAR RLS DO STORAGE BUCKET
-- O erro pode estar vindo do Storage, não da tabela!

-- ============================================
-- OPÇÃO 1: Tornar o bucket público (RECOMENDADO)
-- ============================================
-- Execute isso no SQL Editor:

UPDATE storage.buckets 
SET public = true 
WHERE name = 'processos';

-- ============================================
-- OPÇÃO 2: Criar políticas para o Storage
-- ============================================

-- Remover políticas antigas e as que vamos recriar (permite reexecutar o script)
DROP POLICY IF EXISTS "Public Access" ON storage.objects;
DROP POLICY IF EXISTS "Authenticated users can upload" ON storage.objects;
DROP POLICY IF EXISTS "Public can upload" ON storage.objects;
DROP POLICY IF EXISTS "Public can upload to processos" ON storage.objects;
DROP POLICY IF EXISTS "Public can read from processos" ON storage.objects;
DROP POLICY IF EXISTS "Public can download from processos" ON storage.objects;
DROP POLICY IF EXISTS "Public can delete from processos" ON storage.objects;

-- Política para permitir upload público
CREATE POLICY "Public can upload to processos"
ON storage.objects
FOR INSERT
TO public
WITH CHECK (bucket_id = 'processos');

-- Política para permitir leitura pública
CREATE POLICY "Public can read from processos"
ON storage.objects
FOR SELECT
TO public
USING (bucket_id = 'processos');

-- Política para permitir download público
CREATE POLICY "Public can download from processos"
ON storage.objects
FOR SELECT
TO public
USING (bucket_id = 'processos');

-- Política para permitir DELETE no bucket processos (worker limpar após processar)
DROP POLICY IF EXISTS "Public can delete from processos" ON storage.objects;
CREATE POLICY "Public can delete from processos"
ON storage.objects
FOR DELETE
TO public
USING (bucket_id = 'processos');

-- ============================================
-- VERIFICAÇÃO
-- ============================================
SELECT 
    name,
    public as "Bucket Público",
    file_size_limit as "Limite de Tamanho"
FROM storage.buckets 
WHERE name = 'processos';

-- Se "Bucket Público" = true, está configurado corretamente!
