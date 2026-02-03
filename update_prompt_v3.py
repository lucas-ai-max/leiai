import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

NEW_PROMPT = """Analise este FORMULÁRIO DE SINISTRO.

🎯 OBJETIVO: Extrair dados exatos do cabeçalho e detalhes do veículo.

⚠️ REGRA DE OURO (COBERTURA):
O formulário tem duas partes distintas:
1. CABEÇALHO AZUL (Topo): Indica a cobertura CONTRATADA/INICIAL. Tem campos "SEGURADO: [VALOR]" e "TERCEIROS: [VALOR]".
2. CONCLUSÃO (Rodapé): Indica o parecer final (Deferido/Indeferido).

Para os campos 'analise_cobertura', extraia APENAS do CABEÇALHO AZUL.
Se no topo está escrito "SIM", a resposta É "SIM", mesmo que a conclusão lá embaixo seja "Negado".
NÃO misture a decisão final com a cobertura inicial.

Retorne JSON:
{
  "_debug_contexto_topo": "Copie as primeiras 3 linhas de texto extraído aqui para conferência.",
  "analise_cobertura": {
    "segurado": "Valor exato abaixo de SEGURADO no topo (SIM/NÃO)",
    "terceiros": "Valor exato abaixo de TERCEIROS no topo (SIM/NÃO)"
  },
  "veiculo": {
    "placa": "Valor do campo PLACA",
    "modelo": "Valor do campo VEÍCULO",
    "fipe": "Valor numérico em R$ FIPE"
  },
  "sinistro": {
    "data": "DATA DO FATO",
    "hora": "HORA DO FATO",
    "coberto_perg": "Valor de 'ESTA COBERTO?'"
  },
  "conclusao": {
    "obs": "Resumo do RELATO DO FATO ou CONCLUSÃO final",
    "ressarcimento": "Valor de RESSARCIMENTO (SIM/NÃO)"
  }
}"""

try:
    print("Atualizando prompt V3 (Regra de Ouro + Debug)...")
    data = supabase.table('prompt_config').update({'prompt_text': NEW_PROMPT, 'updated_at': 'now()'}).eq('id', 1).execute()
    print("✅ Prompt V3 atualizado!")
except Exception as e:
    print(f"❌ Erro: {e}")
