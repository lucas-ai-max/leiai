import { useState, useEffect } from 'react'
import { supabase } from './supabaseClient'
import { Plus, Folder, Trash2, Edit2, Check, X, LogOut, LayoutDashboard, Database, Settings, ArrowRight } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

export default function ProjectManager({ onSelectProject }) {
    const navigate = useNavigate()
    const [projetos, setProjetos] = useState([])
    const [novoProjeto, setNovoProjeto] = useState('')
    const [editando, setEditando] = useState(null)
    const [novoNome, setNovoNome] = useState('')
    const [projetoAtivo, setProjetoAtivo] = useState(null)
    const [loading, setLoading] = useState(true)

    // Dedicated project ID for Salesforce (to verify filtering)
    const SALESFORCE_PROJECT_ID = '00000000-0000-0000-0000-000000000001'

    useEffect(() => {
        fetchProjetos()
    }, [])

    async function fetchProjetos() {
        try {
            const { data, error } = await supabase
                .from('projeto')
                .select('id, nome, created_at')
                .order('created_at', { ascending: false })
            if (error) throw error
            // Filter out Salesforce Project
            const list = (data || []).filter(p => p.id !== SALESFORCE_PROJECT_ID)
            setProjetos(list)

            // Auto-select first project if none active
            setProjetoAtivo(prev => {
                if (list.length === 0) return null
                if (prev && list.find(p => p.id === prev.id)) return prev
                return list[0]
            })

            // Notify parent about initial selection
            if (list.length > 0 && onSelectProject) {
                // We delay slightly to ensure state is settled
                setTimeout(() => onSelectProject(list[0]), 0)
            }
        } catch (error) {
            console.error('Erro ao buscar projetos:', error)
        } finally {
            setLoading(false)
        }
    }

    async function criarProjeto() {
        if (!novoProjeto.trim()) return
        try {
            const { data, error } = await supabase
                .from('projeto')
                .insert([{ nome: novoProjeto.trim() }])
                .select()
            if (error) throw error
            setNovoProjeto('')
            fetchProjetos()
        } catch (error) {
            console.error('Erro ao criar projeto:', error)
            alert('Erro ao criar projeto')
        }
    }

    async function excluirProjeto(id) {
        if (!confirm('Tem certeza? Isso apagará todos os documentos associados.')) return
        try {
            const { error } = await supabase
                .from('projeto')
                .delete()
                .eq('id', id)
            if (error) throw error
            if (projetoAtivo?.id === id) setProjetoAtivo(null)
            fetchProjetos()
        } catch (error) {
            console.error('Erro ao excluir projeto:', error)
            alert('Erro ao excluir projeto')
        }
    }

    async function atualizarProjeto(id) {
        if (!novoNome.trim()) return
        try {
            const { error } = await supabase
                .from('projeto')
                .update({ nome: novoNome.trim() })
                .eq('id', id)
            if (error) throw error
            setEditando(null)
            fetchProjetos()
        } catch (error) {
            console.error('Erro ao atualizar projeto:', error)
        }
    }

    function selecionarProjeto(proj) {
        setProjetoAtivo(proj)
        if (onSelectProject) onSelectProject(proj)
    }

    return (
        <div className="flex flex-col h-full bg-slate-50 border-r border-slate-200 w-80 flex-shrink-0">
            {/* Header */}
            <div className="p-4 bg-white border-b border-slate-200">
                <div className="flex items-center gap-2 mb-4 text-emerald-700">
                    <LayoutDashboard size={20} />
                    <h2 className="font-bold text-lg">ProcessIA</h2>
                </div>

                {/* Salesforce Button Highlighted */}
                <button
                    onClick={() => navigate('/salesforce')}
                    className="w-full mb-4 flex items-center gap-3 px-4 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl shadow-md hover:shadow-lg hover:from-blue-700 hover:to-indigo-700 transition-all group"
                >
                    <div className="bg-white/20 p-1.5 rounded-lg">
                        <Database size={18} className="text-white" />
                    </div>
                    <div className="text-left flex-1">
                        <span className="block text-xs font-medium text-blue-100 uppercase tracking-wider">Módulo</span>
                        <span className="block font-bold">Salesforce</span>
                    </div>
                    <ArrowRight size={16} className="opacity-0 group-hover:opacity-100 -translate-x-2 group-hover:translate-x-0 transition-all" />
                </button>

                <div className="flex gap-2">
                    <input
                        type="text"
                        value={novoProjeto}
                        onChange={(e) => setNovoProjeto(e.target.value)}
                        placeholder="Novo projeto..."
                        className="flex-1 px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
                        onKeyPress={(e) => e.key === 'Enter' && criarProjeto()}
                    />
                    <button
                        onClick={criarProjeto}
                        disabled={!novoProjeto.trim()}
                        className="p-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50 transition-colors"
                    >
                        <Plus size={18} />
                    </button>
                </div>
            </div>

            {/* List */}
            <div className="flex-1 overflow-y-auto p-3 space-y-2">
                <h3 className="px-2 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Meus Projetos</h3>

                {loading ? (
                    <div className="text-center py-8 text-slate-400">
                        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-emerald-500 mx-auto mb-2"></div>
                        Carregando...
                    </div>
                ) : projetos.length === 0 ? (
                    <div className="text-center py-8 text-slate-400 text-sm">
                        Nenhum projeto criado
                    </div>
                ) : (
                    projetos.map((proj) => (
                        <div
                            key={proj.id}
                            className={`group flex items-center justify-between p-3 rounded-xl cursor-pointer transition-all border ${projetoAtivo?.id === proj.id
                                ? 'bg-white border-emerald-500 shadow-sm ring-1 ring-emerald-500/20'
                                : 'bg-white border-transparent hover:border-slate-200 hover:shadow-sm text-slate-600'
                                }`}
                            onClick={() => selecionarProjeto(proj)}
                        >
                            <div className="flex items-center gap-3 flex-1 min-w-0">
                                <div className={`p-2 rounded-lg ${projetoAtivo?.id === proj.id ? 'bg-emerald-50 text-emerald-600' : 'bg-slate-100 text-slate-400 group-hover:bg-slate-50 group-hover:text-slate-500'
                                    }`}>
                                    <Folder size={18} />
                                </div>

                                {editando === proj.id ? (
                                    <div className="flex-1 flex items-center gap-1" onClick={e => e.stopPropagation()}>
                                        <input
                                            type="text"
                                            value={novoNome}
                                            onChange={(e) => setNovoNome(e.target.value)}
                                            className="w-full px-2 py-1 text-sm border border-emerald-500 rounded focus:outline-none"
                                            autoFocus
                                            onKeyPress={(e) => e.key === 'Enter' && atualizarProjeto(proj.id)}
                                        />
                                        <button onClick={() => atualizarProjeto(proj.id)} className="text-emerald-600 hover:bg-emerald-50 p-1 rounded">
                                            <Check size={14} />
                                        </button>
                                        <button onClick={() => setEditando(null)} className="text-red-500 hover:bg-red-50 p-1 rounded">
                                            <X size={14} />
                                        </button>
                                    </div>
                                ) : (
                                    <span className={`text-sm font-medium truncate ${projetoAtivo?.id === proj.id ? 'text-slate-900' : ''}`}>
                                        {proj.nome}
                                    </span>
                                )}
                            </div>

                            <div className="flex items-center opacity-0 group-hover:opacity-100 transition-opacity ml-2">
                                <button
                                    onClick={(e) => {
                                        e.stopPropagation()
                                        setEditando(proj.id)
                                        setNovoNome(proj.nome)
                                    }}
                                    className="p-1.5 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                                    title="Renomear"
                                >
                                    <Edit2 size={14} />
                                </button>
                                <button
                                    onClick={(e) => {
                                        e.stopPropagation()
                                        excluirProjeto(proj.id)
                                    }}
                                    className="p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                                    title="Excluir"
                                >
                                    <Trash2 size={14} />
                                </button>
                            </div>
                        </div>
                    ))
                )}
            </div>

            {/* Footer */}
            <div className="p-4 border-t border-slate-200 bg-white">
                <button
                    onClick={() => supabase.auth.signOut()}
                    className="flex items-center gap-2 text-sm text-slate-500 hover:text-red-600 transition-colors w-full px-2 py-1"
                >
                    <LogOut size={16} />
                    <span>Sair</span>
                </button>
            </div>
        </div>
    )
}
