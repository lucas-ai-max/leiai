# Onde está o PromptEditor (frontend)

O **PromptEditor.jsx** não fica neste repositório (**processia**). Ele fica no projeto do **frontend**, em outra pasta.

## Caminho do frontend

De acordo com o **SETUP_COMPLETO.md**, o frontend fica em:

```
E:\Projetos Cursor\frontend-processia
```

Ou seja: pasta **frontend-processia**, no mesmo nível que **ProcessIA** (não dentro de processia).

## Onde deve estar o PromptEditor

Dentro de **frontend-processia**, o arquivo costuma estar em um destes caminhos:

- `src/components/PromptEditor.jsx`
- `src/PromptEditor.jsx`
- `components/PromptEditor.jsx`

## Como abrir no Cursor

1. **Abrir a pasta do frontend no Cursor**
   - Menu **File → Open Folder** (ou **Arquivo → Abrir Pasta**)
   - Navegue até: `E:\Projetos Cursor\frontend-processia`
   - Abra essa pasta

2. **Ou adicionar ao workspace**
   - **File → Add Folder to Workspace**
   - Selecione a pasta `frontend-processia`
   - Assim você terá processia + frontend-processia no mesmo workspace

3. **Procurar o arquivo**
   - Com a pasta **frontend-processia** aberta, use a busca do Cursor (Ctrl+P) e digite: `PromptEditor`
   - Ou no explorador de arquivos, procure por **PromptEditor.jsx** dentro de **src** ou **components**

## Depois de encontrar o PromptEditor.jsx

1. Abra o arquivo **PromptEditor.jsx**.
2. Use o conteúdo do arquivo **PromptEditor_loadPrompt_snippet.jsx** (que está dentro de **processia**) para substituir o `useEffect` que carrega o prompt.
3. Troque **todas** as ocorrências de **`.maybe_single()`** por **`.maybeSingle()`** no arquivo.

Os arquivos **PATCH_APPLICAR_PROMPT_EDITOR.js** e **PromptEditor_loadPrompt_snippet.jsx** estão na pasta **processia** (este repositório) para você consultar ou copiar.
