import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

# Prompt V5: Baseado na V4 (Pattern Matching), mas SEM o campo de debug
NEW_PROMPT = """Analise este FORMULÁRIO DE SINISTRO.

🎯 ESTRUTURA DE LEITURA (CRÍTICO):
O texto extraído do PDF pode vir "quebrado" verticalmente. Exemplo real:
"SEGURADO:"
"TERCEIROS:"
"SIM"
"SIM"

Neste caso, a lógica é sequencial:
- O primeiro "SIM" pertence ao primeiro rótulo ("SEGURADO").
- O segundo "SIM" pertence ao segundo rótulo ("TERCEIROS").

Se você encontrar os rótulos "SEGURADO:" e "TERCEIROS:" seguidos por dois valores (SIM/NÃO) em linhas abaixo, associe-os na ordem de aparição.

Retorne JSON:
{
  "analise_cobertura": {
    "segurado": "Valor associado ao rótulo SEGURADO (Geralmente o primeiro valor abaixo)",
    "terceiros": "Valor associado ao rótulo TERCEIROS (Geralmente o segundo valor abaixo)"
  },
  "veiculo": {
    "placa": "Valor do campo PLACA",
    "modelo": "Valor do campo VEÍCULO"
  },
  "sinistro": {
    "data": "DATA DO FATO",
    "hora": "HORA DO FATO",
    "coberto_perg": "Valor de 'ESTA COBERTO?'"
  },
  "conclusao": {
    "obs": "Resumo do RELATO DO FATO ou CONCLUSÃO final nos campos inferiores",
    "ressarcimento": "Valor de RESSARCIMENTO"
  }
}
IGNORE completamente o parecer final ("Indefiro", "Nego", "Sem cobertura") para preencher os campos de 'analise_cobertura'. Eles se referem EXCLUSIVAMENTE ao cabeçalho.
"""

# ID do Prompt (1)
PROMPT_ID = 1

try:
    print("Atualizando prompt V5 (Cleanup Debug)...")
    data = supabase.table('prompt_config').update({'prompt_text': NEW_PROMPT, 'updated_at': 'now()'}).eq('id', PROMPT_ID).execute()
    print("✅ Prompt V5 atualizado (Debug removido)!")
except Exception as e:
    print(f"❌ Erro: {e}")
