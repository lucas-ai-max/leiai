import time
import json
import os
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor
from supabase import create_client
from config import settings
from gemini_client import GeminiClient
from storage import ResponseStorage

# Variáveis globais (inicializadas no main_loop)
supabase = None
ai_client = None
storage = None
semaphore = None

def load_prompt():
    """Carrega seu prompt padrão"""
    try:
        with open("prompt_analise.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print("⚠️ Arquivo prompt_analise.txt não encontrado. Usando prompt padrão.")
        return "Analise o documento jurídico e extraia as informações solicitadas."

PROMPT_BASE = load_prompt()

def process_file_task(record):
    """Tarefa individual de processamento"""
    filename = record['filename']
    storage_path = record.get('storage_path')
    doc_id_db = record['id']
    
    with semaphore:  # Garante limite de threads ativas
        tmp_path = None
        try:
            print(f"▶️ Processando: {filename}")
            
            # 1. Marcar como PROCESSANDO
            supabase.table(settings.TABLE_GERENCIAMENTO).update(
                {"status": "PROCESSANDO", "started_at": "now()"}
            ).eq("id", doc_id_db).execute()

            # 2. Baixar do Supabase Storage
            if not storage_path:
                raise ValueError("Caminho do arquivo no storage não encontrado")

            print(f"   ⬇️ Baixando: {storage_path}")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                # Baixa do bucket 'processos'
                data = supabase.storage.from_("processos").download(storage_path)
                tmp.write(data)
                tmp_path = tmp.name

            # 3. Análise com Gemini
            print(f"   🤖 Enviando para IA...")
            prompt_final = f"{PROMPT_BASE}\n\nResponda estritamente em JSON, seguindo as chaves do modelo."
            
            json_text = ai_client.analyze_document(tmp_path, prompt_final)
            data_analise = json.loads(json_text)
            
            # Garantir campos obrigatórios para o storage
            data_analise['arquivo_original'] = filename
            data_analise['numero_processo'] = data_analise.get('numero_processo', 'N/A')
            
            # 4. Salvar no Banco (Tabela de Respostas)
            storage.save_analysis(**data_analise)
            
            # 5. Finalizar Fila
            supabase.table(settings.TABLE_GERENCIAMENTO).update(
                {"status": "CONCLUIDO", "completed_at": "now()"}
            ).eq("id", doc_id_db).execute()
            
            # 6. Remover arquivo do Storage após processamento bem-sucedido
            try:
                supabase.storage.from_("processos").remove([storage_path])
                print(f"   🗑️ Arquivo removido do Storage: {storage_path}")
            except Exception as delete_error:
                print(f"⚠️ Erro ao remover arquivo do Storage: {delete_error}")
                # Não falha o processamento se não conseguir deletar
            
            print(f"✅ Sucesso: {filename}")

        except Exception as e:
            print(f"❌ Erro {filename}: {str(e)}")
            import traceback
            error_msg = str(e)[:500]  # Limitar tamanho da mensagem
            # Salvar erro no banco para o Front ver
            try:
                supabase.table(settings.TABLE_GERENCIAMENTO).update(
                    {"status": "ERRO", "error_message": error_msg}
                ).eq("id", doc_id_db).execute()
            except Exception as update_error:
                print(f"⚠️ Erro ao atualizar status no banco: {update_error}")
            
        finally:
            # Limpar arquivo temporário local
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception as cleanup_error:
                    print(f"⚠️ Erro ao limpar arquivo temporário: {cleanup_error}")

def main_loop():
    # Inicialização (apenas quando executar)
    global supabase, ai_client, storage, semaphore
    
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    ai_client = GeminiClient()
    storage = ResponseStorage()
    semaphore = threading.Semaphore(settings.MAX_WORKERS)
    
    print(f"🚀 Worker iniciado! Só processa ao clicar em 'Iniciar processamento' no frontend.")
    
    executor = ThreadPoolExecutor(max_workers=settings.MAX_WORKERS)
    TABLE_PROCESSAR_AGORA = "processar_agora"
    
    while True:
        try:
            # Só processa quando houver registro em processar_agora (botão no frontend)
            trigger_resp = supabase.table(TABLE_PROCESSAR_AGORA).select("id, projeto_id").limit(settings.MAX_WORKERS).execute()
            triggers = trigger_resp.data if trigger_resp.data else []
            
            if not triggers:
                time.sleep(5)
                continue
            
            for trigger in triggers:
                projeto_id = trigger.get("projeto_id")
                try:
                    query = supabase.table(settings.TABLE_GERENCIAMENTO).select("*").eq("status", "PENDENTE").not_.is_("storage_path", "null").limit(settings.MAX_WORKERS)
                    if projeto_id:
                        query = query.eq("projeto_id", projeto_id)
                    response = query.execute()
                    files = response.data if response.data else []
                    if files:
                        print(f"📦 Processando {len(files)} arquivo(s) (projeto: {projeto_id or 'todos'})")
                        for file_record in files:
                            executor.submit(process_file_task, file_record)
                        time.sleep(2)
                finally:
                    try:
                        supabase.table(TABLE_PROCESSAR_AGORA).delete().eq("id", trigger["id"]).execute()
                    except Exception:
                        pass
            
            time.sleep(2)

        except KeyboardInterrupt:
            print("\n⏹️ Worker interrompido pelo usuário")
            executor.shutdown(wait=True)
            break
        except Exception as e:
            print(f"⚠️ Erro no loop: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(5)

if __name__ == "__main__":
    main_loop()
