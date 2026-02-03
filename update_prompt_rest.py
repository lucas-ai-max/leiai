import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

NEW_PROMPT = """Analise a imagem/texto deste FORMULÁRIO PARA ANÁLISE DE SINISTRO e extraia os dados EXATAMENTE como aparecem. Retorne APENAS JSON:

{
  "analise_cobertura": {
    "segurado": "Valor do campo SEGURADO no topo azul (SIM/NÃO)",
    "terceiros": "Valor do campo TERCEIROS no topo azul (SIM/NÃO)"
  },
  "veiculo": {
    "placa": "Valor do campo PLACA SEGURADO",
    "modelo": "Valor do campo VEÍCULO",
    "valor_fipe": "Valor numérico do campo R$ FIPE MÊS FATO"
  },
  "sinistro": {
    "data": "DATA DO FATO",
    "hora": "HORA DO FATO",
    "esta_coberto": "Valor do campo ESTA COBERTO? (SIM/NÃO)",
    "assistencia_24h": "Valor do campo ASSISTÊNCIA 24 HRS"
  },
  "conclusao": {
    "ressarcimento": "Valor do campo RESSARCIMENTO no rodapé (SIM/NÃO)",
    "item_regulamento": "Texto do campo ITEM DO REGULAMENTO PARA SEGURADO",
    "solicitado_sindicancia": "Valor do campo SOLICITADO SINDICÂNCIA/PERÍCIA"
  },
  "observacoes": "Resumo breve do RELATO DO FATO EM BO"
}

IMPORTANTE:
- Extraia os valores exatos.
- Se o campo estiver vazio, retorne null.
- Atenção aos campos de SIM/NÃO no topo e rodapé."""

try:
    print("Tentando atualizar prompt ID 1...")
    data = supabase.table('prompt_config').update({'prompt_text': NEW_PROMPT, 'updated_at': 'now()'}).eq('id', 1).execute()
    print("✅ Prompt atualizado via REST! Registros:", len(data.data))
except Exception as e:
    print(f"⚠️ Erro Update: {e}")
    # Fallback insert
    try:
        print("Tentando inserir prompt ID 1...")
        supabase.table('prompt_config').insert({'id': 1, 'prompt_text': NEW_PROMPT}).execute()
        print("✅ Prompt inserido via REST!")
    except Exception as e2:
        print(f"❌ Erro Insert: {e2}")
