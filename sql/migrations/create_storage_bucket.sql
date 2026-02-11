-- Criação do Bucket 'docs' e Políticas de Segurança
-- Execute no SQL Editor do Supabase

-- 1. Criar o bucket 'docs' se não existir
INSERT INTO storage.buckets (id, name, public)
VALUES ('docs', 'docs', true)
ON CONFLICT (id) DO NOTHING;

-- 2. Políticas de Segurança (RLS) para 'docs'

-- Permitir Select público (Download)
DROP POLICY IF EXISTS "Public Access Docs" ON storage.objects;
CREATE POLICY "Public Access Docs"
ON storage.objects FOR SELECT
USING ( bucket_id = 'docs' );

-- Permitir Insert (Upload) para todos (anon e authenticated)
DROP POLICY IF EXISTS "Allow Upload Docs" ON storage.objects;
CREATE POLICY "Allow Upload Docs"
ON storage.objects FOR INSERT
WITH CHECK ( bucket_id = 'docs' );

-- Permitir Delete
DROP POLICY IF EXISTS "Allow Delete Docs" ON storage.objects;
CREATE POLICY "Allow Delete Docs"
ON storage.objects FOR DELETE
USING ( bucket_id = 'docs' );
