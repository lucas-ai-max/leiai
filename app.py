<<<<<<< HEAD
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import streamlit as st
from pathlib import Path
import glob
import os
import sys
=======
import streamlit as st
from pathlib import Path
from processor import DocumentProcessor
from vectorstore import VectorStore
from analyzer import DocumentAnalyzer
from storage import ResponseStorage
from file_manager import FileManager
import glob
import os
>>>>>>> b5e15dc0d9832b696102fc7e6f8c4b6f2b1f24cf
from datetime import datetime
import pandas as pd
import json
import logging
import warnings
<<<<<<< HEAD
from threading import Lock

# Configurar encoding UTF-8 para Windows
# NOTA: Não reconfigurar sys.stdout/stderr para evitar "I/O operation on closed file"
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    # Não reconfigurar sys.stdout/stderr - pode causar problemas com Streamlit
=======
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import threading
from config import settings
>>>>>>> b5e15dc0d9832b696102fc7e6f8c4b6f2b1f24cf

# Configurar logging para filtrar erros de WebSocket do Tornado
logging.getLogger("tornado.access").setLevel(logging.ERROR)
logging.getLogger("tornado.application").setLevel(logging.ERROR)
logging.getLogger("tornado.general").setLevel(logging.ERROR)
logging.getLogger("tornado.websocket").setLevel(logging.ERROR)

# Suprimir warnings de WebSocket fechado
warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*WebSocket.*")
warnings.filterwarnings("ignore", message=".*Task exception was never retrieved.*")

# #region agent log
def debug_log(location, message, data, hypothesis_id="A", session_id="debug-session", run_id="run1"):
<<<<<<< HEAD
    """Debug logging helper - garante que diretório existe"""
    log_path = r'c:\Users\TRIA 2026\Downloads\ProcessIA\.cursor\debug.log'
    try:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
=======
    """Debug logging helper"""
    try:
>>>>>>> b5e15dc0d9832b696102fc7e6f8c4b6f2b1f24cf
        log_entry = {
            "sessionId": session_id,
            "runId": run_id,
            "hypothesisId": hypothesis_id,
            "location": location,
            "message": message,
            "data": data,
<<<<<<< HEAD
            "timestamp": int(__import__('time').time()*1000)
        }
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
=======
            "timestamp": datetime.now().isoformat()
        }
        log_path = os.path.join(os.path.dirname(__file__), ".cursor", "debug.log")
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
>>>>>>> b5e15dc0d9832b696102fc7e6f8c4b6f2b1f24cf
    except Exception as e:
        # Fallback: tentar escrever no diretório atual
        try:
            with open("debug.log", "a", encoding="utf-8") as f:
<<<<<<< HEAD
                f.write(json.dumps({"error": str(e), "error_type": type(e).__name__, "original": {"location": location, "message": message}}, ensure_ascii=False) + "\n")
        except:
            pass
# Teste inicial
debug_log("app.py:62", "DEBUG LOG INICIALIZADO", {"test": True}, "TEST")
# #endregion

# Importar processor normalmente (sem reload forçado para evitar conflitos)
try:
    # #region agent log
    debug_log("app.py:67", "TENTANDO IMPORTAR processor", {"path": str(Path(__file__).parent)}, "A")
    # #endregion
    from processor import DocumentProcessor
    # #region agent log
    debug_log("app.py:71", "DocumentProcessor IMPORTADO", {}, "A")
    # #endregion
    # Não usar print() aqui - sys.stdout pode estar fechado com Streamlit
except Exception as e:
    # #region agent log
    debug_log("app.py:75", "ERRO ao importar processor", {"error": str(e), "error_type": type(e).__name__}, "A,E")
    # #endregion
    # Não usar print() aqui - sys.stdout pode estar fechado com Streamlit
    # Verificar se DocumentProcessor foi importado mesmo assim
    try:
        from processor import DocumentProcessor
        # DocumentProcessor disponível apesar do erro - continuar
    except:
        # Se não conseguir importar, não fazer raise para não bloquear o app
        # #region agent log
        debug_log("app.py:84", "DocumentProcessor NÃO DISPONÍVEL", {"error": str(e)}, "A,E")
        # #endregion
        pass

from config import settings
from vectorstore import VectorStore
from analyzer import DocumentAnalyzer
from storage import ResponseStorage
from file_manager import FileManager

=======
                f.write(json.dumps({"error": str(e), "original": log_entry}, ensure_ascii=False) + "\n")
        except:
            pass
# Teste inicial
debug_log("app.py:31", "DEBUG LOG INICIALIZADO", {"test": True}, "TEST")
# #endregion

>>>>>>> b5e15dc0d9832b696102fc7e6f8c4b6f2b1f24cf
# Configuração da página
st.set_page_config(
    page_title="Análise de Processos Jurídicos",
    page_icon="⚖️",
    layout="wide"
)

# Título
st.title("⚖️ Análise Inteligente de Processos Jurídicos")
st.markdown("**Powered by GPT-4.1 + pypdf + Supabase**")
st.markdown("---")

# Inicializar componentes
@st.cache_resource
def init_components():
    try:
<<<<<<< HEAD
        # #region agent log
        debug_log("app.py:112", "INICIANDO init_components", {}, "C")
        # #endregion
        
        # #region agent log
        debug_log("app.py:114", "Criando VectorStore", {}, "C")
        # #endregion
        vectorstore = VectorStore()
        
        # #region agent log
        debug_log("app.py:116", "Criando DocumentProcessor", {}, "C")
        # #endregion
        processor = DocumentProcessor()
        
        # #region agent log
        debug_log("app.py:118", "Criando DocumentAnalyzer", {}, "C")
        # #endregion
        analyzer = DocumentAnalyzer(vectorstore=vectorstore)
        
        # #region agent log
        debug_log("app.py:120", "Criando ResponseStorage", {}, "C")
        # #endregion
        storage = ResponseStorage()
        
        # #region agent log
        debug_log("app.py:122", "Criando FileManager", {}, "C")
        # #endregion
        file_manager = FileManager()
        
        # #region agent log
        debug_log("app.py:124", "COMPONENTES INICIALIZADOS", {"processor": str(type(processor)), "vectorstore": str(type(vectorstore))}, "C")
        # #endregion
        
        return {
            "processor": processor,
            "vectorstore": vectorstore,
            "analyzer": analyzer,
            "storage": storage,
            "file_manager": file_manager
        }
    except Exception as e:
        # #region agent log
        debug_log("app.py:131", "ERRO ao inicializar componentes", {"error": str(e), "error_type": type(e).__name__}, "C,E")
        # #endregion
        import traceback
        error_details = traceback.format_exc()
        debug_log("app.py:134", "TRACEBACK init_components", {"traceback": error_details[:2000]}, "C,E")
        st.error(f"❌ Erro ao inicializar componentes: {str(e)}")
        st.warning("⚠️ Verifique se o arquivo .env está configurado corretamente")
        st.code(error_details[:1000])
        return None

# #region agent log
debug_log("app.py:140", "CHAMANDO init_components", {}, "C")
# #endregion
components = init_components()

# #region agent log
debug_log("app.py:143", "init_components RETORNOU", {"components_is_none": components is None}, "C")
# #endregion

if components is None:
    # #region agent log
    debug_log("app.py:145", "COMPONENTES NONE - PARANDO", {}, "C,E")
    # #endregion
=======
        vectorstore = VectorStore()
        return {
            "processor": DocumentProcessor(),
            "vectorstore": vectorstore,
            "analyzer": DocumentAnalyzer(vectorstore=vectorstore),
            "storage": ResponseStorage(),
            "file_manager": FileManager()
        }
    except Exception as e:
        st.error(f"❌ Erro ao inicializar componentes: {str(e)}")
        st.warning("⚠️ Verifique se o arquivo .env está configurado corretamente")
        return None

components = init_components()

if components is None:
>>>>>>> b5e15dc0d9832b696102fc7e6f8c4b6f2b1f24cf
    st.error("⚠️ Não foi possível inicializar a aplicação. Verifique o arquivo .env")
    st.stop()

# Inicializar estado da sessão
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'stop_requested' not in st.session_state:
    st.session_state.stop_requested = False
if 'logs' not in st.session_state:
    st.session_state.logs = []

# Lock para thread-safety nos logs e status
log_lock = Lock()
progress_lock = Lock()

# Sidebar - Configurações
st.sidebar.header("⚙️ Configurações")

folder_path = st.sidebar.text_input(
    "📁 Caminho da Pasta com PDFs",
    placeholder=r"E:\Documentos\PDFs",
    help="Digite o caminho completo da pasta contendo os arquivos PDF"
)

