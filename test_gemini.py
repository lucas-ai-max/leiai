"""
Script para testar a conexao com Gemini API
Execute: python test_gemini.py
"""

from config import settings
import google.generativeai as genai

print("Testando conexao com Gemini API...\n")

# 1. Verificar API Key
if not settings.GOOGLE_API_KEY:
    print("[ERRO] GOOGLE_API_KEY nao configurada no .env")
    exit(1)

print(f"[OK] API Key encontrada: {settings.GOOGLE_API_KEY[:20]}...")

# 2. Configurar
try:
    genai.configure(api_key=settings.GOOGLE_API_KEY)
    print("[OK] Gemini API configurado")
except Exception as e:
    print(f"[ERRO] Erro ao configurar: {e}")
    exit(1)

# 3. Listar modelos disponíveis
print(f"\nTentando listar modelos disponiveis...")
try:
    models = genai.list_models()
    model_list = list(models)
    print(f"[OK] {len(model_list)} modelos encontrados")
    print("\nModelos disponiveis:")
    for model in model_list:
        if 'generateContent' in model.supported_generation_methods:
            print(f"  - {model.name}")
except Exception as e:
    print(f"[AVISO] Nao foi possivel listar modelos: {e}")

# 4. Testar modelo específico
print(f"\nTestando modelo: {settings.MODEL_FAST}")
try:
    model = genai.GenerativeModel(settings.MODEL_FAST)
    print(f"[OK] Modelo '{settings.MODEL_FAST}' criado com sucesso")
    
    # Teste simples
    print("\nFazendo teste de geracao...")
    response = model.generate_content("Responda apenas: OK")
    print(f"[OK] Resposta recebida: {response.text}")
    print("\n[OK] TUDO FUNCIONANDO!")
    
except Exception as e:
    error_msg = str(e)
    print(f"\n[ERRO] Erro ao testar modelo:")
    print(f"   {error_msg}")
    
    if "not found" in error_msg.lower() or "404" in error_msg or "NotFound" in error_msg:
        print(f"\n[SOLUCAO]")
        print(f"   O modelo '{settings.MODEL_FAST}' nao foi encontrado.")
        print(f"   Tente usar um destes modelos:")
        print(f"   - gemini-1.5-flash")
        print(f"   - gemini-1.5-pro")
        print(f"   - gemini-pro")
        print(f"\n   Edite config.py e altere MODEL_FAST para um dos modelos acima.")
    elif "api key" in error_msg.lower() or "401" in error_msg or "403" in error_msg:
        print(f"\n[SOLUCAO]")
        print(f"   Erro de autenticacao. Verifique se GOOGLE_API_KEY esta correto.")
        print(f"   Obtenha uma nova chave em: https://aistudio.google.com/app/apikey")
    
    exit(1)
