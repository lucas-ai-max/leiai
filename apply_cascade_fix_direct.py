# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv
import psycopg2

# Load environment variables
load_dotenv()

# Parse Supabase URL to get database connection details
# Format: https://PROJECT_REF.supabase.co
supabase_url = os.getenv('SUPABASE_URL')
project_ref = supabase_url.replace('https://', '').replace('.supabase.co', '')

# Supabase PostgreSQL connection string
# Format: postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres
db_password = os.getenv('SUPABASE_DB_PASSWORD', 'your_db_password_here')

conn_string = f"postgresql://postgres.{project_ref}:{db_password}@aws-0-sa-east-1.pooler.supabase.com:6543/postgres"

print("⚠️ Para executar a migration, você tem 2 opções:\n")

print("OPÇÃO 1 - Supabase SQL Editor (RECOMENDADO):")
print("=" * 60)
print("1. Acesse: https://supabase.com/dashboard/project/" + project_ref + "/sql/new")
print("2. Cole e execute este SQL:\n")

sql = """-- Migration: Corrigir constraint de chave estrangeira
-- Adiciona ON DELETE CASCADE para permitir exclusão de projetos com casos vinculados

-- 1. Remover a constraint antiga
ALTER TABLE casos_processamento 
DROP CONSTRAINT IF EXISTS casos_processamento_projeto_id_fkey;

-- 2. Adicionar nova constraint com ON DELETE CASCADE
ALTER TABLE casos_processamento 
ADD CONSTRAINT casos_processamento_projeto_id_fkey 
FOREIGN KEY (projeto_id) 
REFERENCES projeto(id) 
ON DELETE CASCADE;

-- Verificar
SELECT 'Constraint atualizada com sucesso!' AS status;"""

print(sql)
print("\n" + "=" * 60)

print("\nOPÇÃO 2 - Via psycopg2 (se tiver senha do DB):")
print("=" * 60)
print("Edite este arquivo e adicione SUPABASE_DB_PASSWORD no .env")
print("Depois execute: python apply_cascade_fix_direct.py")
print("=" * 60)

print("\n✅ Após executar, você poderá excluir projetos sem erro de constraint!")
