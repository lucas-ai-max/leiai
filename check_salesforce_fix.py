import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

PROJ_ID = '00000000-0000-0000-0000-000000000001'

try:
    res = supabase.table('projeto').select('*').eq('id', PROJ_ID).execute()
    if res.data:
        print(f"✅ Projeto encontrado: {res.data[0]['nome']}")
    else:
        print("❌ Projeto NÃO encontrado! Criando...")
        supabase.table('projeto').insert({'id': PROJ_ID, 'nome': 'Importações Salesforce'}).execute()
        print("✅ Projeto criado agora.")
except Exception as e:
    print(f"❌ Erro: {e}")