batch_size = st.sidebar.number_input(
    "📦 Quantidade de documentos por lote",
    min_value=1,
    max_value=100,
    value=5,
    help="Quantos documentos processar por vez"
)

<<<<<<< HEAD
# Processamento sequencial - multithread removido
=======
max_workers = st.sidebar.number_input(
    "🧵 Número de Threads (paralelismo)",
    min_value=1,
    max_value=16,
    value=settings.MAX_WORKERS,
    help="Quantas threads usar para processamento paralelo. Mais threads = mais rápido, mas consome mais recursos."
)
>>>>>>> b5e15dc0d9832b696102fc7e6f8c4b6f2b1f24cf

# Botões de controle
st.sidebar.markdown("---")
st.sidebar.markdown("### 🎮 Controles")
col1, col2 = st.sidebar.columns(2)
with col1:
    start_button = st.button("▶️ Iniciar", type="primary", disabled=st.session_state.processing or not folder_path, use_container_width=True)
with col2:
    stop_button = st.button("⏹️ Parar", disabled=not st.session_state.processing, use_container_width=True)

if stop_button:
    st.session_state.stop_requested = True
    st.sidebar.warning("⚠️ Parada solicitada...")

# Estatísticas na sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Estatísticas")
try:
    all_files = components["file_manager"].get_all()
    if all_files:
        status_counts = {}
        for file_data in all_files:
            status = file_data.get("status", "PENDENTE")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        st.sidebar.metric("✅ Concluídos", status_counts.get("CONCLUIDO", 0))
        st.sidebar.metric("⏳ Processando", status_counts.get("PROCESSANDO", 0))
        st.sidebar.metric("⏸️ Pendentes", status_counts.get("PENDENTE", 0))
<<<<<<< HEAD
        erro_count = status_counts.get("ERRO", 0)
        st.sidebar.metric("❌ Erros", erro_count)
        st.sidebar.metric("✓ Já Processados", status_counts.get("JA_PROCESSADO", 0))
        
        # Botão para limpar status de ERRO
        if erro_count > 0:
            st.sidebar.markdown("---")
            if st.sidebar.button("🧹 Limpar Status de ERRO", help="Reseta todos os arquivos com status ERRO para PENDENTE"):
                try:
                    reset_count = components["file_manager"].reset_errors()
                    st.sidebar.success(f"✅ {reset_count} arquivo(s) resetado(s) para PENDENTE")
                    st.rerun()
                except Exception as e:
                    st.sidebar.error(f"❌ Erro ao limpar status: {str(e)}")
=======
        st.sidebar.metric("❌ Erros", status_counts.get("ERRO", 0))
        st.sidebar.metric("✓ Já Processados", status_counts.get("JA_PROCESSADO", 0))
>>>>>>> b5e15dc0d9832b696102fc7e6f8c4b6f2b1f24cf
except:
    pass

