import time
import threading
from concurrent.futures import ThreadPoolExecutor
from supabase import create_client
from config import settings
from salesforce_client import SalesforceClient
from zip_processor import ZipProcessor

# Globals
supabase = None
sf_client = None
zip_processor = None
semaphore = None

def process_case_task(case_record):
    """
    1. Fetch URL from Salesforce
    2. Process ZIP
    3. Update Status
    """
    case_id = case_record['id']
    case_number = case_record['numero_caso']
    
    with semaphore:
        try:
            print(f"▶️ Iniciando Caso: {case_number}")
            
            # CRITICAL: Mark as PROCESSANDO immediately to prevent duplicate processing
            update_result = supabase.table(settings.TABLE_CASOS).update(
                {"status": "PROCESSANDO", "updated_at": "now()"}
            ).eq("id", case_id).eq("status", "PENDENTE").execute()
            
            # If no rows updated, another thread already grabbed this case
            if not update_result.data or len(update_result.data) == 0:
                print(f"   ⏭️ Caso {case_number} já está sendo processado por outra thread, pulando.")
                return
            
            # 1. Fetch ZIP URL
            print(f"   🔎 Buscando caso {case_number} na API...")
            zip_url = sf_client.get_case_zip_url(case_number)
            
            if not zip_url:
                print(f"   ⚠️ Aviso: Nenhum ZIP encontrado para caso {case_number}.")
                supabase.table(settings.TABLE_CASOS).update(
                    {"status": "CONCLUIDO", "error_message": "⚠️ Nenhum arquivo ZIP disponível", "updated_at": "now()"}
                ).eq("id", case_id).execute()
                return
            
            print(f"   ✅ ZIP encontrado: {zip_url[:50]}...")
            
            # Update DB
            print(f"   💾 Atualizando banco de dados...")
            supabase.table(settings.TABLE_CASOS).update(
                {"zip_url": zip_url, "status": "PROCESSA_ZIP"}
            ).eq("id", case_id).execute()
            print(f"   ✅ Status atualizado: PROCESSA_ZIP")
            
            # 2. Process ZIP
            print(f"   📦 Iniciando processamento do ZIP...")
            
            # Use dedicated Salesforce project ID if none provided
            projeto_id = case_record.get('projeto_id') or settings.SALESFORCE_PROJECT_ID
            
            result = zip_processor.process_zip_url(
                case_number, 
                zip_url, 
                case_id, 
                projeto_id=projeto_id
            )
            
            if result['success']:
                print(f"   ✅ ZIP processado com sucesso!")
                print(f"   💾 Marcando caso como CONCLUÍDO...")
                supabase.table(settings.TABLE_CASOS).update(
                    {"status": "CONCLUIDO", "updated_at": "now()", "error_message": None}
                ).eq("id", case_id).execute()
                print(f"✅ Caso {case_number} processado com sucesso!")
            else:
                raise ValueError(result['error'])

        except Exception as e:
            error_msg = str(e)[:1000]
            print(f"❌ Erro Caso {case_number}: {error_msg}")
            print(f"   💾 Marcando caso como ERRO no banco...")
            supabase.table(settings.TABLE_CASOS).update(
                {"status": "ERRO", "error_message": error_msg, "updated_at": "now()"}
            ).eq("id", case_id).execute()
            print(f"   ✅ Status de erro registrado.")

def main_loop():
    global supabase, sf_client, zip_processor, semaphore
    
    # Initialize
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    sf_client = SalesforceClient()
    zip_processor = ZipProcessor()
    
    # Max concurrent imports (don't kill Salesforce API)
    # 5-10 is reasonable.
    start_workers = 5 
    semaphore = threading.Semaphore(start_workers)
    executor = ThreadPoolExecutor(max_workers=start_workers)
    
    print(f"🚀 Pipeline Salesforce Iniciado! ({start_workers} threads)")
    
    # Iniciar Worker de Análise em paralelo
    import worker
    print("🤖 Iniciando Worker de Análise (AI) em background...")
    ai_thread = threading.Thread(target=worker.main_loop, daemon=True)
    ai_thread.start()
    
    print(f"   Aguardando casos na tabela '{settings.TABLE_CASOS}'...")

    while True:
        try:
            # Poll PENDING cases
            response = supabase.table(settings.TABLE_CASOS)\
                .select("*")\
                .eq("status", "PENDENTE")\
                .limit(start_workers)\
                .execute()
                
            cases = response.data if response.data else []
            
            if not cases:
                time.sleep(5)
                continue
            
            print(f"📦 Encontrados {len(cases)} casos pendentes.")
            for case in cases:
                executor.submit(process_case_task, case)
            
            time.sleep(2)
            
        except KeyboardInterrupt:
            print("\n⏹️ Pipeline interrompido.")
            executor.shutdown(wait=True)
            break
        except Exception as e:
            print(f"⚠️ Erro no loop principal: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main_loop()
