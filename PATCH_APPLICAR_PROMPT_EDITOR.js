/**
 * PATCH PARA PromptEditor.jsx
 *
 * O arquivo PromptEditor.jsx NÃO está neste workspace (só o backend processia).
 * Aplique manualmente no seu projeto frontend:
 *
 * COMO APLICAR:
 * 1. Abra o projeto do frontend (onde está PromptEditor.jsx).
 * 2. Busque por "maybe_single" e substitua TODAS por "maybeSingle".
 * 3. Localize a função que carrega o prompt (em torno da linha 71; ex.: loadPrompt ou o corpo do useEffect).
 * 4. Substitua a lógica de carregamento pela que está abaixo (ajuste nomes: projetoId, setPromptText, setSchema, setSavedAt, supabase conforme o seu componente).
 * 5. Garanta que o useEffect que chama o carregamento tenha [projetoId] nas dependências.
 */

// ========== SUBSTITUIR a função que carrega o prompt (loadPrompt ou o useEffect que busca) ==========

async function loadPrompt() {
  // #region agent log
  // fetch('http://127.0.0.1:7244/ingest/...', { method: 'POST', ... }).catch(() => {});
  // #endregion
  if (!projetoId) {
    setPromptText('');
    setSchema([]);
    setSavedAt(null);
    return;
  }
  try {
    const { data, error } = await supabase
      .from('prompt_config')
      .select('prompt_text, updated_at, schema_json')
      .eq('projeto_id', projetoId)
      .maybeSingle();  // <- camelCase (nunca maybe_single)

    if (error) {
      console.error('Erro ao carregar prompt:', error);
      setPromptText('');
      setSchema([]);
      setSavedAt(null);
      return;
    }

    // Projeto sem prompt salvo = campo vazio (não usar "prompt padrão" no editor)
    if (!data) {
      setPromptText('');
      setSchema([]);
      setSavedAt(null);
      return;
    }

    setPromptText(data.prompt_text ?? '');
    setSchema(data.schema_json ?? []);
    setSavedAt(data.updated_at ? new Date(data.updated_at).toLocaleString('pt-BR') : null);
  } catch (e) {
    console.error('Exception loading prompt', e);
    setPromptText('');
    setSchema([]);
    setSavedAt(null);
  }
}

// ========== Dependência do useEffect ==========
// Garantir que o useEffect que chama loadPrompt dependa de projetoId:
//   useEffect(() => { loadPrompt(); }, [projetoId]);
