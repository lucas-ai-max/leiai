# "Usando prompt padrão (tabela não existe ou está vazia)" e "Tentando inser..."

## Aplicar o patch

No repositório foi criado o arquivo **`PATCH_APPLICAR_PROMPT_EDITOR.js`** com a lógica completa para carregar o prompt (uso de `.maybeSingle()`, filtro por `projeto_id`, e campo vazio quando não houver prompt salvo). Abra o seu **PromptEditor.jsx** no projeto do frontend e:

1. Busque por **`maybe_single`** e substitua **todas** as ocorrências por **`maybeSingle`**.
2. Na função que carrega o prompt (em torno da linha 71), use a lógica do arquivo `PATCH_APPLICAR_PROMPT_EDITOR.js`: filtrar por `projeto_id`, usar `.maybeSingle()`, e quando `data === null` **não** preencher com prompt padrão — deixar o campo vazio (`setPromptText('')`, etc.).
3. Garanta que o `useEffect` que chama o carregamento tenha **`[projetoId]`** nas dependências.

(O repositório **processia** não contém os arquivos do frontend; o patch é para você aplicar no projeto onde está o React/Vite.)

---

## Onde aparece

- **PromptEditor.jsx:71** — essa mensagem é logada na linha 71 do `PromptEditor.jsx`, no trecho que trata quando o carregamento do prompt “falha” ou “vem vazio”.

---

## O que essa mensagem significa

- **"Usando prompt padrão (tabela não existe ou está vazia)"**  
  O app tentou carregar o prompt do Supabase (`prompt_config`) e:
  - **não encontrou nenhum registro** para o projeto atual (`data === null`), ou
  - **a consulta falhou** (ex.: tabela não existe, RLS, ou ainda `.maybe_single()` em vez de `.maybeSingle()`).

  Quando isso acontece, o código na linha 71 usa um prompt padrão (fallback).

- **"App.jsx:348 Tentando inser..."**  
  Provavelmente **"Tentando inserir"** — o app está tentando inserir algo (ex.: em `documento_gerenciamento`, `processar_agora` ou `prompt_config`). Se a mensagem for cortada ou aparecer erro em seguida, pode ser falha de insert (tabela, RLS ou colunas).

---

## O que fazer

### 1. O que verificar no PromptEditor.jsx (em torno da linha 71)

- **Antes da linha 71** (na função que carrega o prompt):
  1. A chamada ao Supabase deve usar **`.maybeSingle()`** (camelCase), nunca `.maybe_single()`.  
     Ver: `PATCH_LOAD_PROMPT_DEBUG.md`.
  2. A query deve filtrar por projeto: **`.eq('projeto_id', projetoId)`**.  
     Se `projetoId` for `null`, não chame o Supabase (ou trate como “sem projeto” e deixe o campo vazio).
  3. Se a resposta for **`data === null`** e **`projetoId` estiver definido**, significa que **esse projeto ainda não tem prompt salvo**. Nesse caso:
     - **Não** preencha o editor com “prompt padrão”; deixe o campo **vazio** para o usuário digitar e salvar.
     - Só use “prompt padrão” se fizer sentido para outro fluxo (ex.: worker); no Editor de Prompt, “sem dado” = campo vazio.
- **Para debugar:** logo antes da linha 71, faça `console.log('loadPrompt', { projetoId, error, data: data ? 'hasData' : null })` para ver se o problema é `error` (query falhou) ou `data === null` (projeto sem prompt salvo).

### 2. Garantir que a tabela existe e está correta (Supabase)

Rode no **SQL Editor** do Supabase o script abaixo para verificar/criar a estrutura:

```sql
-- Verificar se prompt_config existe e tem projeto_id
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = 'prompt_config'
ORDER BY ordinal_position;

-- Ver quantos registros existem e se têm projeto_id
SELECT id, projeto_id, LEFT(prompt_text, 50) AS prompt_preview
FROM public.prompt_config
LIMIT 10;
```

Se a tabela **não existir** ou **não tiver** a coluna `projeto_id`:

1. Execute **`migration_projetos.sql`** (cria/ajusta tabelas e adiciona `projeto_id`).
2. Se já existir `prompt_config` mas sem `projeto_id`, a migração adiciona a coluna e a constraint; depois disso o upsert por `projeto_id` (frontend) passa a funcionar.

### 3. "Tentando inserir" que falha

Se junto com "Tentando inser..." aparecer erro no console (ex.: 404, 406, RLS, duplicate key):

- **Inserção em `documento_gerenciamento`:** confira RLS e se a tabela tem `projeto_id`, `storage_path`, etc. (conforme `migration_projetos.sql` e `migration_storage.sql`).
- **Inserção em `processar_agora`:** confira se a tabela existe (`create_processar_agora.sql`) e se o frontend envia `projeto_id`.
- **Inserção em `prompt_config`:** confira constraint única em `projeto_id` (`fix_prompt_config_on_conflict.sql`) e que o payload inclui `projeto_id` e `onConflict: 'projeto_id'`.

Copie a mensagem de erro **completa** do console (incluindo a linha que vem depois de "Tentando inser...") para ajustar o ponto exato (App.jsx:348 ou outra).

---

## Resumo

| Mensagem | Causa provável | Ação |
|----------|----------------|------|
| Usando prompt padrão (tabela não existe ou está vazia) | Query em `prompt_config` falha ou retorna vazio (ex.: `.maybe_single()`, sem `projeto_id`, tabela sem dados). | Usar `.maybeSingle()`, filtrar por `projeto_id`, e garantir tabela/estrutura com `migration_projetos.sql`. |
| App.jsx:348 Tentando inser... | Log de uma inserção (documento, processar_agora ou prompt). | Ver erro completo no console; checar tabela, RLS e payload (projeto_id, etc.). |
