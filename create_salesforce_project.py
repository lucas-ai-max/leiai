# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

# Create Supabase client
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_ROLE_KEY')
)

SALESFORCE_PROJECT_ID = '00000000-0000-0000-0000-000000000001'

print("Criando projeto Salesforce...")

try:
    # Insert Salesforce project
    result = supabase.table('projeto').upsert({
        'id': SALESFORCE_PROJECT_ID,
        'nome': 'Importações Salesforce'
    }, on_conflict='id').execute()
    
    print("✅ Projeto Salesforce criado/atualizado com sucesso!")
    print(f"   ID: {SALESFORCE_PROJECT_ID}")
    print(f"   Nome: Importações Salesforce")
    
    # Verify
    verify = supabase.table('projeto').select('*').eq('id', SALESFORCE_PROJECT_ID).execute()
    if verify.data:
        print(f"\n✅ Verificação:")
        print(f"   Projeto encontrado: {verify.data[0]['nome']}")
        print(f"   Criado em: {verify.data[0]['created_at']}")
    else:
        print("\n⚠️ Projeto não encontrado após inserção")
        
except Exception as e:
    print(f"❌ Erro ao criar projeto: {str(e)}")
    print("\n💡 Execute este SQL manualmente no Supabase SQL Editor:")
    print("""
INSERT INTO projeto (id, nome)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'Importações Salesforce'
)
ON CONFLICT (id) DO NOTHING;
""")
