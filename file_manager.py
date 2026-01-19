from supabase import create_client, Client
from typing import Dict, List, Optional
from config import settings
from datetime import datetime

class FileManager:
    """Gerenciador de arquivos no Supabase"""
    
    def __init__(self):
        self.supabase: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
    
    def register_file(self, filename: str, file_size_mb: float, caminho_original: str) -> Optional[Dict]:
        """Registra novo arquivo para processamento com retry"""
        record = {
            "filename": filename,
            "status": "PENDENTE",
            "file_size_mb": file_size_mb,
            "caminho_original": caminho_original,
            "created_at": datetime.now().isoformat()
        }
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = self.supabase.table(settings.TABLE_GERENCIAMENTO)\
                    .insert(record)\
                    .execute()
                return result.data[0] if result.data else None
            except Exception as e:
                # Se já existe (duplicate key), retornar existing
                error_str = str(e).lower()
                if "duplicate" in error_str or "unique" in error_str or "already exists" in error_str:
                    existing = self.get_by_filename(filename)
                    if existing:
                        if existing.get("status") == "ERRO":
                            return self.update_status(filename, "PENDENTE", error_message=None, existing_data=existing)
                        return existing
                    return None
                
                # Retry em caso de erro de conexão
                if attempt < max_retries - 1:
                    import time
                    time.sleep(1)
                    continue
                
                # Se falhar todas as tentativas, tentar buscar se já existe
                existing = self.get_by_filename(filename)
                if existing:
                    return existing
                return None
    
    def update_status(self, filename: str, status: str, 
                     document_id: str = None,
                     error_message: str = None,
                     total_chunks: int = None,
                     total_pages: int = None,
                     existing_data: Dict = None):
        """Atualiza status do arquivo"""
        update_data = {
            "status": status,
            "updated_at": datetime.now().isoformat()
        }
        
        if document_id:
            update_data["document_id"] = document_id
        if error_message is not None:
            update_data["error_message"] = error_message
        if total_chunks is not None:
            update_data["total_chunks"] = total_chunks
        if total_pages is not None:
            update_data["total_pages"] = total_pages
        
        # Usar existing_data se fornecido, senão buscar (com retry)
        if existing_data is None:
            existing_data = self.get_by_filename(filename) or {}
        
        # Atualizar timestamps específicos
        if status == "PROCESSANDO" and not existing_data.get("started_at"):
            update_data["started_at"] = datetime.now().isoformat()
        elif status in ["CONCLUIDO", "ERRO", "JA_PROCESSADO"]:
            update_data["completed_at"] = datetime.now().isoformat()
        
        # Retry em caso de erro de conexão
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = self.supabase.table(settings.TABLE_GERENCIAMENTO)\
                    .update(update_data)\
                    .eq("filename", filename)\
                    .execute()
                
                return result.data[0] if result.data else None
            except Exception as e:
                if attempt < max_retries - 1:
                    import time
                    time.sleep(1)  # Aguardar 1 segundo antes de tentar novamente
                    continue
                # Se falhar todas as tentativas, logar mas não quebrar
                print(f"Erro ao atualizar status de {filename} após {max_retries} tentativas: {str(e)}")
                return None
    
    def get_by_filename(self, filename: str) -> Optional[Dict]:
        """Busca arquivo por nome com retry"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = self.supabase.table(settings.TABLE_GERENCIAMENTO)\
                    .select("*")\
                    .eq("filename", filename)\
                    .execute()
                
                return result.data[0] if result.data else None
            except Exception as e:
                if attempt < max_retries - 1:
                    import time
                    time.sleep(1)  # Aguardar 1 segundo antes de tentar novamente
                    continue
                # Se falhar todas as tentativas, retornar None
                print(f"Erro ao buscar {filename} após {max_retries} tentativas: {str(e)}")
                return None
    
    def get_all(self, status: Optional[str] = None) -> List[Dict]:
        """Lista todos os arquivos com retry"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                query = self.supabase.table(settings.TABLE_GERENCIAMENTO).select("*")
                
                if status:
                    query = query.eq("status", status)
                
                result = query.order("created_at", desc=True).execute()
                return result.data if result.data else []
            except Exception as e:
                if attempt < max_retries - 1:
                    import time
                    time.sleep(1)
                    continue
                # Se falhar, retornar lista vazia
                print(f"Erro ao buscar arquivos após {max_retries} tentativas: {str(e)}")
                return []
    
    def is_processed(self, filename: str) -> bool:
        """Verifica se arquivo já foi processado"""
        file_data = self.get_by_filename(filename)
        if not file_data:
            return False
        status = file_data.get("status")
        return status in ["CONCLUIDO", "JA_PROCESSADO"]
    
    def reset_errors(self):
        """Reseta arquivos com erro para PENDENTE com retry"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = self.supabase.table(settings.TABLE_GERENCIAMENTO)\
                    .update({"status": "PENDENTE", "error_message": None})\
                    .eq("status", "ERRO")\
                    .execute()
                
                return len(result.data) if result.data else 0
            except Exception as e:
                if attempt < max_retries - 1:
                    import time
                    time.sleep(1)
                    continue
                print(f"Erro ao resetar erros após {max_retries} tentativas: {str(e)}")
                return 0
