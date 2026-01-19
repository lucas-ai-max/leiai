# Sistema de Análise de Processos Jurídicos

Sistema inteligente para análise de processos jurídicos usando **o1 (GPT-4.1)**, **Docling** e **Supabase**.

## 🚀 Features

✅ Processamento paralelo (rápido)  
✅ o1 (GPT-4.1) para máxima qualidade de análise  
✅ Referências automáticas (página + arquivo)  
✅ Salvar respostas por documento  
✅ Prompt customizável  
✅ Interface Streamlit moderna  

## 📋 Instalação

### Opção 1: Modo Leve (Recomendado - Menos CPU/RAM)

Para não sobrecarregar o CPU, use o modo leve que não instala docling (torch, transformers, etc.):

```bash
pip install -r requirements-lite.txt
```

⚠️ **Modo leve:**
- ✅ Usa `pypdf` (muito leve)
- ✅ Sem dependências pesadas (torch, transformers)
- ❌ Sem OCR (texto em imagens não será extraído)
- ❌ Extração de tabelas mais básica

### Opção 2: Modo Completo (Com OCR e tabelas)

Para funcionalidades completas com OCR e tabelas complexas:

```bash
pip install -r requirements.txt
```

⚠️ **Modo completo:**
- ✅ Extração completa com `docling`
- ✅ OCR para PDFs escaneados
- ✅ Estrutura de tabelas complexa
- ❌ Requer muito mais RAM e CPU

### 2. Configurar variáveis de ambiente

Copie o arquivo `.env.example` para `.env` e preencha:

```env
OPENAI_API_KEY=sk-...
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJ...
```

### 3. Configurar banco de dados Supabase

Execute o SQL no Supabase SQL Editor (ver `schema.sql`):

```sql
-- Extensão pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Tabela de chunks
CREATE TABLE documento_chunks (
    id BIGSERIAL PRIMARY KEY,
    document_id TEXT NOT NULL,
    filename TEXT NOT NULL,
    page_number INTEGER NOT NULL,
    chunk_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(3072),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_doc_id ON documento_chunks(document_id);
CREATE INDEX idx_filename ON documento_chunks(filename);
CREATE INDEX ON documento_chunks USING hnsw (embedding vector_cosine_ops);

-- Tabela de respostas
CREATE TABLE documento_respostas (
    id BIGSERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    document_id TEXT NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    references JSONB,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_resp_filename ON documento_respostas(filename);

-- Função de busca
CREATE OR REPLACE FUNCTION match_chunks(
    query_embedding VECTOR(3072),
    match_count INT DEFAULT 8,
    filter_document_id TEXT DEFAULT NULL
)
RETURNS TABLE (
    id BIGINT,
    document_id TEXT,
    filename TEXT,
    page_number INTEGER,
    content TEXT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        c.document_id,
        c.filename,
        c.page_number,
        c.content,
        1 - (c.embedding <=> query_embedding) AS similarity
    FROM documento_chunks c
    WHERE 
        (filter_document_id IS NULL OR c.document_id = filter_document_id)
    ORDER BY c.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;
```

## 🏃 Como Rodar

```bash
streamlit run app.py
```

## 📖 Fluxo de Trabalho

1. **Upload de PDFs** → Docling extrai texto com OCR
2. **Chunks criados** com referência de página
3. **Embeddings gerados** e salvos no Supabase
4. **Perguntas** → o1 analisa e responde com referências
5. **Respostas salvas** por documento

## 🗂️ Estrutura do Projeto

```
projeto_juridico/
├── .env                 # Variáveis de ambiente (criar)
├── requirements.txt     # Dependências Python
├── config.py           # Configurações
├── processor.py        # Extração rápida com Docling
├── vectorstore.py      # Supabase + Embeddings
├── analyzer.py         # IA com o1 para análise
├── storage.py          # Salvar respostas estruturadas
├── app.py              # Streamlit UI
└── README.md
```

## 🔧 Configurações

Edite `config.py` para ajustar:

- `MODEL_O1`: Modelo o1 a usar (padrão: o1-2024-12-17)
- `MODEL_EMBEDDING`: Modelo de embedding (padrão: text-embedding-3-large)
- `CHUNK_SIZE`: Tamanho dos chunks (padrão: 2000)
- `CHUNK_OVERLAP`: Overlap entre chunks (padrão: 300)

## 📝 Uso

1. **Escolher modo**: No sidebar, marque "Modo leve" para usar menos recursos (pypdf em vez de docling)
2. **Processar documentos**: Faça upload dos PDFs e clique em "Processar Documentos"
3. **Fazer perguntas**: Digite sua pergunta e clique em "Responder"
4. **Salvar respostas**: Clique em "Salvar Resposta" para guardar no banco
5. **Ver histórico**: Acesse a aba "Respostas Salvas"

### 💡 Dica: Modo Leve vs Completo

- **Use Modo Leve** se seus PDFs têm texto selecionável (não escaneados)
- **Use Modo Completo** se precisa de OCR ou tabelas complexas

## 🛠️ Tecnologias

- **Docling**: Extração de texto de PDFs com OCR
- **OpenAI o1**: Modelo de IA para análise profunda
- **Supabase**: Banco de dados com pgvector para busca semântica
- **Streamlit**: Interface web moderna e interativa
- **LangChain**: Divisão de texto em chunks

## 📄 Licença

Este projeto é de uso interno.
