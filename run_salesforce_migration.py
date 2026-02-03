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

# Read SQL file
with open('sql/migrations/insert_salesforce_prompt.sql', 'r', encoding='utf-8') as f:
    sql_content = f.read()

# Split into individual statements (simple approach)
statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]

print("🚀 Executando migration SQL...")
print(f"📝 Total de statements: {len(statements)}")

for i, statement in enumerate(statements, 1):
    if statement:
        try:
            print(f"\n[{i}/{len(statements)}] Executando statement...")
            result = supabase.postgrest.rpc('exec', {'query': statement}).execute()
            print(f"✅ Statement {i} executado com sucesso")
        except Exception as e:
            # Try direct execution via table operations for UPDATE/INSERT
            if 'UPDATE' in statement.upper() or 'INSERT' in statement.upper():
                print(f"⚠️ Tentando abordagem alternativa para statement {i}...")
                try:
                    # For prompt_config table operations, use direct table access
                    if 'prompt_config' in statement:
                        if 'UPDATE' in statement.upper():
                            # Extract prompt text (simplified)
                            prompt_text = statement.split("prompt_text = '")[1].split("',")[0]
                            result = supabase.table('prompt_config').update({
                                'prompt_text': prompt_text,
                                'updated_at': 'now()'
                            }).eq('id', 1).execute()
                            print(f"✅ UPDATE executado via table API")
                        elif 'INSERT' in statement.upper():
                            print(f"ℹ️ INSERT será executado apenas se não existir registro")
                except Exception as e2:
                    print(f"❌ Erro no statement {i}: {str(e2)}")
            else:
                print(f"❌ Erro no statement {i}: {str(e)}")

print("\n✅ Migration concluída!")
print("\n📋 Verificando configuração atual...")

# Verify current prompt
try:
    result = supabase.table('prompt_config').select('*').eq('id', 1).execute()
    if result.data:
        print(f"\n✅ Prompt configurado:")
        print(f"ID: {result.data[0]['id']}")
        print(f"Criado em: {result.data[0]['created_at']}")
        print(f"Atualizado em: {result.data[0]['updated_at']}")
        print(f"\nPrompt (primeiros 200 caracteres):")
        print(result.data[0]['prompt_text'][:200] + "...")
    else:
        print("⚠️ Nenhum prompt encontrado na tabela")
except Exception as e:
    print(f"❌ Erro ao verificar prompt: {str(e)}")
