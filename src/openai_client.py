import openai
from config import settings
import fitz  # PyMuPDF
from tenacity import retry, stop_after_attempt, wait_exponential

class OpenAIClient:
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY não configurada no .env")
        
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model_name = settings.MODEL_OPENAI
        print(f"✅ Cliente OpenAI inicializado: {self.model_name}")

    def analyze_document(self, file_path: str, prompt_text: str) -> str:
        """
        Analisa documento usando OpenAI GPT-4o.
        Estratégia: Extrair texto do PDF e enviar como mensagem.
        """
        
        # 1. Extrair texto do PDF
        try:
            doc = fitz.open(file_path)
            text_content = ""
            for page in doc:
                text_content += page.get_text()
            doc.close()
            
            # Estimativa básica de tokens (1 token ~= 4 chars)
            # GPT-4o tem 128k context, mas output é limitado (4k/16k dependendo do modelo)
            # Se for muito grande, avisar no log
            token_est = len(text_content) // 4
            print(f"   📄 Texto extraído: {token_est} tokens (aprox.)")
            
            # DEBUG CRÍTICO: Ver o que está sendo lido
            print("\n   🔍 --- INÍCIO DO TEXTO EXTRAÍDO (DEBUG) ---")
            print(text_content[:600]) # Primeiros 600 caracteres
            print("   🔍 --- FIM DO DEBUG ---\n")

            # Validação anti-alucinação: Se não há texto suficiente, é provável que seja imagem/scan.
            if len(text_content.strip()) < 50:
                print("   ⚠️ AVISO: Texto extraído insuficiente (< 50 chars). Documento pode ser imagem.")
                raise ValueError("DOC_VAZIO: Documento escaneado ou imagem sem camada de texto (OCR necessário).")
            
        except Exception as e:
            raise ValueError(f"Erro ao ler PDF: {e}")

        # 2. Enviar para OpenAI
        json_resp = self._call_openai(text_content, prompt_text)
        return json_resp, text_content

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _call_openai(self, text: str, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "Você é um assistente jurídico especializado em análise de documentos. Responda estritamente em JSON."},
                    {"role": "user", "content": f"{prompt}\n\nDOCUMENTO:\n{text}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Resposta vazia da OpenAI")
            
            return content
            
        except Exception as e:
            # Tratamento básico de erros
            raise ValueError(f"Erro na OpenAI API: {e}")
