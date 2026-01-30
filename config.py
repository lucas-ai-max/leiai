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
    
    # Performance
    CHUNK_SIZE: int = 2000
    CHUNK_OVERLAP: int = 0  # Zero overlap para evitar repetição de conteúdo
    MAX_WORKERS: int = 10  # Quantas threads paralelas
    MAX_TEXT_TOKENS: int = 30000  # Limite para decidir entre Texto Puro vs File API
    
    # Tabelas
    TABLE_EMBEDDINGS: str = "documento_chunks"
    TABLE_RESPOSTAS: str = "analise_jurisprudencial"
    TABLE_GERENCIAMENTO: str = "documento_gerenciamento"
    
    class Config:
        env_file = ".env"

settings = Settings()