# Função para adicionar log (thread-safe)
def add_log(message, level="INFO"):
    """Adiciona mensagem ao log de forma thread-safe"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    with log_lock:
        st.session_state.logs.append(f"[{timestamp}] {level}: {message}")

# Funções helper para atualizações seguras de UI (evitam erros de WebSocket fechado)
def safe_update_logs(log_display, logs, max_lines=50):
    """Atualiza logs de forma segura, ignorando erros de WebSocket fechado"""
    try:
<<<<<<< HEAD
        if log_display is not None and logs:
            log_text = "\n".join(logs[-max_lines:])
            if log_text.strip():  # Só atualizar se houver logs
                try:
                    log_display.code(log_text, language="text")
                except:
                    # Fallback: tentar usar text ao invés de code
                    try:
                        log_display.text(log_text)
                    except:
                        # Último fallback: usar markdown
                        log_display.markdown(f"```\n{log_text}\n```")
=======
        if log_display is not None:
            log_text = "\n".join(logs[-max_lines:])
            log_display.code(log_text, language="text")
>>>>>>> b5e15dc0d9832b696102fc7e6f8c4b6f2b1f24cf
    except (Exception, RuntimeError, AttributeError, TypeError):
        # Ignorar erros de WebSocket fechado e outros erros assíncronos
        pass
    except:
        # Capturar qualquer outro erro silenciosamente
        pass

def safe_update_progress(progress_bar, value):
    """Atualiza barra de progresso de forma segura"""
    try:
        if progress_bar is not None:
            progress_bar.progress(min(max(value, 0.0), 1.0))
    except (Exception, RuntimeError, AttributeError, TypeError):
        # Ignorar erros de WebSocket fechado e outros erros assíncronos
        pass
    except:
        # Capturar qualquer outro erro silenciosamente
        pass

def safe_streamlit_call(func, *args, **kwargs):
    """Chama funções do Streamlit de forma segura"""
    try:
        return func(*args, **kwargs)
    except (Exception, RuntimeError, AttributeError, TypeError):
        # Ignorar erros de WebSocket fechado e outros erros assíncronos
        pass
    except:
        # Capturar qualquer outro erro silenciosamente
        pass

def safe_rerun():
    """Chama st.rerun() de forma segura"""
    try:
        st.rerun()
    except (Exception, RuntimeError, AttributeError, TypeError):
        # Ignorar erros de WebSocket fechado ao fazer rerun
        pass
    except:
        # Capturar qualquer outro erro silenciosamente
        pass

# Criar tabs
tab1, tab2 = st.tabs(["📤 Processamento", "📚 Documentos Analisados"])

# Aba 1: Processamento
with tab1:
    # Opção: Upload de arquivo único ou processar pasta
    st.markdown("### 📤 Escolha o método de processamento")
    opcao_processamento = st.radio(
        "Selecione:",
        ["📁 Processar pasta", "📄 Fazer upload de arquivo único"],
        horizontal=True
    )
    
    st.markdown("---")
    
    # Upload de arquivo único
    if opcao_processamento == "📄 Fazer upload de arquivo único":
        uploaded_file = st.file_uploader(
            "Escolha um arquivo PDF",
            type=["pdf"],
            help="Faça upload de um único arquivo PDF para processar"
        )
        
        if uploaded_file is not None:
<<<<<<< HEAD
            # #region agent log
            debug_log("app.py:249", "UPLOADED FILE DETECTED", {"filename": uploaded_file.name, "size_bytes": len(uploaded_file.getbuffer())}, "A")
            # #endregion
            
=======
>>>>>>> b5e15dc0d9832b696102fc7e6f8c4b6f2b1f24cf
            # Salvar arquivo temporariamente
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.getbuffer())
                tmp_path = tmp_file.name
            
            filename = uploaded_file.name
            file_size_mb = len(uploaded_file.getbuffer()) / (1024 * 1024)
            
<<<<<<< HEAD
            # Salvar tmp_path no session_state para persistir entre reruns
            st.session_state['uploaded_tmp_path'] = tmp_path
            st.session_state['uploaded_filename'] = filename
            st.session_state['uploaded_file_size_mb'] = file_size_mb
            
            # #region agent log
            debug_log("app.py:257", "TEMP FILE CREATED", {"tmp_path": tmp_path, "filename": filename, "tmp_path_exists": os.path.exists(tmp_path)}, "A,F")
            # #endregion
            
            st.success(f"✅ Arquivo carregado: **{filename}** ({file_size_mb:.2f} MB)")
        
        # Usar dados do session_state se disponível (após rerun)
        if 'uploaded_tmp_path' in st.session_state:
            tmp_path = st.session_state['uploaded_tmp_path']
            filename = st.session_state['uploaded_filename']
            file_size_mb = st.session_state['uploaded_file_size_mb']
            
            # #region agent log
            debug_log("app.py:270", "USING SESSION STATE", {"tmp_path": tmp_path, "filename": filename, "tmp_path_exists": os.path.exists(tmp_path) if tmp_path else False}, "A")
            # #endregion
=======
            st.success(f"✅ Arquivo carregado: **{filename}** ({file_size_mb:.2f} MB)")
>>>>>>> b5e15dc0d9832b696102fc7e6f8c4b6f2b1f24cf
            
            # Verificar se já foi processado
            try:
                existing = components["file_manager"].get_by_filename(filename)
<<<<<<< HEAD
                # #region agent log
                debug_log("app.py:263", "EXISTING FILE CHECK", {"filename": filename, "existing": existing is not None, "status": existing.get("status") if existing else None}, "A")
                # #endregion
                if existing and existing.get("status") == "CONCLUIDO":
                    # #region agent log
                    debug_log("app.py:265", "FILE ALREADY CONCLUIDO", {"filename": filename}, "A")
                    # #endregion
                    st.info(f"ℹ️ **{filename}** já foi processado anteriormente.")
                    if st.button(f"🔄 Reprocessar {filename}", type="primary"):
                        # #region agent log
                        debug_log("app.py:267", "REPROCESS BUTTON CLICKED", {"filename": filename}, "A")
                        # #endregion
=======
                if existing and existing.get("status") == "CONCLUIDO":
                    st.info(f"ℹ️ **{filename}** já foi processado anteriormente.")
                    if st.button(f"🔄 Reprocessar {filename}", type="primary"):
>>>>>>> b5e15dc0d9832b696102fc7e6f8c4b6f2b1f24cf
                        # Resetar status para processar novamente
                        components["file_manager"].update_status(filename, "PENDENTE", existing_data=existing)
                        safe_rerun()
                elif existing and existing.get("status") == "PROCESSANDO":
<<<<<<< HEAD
                    # #region agent log
                    debug_log("app.py:271", "FILE ALREADY PROCESSANDO", {"filename": filename}, "A")
                    # #endregion
                    st.warning(f"⚠️ **{filename}** está sendo processado. Aguarde a conclusão.")
                else:
                    # #region agent log
                    debug_log("app.py:294", "FILE READY TO PROCESS", {"filename": filename, "processing_state": st.session_state.processing, "existing": existing is not None}, "A")
                    # #endregion
                    
                    # Registrar no banco se necessário
                    try:
                        if not existing:
                            # #region agent log
                            debug_log("app.py:299", "REGISTERING NEW FILE", {"filename": filename}, "A")
                            # #endregion
                            components["file_manager"].register_file(filename, file_size_mb, tmp_path)
                    except Exception as reg_error:
                        # #region agent log
                        debug_log("app.py:299", "REGISTER FILE ERROR", {"filename": filename, "error": str(reg_error)}, "A")
                        # #endregion
                        pass
                    
                    # #region agent log
                    debug_log("app.py:305", "BEFORE BUTTON RENDER", {"filename": filename, "processing_state": st.session_state.processing, "existing_status": existing.get("status") if existing else None, "tmp_path": tmp_path, "tmp_path_exists": os.path.exists(tmp_path) if tmp_path else False}, "A")
                    # #endregion
                    
                    # VERIFICAR SE tmp_path EXISTE
                    if not tmp_path:
                        st.error(f"❌ Erro: tmp_path não definido para {filename}")
                    elif not os.path.exists(tmp_path):
                        st.error(f"❌ Erro: Arquivo temporário não encontrado: {tmp_path}")
                        st.warning("💡 Tente fazer upload do arquivo novamente.")
                    else:
                        # Arquivo existe, mostrar informação
                        file_size = os.path.getsize(tmp_path) / (1024 * 1024)
                        st.caption(f"📁 Arquivo pronto: {file_size:.2f} MB")
                    
                    # Verificar se pode processar
                    can_process = not st.session_state.processing
                    if existing and existing.get("status") == "PROCESSANDO":
                        can_process = False
                    if not tmp_path or not os.path.exists(tmp_path):
                        can_process = False  # Não pode processar se arquivo não existe
                    
                    # Botão para processar - só desabilitado quando estiver processando
                    button_label = f"▶️ Processar {filename}"
                    if not can_process:
                        if not tmp_path or not os.path.exists(tmp_path):
                            button_label = f"❌ Arquivo não encontrado"
                        else:
                            button_label = f"⏸️ Processando..." if st.session_state.processing else f"⏳ Aguarde..."
                    
                    button_clicked = st.button(
                        button_label, 
                        type="primary", 
                        disabled=not can_process,
                        key=f"process_btn_{filename}"
                    )
                    
                    # #region agent log
                    debug_log("app.py:318", "AFTER BUTTON RENDER", {"filename": filename, "button_clicked": button_clicked, "processing_state": st.session_state.processing, "can_process": can_process}, "A")
                    # #endregion
                    
                    if button_clicked and can_process:
                        # #region agent log
                        debug_log("app.py:283", "BUTTON CLICKED - INSIDE IF", {"filename": filename, "tmp_path": tmp_path, "tmp_path_exists": os.path.exists(tmp_path) if tmp_path else False}, "A")
                        # #endregion
                        
                        # Marcar como processando e salvar flag para iniciar processamento
                        st.session_state.processing = True
                        st.session_state.stop_requested = False
                        st.session_state.logs = []
                        st.session_state['should_start_processing'] = filename
                        
                        # Forçar rerun imediato para desabilitar o botão
                        st.rerun()
                    
                    # Verificar se deve iniciar o processamento (após rerun quando botão foi clicado)
                    should_start = st.session_state.get('should_start_processing') == filename
                    add_log(f"🔵 DEBUG: should_start={should_start}, processing={st.session_state.processing}, filename={filename}", "DEBUG")
                    
                    if should_start and st.session_state.processing:
                        # Limpar flag para não reiniciar em loops
                        st.session_state['should_start_processing'] = None
                        
                        # VERIFICAR SE ARQUIVO EXISTE ANTES DE PROCESSAR
                        if not tmp_path or not os.path.exists(tmp_path):
                            error_msg = f"❌ ERRO CRÍTICO: Arquivo temporário não encontrado! tmp_path={tmp_path}, exists={os.path.exists(tmp_path) if tmp_path else False}"
                            add_log(error_msg, "ERROR")
                            st.error(error_msg)
                            st.session_state.processing = False
                            if 'uploaded_tmp_path' in st.session_state:
                                del st.session_state['uploaded_tmp_path']
                            if 'uploaded_filename' in st.session_state:
                                del st.session_state['uploaded_filename']
                            if 'uploaded_file_size_mb' in st.session_state:
                                del st.session_state['uploaded_file_size_mb']
                            safe_rerun()
                        else:
                            add_log(f"✅ Arquivo encontrado: {tmp_path} ({os.path.getsize(tmp_path)} bytes)", "DEBUG")
=======
                    st.warning(f"⚠️ **{filename}** está sendo processado. Aguarde a conclusão.")
                else:
                    # Registrar no banco se necessário
                    if not existing:
                        components["file_manager"].register_file(filename, file_size_mb, tmp_path)
                    
                    # Botão para processar
                    if st.button(f"▶️ Processar {filename}", type="primary", disabled=st.session_state.processing):
                        st.session_state.processing = True
                        st.session_state.stop_requested = False
                        st.session_state.logs = []
                        
                        add_log(f"Iniciando processamento de {filename}")
>>>>>>> b5e15dc0d9832b696102fc7e6f8c4b6f2b1f24cf
                        
                        # Logs em tempo real
                        st.markdown("### 📋 Logs do Processamento")
                        log_display = st.empty()
                        progress_bar = st.progress(0)
                        
<<<<<<< HEAD
                        add_log(f"Iniciando processamento de {filename}")
                        add_log(f"📁 Arquivo: {tmp_path}")
                        add_log(f"📊 Tamanho: {os.path.getsize(tmp_path) / (1024*1024):.2f} MB")
                        
=======
>>>>>>> b5e15dc0d9832b696102fc7e6f8c4b6f2b1f24cf
                        chunks_count = [0]
                        
                        try:
                            # Atualizar status para PROCESSANDO
                            components["file_manager"].update_status(filename, "PROCESSANDO")
                            add_log(f"Iniciando: {filename}")
                            
                            safe_update_logs(log_display, st.session_state.logs)
                            
                            def save_chunks_batch(chunks_batch):
<<<<<<< HEAD
                                # Log IMEDIATO quando callback é chamado
                                add_log(f"{filename}: 🔵 CALLBACK RECEBIDO - {len(chunks_batch)} chunks", "DEBUG")
                                
                                chunks_count[0] += len(chunks_batch)
                                add_log(f"{filename}: {len(chunks_batch)} chunks recebidos no callback")
                                add_log(f"{filename}: Total acumulado: {chunks_count[0]} chunks processados")
                                try:
                                    # Log ANTES de chamar store_chunks
                                    add_log(f"{filename}: 🔵 ANTES DE CHAMAR store_chunks com {len(chunks_batch)} chunks...")
                                    
                                    # CHAMADA CRÍTICA - adicionar log aqui
                                    components["vectorstore"].store_chunks(chunks_batch)
                                    
                                    add_log(f"{filename}: ✅ {len(chunks_batch)} chunks salvos no banco com sucesso")
                                except Exception as e:
                                    import traceback
                                    error_details = traceback.format_exc()
                                    add_log(f"{filename}: ❌ ERRO ao salvar chunks - {str(e)}", "ERROR")
                                    add_log(f"{filename}: Traceback: {error_details[:1000]}", "ERROR")
                                    raise
=======
                                chunks_count[0] += len(chunks_batch)
                                add_log(f"{filename}: {chunks_count[0]} chunks processados")
                                components["vectorstore"].store_chunks(chunks_batch)
>>>>>>> b5e15dc0d9832b696102fc7e6f8c4b6f2b1f24cf
                            
                            add_log(f"{filename}: Extraindo texto...")
                            safe_update_progress(progress_bar, 0.1)
                            
<<<<<<< HEAD
                            # #region agent log
                            debug_log("app.py:312", "BEFORE process_incremental call", {"tmp_path": tmp_path, "filename": filename, "tmp_path_exists": os.path.exists(tmp_path) if tmp_path else False}, "A,F")
                            # #endregion
                            
                            try:
                                add_log(f"{filename}: 🔵 CHAMANDO process_incremental...")
                                doc = components["processor"].process_incremental(
                                    tmp_path,
                                    filename=filename,
                                    chunk_callback=save_chunks_batch,
                                    batch_size=5  # Reduzido para salvar chunks imediatamente após extração
                                )
                                add_log(f"{filename}: ✅ process_incremental concluído!")
                                # #region agent log
                                debug_log("app.py:319", "AFTER process_incremental SUCCESS", {"doc_keys": list(doc.keys()) if doc else None, "total_pages": doc.get('metadata', {}).get('total_pages') if doc else None}, "A")
                                # #endregion
                            except Exception as e:
                                # #region agent log
                                debug_log("app.py:319", "process_incremental ERROR", {"error": str(e), "error_type": type(e).__name__}, "A,E")
                                # #endregion
                                raise
                            
                            total_pages = doc.get('metadata', {}).get('total_pages', 0)
                            add_log(f"{filename}: {total_pages} páginas, {chunks_count[0]} chunks processados")
                            safe_update_progress(progress_bar, 0.9)
                            
                            # Verificar se chunks foram salvos no banco
                            if chunks_count[0] > 0:
                                document_id = doc.get("document_id")
                                if document_id:
                                    try:
                                        has_chunks = components["vectorstore"].has_chunks(document_id=document_id)
                                        add_log(f"{filename}: ✅ Verificação final - Chunks no banco: {has_chunks}")
                                        if has_chunks:
                                            # Contar quantos chunks existem
                                            try:
                                                from supabase import create_client
                                                from config import settings
                                                supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
                                                result = supabase.table(settings.TABLE_EMBEDDINGS).select("id", count="exact").eq("document_id", document_id).execute()
                                                count = result.count if hasattr(result, 'count') else len(result.data) if result.data else 0
                                                add_log(f"{filename}: ✅ Total de {count} chunks salvos na tabela documento_chunks")
                                            except Exception as count_error:
                                                add_log(f"{filename}: Aviso - Erro ao contar chunks: {str(count_error)}", "WARNING")
                                    except Exception as check_error:
                                        add_log(f"{filename}: Aviso - Erro ao verificar chunks: {str(check_error)}", "WARNING")
                                
                                # Atualizar status para CONCLUIDO
                                components["file_manager"].update_status(
                                    filename,
                                    "CONCLUIDO",
                                    document_id=doc["document_id"],
                                    total_chunks=chunks_count[0],
                                    total_pages=total_pages
                                )
                                add_log(f"{filename}: Status CONCLUIDO atualizado")
                                
                                safe_update_progress(progress_bar, 1.0)
                                add_log(f"✅ {filename} concluído! ({chunks_count[0]} chunks extraídos e embeddings gerados)")
                                
                                safe_streamlit_call(st.success, f"✅ **{filename}** concluído! ({chunks_count[0]} chunks extraídos e embeddings gerados)")
                                safe_streamlit_call(st.balloons)
                                
                                # ANÁLISE AUTOMÁTICA DESABILITADA TEMPORARIAMENTE PARA ACELERAR PROCESSAMENTO
                                # Para habilitar novamente, descomente o código abaixo:
                                """
                                add_log(f"{filename}: Iniciando análise RAG...")
                                try:
