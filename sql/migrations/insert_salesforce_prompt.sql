-- Migration: Inserir prompt específico para Salesforce
-- Este prompt extrai campos da ANÁLISE DE COBERTURA dos documentos do Salesforce

-- Primeiro, garantir que a tabela prompt_config existe
CREATE TABLE IF NOT EXISTS prompt_config (
    id INTEGER PRIMARY KEY DEFAULT 1,
    prompt_text TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT single_row CHECK (id = 1)
);

-- Atualizar o prompt para incluir os campos de Análise de Cobertura
UPDATE prompt_config
SET 
    prompt_text = 'Analise a imagem/texto deste FORMULÁRIO PARA ANÁLISE DE SINISTRO e extraia os dados EXATAMENTE como aparecem. Retorne APENAS JSON:

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
- Atenção aos campos de SIM/NÃO no topo e rodapé.',
    updated_at = NOW()
WHERE id = 1;

-- Se não existir registro, inserir (fallback)
INSERT INTO prompt_config (id, prompt_text)
SELECT 1, 'Analise a imagem/texto deste FORMULÁRIO PARA ANÁLISE DE SINISTRO e extraia os dados EXATAMENTE como aparecem. Retorne APENAS JSON:

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
- Atenção aos campos de SIM/NÃO no topo e rodapé.'
WHERE NOT EXISTS (SELECT 1 FROM prompt_config WHERE id = 1);

-- Desabilitar RLS para permitir acesso público
ALTER TABLE prompt_config DISABLE ROW LEVEL SECURITY;

-- Comentário
COMMENT ON TABLE prompt_config IS 'Armazena o prompt customizado para análise de documentos Salesforce';
