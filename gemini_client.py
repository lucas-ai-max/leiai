import google.generativeai as genai
from config import settings
import time
import os
import fitz  # PyMuPDF
from tenacity import retry, stop_after_attempt, wait_exponential

# Configuração Global
try:
    genai.configure(api_key=settings.GOOGLE_API_KEY)
except Exception as e:
    print(f"⚠️ Erro ao configurar Gemini API: {e}")

class GeminiClient:
    def __init__(self):
        # Verificar se a API key está configurada
        if not settings.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY não configurada no .env")
        
        # Tentar criar o modelo (lazy initialization)
        self.model_name = settings.MODEL_FAST
        self._model = None
        
    @property
    def model(self):
        """Lazy initialization do modelo"""
        if self._model is None:
            try:
                self._model = genai.GenerativeModel(self.model_name)
                print(f"✅ Modelo Gemini inicializado: {self.model_name}")
            except Exception as e:
                error_msg = str(e)
                if "NotFound" in error_msg or "404" in error_msg or "not found" in error_msg.lower():
                    raise ValueError(
                        f"Modelo '{self.model_name}' não encontrado!\n"
                        f"Modelos disponíveis: gemini-2.0-flash, gemini-2.5-flash, gemini-2.0-flash-lite\n"
                        f"Verifique se o nome está correto em config.py"
                    )
                elif "API key" in error_msg or "401" in error_msg or "403" in error_msg or "permission" in error_msg.lower():
                    raise ValueError(
                        f"Erro de autenticação com Gemini API!\n"
                        f"Verifique se GOOGLE_API_KEY está correto no .env\n"
                        f"Obtenha uma nova chave em: https://aistudio.google.com/app/apikey"
                    )
                else:
                    raise ValueError(f"Erro ao inicializar modelo Gemini: {error_msg}")
        return self._model

    def analyze_document(self, file_path: str, prompt_text: str) -> str:
        """Decide a melhor estratégia: Texto Puro (Rápido) ou File API (Gigantes)"""
        
        # 1. Tentar ler texto para estimar tamanho
        try:
            doc = fitz.open(file_path)
            text_content = ""
            for page in doc:
                text_content += page.get_text()
            doc.close()
            # Estimativa grosseira: 1 token ~= 4 caracteres
            token_count = len(text_content) // 4
        except Exception:
            token_count = 9999999  # Se falhar a leitura, assume gigante

        # ROTA A: Documento "Leve" (Texto Direto)
        if token_count < settings.MAX_TEXT_TOKENS:
            print(f"🚀 [ROTA FLASH] Enviando texto puro ({token_count} tokens)...")
            return self._call_gemini_text(text_content, prompt_text)
        
        # ROTA B: Documento "Pesado" (File API)
        else:
            print(f"🐘 [ROTA HEAVY] Arquivo grande ({token_count} tokens). Usando File API...")
            return self._call_gemini_file(file_path, prompt_text)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _call_gemini_text(self, text: str, prompt: str) -> str:
        try:
            response = self.model.generate_content(
                f"{prompt}\n\nDOCUMENTO:\n{text}",
                generation_config={"response_mime_type": "application/json"}
            )
            if not response.text:
                raise ValueError("Resposta vazia do Gemini API")
            return response.text
        except Exception as e:
            error_msg = str(e)
            error_lower = error_msg.lower()
            
            # Erro de modelo não encontrado
            if "notfound" in error_lower or "404" in error_msg or "not found" in error_lower:
                raise ValueError(
                    f"❌ Modelo '{self.model_name}' não encontrado!\n"
                    f"   Verifique se o modelo está correto em config.py\n"
                    f"   Modelos válidos: gemini-2.0-flash, gemini-2.5-flash, gemini-2.0-flash-lite"
                )
            
            # Erro de autenticação
            elif "api key" in error_lower or "401" in error_msg or "403" in error_msg or "permission" in error_lower or "unauthorized" in error_lower:
                raise ValueError(
                    f"❌ Erro de autenticação com Gemini API!\n"
                    f"   Verifique se GOOGLE_API_KEY está correto no .env\n"
                    f"   Obtenha uma nova chave em: https://aistudio.google.com/app/apikey"
                )
            
            # Erro de quota/rate limit
            elif "quota" in error_lower or "rate limit" in error_lower or "429" in error_msg:
                raise ValueError(
                    f"❌ Limite de quota excedido!\n"
                    f"   Aguarde alguns minutos ou verifique sua quota em: https://aistudio.google.com/"
                )
            
            # Outros erros
            else:
                raise ValueError(f"Erro ao chamar Gemini API: {error_msg}")

    def _call_gemini_file(self, file_path: str, prompt: str) -> str:
        uploaded_file = None
        try:
            # 1. Upload temporário para o Google
            print(f"   ⬆️ Upload Google: {os.path.basename(file_path)}")
            uploaded_file = genai.upload_file(path=file_path, display_name="Processo Juridico")
            
            # 2. Esperar processamento
            while uploaded_file.state.name == "PROCESSING":
                time.sleep(2)
                uploaded_file = genai.get_file(uploaded_file.name)
            
            if uploaded_file.state.name == "FAILED":
                raise ValueError("Google falhou ao processar o PDF")

            # 3. Gerar Análise
            print(f"   🧠 Analisando...")
            response = self.model.generate_content(
                [uploaded_file, prompt],
                generation_config={"response_mime_type": "application/json"}
            )
            return response.text
            
        finally:
            # 4. Limpeza no Google (importante para não acumular lixo)
            if uploaded_file:
                try:
                    genai.delete_file(uploaded_file.name)
                except:
                    pass
