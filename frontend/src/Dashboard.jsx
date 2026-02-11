import { useState } from 'react'
import ProjectManager from './ProjectManager'
import PromptEditor from './PromptEditor'
import DocumentList from './DocumentList'

export default function Dashboard() {
    const [selectedProject, setSelectedProject] = useState(null)

    return (
        <div className="flex h-screen bg-slate-100 overflow-hidden">
            {/* Sidebar */}
            <ProjectManager onSelectProject={setSelectedProject} />

            {/* Main Content */}
            <main className="flex-1 overflow-y-auto p-8 relative">
                {selectedProject ? (
                    <div className="max-w-5xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">

                        <header className="mb-8">
                            <h1 className="text-3xl font-bold text-slate-900 tracking-tight">
                                {selectedProject.nome}
                            </h1>
                            <p className="text-slate-500 text-sm mt-1">
                                Gerenciado pelo ProcessIA • {selectedProject.id}
                            </p>
                        </header>

                        {/* Editor de Prompt */}
                        <PromptEditor
                            projetoId={selectedProject.id}
                            onPromptSaved={() => { }}
                            readOnly={false} // TODO: Implementar lógica de bloqueio se necessário
                        />

                        {/* Lista de Documentos */}
                        <DocumentList projetoId={selectedProject.id} />

                    </div>
                ) : (
                    <div className="flex flex-col items-center justify-center h-full text-slate-400">
                        <div className="w-16 h-16 mb-4 rounded-2xl bg-slate-200 animate-pulse" />
                        <p className="text-lg font-medium text-slate-500">Selecione um projeto para começar</p>
                    </div>
                )}
            </main>
        </div>
    )
}