=======
                            doc = components["processor"].process_incremental(
                                tmp_path,
                                filename=filename,
                                chunk_callback=save_chunks_batch,
                                batch_size=50
                            )
                            
                            total_pages = doc.get('metadata', {}).get('total_pages', 0)
                            add_log(f"{filename}: {total_pages} páginas, {chunks_count[0]} chunks")
                            
                            # Análise automática
                            if chunks_count[0] > 0:
                                add_log(f"{filename}: Iniciando análise RAG...")
                                safe_update_progress(progress_bar, 0.7)
                                
                                try:
                                    add_log(f"{filename}: Chamando GPT-4.1 para análise...")
                                    
>>>>>>> b5e15dc0d9832b696102fc7e6f8c4b6f2b1f24cf
                                    analise_result, resposta_bruta = components["analyzer"].analyze_full_document_rag(
                                        doc["document_id"],
                                        filename,
                                        return_raw_response=True
                                    )
<<<<<<< HEAD
                                    components["storage"].save_analysis(**analise_result)
                                    add_log(f"{filename}: Análise salva com sucesso")
                                except Exception as e:
                                    add_log(f"{filename}: ERRO na análise - {str(e)}", "ERROR")
                                """
                            else:
                                add_log(f"{filename}: ⚠️ Nenhum chunk criado", "WARNING")
=======
                                    
                                    add_log(f"{filename}: Análise GPT-4.1 concluída. Resposta: {len(resposta_bruta)} chars")
                                    
                                    # Mostrar resposta da IA
                                    safe_streamlit_call(st.markdown, f"#### 🤖 Resposta da IA - {filename}")
                                    try:
                                        with st.expander("📄 Ver resposta completa", expanded=False):
                                            safe_streamlit_call(st.markdown, resposta_bruta)
                                    except Exception:
                                        pass
                                    
                                    safe_update_progress(progress_bar, 0.9)
                                    add_log(f"{filename}: Salvando no banco...")
                                    
                                    # Salvar análise
                                    try:
                                        components["storage"].save_analysis(**analise_result)
                                        add_log(f"{filename}: Análise salva com sucesso")
                                        
                                        # Deletar chunks após análise salva com sucesso
                                        document_id = doc.get("document_id")
                                        if document_id:
                                            deleted_count = components["vectorstore"].delete_chunks_by_document_id(document_id)
                                            add_log(f"{filename}: {deleted_count} chunks deletados após análise")
                                    except Exception as save_error:
                                        add_log(f"{filename}: ERRO ao salvar - {str(save_error)}", "ERROR")
                                        raise
                                    
                                    # Atualizar status para CONCLUIDO
                                    components["file_manager"].update_status(
                                        filename,
                                        "CONCLUIDO",
                                        document_id=doc["document_id"],
                                        total_chunks=chunks_count[0],
                                        total_pages=total_pages
                                    )
                                    add_log(f"{filename}: Status CONCLUIDO atualizado")
                                    
                                    safe_update_progress(progress_bar, 1.0)
                                    add_log(f"✅ {filename} concluído!")
                                    
                                    safe_streamlit_call(st.success, f"✅ **{filename}** concluído! ({chunks_count[0]} chunks)")
                                    safe_streamlit_call(st.balloons)
                                    
                                except Exception as e:
                                    error_msg = str(e)
                                    add_log(f"{filename}: ERRO na análise - {error_msg}", "ERROR")
                                    components["file_manager"].update_status(
                                        filename,
                                        "ERRO",
                                        error_message=f"Erro análise: {error_msg[:200]}"
                                    )
                                    safe_streamlit_call(st.error, f"❌ **{filename}**: {error_msg}")
                            else:
                                add_log(f"{filename}: Nenhum chunk criado", "WARNING")
>>>>>>> b5e15dc0d9832b696102fc7e6f8c4b6f2b1f24cf
                                components["file_manager"].update_status(
                                    filename,
                                    "ERRO",
                                    error_message="Nenhum chunk foi criado"
                                )
                                safe_streamlit_call(st.error, f"❌ **{filename}**: Nenhum chunk foi criado")
                            
                        except Exception as e:
                            error_msg = str(e)
                            add_log(f"{filename}: ERRO no processamento - {error_msg}", "ERROR")
                            components["file_manager"].update_status(
                                filename,
                                "ERRO",
                                error_message=f"Erro processamento: {error_msg[:200]}"
                            )
                            safe_streamlit_call(st.error, f"❌ **{filename}**: {error_msg}")
                        finally:
                            st.session_state.processing = False
                            safe_update_logs(log_display, st.session_state.logs)
                            
<<<<<<< HEAD
                            # Limpar arquivo temporário e session_state
                            try:
                                if tmp_path and os.path.exists(tmp_path):
                                    os.unlink(tmp_path)
                            except:
                                pass
                            
                            # Limpar dados do session_state
                            if 'uploaded_tmp_path' in st.session_state:
                                del st.session_state['uploaded_tmp_path']
                            if 'uploaded_filename' in st.session_state:
                                del st.session_state['uploaded_filename']
                            if 'uploaded_file_size_mb' in st.session_state:
                                del st.session_state['uploaded_file_size_mb']
                            
=======
                            # Limpar arquivo temporário
                            try:
                                os.unlink(tmp_path)
                            except:
                                pass
                            
>>>>>>> b5e15dc0d9832b696102fc7e6f8c4b6f2b1f24cf
                            safe_rerun()
            except Exception as e:
                st.error(f"❌ Erro ao verificar status: {str(e)}")
    
    # Processar pasta (código existente)
    elif opcao_processamento == "📁 Processar pasta":
        # Área principal
        if folder_path and os.path.exists(folder_path):
            # Buscar PDFs na pasta
            pdf_files = glob.glob(os.path.join(folder_path, "*.pdf"))
            
            if pdf_files:
                # Ordenar por tamanho (menor para maior)
                pdf_files_with_size = [(f, os.path.getsize(f)) for f in pdf_files]
                pdf_files_with_size.sort(key=lambda x: x[1])  # Ordenar por tamanho
                pdf_files = [f[0] for f in pdf_files_with_size]  # Pegar apenas os caminhos
                
                st.success(f"✅ {len(pdf_files)} arquivo(s) PDF encontrado(s) na pasta (ordenados do menor para o maior)")
                
                # Registrar arquivos no banco se necessário
                for pdf_file in pdf_files:
                    filename = os.path.basename(pdf_file)
                    file_size_mb = os.path.getsize(pdf_file) / (1024 * 1024)
                    
                    try:
                        # Verificar se já existe no banco
                        existing = components["file_manager"].get_by_filename(filename)
                        if not existing:
                            # Registrar novo arquivo
                            try:
                                components["file_manager"].register_file(filename, file_size_mb, pdf_file)
                            except Exception as e:
                                pass  # Ignorar se já existe ou erro de conexão
                        elif existing and existing.get("status") not in ["CONCLUIDO", "JA_PROCESSADO"]:
                            # Atualizar tamanho se necessário
                            if existing.get("file_size_mb") != file_size_mb:
                                try:
                                    components["file_manager"].update_status(
                                        filename, 
                                        existing.get("status"),
                                        existing_data=existing  # Passar existing para evitar nova query
                                    )
                                except Exception:
                                    pass  # Ignorar erro de conexão
                    except Exception:
                        pass  # Continuar mesmo se houver erro
            
            # Buscar status de todos os arquivos do banco
            all_file_statuses = {}
            try:
                db_files = components["file_manager"].get_all()
                for db_file in db_files:
                    all_file_statuses[db_file["filename"]] = db_file
            except:
                pass
            
            # Mostrar tabela de documentos
            st.markdown("### 📊 Status dos Documentos")
            
            # Criar DataFrame para exibição
            docs_data = []
            for pdf_file in pdf_files:
                filename = os.path.basename(pdf_file)
                size_mb = os.path.getsize(pdf_file) / (1024 * 1024)
                
                db_file = all_file_statuses.get(filename, {})
                status = db_file.get("status", "PENDENTE")
                
                # Formatar status para exibição
                error_msg = db_file.get('error_message') or 'Erro desconhecido'
                if isinstance(error_msg, str) and len(error_msg) > 30:
                    error_msg = error_msg[:30] + "..."
                
                status_display = {
                    "PENDENTE": "⏸️ Pendente",
                    "PROCESSANDO": "⏳ Processando",
                    "CONCLUIDO": "✅ Concluído",
                    "ERRO": f"❌ Erro: {error_msg}",
                    "JA_PROCESSADO": "✅ Já processado"
                }.get(status, status)
                
                chunks = db_file.get("total_chunks", 0)
                pages = db_file.get("total_pages", 0)
                
                docs_data.append({
                    "Arquivo": filename,
                    "Tamanho (MB)": f"{size_mb:.2f}",
                    "Status": status_display,
                    "Chunks": str(chunks) if chunks else "-",
                    "Páginas": str(pages) if pages else "-"
                })
            
            # Exibir tabela única com todos os documentos
            if docs_data:
                df = pd.DataFrame(docs_data)
                st.dataframe(df, width='stretch', height=400)
                
                # Processar documentos
                if start_button:
                    st.session_state.processing = True
                    st.session_state.stop_requested = False
                    st.session_state.logs = []
                    
                    add_log(f"Iniciando processamento em lote de até {batch_size} documentos")
                    
                    # Resetar documentos travados em PROCESSANDO de execuções anteriores
                    try:
                        stuck_files = components["file_manager"].get_all("PROCESSANDO")
                        for stuck in stuck_files:
                            components["file_manager"].update_status(
                                stuck["filename"],
                                "PENDENTE",
                                existing_data=stuck
                            )
                        if stuck_files:
                            add_log(f"Resetados {len(stuck_files)} arquivo(s) travados em PROCESSANDO")
                    except:
                        pass
                    
                    # REBUSCAR status atualizado do banco após o reset
                    all_file_statuses = {}
                    try:
                        db_files = components["file_manager"].get_all()
                        for db_file in db_files:
                            all_file_statuses[db_file["filename"]] = db_file
                        add_log(f"Status atualizado do banco: {len(all_file_statuses)} arquivo(s) carregados")
                    except Exception as e:
                        add_log(f"Erro ao rebuscar status: {str(e)}", "WARNING")
                    
                    # Logs em tempo real
                    st.markdown("---")
                    st.markdown("### 📋 Logs do Processamento")
                    log_display = st.empty()
                    progress_bar = st.progress(0)
                    
<<<<<<< HEAD
                    # Atualizar logs inicialmente
                    safe_update_logs(log_display, st.session_state.logs)
                    
=======
>>>>>>> b5e15dc0d9832b696102fc7e6f8c4b6f2b1f24cf
                    # Filtrar documentos pendentes (ordenados por tamanho) usando status ATUALIZADO
                    docs_to_process = []
                    for pdf_file in pdf_files:  # Já ordenados por tamanho
                        filename = os.path.basename(pdf_file)
                        db_file = all_file_statuses.get(filename, {})  # Usar status ATUALIZADO
                        status = db_file.get("status", "PENDENTE")
                        
                        if status in ["PENDENTE", "ERRO"]:
                            docs_to_process.append(pdf_file)
                            add_log(f"Adicionado à fila: {filename} (status: {status})", "DEBUG")
                            if len(docs_to_process) >= batch_size:
                                break
                    
                    add_log(f"Documentos pendentes selecionados: {len(docs_to_process)} (ordenados do menor para o maior)")
                    total_docs = len(docs_to_process)
                    
<<<<<<< HEAD
                    # Atualizar logs após seleção
                    safe_update_logs(log_display, st.session_state.logs)
                    
=======
>>>>>>> b5e15dc0d9832b696102fc7e6f8c4b6f2b1f24cf
                    if total_docs == 0:
                        st.info("ℹ️ Nenhum documento pendente para processar!")
                        st.session_state.processing = False
                    else:
<<<<<<< HEAD
                        # Processar documentos sequencialmente
                        add_log(f"Iniciando processamento sequencial de {total_docs} documentos")
                        safe_update_logs(log_display, st.session_state.logs)
=======
                        # Processar documentos em paralelo usando multithreading
                        # Usar o valor selecionado pelo usuário, mas não mais que o total de documentos
                        num_threads = min(max_workers, total_docs)
                        add_log(f"Iniciando processamento paralelo com {num_threads} threads (configurado: {max_workers}, documentos: {total_docs})")
>>>>>>> b5e15dc0d9832b696102fc7e6f8c4b6f2b1f24cf
                        
                        # Criar função para processar um documento
                        def process_single_document(pdf_file, idx, total_docs):
                            """Processa um único documento"""
                            filename = os.path.basename(pdf_file)
                            
                            try:
                                # Atualizar status para PROCESSANDO
                                try:
                                    components["file_manager"].update_status(filename, "PROCESSANDO")
                                except:
                                    pass
                                
<<<<<<< HEAD
                                add_log(f"[{idx+1}/{total_docs}] Iniciando: {filename}")
=======
                                with log_lock:
                                    add_log(f"[{idx+1}/{total_docs}] Iniciando: {filename}")
>>>>>>> b5e15dc0d9832b696102fc7e6f8c4b6f2b1f24cf
                                
                                # Verificar se já tem chunks/embeddings salvos
                                existing_file_data = components["file_manager"].get_by_filename(filename)
                                doc = None
                                chunks_count = [0]
                                
                                # Verificar se já tem chunks no banco
                                if existing_file_data and existing_file_data.get("document_id") and existing_file_data.get("total_chunks", 0) > 0:
                                    document_id_existing = existing_file_data["document_id"]
                                    
                                    # Verificar se chunks realmente existem no banco
                                    if components["vectorstore"].has_chunks(document_id=document_id_existing):
<<<<<<< HEAD
                                        add_log(f"[{idx+1}/{total_docs}] {filename}: Chunks já existem no banco, reutilizando...")
=======
                                        with log_lock:
                                            add_log(f"[{idx+1}/{total_docs}] {filename}: Chunks já existem no banco, reutilizando...")
>>>>>>> b5e15dc0d9832b696102fc7e6f8c4b6f2b1f24cf
                                        chunks_count[0] = existing_file_data.get("total_chunks", 0)
                                        total_pages = existing_file_data.get("total_pages", 0)
                                        
                                        # Criar objeto doc simulado com o document_id existente
                                        doc = {
                                            "document_id": document_id_existing,
                                            "filename": filename,
                                            "metadata": {
                                                "total_pages": total_pages
                                            }
                                        }
<<<<<<< HEAD
                                        add_log(f"[{idx+1}/{total_docs}] {filename}: Reutilizando {chunks_count[0]} chunks existentes")
                                    else:
                                        # Document_id salvo mas chunks não existem mais, reprocessar
                                        add_log(f"[{idx+1}/{total_docs}] {filename}: Document ID encontrado mas chunks não existem, reprocessando...")
=======
                                        with log_lock:
                                            add_log(f"[{idx+1}/{total_docs}] {filename}: Reutilizando {chunks_count[0]} chunks existentes")
                                    else:
                                        # Document_id salvo mas chunks não existem mais, reprocessar
                                        with log_lock:
                                            add_log(f"[{idx+1}/{total_docs}] {filename}: Document ID encontrado mas chunks não existem, reprocessando...")
>>>>>>> b5e15dc0d9832b696102fc7e6f8c4b6f2b1f24cf
                                        doc = None
                                
                                # Se não tem chunks, processar PDF
                                if doc is None:
                                    chunks_count = [0]
                                    
<<<<<<< HEAD
                                    def save_chunks_batch(chunks_batch, document_id, filename_cb):
                                        # Log IMEDIATO quando callback é chamado
                                        add_log(f"[{idx+1}/{total_docs}] {filename_cb}: 🔵 CALLBACK RECEBIDO - {len(chunks_batch)} chunks", "DEBUG")
                                        
                                        chunks_count[0] += len(chunks_batch)
                                        add_log(f"[{idx+1}/{total_docs}] {filename_cb}: {len(chunks_batch)} chunks recebidos no callback")
                                        add_log(f"[{idx+1}/{total_docs}] {filename_cb}: Total acumulado: {chunks_count[0]} chunks processados")
                                        try:
                                            # Log ANTES de chamar store_chunks
                                            add_log(f"[{idx+1}/{total_docs}] {filename_cb}: 🔵 ANTES DE CHAMAR store_chunks com {len(chunks_batch)} chunks...")
                                            
                                            # CHAMADA CRÍTICA - adicionar log aqui
                                            components["vectorstore"].store_chunks(chunks_batch)
                                            
                                            add_log(f"[{idx+1}/{total_docs}] {filename_cb}: ✅ {len(chunks_batch)} chunks salvos no banco com sucesso")
                                        except Exception as e:
                                            import traceback
                                            error_details = traceback.format_exc()
                                            add_log(f"[{idx+1}/{total_docs}] {filename_cb}: ❌ ERRO ao salvar chunks - {str(e)}", "ERROR")
                                            add_log(f"[{idx+1}/{total_docs}] {filename_cb}: Traceback: {error_details[:1000]}", "ERROR")
                                            raise
                                    
                                    add_log(f"[{idx+1}/{total_docs}] {filename}: Extraindo texto...")
=======
                                    def save_chunks_batch(chunks_batch):
                                        chunks_count[0] += len(chunks_batch)
                                        with log_lock:
                                            add_log(f"[{idx+1}/{total_docs}] {filename}: {chunks_count[0]} chunks processados")
                                        components["vectorstore"].store_chunks(chunks_batch)
                                    
                                    with log_lock:
                                        add_log(f"[{idx+1}/{total_docs}] {filename}: Extraindo texto...")
>>>>>>> b5e15dc0d9832b696102fc7e6f8c4b6f2b1f24cf
                                    
                                    doc = components["processor"].process_incremental(
                                        pdf_file,
                                        filename=filename,
                                        chunk_callback=save_chunks_batch,
<<<<<<< HEAD
                                        batch_size=5  # Reduzido para salvar chunks imediatamente após extração
                                    )
                                    
                                    total_pages = doc.get('metadata', {}).get('total_pages', 0)
                                    add_log(f"[{idx+1}/{total_docs}] {filename}: {total_pages} páginas, {chunks_count[0]} chunks")
                                
                                # Verificar se chunks foram salvos e atualizar status
                                if chunks_count[0] > 0:
                                    document_id = doc.get("document_id")
                                    if document_id:
                                        try:
                                            has_chunks = components["vectorstore"].has_chunks(document_id=document_id)
                                            add_log(f"[{idx+1}/{total_docs}] {filename}: ✅ Verificação final - Chunks no banco: {has_chunks}")
                                            if has_chunks:
                                                # Contar quantos chunks existem
                                                try:
                                                    from supabase import create_client
                                                    from config import settings
                                                    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
                                                    result = supabase.table(settings.TABLE_EMBEDDINGS).select("id", count="exact").eq("document_id", document_id).execute()
                                                    count = result.count if hasattr(result, 'count') else len(result.data) if result.data else 0
                                                    add_log(f"[{idx+1}/{total_docs}] {filename}: ✅ Total de {count} chunks salvos na tabela documento_chunks")
                                                except:
                                                    pass
                                        except Exception as check_error:
                                            add_log(f"[{idx+1}/{total_docs}] {filename}: Aviso - Erro ao verificar chunks: {str(check_error)}", "WARNING")
                                    
                                    # Atualizar status para CONCLUIDO
                                    try:
                                        status_result = components["file_manager"].update_status(
                                            filename,
                                            "CONCLUIDO",
                                            document_id=doc["document_id"],
                                            total_chunks=chunks_count[0],
                                            total_pages=total_pages
                                        )
                                        add_log(f"[{idx+1}/{total_docs}] {filename}: Status CONCLUIDO atualizado")
                                        add_log(f"[{idx+1}/{total_docs}] ✅ {filename} concluído! ({chunks_count[0]} chunks extraídos e embeddings gerados)")
                                    except Exception as status_error:
                                        add_log(f"[{idx+1}/{total_docs}] {filename}: ERRO status - {str(status_error)}", "ERROR")
                                    
                                    # ANÁLISE AUTOMÁTICA DESABILITADA TEMPORARIAMENTE PARA ACELERAR PROCESSAMENTO
                                    # Para habilitar novamente, descomente o código abaixo:
                                    """
                                    add_log(f"[{idx+1}/{total_docs}] {filename}: Iniciando análise RAG...")
                                    try:
