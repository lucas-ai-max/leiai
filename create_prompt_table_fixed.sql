-- Script para criar a tabela prompt_config no Supabase
-- Execute este script no SQL Editor do Supabase

-- Remover tabela se existir (para recriar limpa)
DROP TABLE IF EXISTS public.prompt_config CASCADE;

-- Criar tabela
CREATE TABLE public.prompt_config (
    id INTEGER PRIMARY KEY DEFAULT 1,
    prompt_text TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT single_row CHECK (id = 1)
);

-- Inserir prompt padrão
INSERT INTO public.prompt_config (id, prompt_text)
VALUES (1, 'Analise o documento jurídico e extraia estas informações em formato JSON:

{
  "numero_processo": "Número do processo",
  "tipo_documento": "Tipo do documento",
  "partes": "Partes envolvidas",
  "juiz": "Nome do juiz",
  "data_decisao": "Data da decisão",
  "resultado": "Resultado da decisão",
  "resumo": "Resumo breve"
}

CHAVES OBRIGATÓRIAS (use exatamente estes nomes):
numero_processo, tipo_documento, partes, juiz, data_decisao, resultado, resumo

INSTRUÇÕES CRÍTICAS:
- Retorne APENAS um objeto JSON válido, sem texto antes ou depois
- Use EXATAMENTE as chaves listadas acima
- NÃO adicione chaves que não estão na lista acima
- NÃO remova chaves da lista acima
- Use "N/A" para campos não encontrados no documento
- Seja preciso e objetivo nas extrações
- Para listas, use arrays JSON: ["item1", "item2"]
- Para valores monetários, use formato "R$ X.XXX,XX"
- Para datas, use formato DD/MM/AAAA quando possível

Analise o documento e retorne o JSON com os dados extraídos usando APENAS as chaves acima:')
ON CONFLICT (id) DO NOTHING;

-- Desabilitar RLS (para permitir leitura/escrita pública)
ALTER TABLE public.prompt_config DISABLE ROW LEVEL SECURITY;

-- Criar políticas RLS caso RLS seja habilitado no futuro
DROP POLICY IF EXISTS "Allow public select on prompt_config" ON public.prompt_config;
CREATE POLICY "Allow public select on prompt_config"
ON public.prompt_config
FOR SELECT
TO public
USING (true);

DROP POLICY IF EXISTS "Allow public insert on prompt_config" ON public.prompt_config;
CREATE POLICY "Allow public insert on prompt_config"
ON public.prompt_config
FOR INSERT
TO public
WITH CHECK (true);

DROP POLICY IF EXISTS "Allow public update on prompt_config" ON public.prompt_config;
CREATE POLICY "Allow public update on prompt_config"
ON public.prompt_config
FOR UPDATE
TO public
USING (true)
WITH CHECK (true);

-- Comentário
COMMENT ON TABLE public.prompt_config IS 'Armazena o prompt customizado para análise de documentos';

-- Verificar se foi criada
SELECT 'Tabela prompt_config criada com sucesso!' as status;
