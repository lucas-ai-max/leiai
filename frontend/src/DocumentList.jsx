import { useState, useEffect } from 'react'
import { supabase } from './supabaseClient'
import { Upload, FileText, Trash2, Play, CheckCircle, AlertCircle, Loader2, Download, Search } from 'lucide-react'

export default function DocumentList({ projetoId }) {
    const [docs, setDocs] = useState([])
    const [loading, setLoading] = useState(false)
    const [uploading, setUploading] = useState(false)
    const [dragActive, setDragActive] = useState(false)

    useEffect(() => {
        if (projetoId) fetchDocs()
    }, [projetoId])

    async function fetchDocs() {
        setLoading(true)
        try {
            const { data, error } = await supabase
                .from('documento_gerenciamento')
                .select('*')
                .eq('projeto_id', projetoId)
                .order('created_at', { ascending: false })

            if (error) throw error
            setDocs(data || [])
        } catch (error) {
            console.error('Erro ao buscar documentos:', error)
        } finally {
            setLoading(false)
        }
    }

    async function handleFileUpload(files) {
        if (!files || files.length === 0) return
        setUploading(true)

        try {
            const uploads = Array.from(files).map(async (file) => {
                const fileExt = file.name.split('.').pop()
                const fileName = `${Math.random().toString(36).substring(2)}.${fileExt}`
                const filePath = `${projetoId}/${fileName}`

                // 1. Upload Storage
                const { error: storageError } = await supabase.storage
                    .from('processos')
                    .upload(filePath, file)

                if (storageError) throw storageError

                // 2. Insert DB
                const { error: dbError } = await supabase
                    .from('documento_gerenciamento')
                    .insert({
                        projeto_id: projetoId,
                        filename: file.name,
                        storage_path: filePath,
                        status: 'PENDENTE',
                        tamanho_bytes: file.size
                    })

                if (dbError) throw dbError
            })

            await Promise.all(uploads)
            fetchDocs()
        } catch (error) {
            console.error('Erro no upload COMPLETO:', JSON.stringify(error, null, 2))
            console.error('Erro detalhes:', error)
            alert(`Erro ao fazer upload: ${error.message || 'Erro desconhecido'} \nDetalhes: ${error.details || ''} \nDica: ${error.hint || ''}`)
        } finally {
            setUploading(false)
        }
    }

    async function processarDoc(docId) {
        try {
            // Marca como PROCESSANDO para o worker pegar (ou dispara chamada de API)
            // Se o worker python roda em polling, basta mudar status
            // Se usa Edge Function, chamaria aqui.
            // Assumindo worker polling:
            /*
            await supabase
                .from('documento_gerenciamento')
                .update({ status: 'PROCESSANDO' }) // Na vdd o worker pega PENDENTE
                .eq('id', docId)

            // Na arquitetura atual, o worker Python monitora a tabela?
            // Se sim, ele pega 'PENDENTE'. Se já está PENDENTE, talvez precise forçar reprocessamento?
            // Mas o upload já deixa em PENDENTE.
            */
            alert('Documento na fila de processamento!')
            // TODO: Se o worker Python precisa de gatilho manual, implementar aqui.
            // Por enquanto, documentos PENDENTES são processados automaticamente pelo worker.
        } catch (error) {
            console.error(error)
        }
    }

    async function downloadDoc(caminho, nome) {
        try {
            const { data, error } = await supabase.storage
                .from('processos')
                .download(caminho)
            if (error) throw error

            const url = URL.createObjectURL(data)
            const a = document.createElement('a')
            a.href = url
            a.download = nome
            a.click()
            URL.revokeObjectURL(url)
        } catch (error) {
            console.error('Erro download:', error)
            alert('Erro ao baixar arquivo.')
        }
    }

    async function deleteDoc(id, caminho) {
        if (!confirm('Tem certeza?')) return
        try {
            if (caminho) {
                await supabase.storage.from('processos').remove([caminho])
            }
            await supabase.from('documento_gerenciamento').delete().eq('id', id)
            fetchDocs()
        } catch (error) {
            console.error('Erro delete:', error)
        }
    }

    // Drag & Drop handlers
    const handleDrag = (e) => {
        e.preventDefault()
        e.stopPropagation()
        if (e.type === "dragenter" || e.type === "dragover") setDragActive(true)
        else if (e.type === "dragleave") setDragActive(false)
    }
    const handleDrop = (e) => {
        e.preventDefault()
        e.stopPropagation()
        setDragActive(false)
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFileUpload(e.dataTransfer.files)
        }
    }

    async function triggerProcess() {
        try {
            const { error } = await supabase
                .from('processar_agora')
                .insert({ projeto_id: projetoId })

            if (error) throw error
            alert('Processamento iniciado! O worker irá pegar os arquivos em breve.')
            fetchDocs() // Atualizar status visualmente (ficará PENDENTE até o worker rodar)
        } catch (error) {
            console.error('Erro ao iniciar:', error)
            alert('Erro ao iniciar processamento.')
        }
    }

    return (
        <div className="bg-white rounded-xl shadow-lg border border-slate-200 overflow-hidden">
            <div className="px-6 py-4 bg-slate-50 border-b border-slate-200 flex justify-between items-center">
                <h3 className="font-bold text-slate-900 flex items-center gap-2">
                    <FileText className="h-5 w-5 text-blue-600" />
                    Documentos do Projeto
                </h3>
                <div className="flex gap-2 items-center">
                    <span className="text-xs text-slate-500 font-mono bg-slate-200 px-2 py-1 rounded">
                        {docs.length} arquivo{docs.length !== 1 && 's'}
                    </span>
                    <button
                        onClick={triggerProcess}
                        className="flex items-center gap-2 px-3 py-1.5 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 text-xs font-bold transition-colors shadow-sm"
                    >
                        <Play size={14} />
                        Processar Fila
                    </button>
                </div>
            </div>

            {/* Upload Area */}
            <div
                className={`p-8 border-b border-slate-200 transition-colors text-center cursor-pointer
                    ${dragActive ? 'bg-blue-50 border-blue-300' : 'bg-white hover:bg-slate-50'}
                    ${uploading ? 'opacity-50 pointer-events-none' : ''}
                `}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                onClick={() => document.getElementById('file-upload').click()}
            >
                <input
                    type="file"
                    id="file-upload"
                    multiple
                    className="hidden"
                    onChange={(e) => handleFileUpload(e.target.files)}
                    accept=".pdf,.doc,.docx,.txt"
                />

                {uploading ? (
                    <div className="flex flex-col items-center gap-3">
                        <Loader2 className="h-8 w-8 text-blue-600 animate-spin" />
                        <span className="text-sm font-medium text-slate-600">Enviando arquivos...</span>
                    </div>
                ) : (
                    <div className="flex flex-col items-center gap-3">
                        <div className="p-3 bg-blue-100 text-blue-600 rounded-full">
                            <Upload className="h-6 w-6" />
                        </div>
                        <div>
                            <p className="text-sm font-medium text-slate-900">
                                Clique para selecionar ou arraste arquivos aqui
                            </p>
                            <p className="text-xs text-slate-500 mt-1">
                                PDF, Word ou Texto (Máx 50MB)
                            </p>
                        </div>
                    </div>
                )}
            </div>

            {/* List */}
            <div className="overflow-x-auto max-h-[500px]">
                {loading ? (
                    <div className="p-8 text-center text-slate-400">
                        <Loader2 className="h-6 w-6 animate-spin mx-auto mb-2" />
                        Carregando...
                    </div>
                ) : docs.length === 0 ? (
                    <div className="p-12 text-center text-slate-400">
                        <p>Nenhum documento ainda.</p>
                    </div>
                ) : (
                    <table className="min-w-full divide-y divide-slate-200">
                        <thead className="bg-slate-50 sticky top-0">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">Nome</th>
                                <th className="px-6 py-3 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">Status</th>
                                <th className="px-6 py-3 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">Data</th>
                                <th className="px-6 py-3 text-right text-xs font-bold text-slate-500 uppercase tracking-wider">Ações</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-slate-200">
                            {docs.map((doc) => (
                                <tr key={doc.id} className="hover:bg-slate-50">
                                    <td className="px-6 py-4">
                                        <div className="flex items-center gap-3">
                                            <FileText className="h-4 w-4 text-slate-400" />
                                            <span className="text-sm font-medium text-slate-900 truncate max-w-xs" title={doc.filename}>
                                                {doc.filename}
                                            </span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium
                                            ${doc.status === 'CONCLUIDO' ? 'bg-green-100 text-green-800' :
                                                doc.status === 'ERRO' ? 'bg-red-100 text-red-800' :
                                                    'bg-blue-100 text-blue-800'}`}>
                                            {doc.status === 'CONCLUIDO' && <CheckCircle size={12} />}
                                            {doc.status === 'ERRO' && <AlertCircle size={12} />}
                                            {(doc.status === 'PENDENTE' || doc.status === 'PROCESSANDO') && <Loader2 size={12} className="animate-spin" />}
                                            {doc.status}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 text-xs text-slate-500">
                                        {new Date(doc.created_at).toLocaleDateString('pt-BR')}
                                    </td>
                                    <td className="px-6 py-4 text-right flex items-center justify-end gap-2">
                                        <button
                                            onClick={() => downloadDoc(doc.storage_path, doc.filename)}
                                            className="p-1.5 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors"
                                            title="Baixar"
                                        >
                                            <Download size={16} />
                                        </button>
                                        <button
                                            onClick={() => deleteDoc(doc.id, doc.storage_path)}
                                            className="p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
                                            title="Excluir"
                                        >
                                            <Trash2 size={16} />
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    )
}
