import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

try:
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cursor = conn.cursor()
    
    with open(r'e:\Projetos Cursor\Leiai -Antigravity\leiai\sql\migrations\insert_salesforce_prompt.sql', 'r', encoding='utf-8') as f:
        sql = f.read()
        cursor.execute(sql)
        conn.commit()
        print("✅ Prompt atualizado com sucesso no Supabase!")
        
    cursor.close()
    conn.close()
except Exception as e:
    print(f"❌ Erro ao atualizar prompt: {e}")
