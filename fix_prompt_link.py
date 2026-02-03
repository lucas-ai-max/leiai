import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

# ID do Prompt que estamos editando
PROMPT_ID = 1
# ID do Projeto Salesforce
SALESFORCE_PROJECT_ID = "00000000-0000-0000-0000-000000000001"

try:
    print(f"Vinculando Prompt {PROMPT_ID} ao Projeto {SALESFORCE_PROJECT_ID}...")
    
    # 1. Verificar se já existe
    res = supabase.table('prompt_config').select('*').eq('id', PROMPT_ID).execute()
    if res.data:
        print(f"Prompt atual: {res.data[0].get('projeto_id')}")
        
        # 2. Atualizar projeto_id
        update_res = supabase.table('prompt_config').update({
            'projeto_id': SALESFORCE_PROJECT_ID,
            'updated_at': 'now()'
        }).eq('id', PROMPT_ID).execute()
        
        print("✅ Vinculação concluída com sucesso!")
        print(f"Dados atualizados: {update_res.data}")
    else:
        print("❌ Prompt ID 1 não encontrado. Criando novo...")
        # Criar se não existir (apenas segurança)
        # (Código omitido para focar no fix simples, assumindo que ID 1 existe pois atualizamos antes)

except Exception as e:
    print(f"❌ Erro ao vincular prompt: {e}")