=======
                                        batch_size=50
                                    )
                                    
                                    total_pages = doc.get('metadata', {}).get('total_pages', 0)
                                    with log_lock:
                                        add_log(f"[{idx+1}/{total_docs}] {filename}: {total_pages} páginas, {chunks_count[0]} chunks")
                                
                                # Continuar com análise se tiver chunks
                                if chunks_count[0] > 0:
                                    with log_lock:
                                        add_log(f"[{idx+1}/{total_docs}] {filename}: Iniciando análise RAG...")
                                    
                                    try:
                                        with log_lock:
                                            add_log(f"[{idx+1}/{total_docs}] {filename}: Chamando GPT-4.1 para análise...")
                                        
>>>>>>> b5e15dc0d9832b696102fc7e6f8c4b6f2b1f24cf
                                        analise_result, resposta_bruta = components["analyzer"].analyze_full_document_rag(
                                            doc["document_id"],
                                            filename,
                                            return_raw_response=True
                                        )
<<<<<<< HEAD
                                        components["storage"].save_analysis(**analise_result)
                                        add_log(f"[{idx+1}/{total_docs}] {filename}: Análise salva com sucesso")
                                    except Exception as e:
                                        add_log(f"[{idx+1}/{total_docs}] {filename}: ERRO na análise - {str(e)}", "ERROR")
                                    """
                                    
                                    return {"success": True, "filename": filename, "idx": idx}
                                else:
                                    add_log(f"[{idx+1}/{total_docs}] {filename}: ⚠️ Nenhum chunk encontrado", "WARNING")
                                    return {"success": False, "filename": filename, "idx": idx, "error": "Nenhum chunk"}
                            
                            except Exception as proc_error:
                                add_log(f"[{idx+1}/{total_docs}] {filename}: ERRO no processamento - {str(proc_error)}", "ERROR")
=======
                                        
                                        with log_lock:
                                            add_log(f"[{idx+1}/{total_docs}] {filename}: Análise GPT-4.1 concluída. Resposta: {len(resposta_bruta)} chars")
                                        
                                        with log_lock:
                                            add_log(f"[{idx+1}/{total_docs}] {filename}: Salvando no banco...")
                                        
                                        # Salvar análise
                                        components["storage"].save_analysis(**analise_result)
                                        with log_lock:
                                            add_log(f"[{idx+1}/{total_docs}] {filename}: Análise salva com sucesso")
                                        
                                        # Deletar chunks após análise salva com sucesso
                                        document_id = doc.get("document_id")
                                        if document_id:
                                            deleted_count = components["vectorstore"].delete_chunks_by_document_id(document_id)
                                            with log_lock:
                                                add_log(f"[{idx+1}/{total_docs}] {filename}: {deleted_count} chunks deletados após análise")
                                        
                                        # Contar campos extraídos
                                        campos_extraidos = len([k for k in analise_result.keys() if k.startswith('p')])
                                        with log_lock:
                                            add_log(f"[{idx+1}/{total_docs}] {filename}: {campos_extraidos} campos extraídos")
                                        
                                        # Mostrar número do processo
                                        if analise_result.get('numero_processo'):
                                            with log_lock:
                                                add_log(f"[{idx+1}/{total_docs}] {filename}: Processo {analise_result.get('numero_processo')}")
                                        else:
                                            with log_lock:
                                                add_log(f"[{idx+1}/{total_docs}] {filename}: ATENÇÃO - Processo não identificado!", "WARNING")
                                        
                                        # Atualizar status para CONCLUIDO
                                        with log_lock:
                                            add_log(f"[{idx+1}/{total_docs}] {filename}: Atualizando status...")
                                        
                                        try:
                                            status_result = components["file_manager"].update_status(
                                                filename,
                                                "CONCLUIDO",
                                                document_id=doc["document_id"],
                                                total_chunks=chunks_count[0],
                                                total_pages=total_pages
                                            )
                                            if status_result:
                                                with log_lock:
                                                    add_log(f"[{idx+1}/{total_docs}] {filename}: Status CONCLUIDO atualizado")
                                            else:
                                                with log_lock:
                                                    add_log(f"[{idx+1}/{total_docs}] {filename}: AVISO - update_status retornou None", "WARNING")
                                        except Exception as status_error:
                                            with log_lock:
                                                add_log(f"[{idx+1}/{total_docs}] {filename}: ERRO status - {str(status_error)}", "ERROR")
                                        
                                        with log_lock:
                                            add_log(f"[{idx+1}/{total_docs}] ✅ {filename} concluído!")
                                        
                                        return {"success": True, "filename": filename, "idx": idx}
                                    
                                    except Exception as e:
                                        import traceback
                                        error_msg = str(e)
                                        tb_str = traceback.format_exc()
                                        with log_lock:
                                            add_log(f"[{idx+1}/{total_docs}] {filename}: ERRO DETALHADO:", "ERROR")
                                            add_log(f"Mensagem: {error_msg}", "ERROR")
                                            add_log(f"Traceback: {tb_str[:500]}", "ERROR")
                                        
                                        try:
                                            components["file_manager"].update_status(
                                                filename,
                                                "ERRO",
                                                error_message=f"Erro análise: {error_msg[:200]}"
                                            )
                                            with log_lock:
                                                add_log(f"[{idx+1}/{total_docs}] {filename}: Status ERRO atualizado", "INFO")
                                        except Exception as status_error:
                                            with log_lock:
                                                add_log(f"[{idx+1}/{total_docs}] {filename}: Erro ao atualizar status ERRO: {str(status_error)}", "ERROR")
                                        
                                        return {"success": False, "filename": filename, "idx": idx, "error": error_msg}
                                
                                else:
                                    with log_lock:
                                        add_log(f"[{idx+1}/{total_docs}] {filename}: Nenhum chunk encontrado, pulando análise")
                                    return {"success": False, "filename": filename, "idx": idx, "error": "Nenhum chunk"}
                            
                            except Exception as proc_error:
                                with log_lock:
                                    add_log(f"[{idx+1}/{total_docs}] {filename}: ERRO no processamento - {str(proc_error)}", "ERROR")
>>>>>>> b5e15dc0d9832b696102fc7e6f8c4b6f2b1f24cf
                                try:
                                    components["file_manager"].update_status(
                                        filename,
                                        "ERRO",
                                        error_message=f"Erro processamento: {str(proc_error)[:200]}"
                                    )
                                except:
                                    pass
                                return {"success": False, "filename": filename, "idx": idx, "error": str(proc_error)}
                        
<<<<<<< HEAD
                        # Processar documentos sequencialmente
                        completed_count = 0
                        add_log(f"🔄 Processando {total_docs} documentos sequencialmente...")
                        safe_update_logs(log_display, st.session_state.logs)
                        
                        for idx, pdf_file in enumerate(docs_to_process):
                            if st.session_state.stop_requested:
                                add_log("⏹️ Processamento interrompido pelo usuário")
                                break
                            
                            try:
                                add_log(f"📄 Processando [{idx+1}/{total_docs}]: {os.path.basename(pdf_file)}")
                                safe_update_logs(log_display, st.session_state.logs)
                                
                                result = process_single_document(pdf_file, idx, total_docs)
                                completed_count += 1
                                
                                # Log do resultado
                                if result and result.get("success"):
                                    add_log(f"✅ [{idx+1}/{total_docs}] {result.get('filename')} concluído")
                                else:
                                    error_msg = result.get('error', 'Erro desconhecido') if result else 'Nenhum resultado retornado'
                                    add_log(f"❌ [{idx+1}/{total_docs}] {result.get('filename', os.path.basename(pdf_file))} falhou: {error_msg}", "ERROR")
                                
                                # Atualizar progresso após cada documento
                                try:
                                    safe_update_progress(progress_bar, completed_count / total_docs)
                                    safe_update_logs(log_display, st.session_state.logs)
                                except:
                                    pass
                                
                            except Exception as e:
                                import traceback
                                error_details = traceback.format_exc()
                                filename = os.path.basename(pdf_file)
                                
                                add_log(f"❌ ERRO CRÍTICO ao processar [{idx+1}/{total_docs}] {filename}: {str(e)}", "ERROR")
                                add_log(f"Tipo do erro: {type(e).__name__}", "ERROR")
                                add_log(f"Traceback: {error_details[:1500]}", "ERROR")
                                
                                # Tentar atualizar status do arquivo para ERRO
                                try:
                                    components["file_manager"].update_status(
                                        filename,
                                        "ERRO",
                                        error_message=f"Erro processamento: {str(e)[:200]}"
                                    )
                                except:
                                    pass
                                
                                completed_count += 1  # Contar mesmo com erro
                                
                                # Atualizar progresso
                                try:
                                    safe_update_progress(progress_bar, completed_count / total_docs)
                                    safe_update_logs(log_display, st.session_state.logs)
                                except:
                                    pass
                        
                        add_log(f"✅ Processamento concluído: {completed_count}/{total_docs} documentos processados")
=======
                        # Processar documentos em paralelo
                        completed_count = [0]
                        with ThreadPoolExecutor(max_workers=num_threads) as executor:
                            # Submeter todas as tarefas
                            future_to_doc = {
                                executor.submit(process_single_document, pdf_file, idx, total_docs): (pdf_file, idx)
                                for idx, pdf_file in enumerate(docs_to_process)
                            }
                            
                            # Processar resultados conforme completam
                            for future in as_completed(future_to_doc):
                                if st.session_state.stop_requested:
                                    break
                                
                                result = future.result()
                                completed_count[0] += 1
                                
                                # Atualizar progresso
                                with progress_lock:
                                    try:
                                        safe_update_progress(progress_bar, completed_count[0] / total_docs)
                                        safe_update_logs(log_display, st.session_state.logs)
                                    except:
                                        pass
                        
                        add_log(f"✅ Processamento concluído: {completed_count[0]}/{total_docs} documentos processados")
>>>>>>> b5e15dc0d9832b696102fc7e6f8c4b6f2b1f24cf
                        
                        # Finalizar processamento
                        st.session_state.processing = False
                        safe_update_progress(progress_bar, 1.0)
                        safe_update_logs(log_display, st.session_state.logs)
                    
                    # Finalizar processamento
                    st.session_state.processing = False
                    safe_update_progress(progress_bar, 1.0)
                    add_log("✅ Processamento finalizado!")
                    safe_update_logs(log_display, st.session_state.logs)
                    
                    if not st.session_state.stop_requested:
                        safe_streamlit_call(st.balloons)
                        safe_streamlit_call(st.success, "🎉 Processamento em lote concluído!")
                    
                    st.rerun()
        else:
            st.warning("⚠️ Nenhum arquivo PDF encontrado na pasta especificada")
    elif folder_path:
        st.error(f"❌ Caminho não encontrado: {folder_path}")
    else:
        st.info("👆 Digite o caminho da pasta com os PDFs no painel lateral")

    # Exibir logs se houver
    if st.session_state.logs:
        st.markdown("---")
        st.markdown("### 📋 Logs Recentes")
        log_text = "\n".join(st.session_state.logs[-100:])
<<<<<<< HEAD
        if log_text.strip():
            st.code(log_text, language="text", line_numbers=False)
        else:
            st.info("ℹ️ Logs vazios")
    elif st.session_state.processing:
        st.info("⏳ Processamento em andamento... Os logs aparecerão aqui em breve.")
=======
        st.code(log_text, language="text")
>>>>>>> b5e15dc0d9832b696102fc7e6f8c4b6f2b1f24cf

# Aba 2: Visualizar Documentos Analisados
with tab2:
    st.markdown("### 📚 Documentos Analisados")
    st.markdown("Visualize e consulte as análises jurídicas já processadas.")
    
    try:
        # Buscar todas as análises
        all_analyses = components["storage"].get_all()
        
        if not all_analyses:
            st.info("📭 Nenhum documento analisado ainda. Processe alguns documentos na aba de Processamento.")
        else:
            # Filtros
            col1, col2, col3 = st.columns(3)
            
            with col1:
                filter_processo = st.text_input(
                    "🔍 Filtrar por Número do Processo",
                    placeholder="0000000-00.0000.0.00.0000",
                    help="Digite o número do processo para buscar"
                )
            
            with col2:
                filter_arquivo = st.text_input(
                    "📄 Filtrar por Nome do Arquivo",
                    placeholder="Nome do arquivo",
                    help="Digite parte do nome do arquivo"
                )
            
            with col3:
                filter_juiz = st.text_input(
                    "⚖️ Filtrar por Juiz",
                    placeholder="Nome do juiz",
                    help="Digite o nome do juiz"
                )
            
            # Aplicar filtros
            filtered_analyses = all_analyses
            
            if filter_processo:
                filtered_analyses = [a for a in filtered_analyses if filter_processo.lower() in a.get("numero_processo", "").lower()]
            
            if filter_arquivo:
                filtered_analyses = [a for a in filtered_analyses if filter_arquivo.lower() in a.get("arquivo_original", "").lower()]
            
            if filter_juiz:
                filtered_analyses = [a for a in filtered_analyses if filter_juiz.lower() in (a.get("juiz") or "").lower()]
            
            st.markdown(f"**Total encontrado:** {len(filtered_analyses)} documento(s)")
            st.markdown("---")
            
            # Lista de documentos
            if filtered_analyses:
                for idx, analysis in enumerate(filtered_analyses):
                    with st.expander(
                        f"📄 {analysis.get('arquivo_original', 'Sem nome')} - {analysis.get('numero_processo', 'Sem processo')}",
                        expanded=False
                    ):
                        col_info1, col_info2 = st.columns(2)
                        
                        with col_info1:
                            st.markdown("**📋 Informações do Processo**")
                            st.markdown(f"**Número do Processo:** {analysis.get('numero_processo', 'N/A')}")
                            st.markdown(f"**Arquivo:** {analysis.get('arquivo_original', 'N/A')}")
                            st.markdown(f"**Juiz:** {analysis.get('juiz', 'N/A')}")
                            st.markdown(f"**Vara:** {analysis.get('vara', 'N/A')}")
                            st.markdown(f"**Tribunal:** {analysis.get('tribunal', 'N/A')}")
                        
                        with col_info2:
                            st.markdown("**📅 Informações da Decisão**")
                            st.markdown(f"**Data da Decisão:** {analysis.get('data_decisao', 'N/A')}")
                            st.markdown(f"**Tipo de Decisão:** {analysis.get('tipo_decisao', 'N/A')}")
                            st.markdown(f"**Analisado por:** {analysis.get('analisado_por', 'N/A')}")
                            created_at = analysis.get('created_at')
                            if created_at:
                                try:
                                    from datetime import datetime
                                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                                    st.markdown(f"**Data de Análise:** {dt.strftime('%d/%m/%Y %H:%M')}")
                                except:
                                    st.markdown(f"**Data de Análise:** {created_at}")
                        
                        # Decisão do Juiz
                        decisao_resposta = analysis.get('decisao_resposta')
                        if decisao_resposta:
                            st.markdown("---")
                            st.markdown("### 🎯 Decisão do Juiz sobre Desconsideração")
                            st.markdown(f"**Resposta:** {decisao_resposta}")
                            
                            decisao_justificativa = analysis.get('decisao_justificativa')
                            if decisao_justificativa:
                                st.markdown(f"**Justificativa:** {decisao_justificativa}")
                            
                            decisao_referencia = analysis.get('decisao_referencia')
                            if decisao_referencia:
                                st.markdown(f"**Referência:** {decisao_referencia}")
                        
                        # Listar todas as perguntas e respostas
                        st.markdown("---")
                        st.markdown("### 📝 Respostas às Perguntas")
                        
                        # Carregar perguntas do prompt
                        def carregar_perguntas():
                            perguntas_map = {}
                            try:
                                with open("prompt_analise.txt", "r", encoding="utf-8") as f:
                                    content = f.read()
                                    import re
                                    # Buscar padrão [1.1], [1.2], etc. seguido da pergunta
                                    pattern = r'\[\*?(\d+)\.(\d+)\*?\]\s+(.+?)(?=\n\n\*\*p\d+_|$)'
                                    matches = re.finditer(pattern, content, re.DOTALL)
                                    for match in matches:
                                        bloco = match.group(1)
                                        num = match.group(2)
                                        pergunta_texto = match.group(3).strip()
                                        # Limpar marcação markdown e quebras de linha
                                        pergunta_texto = re.sub(r'\*\*', '', pergunta_texto)
                                        pergunta_texto = re.sub(r'\n+', ' ', pergunta_texto).strip()
                                        key = f"p{bloco}_{num}"
                                        perguntas_map[key] = pergunta_texto
                            except Exception as e:
                                pass
                            return perguntas_map
                        
                        perguntas_map = carregar_perguntas()
                        
                        # Agrupar campos por pergunta (p1_1_resposta, p1_1_justificativa, p1_1_referencia)
                        perguntas_dict = {}
                        for key, value in analysis.items():
                            if key.startswith('p') and ('_resposta' in key or '_justificativa' in key or '_referencia' in key):
                                # Extrair ID da pergunta (ex: p1_1 de p1_1_resposta)
                                pergunta_id = key.rsplit('_', 1)[0]
                                tipo = key.split('_')[-1]
                                
                                if pergunta_id not in perguntas_dict:
                                    perguntas_dict[pergunta_id] = {}
                                perguntas_dict[pergunta_id][tipo] = value
                        
                        # Ordenar perguntas
                        sorted_perguntas = sorted(perguntas_dict.items(), key=lambda x: (
                            int(x[0].split('_')[0][1:]),  # Número do bloco (p1, p2, etc)
                            int(x[0].split('_')[1])        # Número da pergunta (1, 2, etc)
                        ))
                        
                        # Exibir cada pergunta
                        for pergunta_id, campos in sorted_perguntas:
                            # Buscar texto da pergunta ou usar ID como fallback
                            pergunta_texto = perguntas_map.get(pergunta_id, pergunta_id.upper().replace('_', '.'))
                            # Limitar tamanho do título se muito longo
                            titulo = pergunta_texto if len(pergunta_texto) <= 100 else pergunta_texto[:97] + "..."
                            
                            with st.expander(f"**{titulo}**", expanded=False):
                                if 'resposta' in campos:
                                    st.markdown(f"**Resposta:** {campos['resposta']}")
                                if 'justificativa' in campos:
                                    st.markdown(f"**Justificativa:** {campos['justificativa']}")
                                if 'referencia' in campos:
                                    st.markdown(f"**Referência:** {campos['referencia']}")
                        
                        st.markdown("---")
            
            else:
                st.warning("🔍 Nenhum documento encontrado com os filtros aplicados.")
                
    except Exception as e:
        st.error(f"❌ Erro ao buscar análises: {str(e)}")
        st.exception(e)
