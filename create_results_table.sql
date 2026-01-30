-- Tabela para armazenar os resultados das análises
-- Execute este script no SQL Editor do Supabase

CREATE TABLE IF NOT EXISTS resultados_analise (
    id BIGSERIAL PRIMARY KEY,
    arquivo_original TEXT NOT NULL,
    data_processamento TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    dados_json JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índice para busca rápida
CREATE INDEX IF NOT EXISTS idx_resultados_arquivo ON resultados_analise(arquivo_original);
CREATE INDEX IF NOT EXISTS idx_resultados_data ON resultados_analise(data_processamento);

-- Desabilitar RLS (ou criar políticas se necessário)
ALTER TABLE resultados_analise DISABLE ROW LEVEL SECURITY;

-- Comentário
COMMENT ON TABLE resultados_analise IS 'Armazena os resultados das análises de documentos para exportação em CSV';
