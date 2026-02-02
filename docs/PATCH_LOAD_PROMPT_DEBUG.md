# Debug: prompt não aparece ao recarregar

## Análise pós-reprodução (log)

Após reprodução, o `.cursor/debug.log` continua mostrando o mesmo erro (ex.: linhas 1–9, 16–20):

- **H1 CONFIRMADA:** O frontend ainda chama **`.maybe_single()`** — a exceção "maybe_single is not a function" continua ocorrendo.
- **Conclusão:** A correção **tem de ser aplicada no projeto do frontend** (onde está `PromptEditor.jsx`). O repositório atual (processia) **não contém** os arquivos do frontend, então a alteração é manual no seu projeto React/Vite.

## Evidência do log (runtime)

O arquivo `.cursor/debug.log` mostra repetidamente:

```json
{"location":"PromptEditor.jsx:loadPrompt:exception","message":"Exception loading prompt","data":{"error":"supabase.from(...).select(...).eq(...).maybe_single is not a function"}}
```

Ou seja: a função que **carrega** o prompt está chamando **`.maybe_single()`** (snake_case). No cliente Supabase para **JavaScript** o método é **`.maybeSingle()`** (camelCase). Por isso o carregamento falha e o campo fica vazio ao recarregar.

---

## Hipóteses

| Id  | Hipótese | Como verificar |
|-----|----------|----------------|
| H1  | O código ainda usa `.maybe_single()` em algum lugar (não foi trocado ou há outro call site). | Buscar no projeto frontend por `maybe_single` e trocar por `maybeSingle`. |
| H2  | A troca foi feita mas o app em execução é build antigo (cache ou servidor não recarregou). | Salvar o arquivo, recarregar o dev server (npm run dev) e dar F5 na página. |
| H3  | Existe mais de um arquivo que chama `prompt_config` (ex.: outro componente) e só um foi corrigido. | Buscar em todo o frontend por `prompt_config` e por `maybe_single`. |

---

## Correção obrigatória (frontend)

1. Abra o projeto do **frontend** (onde está `PromptEditor.jsx`).
2. Busque em **todos** os arquivos por: `maybe_single`
3. Substitua **todas** as ocorrências por: `maybeSingle` (camelCase).
4. Salve os arquivos.
5. Se usar dev server (Vite/React), reinicie ou garanta que a página recarregou (F5).
6. Recarregue a página do app (F5) e abra um projeto que já tem prompt salvo (ex.: "gastos").

---

## Trecho esperado no PromptEditor (carregar prompt)

A chamada ao Supabase deve ficar assim (camelCase):

```js
const { data, error } = await supabase
  .from('prompt_config')
  .select('prompt_text, updated_at, schema_json')
  .eq('projeto_id', projetoId)
  .maybeSingle();   // <- talvez no seu código esteja .maybe_single()
```

Se no seu arquivo estiver `.maybe_single()`, troque para `.maybeSingle()`.

---

## Depois de corrigir

Apague o log de debug (ou use o botão de limpar) e reproduza:

1. Abra o app, selecione o projeto "gastos" (ou outro que já tem prompt salvo).
2. Recarregue a página (F5).
3. O campo do Editor de Prompt deve mostrar o texto salvo.

Se após a troca o erro sumir do console e o prompt ainda não aparecer, pode ser que `projetoId` esteja `null` no primeiro render — aí o próximo passo é garantir que o `useEffect` que chama o carregamento dependa de `projetoId` e que o App passe `projetoId={projetoAtivo?.id ?? null}`.
