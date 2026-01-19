from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    SUPABASE_URL: str
    SUPABASE_KEY: str
    
    # Modelos
    MODEL_O1: str = "gpt-4.1"  # GPT-4.1
    MODEL_EMBEDDING: str = "text-embedding-3-large"  # Reduzido para 1536 dimensões automaticamente (compatível com Supabase HNSW)
    
    # Performance
    CHUNK_SIZE: int = 2000
    CHUNK_OVERLAP: int = 300
    MAX_WORKERS: int = 4  # Paralelo
    MAX_DOCUMENTS: int = 10  # Limite máximo de documentos na tabela (FIFO)
    
    # Tabelas
    TABLE_EMBEDDINGS: str = "documento_chunks"
    TABLE_RESPOSTAS: str = "analise_jurisprudencial"
    TABLE_GERENCIAMENTO: str = "documento_gerenciamento"
    
    class Config:
        env_file = ".env"

settings = Settings()
