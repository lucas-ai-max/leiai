from supabase import create_client, Client
from typing import Dict, List, Optional
from config import settings
from datetime import datetime
import logging

class FileManager:
    """Gerenciador de arquivos no Supabase"""
    
    def __init__(self):
        self.supabase: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
        self.logger = logging.getLogger(__name__)
    
    def _is_cloudflare_error(self, error: Exception) -> bool:
        """Verifica se o erro é relacionado ao Cloudflare/Supabase"""
        error_str = str(error).lower()
        return any(keyword in error_str for keyword in [
            'cloudflare', 
            'bad request', 
            'json could not be generated',
            '400'
        ])
    
    def _log_error(self, message: str, filename: str = None, error: Exception = None):
        """Loga erro de forma controlada, suprimindo erros conhecidos do Cloudflare"""
        if error and self._is_cloudflare_error(error):
            # Para erros do Cloudflare, apenas logar em nível DEBUG para não poluir o terminal
            self.logger.debug(f"{message} (erro temporário de conexão)")
        else:
            # Para outros erros, logar normalmente
            if filename:
                self.logger.warning(f"{message}: {filename}")
            else:
                self.logger.warning(message)
    
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
                
                # Retry em caso de erro de conexão com backoff exponencial
                if attempt < max_retries - 1:
                    import time
                    wait_time = 2 ** (attempt + 1)  # Backoff exponencial: 2s, 4s
                    time.sleep(wait_time)
                    continue
                
                # Se falhar todas as tentativas, tentar buscar se já existe
                existing = self.get_by_filename(filename)
                if existing:
                    return existing
                self._log_error(f"Erro ao registrar arquivo após {max_retries} tentativas", filename, e)
                return None
    
    def update_status(self, filename: str, status: str, 
                     document_id: str = None,
                     error_message: str = None,
                     total_chunks: int = None,
                     total_pages: int = None,
                     existing_data: Dict = None):
        """Atualiza status do arquivo com retry e backoff exponencial"""
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
        
        # Retry em caso de erro de conexão com backoff exponencial
        max_retries = 3
        import time
        for attempt in range(max_retries):
            try:
                result = self.supabase.table(settings.TABLE_GERENCIAMENTO)\
                    .update(update_data)\
                    .eq("filename", filename)\
                    .execute()
                
                return result.data[0] if result.data else None
            except Exception as e:
                if attempt < max_retries - 1:
                    # Backoff exponencial: 2s, 4s
                    wait_time = 2 ** (attempt + 1)
                    time.sleep(wait_time)
                    continue
                # Se falhar todas as tentativas, logar mas não quebrar
                self._log_error(f"Erro ao atualizar status após {max_retries} tentativas", filename, e)
                return None
    
    def get_by_filename(self, filename: str) -> Optional[Dict]:
        """Busca arquivo por nome com retry e backoff exponencial"""
        max_retries = 3
        import time
        for attempt in range(max_retries):
            try:
                result = self.supabase.table(settings.TABLE_GERENCIAMENTO)\
                    .select("*")\
                    .eq("filename", filename)\
                    .execute()
                
                return result.data[0] if result.data else None
            except Exception as e:
                if attempt < max_retries - 1:
                    # Backoff exponencial: 2s, 4s
                    wait_time = 2 ** (attempt + 1)
                    time.sleep(wait_time)
                    continue
                # Se falhar todas as tentativas, logar e retornar None
                self._log_error(f"Erro ao buscar após {max_retries} tentativas", filename, e)
                return None
    
    def get_all(self, status: Optional[str] = None) -> List[Dict]:
        """Lista todos os arquivos com retry e backoff exponencial"""
        max_retries = 3
        import time
        for attempt in range(max_retries):
            try:
                query = self.supabase.table(settings.TABLE_GERENCIAMENTO).select("*")
                
                if status:
                    query = query.eq("status", status)
                
                result = query.order("created_at", desc=True).execute()
                return result.data if result.data else []
            except Exception as e:
                if attempt < max_retries - 1:
                    # Backoff exponencial: 2s, 4s
                    wait_time = 2 ** (attempt + 1)
                    time.sleep(wait_time)
                    continue
                # Se falhar, logar e retornar lista vazia
                self._log_error(f"Erro ao buscar arquivos após {max_retries} tentativas", error=e)
                return []
    
    def is_processed(self, filename: str) -> bool:
        """Verifica se arquivo já foi processado"""
        file_data = self.get_by_filename(filename)
        if not file_data:
            return False
        status = file_data.get("status")
        return status in ["CONCLUIDO", "JA_PROCESSADO"]
    
    def reset_errors(self):
        """Reseta arquivos com erro para PENDENTE com retry e backoff exponencial"""
        max_retries = 3
        import time
        for attempt in range(max_retries):
            try:
                result = self.supabase.table(settings.TABLE_GERENCIAMENTO)\
                    .update({"status": "PENDENTE", "error_message": None})\
                    .eq("status", "ERRO")\
                    .execute()
                
                return len(result.data) if result.data else 0
            except Exception as e:
                if attempt < max_retries - 1:
                    # Backoff exponencial: 2s, 4s
                    wait_time = 2 ** (attempt + 1)
                    time.sleep(wait_time)
                    continue
                self._log_error(f"Erro ao resetar erros após {max_retries} tentativas", error=e)
                return 0
