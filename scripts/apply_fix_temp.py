# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv
from supabase import create_client
import sys

# Load environment variables
load_dotenv()

# Create Supabase client
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not url or not key:
    print("❌ Erro: SUPABASE_URL ou SUPABASE_SERVICE_ROLE_KEY não encontrados no .env")
    sys.exit(1)

supabase = create_client(url, key)

sql_file = 'sql/fixes/fix_add_tamanho_bytes.sql'

print(f"🚀 Lendo arquivo SQL: {sql_file}")

try:
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
except FileNotFoundError:
    print(f"❌ Erro: Arquivo {sql_file} não encontrado.")
    sys.exit(1)

# Split into individual statements (simple approach)
statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]

print("🚀 Executando fix SQL...")
print(f"📝 Total de statements: {len(statements)}")

for i, statement in enumerate(statements, 1):
    if statement:
        try:
            print(f"\n[{i}/{len(statements)}] Executando statement...")
            # Use rpc 'exec' as seen in other scripts
            result = supabase.postgrest.rpc('exec', {'query': statement}).execute()
            print(f"✅ Statement {i} executado com sucesso")
        except Exception as e:
             # Basic retry implies maybe it's not an RPC exec compatible query or needs direct handling?
             # For ADD COLUMN, specific RPC exec is usually needed if direct DDL isn't exposed.
             print(f"❌ Erro no statement {i}: {str(e)}")
             # Don't exit, might be 'already exists'
             
print("\n✅ Execução finalizada!")
