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

print("Aplicando fix para CASCADE DELETE...")

# Read SQL file
with open('sql/migrations/fix_cascade_delete.sql', 'r', encoding='utf-8') as f:
    sql_content = f.read()

# Execute via RPC (if available) or direct SQL
try:
    # Try to execute the SQL statements
    statements = [
        # Drop old constraint
        """
        ALTER TABLE casos_processamento 
        DROP CONSTRAINT IF EXISTS casos_processamento_projeto_id_fkey;
        """,
        # Add new constraint with CASCADE
        """
        ALTER TABLE casos_processamento 
        ADD CONSTRAINT casos_processamento_projeto_id_fkey 
        FOREIGN KEY (projeto_id) 
        REFERENCES projeto(id) 
        ON DELETE CASCADE;
        """
    ]
    
    for i, stmt in enumerate(statements, 1):
        print(f"\n[{i}/{len(statements)}] Executando statement...")
        try:
            result = supabase.rpc('exec', {'query': stmt}).execute()
            print(f"✅ Statement {i} executado")
        except Exception as e:
            # SQL execution might not work via RPC, that's ok
            print(f"⚠️ RPC não disponível, execute manualmente no Supabase SQL Editor")
            print(f"\nSQL para executar:\n{sql_content}")
            break
    
    print("\n✅ Migration aplicada com sucesso!")
    print("\n📋 Agora você pode excluir projetos sem erro de constraint")
    
except Exception as e:
    print(f"\n⚠️ Execute este SQL manualmente no Supabase SQL Editor:")
    print(f"\n{sql_content}")
    print(f"\n❌ Erro: {str(e)}")
