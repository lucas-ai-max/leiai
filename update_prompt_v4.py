import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

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
  "_debug_contexto_topo": "Copie as linhas contendo SEGURADO, TERCEIROS e os valores SIM/NÃO encontrados.",
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

try:
    print("Atualizando prompt V4 (Few-Shot Pattern)...")
    data = supabase.table('prompt_config').update({'prompt_text': NEW_PROMPT, 'updated_at': 'now()'}).eq('id', 1).execute()
    print("✅ Prompt V4 atualizado!")
except Exception as e:
    print(f"❌ Erro: {e}")
