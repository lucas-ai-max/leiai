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

# New prompt with coverage analysis fields
new_prompt = '''Analise o documento e extraia as seguintes informações em JSON:

{
  "numero_processo": "Número do processo (se houver)",
  "tipo_documento": "Tipo do documento",
  "partes": "Partes envolvidas",
  "data_documento": "Data do documento",
  "analise_cobertura": {
    "segurado": "SIM ou NÃO - indica se há cobertura para segurado",
    "terceiros": "SIM ou NÃO - indica se há cobertura para terceiros"
  },
  "observacoes": "Observações relevantes sobre a análise de cobertura"
}

IMPORTANTE:
- Para os campos "segurado" e "terceiros", retorne APENAS "SIM" ou "NÃO"
- Se não encontrar informação sobre cobertura, retorne "NÃO"
- Retorne APENAS o JSON válido, sem texto adicional'''

print("Atualizando prompt no Supabase...")

try:
    # Update the prompt
    result = supabase.table('prompt_config').update({
        'prompt_text': new_prompt
    }).eq('id', 1).execute()
    
    print("✅ Prompt atualizado com sucesso!")
    
    # Verify
    verify = supabase.table('prompt_config').select('*').eq('id', 1).execute()
    if verify.data:
        print(f"\n✅ Verificação:")
        print(f"ID: {verify.data[0]['id']}")
        print(f"Atualizado em: {verify.data[0]['updated_at']}")
        print(f"\nPrompt configurado (primeiros 300 caracteres):")
        print(verify.data[0]['prompt_text'][:300] + "...")
        
except Exception as e:
    print(f"❌ Erro ao atualizar prompt: {str(e)}")
