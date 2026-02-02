# 🔒 Solução Completa para Erro RLS

## Erro
```
new row violates row-level security policy
```

## ⚠️ IMPORTANTE: O erro pode vir de 2 lugares!

1. **Tabela `documento_gerenciamento`** - RLS bloqueando INSERT
2. **Storage Bucket `processos`** - RLS bloqueando UPLOAD

## 🚀 Solução Passo a Passo

### PASSO 1: Desabilitar RLS na Tabela

Execute no **SQL Editor** do Supabase:

```sql
-- Desabilitar RLS na tabela
ALTER TABLE documento_gerenciamento DISABLE ROW LEVEL SECURITY;

-- Remover todas as políticas
DO $$ 
DECLARE
    r RECORD;
BEGIN
    FOR r IN (
        SELECT policyname 
        FROM pg_policies 
        WHERE schemaname = 'public' 
        AND tablename = 'documento_gerenciamento'
    ) LOOP
        EXECUTE format('DROP POLICY IF EXISTS %I ON public.documento_gerenciamento', r.policyname);
    END LOOP;
END $$;

-- Verificar
SELECT 
    tablename,
    CASE 
        WHEN rowsecurity THEN '❌ RLS HABILITADO'
        ELSE '✅ RLS DESABILITADO'
    END as status
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename = 'documento_gerenciamento';
```

**Resultado esperado:** `✅ RLS DESABILITADO`

---

### PASSO 2: Configurar Storage Bucket

O Storage também tem RLS! Execute:

```sql
-- Tornar o bucket público
UPDATE storage.buckets 
SET public = true 
WHERE name = 'processos';

-- Remover políticas antigas do Storage
DROP POLICY IF EXISTS "Public Access" ON storage.objects;
DROP POLICY IF EXISTS "Authenticated users can upload" ON storage.objects;
DROP POLICY IF EXISTS "Public can upload" ON storage.objects;

-- Criar políticas permissivas para o Storage
CREATE POLICY "Public can upload to processos"
ON storage.objects
FOR INSERT
TO public
WITH CHECK (bucket_id = 'processos');

CREATE POLICY "Public can read from processos"
ON storage.objects
FOR SELECT
TO public
USING (bucket_id = 'processos');

-- Verificar
SELECT 
    name,
    public as "Bucket Público",
    CASE 
        WHEN public THEN '✅ Público'
        ELSE '❌ Privado'
    END as status
FROM storage.buckets 
WHERE name = 'processos';
```

**Resultado esperado:** `✅ Público`

---

### PASSO 3: Verificar no Dashboard

1. Acesse: **Storage** → **processos**
2. Verifique se está marcado como **Public bucket**
3. Se não estiver, marque manualmente

---

### PASSO 4: Testar

Após executar os scripts:

1. **Reinicie o servidor frontend** (Ctrl+C e `npm run dev`)
2. Tente fazer upload novamente
3. Abra o **Console do navegador** (F12) para ver logs detalhados

---

## 🔍 Diagnóstico

Se ainda não funcionar, execute este diagnóstico:

```sql
-- 1. Verificar tabela
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE tablename = 'documento_gerenciamento';

-- 2. Verificar políticas da tabela
SELECT * FROM pg_policies 
WHERE tablename = 'documento_gerenciamento';

-- 3. Verificar bucket
SELECT name, public FROM storage.buckets WHERE name = 'processos';

-- 4. Verificar políticas do Storage
SELECT * FROM pg_policies 
WHERE tablename = 'objects' 
AND schemaname = 'storage';
```

---

## ✅ Checklist Final

- [ ] RLS desabilitado na tabela `documento_gerenciamento`
- [ ] Nenhuma política bloqueando a tabela
- [ ] Bucket `processos` está público
- [ ] Políticas do Storage permitem upload público
- [ ] Frontend usando chave **anon public** (não service_role)
- [ ] Servidor frontend reiniciado

---

## 🆘 Se Ainda Não Funcionar

1. Verifique o **Console do navegador** (F12) - agora mostra logs detalhados
2. Verifique se a chave anon está correta no `.env`
3. Tente fazer upload de um arquivo muito pequeno (teste)
4. Verifique se o bucket realmente existe
