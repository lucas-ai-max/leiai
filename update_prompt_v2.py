import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

NEW_PROMPT = """Analise este FORMULÁRIO DE SINISTRO.

⚠️ POSICIONAMENTO CRÍTICO:
1. No TOPO da página, existe um cabeçalho azul com 'ANÁLISE DE COBERTURA PARA:'.
2. Logo abaixo de 'SEGURADO', leia o valor (SIM ou NÃO).
3. Logo abaixo de 'TERCEIROS', leia o valor (SIM ou NÃO).

IGNORE o parecer final ou observações para preencher estes dois campos. Quero o status da cobertura inicial listado no TOPO.

Retorne JSON:
{
  "analise_cobertura": {
    "segurado": "VALOR DO TOPO (SIM/NÃO)",
    "terceiros": "VALOR DO TOPO (SIM/NÃO)"
  },
  "veiculo": {
    "placa": "Valor do campo PLACA",
    "modelo": "Valor do campo VEÍCULO"
  },
  "conclusao": {
    "obs": "Resumo do motivo da negativa/aprovação (texto do campo OBS ou Relato)",
    "resultado_final": "Parecer final (DEFERIDO/INDEFERIDO) baseado no contexto"
  }
}"""

try:
    print("Atualizando prompt V2 (Foco no Topo)...")
    data = supabase.table('prompt_config').update({'prompt_text': NEW_PROMPT, 'updated_at': 'now()'}).eq('id', 1).execute()
    print("✅ Prompt V2 atualizado!")
except Exception as e:
    print(f"❌ Erro: {e}")
