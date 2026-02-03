import io
import zipfile
import requests
import fitz  # PyMuPDF
import os
from datetime import datetime
from supabase import create_client
from config import settings
from browser_downloader import BrowserDownloader

class ZipProcessor:
    def __init__(self):
        # Use Service Role Key to bypass RLS for storage uploads
        self.supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
        self.browser_downloader = BrowserDownloader()

    def process_zip_url(self, case_number: str, zip_url: str, case_id: int, projeto_id: str = None):
        """
        Downloads ZIP, finds valid PDF, uploads to Storage, and registers in DB.
        """
        try:
            # 1. Download ZIP using browser (handles JavaScript redirects)
            print(f"   ⬇️ Baixando ZIP via navegador: {zip_url[:50]}...")
            zip_bytes = self.browser_downloader.download_file(zip_url, timeout_ms=60000)
            zip_buffer = io.BytesIO(zip_bytes)
            
            # 2. Open ZIP
            found_valid_pdf = False
            error_msg = None
            
            with zipfile.ZipFile(zip_buffer) as z:
                # Filter files
                pdf_files = [f for f in z.namelist() if f.lower().endswith('.pdf')]
                analise_files = [f for f in pdf_files if "analise" in f.lower() or "análise" in f.lower()]
                
                # If no "analise" file found, try all PDFs? 
                # User constraint: "extrair apenas o arquivo PDF que contenha 'ANALISE' no nome"
                # So if strictly none, we fail? 
                # Let's stick to strict requirement first.
                
                target_files = analise_files
                
                if not target_files:
                    error_msg = "Nenhum PDF com 'ANALISE' no nome encontrado no ZIP."
                    print(f"   ⚠️ {error_msg}")
                    # Update case status logic handled by caller or here?
                    # Ideally caller handles status. I return result.
                    return {"success": False, "error": error_msg}

                for filename in target_files:
                    print(f"   🔎 Verificando: {filename}")
                    with z.open(filename) as f_pdf:
                        pdf_bytes = f_pdf.read()
                        
                        # 3. Validate Content
                        if self._validate_pdf_content(pdf_bytes):
                            print(f"   ✅ PDF Válido encontrado: {filename}")
                            
                            # 4. Sanitize filename for Supabase Storage
                            # Remove accents, spaces, and special characters
                            import unicodedata
                            import re
                            
                            safe_filename = os.path.basename(filename)
                            # Normalize unicode (remove accents)
                            safe_filename = unicodedata.normalize('NFKD', safe_filename)
                            safe_filename = safe_filename.encode('ASCII', 'ignore').decode('ASCII')
                            # Replace spaces and special chars with underscore
                            safe_filename = re.sub(r'[^a-zA-Z0-9._-]', '_', safe_filename)
                            # Remove multiple underscores
                            safe_filename = re.sub(r'_+', '_', safe_filename)
                            
                            print(f"   📝 Nome sanitizado: {safe_filename}")
                            
                            # 5. Upload to Supabase
                            storage_path = f"salesforce/{case_number}/{safe_filename}"
                            
                            try:
                                self.supabase.storage.from_("processos").upload(
                                    path=storage_path,
                                    file=pdf_bytes,
                                    file_options={"content-type": "application/pdf", "upsert": "true"}
                                )
                                print(f"   ✅ Arquivo enviado para Storage: {storage_path}")
                            except Exception as upload_error:
                                # Check if it's a duplicate/already exists error
                                error_msg = str(upload_error)
                                if 'already exists' in error_msg.lower() or 'duplicate' in error_msg.lower() or '403' in error_msg:
                                    print(f"   ℹ️ Arquivo já existe no Storage, pulando upload.")
                                else:
                                    raise  # Re-raise if it's a different error
                            
                            # 6. Register in DB (only if not already registered)
                            try:
                                self.supabase.table(settings.TABLE_GERENCIAMENTO).insert({
                                    "filename": safe_filename,  # Use sanitized name
                                    "storage_path": storage_path,
                                    "status": "PENDENTE", # Ready for worker.py
                                    "caso_id": case_id,
                                    "projeto_id": projeto_id,
                                    "origem": "SALESFORCE",
                                    "created_at": "now()"
                                }).execute()
                                print(f"   ✅ Documento registrado no banco de dados")
                            except Exception as db_error:
                                error_msg = str(db_error)
                                if 'duplicate' in error_msg.lower() or 'unique' in error_msg.lower():
                                    print(f"   ℹ️ Documento já registrado no banco, pulando.")
                                else:
                                    raise  # Re-raise if it's a different error
                            
                            # Trigger Worker immediately (Fire and Forget)
                            if projeto_id:
                                try:
                                    self.supabase.table(settings.TABLE_PROCESSAR_AGORA).insert({
                                        "projeto_id": projeto_id
                                    }).execute()
                                    print("   ⚡ Worker acionado automaticamente.")
                                except Exception:
                                    pass # Ignore if duplicate or error, worker will eventually pick up manual trigger
                            
                            found_valid_pdf = True
                            break # Stop after finding the first valid one? Or process all? User implies "o arquivo", singular.
                        else:
                            print(f"   ⚠️ Conteúdo inválido (Não é Formulário de Sinistro).")

            if found_valid_pdf:
                print(f"   ✅ Processamento concluído: 1 arquivo válido encontrado")
                return {"success": True, "files_processed": 1}
            else:
                print(f"   ⚠️ Nenhum PDF válido encontrado no ZIP")
                return {"success": False, "error": "Nenhum PDF válido (Formulário) encontrado."}

        except Exception as e:
            print(f"   ❌ Erro processando ZIP: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}

    def _validate_pdf_content(self, pdf_bytes: bytes) -> bool:
        """
        Checks if first page contains 'FORMULÁRIO PARA ANÁLISE DE SINISTRO'
        """
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            if len(doc) < 1:
                return False
            
            text = doc[0].get_text().upper()
            # Normalize text to handle spacing/newlines
            # "FORMULÁRIO PARA ANÁLISE DE SINISTRO"
            # User phrase might vary slightly, but stick to requirement.
            # I'll check keywords
            required_phrase = "FORMULÁRIO PARA ANÁLISE DE SINISTRO"
            
            # Simple check
            if required_phrase in text:
                return True
                
            # Fallback: maybe encoding issues? Check proximity of words?
            # For now, strict check.
            return False
            
        except Exception:
            return False
