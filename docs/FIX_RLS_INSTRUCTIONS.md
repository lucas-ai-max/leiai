# 🔒 Como Corrigir o Erro "Row Level Security Policy"

## Erro
```
new row violates row-level security policy
```

## Causa
O Supabase está bloqueando inserções na tabela `documento_gerenciamento` devido às políticas de Row Level Security (RLS).

## Solução

### Passo 1: Acessar o SQL Editor do Supabase

1. Acesse: https://supabase.com/dashboard
2. Selecione seu projeto
3. No menu lateral, clique em **SQL Editor**
4. Clique em **New query**

### Passo 2: Executar o Script SQL

1. Abra o arquivo `fix_rls_policies.sql` no seu projeto
2. Copie TODO o conteúdo do arquivo
3. Cole no SQL Editor do Supabase
4. Clique em **Run** (ou pressione Ctrl+Enter)

### Passo 3: Verificar se Funcionou

Após executar o script, tente fazer upload de um PDF novamente no frontend.

## O que o Script Faz

1. ✅ Habilita RLS na tabela (se necessário)
2. ✅ Remove políticas antigas que podem estar bloqueando
3. ✅ Cria políticas permissivas para:
   - **INSERT**: Permite inserir novos registros
   - **SELECT**: Permite ler registros
   - **UPDATE**: Permite atualizar registros
4. ✅ Cria colunas faltantes (`storage_path`, `file_size_mb`, `error_message`)

## Alternativa: Desabilitar RLS (NÃO RECOMENDADO)

Se você quiser desabilitar RLS completamente (menos seguro):

```sql
ALTER TABLE documento_gerenciamento DISABLE ROW LEVEL SECURITY;
```

⚠️ **Atenção**: Isso remove toda a segurança. Use apenas para testes.

## Verificar Políticas Existentes

Para ver quais políticas estão ativas:

```sql
SELECT * FROM pg_policies WHERE tablename = 'documento_gerenciamento';
```

## Troubleshooting

### Se ainda não funcionar:

1. Verifique se você está usando a chave **anon public** no frontend (não a service_role)
2. Verifique se a tabela existe: `SELECT * FROM documento_gerenciamento LIMIT 1;`
3. Verifique se as colunas existem: `\d documento_gerenciamento` (no psql) ou veja no Table Editor

### Se precisar de mais segurança:

Você pode criar políticas mais restritivas depois, mas para começar, as políticas permissivas funcionam bem.
