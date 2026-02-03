-- Tabela para gerenciar os Casos vindos da Salesforce
CREATE TABLE IF NOT EXISTS casos_processamento (
    id BIGSERIAL PRIMARY KEY,
    numero_caso TEXT NOT NULL UNIQUE,
    zip_url TEXT,
    status TEXT DEFAULT 'PENDENTE', -- PENDENTE, BAIXANDO, PROCESSA_ZIP, CONCLUIDO, ERRO, IGNORADO
    metadata JSONB DEFAULT '{}'::jsonb, -- Para guardar info extra da API
    projeto_id UUID REFERENCES projeto(id), -- Vincular ao projeto para o worker pegar
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    error_message TEXT
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_casos_status ON casos_processamento(status);
CREATE INDEX IF NOT EXISTS idx_casos_numero ON casos_processamento(numero_caso);

-- Atualizar tabela de documentos para vincular ao caso
ALTER TABLE documento_gerenciamento 
ADD COLUMN IF NOT EXISTS caso_id BIGINT REFERENCES casos_processamento(id),
ADD COLUMN IF NOT EXISTS origem TEXT DEFAULT 'UPLOAD'; -- 'UPLOAD' ou 'SALESFORCE'

CREATE INDEX IF NOT EXISTS idx_doc_caso_id ON documento_gerenciamento(caso_id);
