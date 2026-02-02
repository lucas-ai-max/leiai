-- Criar tabela para armazenar o prompt customizado
-- Execute este script no SQL Editor do Supabase

-- Criar tabela
CREATE TABLE IF NOT EXISTS prompt_config (
    id INTEGER PRIMARY KEY DEFAULT 1,
    prompt_text TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT single_row CHECK (id = 1)
);

-- Inserir prompt padrão
INSERT INTO prompt_config (id, prompt_text)
VALUES (1, 'Analise o documento jurídico e extraia estas informações em JSON:

{
  "numero_processo": "Número do processo",
  "tipo_documento": "Tipo do documento",
  "partes": "Partes envolvidas",
  "juiz": "Nome do juiz",
  "data_decisao": "Data da decisão",
  "resultado": "Resultado da decisão",
  "resumo": "Resumo breve"
}

Retorne APENAS o JSON válido, sem texto adicional.')
ON CONFLICT (id) DO NOTHING;

-- Desabilitar RLS (para permitir leitura/escrita pública)
ALTER TABLE prompt_config DISABLE ROW LEVEL SECURITY;

-- Comentário
COMMENT ON TABLE prompt_config IS 'Armazena o prompt customizado para análise de documentos';
