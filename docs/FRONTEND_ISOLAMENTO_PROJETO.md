# Isolamento de dados por projeto (frontend)

Para que **cada dado pertença a um único projeto** e o **prompt feito pelo usuário seja salvo no projeto**, o frontend precisa:

1. **Salvar** o prompt sempre com `projeto_id` do projeto ativo (um prompt por projeto).
2. **Carregar** o prompt sempre por `projeto_id` e limpar o estado ao trocar de projeto.

---

## Corrigir: prompt não aparece ao recarregar a página

Se o prompt salvo **não aparece** ao recarregar (campo vazio), o log costuma mostrar:

`supabase.from(...).select(...).eq(...).maybe_single is not a function`

**Causa:** no **JavaScript** o cliente Supabase usa **camelCase**. O método correto é **`.maybeSingle()`**, não `.maybe_single()`.

**Onde:** no `PromptEditor.jsx`, na função que carrega o prompt (ex.: `loadPrompt` ou o `useEffect` que chama o Supabase).

**Procurar:**
```js
.eq('projeto_id', projetoId)
.maybe_single()
```

**Substituir por:**
```js
.eq('projeto_id', projetoId)
.maybeSingle()
```

Depois dessa alteração, ao recarregar a página o prompt do projeto será carregado e exibido no campo.

---

## Salvar o prompt no projeto

O prompt criado/editado pelo usuário deve ser gravado **no projeto atual**. No botão "Salvar" do Editor de Prompt:

**Onde:** função que chama o Supabase ao salvar (ex.: `savePrompt` no `PromptEditor.jsx`).

**Garantir** que o upsert inclua **sempre** o `projeto_id` do projeto ativo:

```js
// Salvar prompt NO PROJETO ativo
if (!projetoId) {
  alert('Selecione um projeto para salvar o prompt.');
  return;
}
const { error } = await supabase
  .from('prompt_config')
  .upsert(
    {
      projeto_id: projetoId,   // obrigatório: salva no projeto
      prompt_text: promptText,
      schema_json: schema,     // se a tabela tiver essa coluna
      updated_at: new Date().toISOString(),
    },
    { onConflict: 'projeto_id' }
  );
if (error) {
  console.error('Erro ao salvar prompt no projeto:', error);
  return;
}
setSavedAt(new Date().toLocaleString('pt-BR'));
```

Assim, o prompt fica **vinculado ao projeto**: cada projeto tem seu próprio prompt salvo.

**Banco:** a tabela `prompt_config` precisa ter a coluna `projeto_id` e a constraint única em `projeto_id`. Se ainda não rodou, execute no Supabase o script `migration_projetos.sql` (e, se necessário, `fix_prompt_config_on_conflict.sql`).

---

## Patch: alterações exatas para aplicar

### 1. PromptEditor – carregar prompt **só** do projeto ativo

**Onde:** no componente que carrega o prompt (ex.: `PromptEditor.jsx`), no `useEffect` que chama o Supabase para buscar o prompt.

**Procurar** algo como:
```js
.from('prompt_config')
.select(...)
.eq('id', 1)
```
ou sem `.eq('projeto_id', ...)`.

**Substituir** pela lógica abaixo (e garantir que `projetoId` seja a prop do projeto ativo):

```js
// Só carregar se tiver projeto selecionado
if (!projetoId) {
  setPromptText('');
  setSchema([]);
  setSavedAt(null);
  return;
}
const { data, error } = await supabase
  .from('prompt_config')
  .select('prompt_text, updated_at, schema_json')
  .eq('projeto_id', projetoId)
  .maybeSingle();
if (error) {
  console.error(error);
  return;
}
// Se não houver registro, estado vazio para ESTE projeto
setPromptText(data?.prompt_text ?? '');
setSchema(data?.schema_json ?? []);
setSavedAt(data?.updated_at ? new Date(data.updated_at).toLocaleString('pt-BR') : null);
```

---

### 2. PromptEditor – dependência do `useEffect` no `projetoId`

**Onde:** no mesmo arquivo, no `useEffect` que busca o prompt.

**Procurar:** array de dependências sem `projetoId` (ex.: `[]` ou `[supabase]`).

**Substituir** para incluir `projetoId`:
```js
}, [projetoId]); // recarrega sempre que trocar de projeto
```
Assim, ao clicar em outro projeto, o efeito roda de novo e carrega o prompt do projeto correto (ou vazio).

---

### 3. App – ao trocar de projeto, limpar estado do prompt

**Onde:** no componente pai (ex.: `App.jsx`), onde você define o projeto ativo ao clicar na sidebar.

**Procurar:** algo como `setProjetoAtivo(projeto)` ou `setActiveProject(projeto)`.

**Garantir** que o `PromptEditor` receba sempre o id do projeto ativo e que não haja estado “global” de prompt compartilhado entre projetos. Ou seja:
- O `PromptEditor` deve receber `projetoId={projetoAtivo?.id ?? null}`.
- O carregamento do prompt deve estar **dentro** do `PromptEditor`, com `useEffect` dependendo de `projetoId` (como no item 1 e 2). Assim, ao trocar de projeto, o `projetoId` muda e o efeito recarrega (e mostra vazio se o novo projeto não tiver prompt).

Se no App você tiver estado de “último prompt” ou “schema” e passar para o editor, **remova** esse estado do App e deixe o PromptEditor ser a única fonte: ele carrega do Supabase por `projeto_id` e exibe vazio quando não houver registro.

---

### 4. Listagens – filtrar por `projeto_id`

**documento_gerenciamento (fila de documentos):**

**Procurar:** `.from('documento_gerenciamento').select(...)` sem `.eq('projeto_id', ...)`.

**Substituir/garantir:**
```js
let query = supabase.from('documento_gerenciamento').select('*').order('created_at', { ascending: false });
if (projetoAtivo?.id) query = query.eq('projeto_id', projetoAtivo.id);
const { data } = await query;
```

**resultados_analise (resultados):**

**Procurar:** `.from('resultados_analise').select(...)` sem `.eq('projeto_id', ...)`.

**Substituir/garantir:**
```js
let query = supabase.from('resultados_analise').select('*').order('data_processamento', { ascending: false });
if (projetoAtivo?.id) query = query.eq('projeto_id', projetoAtivo.id);
const { data } = await query;
```

---

## Resumo

| Onde | O que fazer |
|------|-------------|
| **Salvar prompt** | Upsert em `prompt_config` com `projeto_id: projetoId` e `onConflict: 'projeto_id'` — o prompt fica salvo no projeto. |
| **Carregar prompt** | Sempre `.eq('projeto_id', projetoId)`. Se não houver linha, `promptText` e `schema` vazios. |
| **useEffect do prompt** | Depender de `[projetoId]` para recarregar ao trocar de projeto. |
| **Trocar projeto** | PromptEditor recebe novo `projetoId`; estado vem só do Supabase por projeto. |
| **Documentos / Resultados** | Todas as listagens com `.eq('projeto_id', projetoAtivo.id)` quando houver projeto ativo. |
