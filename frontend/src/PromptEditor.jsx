import { useState, useEffect } from 'react'
import { supabase } from './supabaseClient'
import { FileText, Save, Eye, EyeOff, Download, Sparkles, Loader2, Lock, CheckCircle, AlertCircle, RotateCcw } from 'lucide-react'
import { generateSchema, buildFullPrompt } from './api/schemaGenerator'

const PROMPT_TABLE = 'prompt_config'
const DEFAULT_PROMPT = `Analise o documento jurídico e extraia estas informações em JSON:

{
  "numero_processo": "Número do processo",
  "tipo_documento": "Tipo do documento",
  "partes": "Partes envolvidas",
  "juiz": "Nome do juiz",
  "data_decisao": "Data da decisão",
  "resultado": "Resultado da decisão",
  "resumo": "Resumo breve"
}

Retorne APENAS o JSON válido, sem texto adicional.`

function PromptEditor({ projetoId, onPromptSaved, readOnly = false, onLock }) {
  const [prompt, setPrompt] = useState(DEFAULT_PROMPT)
  const [isSaving, setIsSaving] = useState(false)
  const [isExpanded, setIsExpanded] = useState(true)
  const [lastSaved, setLastSaved] = useState(null)
  const [userInput, setUserInput] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedSchema, setGeneratedSchema] = useState(null)

  useEffect(() => {
    // Se estiver bloqueado (readOnly), forçar o recolhimento
    if (readOnly) {
      setIsExpanded(false)
    } else {
      // Se estiver editável, restaurar estado padrão (expandido se tiver dados ou novo)
      setIsExpanded(true)
    }
  }, [readOnly])

  useEffect(() => {
    loadPrompt()
  }, [projetoId])


  // Função para tentar reconstruir o schema visual a partir do texto do prompt salvo
  function tryParseSchemaFromPrompt(text) {
    try {
      // Procura pelo bloco JSON no texto
      const jsonMatch = text.match(/\{[\s\S]*?\}/)
      if (jsonMatch) {
        const jsonStr = jsonMatch[0]
        const schemaObj = JSON.parse(jsonStr)
        // Verificar se parece um schema válido (chaves e strings)
        if (Object.keys(schemaObj).length > 0) {
          setGeneratedSchema(schemaObj)
        }
      }
    } catch (e) {
      // Silenciosamente falha se não conseguir parsear, apenas não mostra a tabela visual
      console.log('Não foi possível reconstruir o schema visual do prompt salvo.')
    }
  }

  async function loadPrompt() {
    if (!supabase) return
    if (!projetoId) {
      setPrompt(DEFAULT_PROMPT)
      setLastSaved(null)
      return
    }

    try {
      const { data, error } = await supabase
        .from(PROMPT_TABLE)
        .select('prompt_text, updated_at')
        .eq('projeto_id', projetoId)
        .maybeSingle()

      if (error) {



        if (error.message && error.message.includes('schema cache')) {
          console.warn(`⚠️ Tabela '${PROMPT_TABLE}' não existe. Execute create_prompt_table_fixed.sql no Supabase.`)
        }
        setPrompt(DEFAULT_PROMPT)
        setLastSaved(null)
        setIsExpanded(true)
        return
      }

      if (data && data.prompt_text) {
        setPrompt(data.prompt_text)
        setLastSaved(new Date(data.updated_at))
        tryParseSchemaFromPrompt(data.prompt_text) // Tenta reconstruir a visualização
        // Estado de expansão agora é controlado pelo useEffect(readOnly)
      } else {
        // Se não houver prompt salvo, usar padrão
        setPrompt(DEFAULT_PROMPT)
        setLastSaved(null)
        // Estado de expansão agora é controlado pelo useEffect(readOnly)
      }
    } catch (error) {
      console.error('Erro detalhado ao carregar prompt:', error)

      console.log('Usando prompt padrão (tabela não existe ou está vazia). Erro:', error.message)
      // Usar prompt padrão se a tabela não existir
    }
  }

  async function savePrompt() {
    if (!supabase) {
      alert('Supabase não configurado')
      return
    }
    if (!projetoId) {
      alert('Selecione um projeto para salvar o prompt.')
      return
    }

    setIsSaving(true)
    console.log('Saving prompt...', { projetoId, prompt, length: prompt.length })

    try {
      const { data, error } = await supabase
        .from(PROMPT_TABLE)
        .upsert({
          projeto_id: projetoId,
          prompt_text: prompt,
          updated_at: new Date().toISOString()
        }, { onConflict: 'projeto_id' })
        .select()

      console.log('Save result:', { data, error })

      if (!error && (!data || data.length === 0)) {
        console.warn('Salvo com sucesso aparentente, mas nenhum dado retornado. RLS pode estar bloqueando.')
        alert('Aviso: O banco de dados parece ter bloqueado a gravação (possível erro de permissão RLS). Verifique o console.')
      }

      if (error) {
        console.error('Supabase error:', error)
        // Verificar se é erro de tabela não encontrada
        if (error.message && error.message.includes('schema cache')) {
          throw new Error(`Tabela '${PROMPT_TABLE}' não existe no Supabase. Execute o script SQL: create_prompt_table_fixed.sql no SQL Editor do Supabase.`)
        }
        throw error
      }

      const savedAt = new Date()
      setLastSaved(savedAt)
      onPromptSaved?.(savedAt)
      alert('✅ Prompt salvo com sucesso!')
    } catch (error) {
      console.error('Erro ao salvar prompt:', error)
      alert(`Erro ao salvar: ${error.message}`)
    } finally {
      setIsSaving(false)
    }
  }

  function downloadPrompt() {
    const blob = new Blob([prompt], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'prompt_custom.txt'
    a.click()
    URL.revokeObjectURL(url)
  }

  async function handleGenerateSchema() {
    if (!userInput.trim()) {
      alert('Digite o que você quer extrair dos documentos')
      return
    }

    setIsGenerating(true)
    try {
      // Pegar API key do .env
      const apiKey = import.meta.env.VITE_GOOGLE_API_KEY || 'AIzaSyDLYk5POIL5uRGC7Yf8I7oak-j2EkDGu5I'

      // Gerar schema com IA
      const schema = await generateSchema(userInput, apiKey)
      setGeneratedSchema(schema)

      // Gerar prompt completo
      const fullPrompt = buildFullPrompt(userInput, schema)
      setPrompt(fullPrompt)

      alert('✅ Estrutura gerada com sucesso! Revise e salve o prompt.')
    } catch (error) {
      alert(`Erro ao gerar estrutura: ${error.message}`)
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <div className="bg-white rounded-xl shadow-lg border border-slate-200 overflow-hidden mb-10">
      {/* Header */}
      <div
        className="px-6 py-4 bg-gradient-to-r from-blue-50 to-indigo-50 border-b border-slate-200 flex justify-between items-center cursor-pointer hover:bg-blue-100 transition-colors"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-3">
          <FileText className="h-5 w-5 text-blue-600" />
          <div>
            <h3 className="font-bold text-slate-900 text-lg">Editor de Prompt</h3>
            <p className="text-xs text-slate-600">
              {isExpanded ? 'Clique para ocultar' : lastSaved ? `Prompt salvo em ${lastSaved.toLocaleString('pt-BR')} • Clique para editar` : 'Clique para editar o prompt de análise'}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {lastSaved && (
            <span className="text-xs text-slate-500">
              Último salvamento: {lastSaved.toLocaleString('pt-BR')}
            </span>
          )}
          {isExpanded ? (
            <EyeOff className="h-5 w-5 text-slate-400" />
          ) : (
            <Eye className="h-5 w-5 text-slate-400" />
          )}
        </div>
      </div>

      {/* Editor (Expandível) */}
      {isExpanded && (
        <div className="p-6">
          {/* Gerador Automático com IA */}
          <div className="mb-6 p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg border border-purple-200">
            <div className="flex items-start gap-3 mb-3">
              <Sparkles className="h-5 w-5 text-purple-600 flex-shrink-0 mt-1" />
              <div className="flex-1">
                <h4 className="font-semibold text-slate-900 mb-1">Gerar Estrutura com IA</h4>
                <p className="text-xs text-slate-600 mb-3">
                  Descreva em linguagem natural o que você quer extrair e a IA criará a estrutura JSON automaticamente
                </p>

                <textarea
                  value={userInput}
                  onChange={(e) => setUserInput(e.target.value)}
                  className="w-full h-24 px-3 py-2 border border-purple-200 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-sm resize-none mb-3"
                  placeholder='Exemplo: "Quero extrair o número do processo, nome das partes, valor da causa, resultado da decisão e fundamentação legal"'
                />

                <button
                  onClick={handleGenerateSchema}
                  disabled={isGenerating || !userInput.trim()}
                  className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-slate-400 disabled:cursor-not-allowed transition-colors text-sm font-medium"
                >
                  {isGenerating ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Gerando estrutura...
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-4 w-4" />
                      Gerar Estrutura com IA
                    </>
                  )}
                </button>

                {generatedSchema && (
                  <div className="mt-3 p-3 bg-white rounded border border-purple-200">
                    <p className="text-xs font-medium text-purple-900 mb-3">✨ Colunas que serão extraídas:</p>
                    <div className="overflow-x-auto">
                      <table className="w-full text-xs border-collapse">
                        <thead>
                          <tr className="bg-purple-50">
                            <th className="border border-purple-200 px-3 py-2 text-left font-semibold text-purple-900">Coluna</th>
                            <th className="border border-purple-200 px-3 py-2 text-left font-semibold text-purple-900">Descrição</th>
                          </tr>
                        </thead>
                        <tbody>
                          {Object.entries(generatedSchema).map(([coluna, descricao], idx) => (
                            <tr key={idx} className={idx % 2 === 0 ? 'bg-white' : 'bg-slate-50'}>
                              <td className="border border-purple-200 px-3 py-2 font-mono font-medium text-slate-800">
                                {coluna}
                              </td>
                              <td className="border border-purple-200 px-3 py-2 text-slate-600">
                                {descricao}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                    <p className="text-xs text-slate-500 mt-2">
                      💡 Estas colunas aparecerão no CSV exportado
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Botões */}
          {/* Botões */}
          <div className="flex gap-3 mt-4">
            {readOnly ? (
              <div className="flex items-center gap-2 px-4 py-2 bg-slate-100 text-slate-500 rounded-lg border border-slate-200 cursor-not-allowed select-none w-full justify-center">
                <Lock className="h-4 w-4" />
                <span className="text-sm font-medium">Prompt Bloqueado - Pr pronto para processamento</span>
              </div>
            ) : (
              <>
                <button
                  onClick={savePrompt}
                  disabled={isSaving}
                  className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-slate-400 disabled:cursor-not-allowed transition-colors"
                >
                  <Save className="h-4 w-4" />
                  {isSaving ? 'Salvando...' : 'Salvar Prompt'}
                </button>

                {onLock && lastSaved && (
                  <button
                    onClick={onLock}
                    className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors shadow-sm ml-auto"
                    title="Finalizar configuração e liberar upload"
                  >
                    <CheckCircle className="h-4 w-4" />
                    Confirmar & Liberar Upload
                  </button>
                )}

                <button
                  onClick={downloadPrompt}
                  className="flex items-center gap-2 px-4 py-2 bg-slate-600 text-white rounded-lg hover:bg-slate-700 transition-colors"
                >
                  <Download className="h-4 w-4" />
                  Baixar
                </button>

                <button
                  onClick={() => setPrompt(DEFAULT_PROMPT)}
                  className="flex items-center gap-2 px-4 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors"
                >
                  <RotateCcw className="h-4 w-4" />
                  Restaurar
                </button>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default PromptEditor
