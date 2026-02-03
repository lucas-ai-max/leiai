import requests
import time
from config import settings

class SalesforceClient:
    def __init__(self):
        self.api_key = settings.SALESFORCE_API_KEY
        self.base_url = settings.SALESFORCE_API_URL
        if not self.api_key:
            raise ValueError("Salesforce API Key not configured!")

    def get_case_zip_url(self, case_number: str) -> str:
        """
        Fetches the ZIP URL for a given case number.
        Returns None if not found (404).
        Raises specific errors for other issues.
        """
        url = self.base_url.format(case_number=case_number)
        headers = {
            "x-api-key": self.api_key,
            "Accept": "application/json"
        }
        
        try:
            print(f"   🔎 Buscando caso {case_number} na API...")
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Estrutura real da API Salesforce:
                # {"sucesso": true, "mensagemErro": null, "arquivos": [...]}
                
                # 1. Verificar se é o formato com "arquivos"
                if isinstance(data, dict) and 'arquivos' in data:
                    arquivos = data.get('arquivos', [])
                    if not isinstance(arquivos, list):
                        print(f"   ⚠️ Campo 'arquivos' não é uma lista. Payload: {data}")
                        return None
                    
                    # Buscar ZIP dentro da lista de arquivos
                    found_types = []
                    print(f"   📋 Total de arquivos na resposta: {len(arquivos)}")
                    for idx, item in enumerate(arquivos, 1):
                        nome = item.get('nomeArquivo', 'sem nome')
                        tipo = str(item.get('tipoArquivo', '')).strip()
                        url = item.get('downloadUrl', '')
                        
                        print(f"   📄 Arquivo {idx}: '{nome}' | Tipo: '{tipo}' | URL: {'✅' if url else '❌'}")
                        found_types.append(tipo)
                        
                        # Case-insensitive comparison
                        if tipo.lower() == 'zip' and url:
                            print(f"   ✅ ZIP encontrado: {nome}")
                            return url
                    
                    print(f"   ⚠️ NENHUM ZIP ENCONTRADO. Tipos encontrados: {found_types}")
                    print(f"   💡 Dica: Verifique se algum arquivo tem tipo 'ZIP' (maiúsculo) ou similar")
                    return None
                
                # 2. Se for lista direta (formato antigo)
                elif isinstance(data, list):
                    found_types = []
                    for item in data:
                        tipo = str(item.get('tipoArquivo', '')).lower()
                        found_types.append(tipo)
                        if tipo == 'zip' and item.get('downloadUrl'):
                            return item.get('downloadUrl')
                    
                    print(f"   ⚠️ NENHUM ZIP ENCONTRADO. Tipos encontrados: {found_types}")
                    return None
                
                # 3. Se for dict simples (fallback)
                elif isinstance(data, dict):
                    url = data.get('downloadUrl') or data.get('url') or data.get('link')
                    if url:
                        return url
                    print(f"   ⚠️ Objeto único sem URL compatível. Payload: {data}")
                    return None
                
                print(f"   ⚠️ Formato de resposta desconhecido: {type(data)}")
                return None

            elif response.status_code == 404:
                print(f"   ❌ Caso {case_number} não encontrado (404).")
                return None
            
            elif response.status_code == 403:
                raise PermissionError(f"Acesso negado (403). Verifique a API Key.")
            
            else:
                raise ConnectionError(f"Erro API Salesforce: {response.status_code} - {response.text}")

        except Exception as e:
            print(f"   ⚠️ Erro de conexão Salesforce: {e}")
            raise e
