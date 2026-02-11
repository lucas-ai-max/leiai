import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { supabase } from './supabaseClient'
import { Play, RefreshCw, CheckCircle, AlertCircle, Clock, ArrowLeft } from 'lucide-react'
import ResultsViewer from './ResultsViewer'
import * as XLSX from 'xlsx'

// Dedicated project ID for Salesforce imports (matches backend config)
const SALESFORCE_PROJECT_ID = '00000000-0000-0000-0000-000000000001'

// Helper function to flatten nested JSON for Excel export
function flattenObject(obj, prefix = '') {
    const result = {}

    for (const [key, value] of Object.entries(obj)) {
        const newKey = prefix ? `${prefix}_${key}` : key

        if (value === null || value === undefined) {
            result[newKey] = ''
        } else if (Array.isArray(value)) {
            result[newKey] = value.join(', ')
        } else if (typeof value === 'object' && value !== null) {
            Object.assign(result, flattenObject(value, newKey))
        } else {
            result[newKey] = value
        }
    }

    return result
}

export default function SalesforceImport() {
    const navigate = useNavigate()
    const [cases, setCases] = useState([])
    const [inputCases, setInputCases] = useState('')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)
    const [stats, setStats] = useState({ total: 0, completed: 0, errors: 0, processing: 0 })

    useEffect(() => {
        fetchCases()
        const interval = setInterval(fetchCases, 5000)
        return () => clearInterval(interval)
    }, [])

    async function fetchCases() {
        try {
            const { data, error } = await supabase
                .from('casos_processamento')
                .select('*')
                .eq('projeto_id', SALESFORCE_PROJECT_ID)
                .order('created_at', { ascending: false })
                .limit(100)

            if (error) throw error

            setCases(data || [])

            // Calculate stats
            const s = { total: data.length, completed: 0, errors: 0, processing: 0 }
            data.forEach(c => {
                if (c.status === 'CONCLUIDO') s.completed++
                else if (c.status === 'ERRO') s.errors++
                else s.processing++
            })
            setStats(s)

        } catch (err) {
            console.error(err)
        }
    }

    async function handleImport() {
        if (!inputCases.trim()) return

        setLoading(true)
        setError(null)

        try {
            // Fix: split by newline OR comma to handle pasted lists correctly
            const caseList = inputCases.split(/[\n,]+/)
                .map(c => c.trim())
                .filter(c => c.length > 0)

            if (caseList.length === 0) return

            const rows = caseList.map(num => ({
                numero_caso: num,
                status: 'PENDENTE',
                projeto_id: SALESFORCE_PROJECT_ID
            }))

            const { error } = await supabase
                .from('casos_processamento')
                .upsert(rows, { onConflict: 'numero_caso', ignoreDuplicates: true })

            if (error) throw error

            setInputCases('') // Clear input
            fetchCases() // Refresh
            alert(`${caseList.length} casos enviados para a fila!`)

        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    async function handleExportExcel() {
        try {
            // Fetch all analysis results for this project
            const { data, error } = await supabase
                .from('resultados_analise')
                .select('*')
                .eq('projeto_id', SALESFORCE_PROJECT_ID)
                .order('data_processamento', { ascending: false })

            if (error) throw error

            if (!data || data.length === 0) {
                alert('Nenhum resultado para exportar')
                return
            }

            // Flatten and prepare data for Excel
            const flatData = data.map(result => ({
                arquivo_original: result.arquivo_original || '',
                data_processamento: result.data_processamento
                    ? new Date(result.data_processamento).toLocaleString('pt-BR')
                    : '',
                ...flattenObject(result.dados_json || {})
            }))

            // Create workbook and worksheet
            const worksheet = XLSX.utils.json_to_sheet(flatData)
            const workbook = XLSX.utils.book_new()
            XLSX.utils.book_append_sheet(workbook, worksheet, 'Resultados')

            // Auto-size columns
            const maxWidth = 50
            const cols = Object.keys(flatData[0] || {}).map(key => ({
                wch: Math.min(
                    Math.max(
                        key.length,
                        ...flatData.map(row => String(row[key] || '').length)
                    ),
                    maxWidth
                )
            }))
            worksheet['!cols'] = cols

            // Generate filename with current date
            const timestamp = new Date().toISOString().split('T')[0]
            const filename = `salesforce_analises_${timestamp}.xlsx`

            // Download file
            XLSX.writeFile(workbook, filename)

            console.log(`✅ Exportados ${data.length} resultados para ${filename}`)

        } catch (err) {
            console.error('Erro ao exportar:', err)
            alert(`Erro ao exportar: ${err.message}`)
        }
    }

    return (
        <div className="max-w-7xl mx-auto p-8 space-y-8 min-h-screen bg-slate-50">
            <header className="mb-6">
                <h1 className="text-3xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
                    <button onClick={() => navigate('/')} className="p-2 -ml-2 hover:bg-slate-100 rounded-full text-slate-500 hover:text-slate-900 transition-colors" title="Voltar ao Menu">
                        <ArrowLeft className="h-6 w-6" />
                    </button>
                    ☁️ Importador Salesforce
                </h1>
                <p className="text-slate-600">
                    Cole os números dos casos (separados por vírgula ou linha) para buscar ZIPs e processar formulários.
                </p>
            </header>

            {/* Input Area */}
            <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
                <label className="block text-sm font-medium text-slate-700 mb-2">
                    Números dos Casos
                </label>
                <textarea
                    value={inputCases}
                    onChange={(e) => setInputCases(e.target.value)}
                    placeholder="Ex: 
20260129282070
20251230281701"
                    className="w-full h-32 p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-mono text-sm leading-relaxed"
                />
                <div className="mt-4 flex items-center justify-between">
                    <p className="text-xs text-slate-500">
                        Separe por vírgula ou quebra de linha. Duplicatas são ignoradas.
                    </p>
                    <button
                        onClick={handleImport}
                        disabled={loading || !inputCases.trim()}
                        className="flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium transition-colors"
                    >
                        {loading ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
                        {loading ? 'Enviando...' : 'Iniciar Importação'}
                    </button>
                </div>
                {error && <p className="mt-2 text-sm text-red-600 bg-red-50 p-2 rounded">{error}</p>}
            </div>

            {/* Stats */}
            <div className="grid grid-cols-4 gap-4">
                <div className="bg-slate-50 p-4 rounded-lg border border-slate-200">
                    <div className="text-2xl font-bold text-slate-800">{stats.total}</div>
                    <div className="text-xs text-slate-500 uppercase font-semibold">Total Recente</div>
                </div>
                <div className="bg-blue-50 p-4 rounded-lg border border-blue-100">
                    <div className="text-2xl font-bold text-blue-800">{stats.processing}</div>
                    <div className="text-xs text-blue-600 uppercase font-semibold">Processando</div>
                </div>
                <div className="bg-green-50 p-4 rounded-lg border border-green-100">
                    <div className="text-2xl font-bold text-green-800">{stats.completed}</div>
                    <div className="text-xs text-green-600 uppercase font-semibold">Concluídos</div>
                </div>
                <div className="bg-red-50 p-4 rounded-lg border border-red-100">
                    <div className="text-2xl font-bold text-red-800">{stats.errors}</div>
                    <div className="text-xs text-red-600 uppercase font-semibold">Erros</div>
                </div>
            </div>

            {/* Table History */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
                <div className="px-6 py-4 border-b border-slate-200 bg-slate-50 flex justify-between items-center">
                    <h2 className="font-bold text-slate-800">Histórico de Importação</h2>
                    <button onClick={fetchCases} className="p-2 hover:bg-slate-200 rounded-full text-slate-500 transition-colors">
                        <RefreshCw className="h-4 w-4" />
                    </button>
                </div>
                <div className="overflow-x-auto max-h-60">
                    <table className="min-w-full divide-y divide-slate-200">
                        <thead className="bg-slate-50 sticky top-0">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">Caso</th>
                                <th className="px-6 py-3 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">Status</th>
                                <th className="px-6 py-3 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">Info</th>
                                <th className="px-6 py-3 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">Atualizado</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-slate-200">
                            {cases.length === 0 && (
                                <tr><td colSpan="4" className="px-6 py-8 text-center text-slate-500">Nenhum caso importado recentemente.</td></tr>
                            )}
                            {cases.map((c) => (
                                <tr key={c.id} className="hover:bg-slate-50">
                                    <td className="px-6 py-4 font-mono text-sm font-medium text-slate-900">{c.numero_caso}</td>
                                    <td className="px-6 py-4">
                                        <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium
                        ${c.status === 'CONCLUIDO' ? 'bg-green-100 text-green-800' :
                                                c.status === 'ERRO' ? 'bg-red-100 text-red-800' :
                                                    'bg-blue-100 text-blue-800'}`}>
                                            {c.status === 'CONCLUIDO' && <CheckCircle size={12} />}
                                            {c.status === 'ERRO' && <AlertCircle size={12} />}
                                            {(c.status === 'PENDENTE' || c.status === 'BAIXANDO') && <Clock size={12} className="animate-spin" />}
                                            {c.status}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 text-xs text-slate-500 max-w-xs truncate" title={c.error_message || c.zip_url}>
                                        {c.error_message ? <span className="text-red-600">{c.error_message}</span> : (c.zip_url ? 'URL obtida' : '-')}
                                    </td>
                                    <td className="px-6 py-4 text-xs text-slate-500">
                                        {new Date(c.updated_at).toLocaleTimeString('pt-BR')}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Results Section Using Shared Component with Details Modal */}
            <div className="mt-8">
                <ResultsViewer
                    projetoId={SALESFORCE_PROJECT_ID}
                    onExportExcel={handleExportExcel}
                />
            </div>
        </div>
    )
}
