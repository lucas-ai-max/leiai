// Cole este trecho no PromptEditor.jsx:
// 1. Substitua a função que carrega o prompt (loadPrompt ou o corpo do useEffect) por este bloco.
// 2. Troque .maybe_single() por .maybeSingle() em todo o arquivo.
// 3. useEffect que chama loadPrompt deve ter [projetoId] nas dependências.

useEffect(() => {
  if (!projetoId) {
    setPromptText('');
    setSchema([]);
    setSavedAt(null);
    return;
  }
  (async () => {
    try {
      const { data, error } = await supabase
        .from('prompt_config')
        .select('prompt_text, updated_at, schema_json')
        .eq('projeto_id', projetoId)
        .maybeSingle();

      if (error) {
        console.error('Erro ao carregar prompt:', error);
        setPromptText('');
        setSchema([]);
        setSavedAt(null);
        return;
      }

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
  })();
}, [projetoId]);
