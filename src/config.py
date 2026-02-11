from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Chaves (Adicione GOOGLE_API_KEY no seu .env)
    OPENAI_API_KEY: str = ""  # Opcional - para embeddings
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str = ""  # Opcional - apenas para criar buckets programaticamente
    GOOGLE_API_KEY: str  # Para análise com Gemini 1.5 Flash
    
    # Modelos
    MODEL_O1: str = "gpt-4.1"  # GPT-4.1 (opcional)
    MODEL_EMBEDDING: str = "text-embedding-3-large"  # Reduzido para 1536 dimensões automaticamente (compatível com Supabase HNSW)
    MODEL_FAST: str = "gemini-2.0-flash"  # Gemini para análise rápida (modelo mais recente)
    MODEL_GEMINI: str = "gemini-2.0-flash"  # Alias para compatibilidade
    MODEL_OPENAI: str = "gpt-4.1-mini"  # Modelo OpenAI mini (Mais rápido e barato)
    
    # Performance
    CHUNK_SIZE: int = 2000
    CHUNK_OVERLAP: int = 0  # Zero overlap para evitar repetição de conteúdo
    MAX_WORKERS: int = 50  # Tier 5 detectado! Modo Turbo ativado. (Ajuste para menos se o PC ficar lento)
    MAX_TEXT_TOKENS: int = 30000  # Limite para decidir entre Texto Puro vs File API
    
    # Tabelas
    TABLE_EMBEDDINGS: str = "documento_chunks"
    TABLE_RESPOSTAS: str = "analise_jurisprudencial"
    TABLE_GERENCIAMENTO: str = "documento_gerenciamento"
    TABLE_CASOS: str = "casos_processamento"
    TABLE_PROCESSAR_AGORA: str = "processar_agora"

    # Integrações
    SALESFORCE_API_URL: str = "https://c22093r8uj.execute-api.us-east-1.amazonaws.com/producao/salesforce/v1/integracoes/obterArquivos/caso/{case_number}"
    SALESFORCE_API_KEY: str = "" # Adicione no .env
    SALESFORCE_PROJECT_ID: str = "00000000-0000-0000-0000-000000000001"  # ID fixo para importações Salesforce
    
    class Config:
        env_file = ".env"

settings = Settings()
