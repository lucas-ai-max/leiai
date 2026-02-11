import { Link } from 'react-router-dom'
import { FolderOpen, CloudLightning, ArrowRight } from 'lucide-react'

export default function LandingPage() {
    return (
        <div className="min-h-screen bg-slate-950 text-slate-50 font-sans selection:bg-orange-500 selection:text-white flex items-center justify-center p-8">
            <div className="max-w-6xl w-full grid grid-cols-1 md:grid-cols-2 gap-8 min-h-[60vh]">

                {/* Card 1: ProcessIA */}
                <Link to="/projetos" className="group relative flex flex-col justify-between p-12 border-2 border-slate-800 bg-slate-900/50 hover:bg-slate-900 hover:border-orange-500 transition-all duration-300 overflow-hidden">
                    <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                        <FolderOpen size={300} strokeWidth={0.5} />
                    </div>

                    <div className="z-10">
                        <div className="inline-flex items-center gap-2 px-3 py-1 border border-slate-700 rounded-full text-xs font-mono text-slate-400 mb-6 group-hover:border-orange-500/50 group-hover:text-orange-400 transition-colors">
                            <span className="w-2 h-2 rounded-full bg-slate-500 group-hover:bg-orange-500 animate-pulse"></span>
                            MODULE_01
                        </div>
                        <h2 className="text-5xl font-bold tracking-tighter mb-4 text-white group-hover:translate-x-2 transition-transform duration-300">
                            PROCESS<span className="text-slate-600 group-hover:text-white transition-colors">IA</span>
                        </h2>
                        <p className="text-xl text-slate-400 max-w-sm font-light leading-relaxed group-hover:text-slate-300 transition-colors">
                            Gerenciamento avançado de documentos e análise jurídica automatizada.
                        </p>
                    </div>

                    <div className="z-10 flex items-center gap-4 text-orange-500 opacity-0 transform translate-y-4 group-hover:opacity-100 group-hover:translate-y-0 transition-all duration-300 delay-75">
                        <span className="font-mono text-sm tracking-widest uppercase font-bold">Acessar Sistema</span>
                        <ArrowRight size={20} />
                    </div>
                </Link>

                {/* Card 2: Salesforce */}
                <Link to="/salesforce" className="group relative flex flex-col justify-between p-12 border-2 border-slate-800 bg-slate-900/50 hover:bg-slate-900 hover:border-blue-500 transition-all duration-300 overflow-hidden">
                    <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                        <CloudLightning size={300} strokeWidth={0.5} />
                    </div>

                    <div className="z-10">
                        <div className="inline-flex items-center gap-2 px-3 py-1 border border-slate-700 rounded-full text-xs font-mono text-slate-400 mb-6 group-hover:border-blue-500/50 group-hover:text-blue-400 transition-colors">
                            <span className="w-2 h-2 rounded-full bg-slate-500 group-hover:bg-blue-500 animate-pulse"></span>
                            MODULE_02
                        </div>
                        <h2 className="text-5xl font-bold tracking-tighter mb-4 text-white group-hover:translate-x-2 transition-transform duration-300">
                            SALESFORCE<span className="text-slate-600 group-hover:text-white transition-colors">OS</span>
                        </h2>
                        <p className="text-xl text-slate-400 max-w-sm font-light leading-relaxed group-hover:text-slate-300 transition-colors">
                            Importação em massa, extração de cobertura e integração CRM.
                        </p>
                    </div>

                    <div className="z-10 flex items-center gap-4 text-blue-500 opacity-0 transform translate-y-4 group-hover:opacity-100 group-hover:translate-y-0 transition-all duration-300 delay-75">
                        <span className="font-mono text-sm tracking-widest uppercase font-bold">Iniciar Importação</span>
                        <ArrowRight size={20} />
                    </div>
                </Link>

            </div>

            <div className="fixed bottom-8 text-slate-600 text-xs font-mono">
                SYSTEM STATUS: ONLINE • V 2.4.0
            </div>
        </div>
    )
}
