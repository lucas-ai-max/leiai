import requests
import time
from config import settings

class SalesforceClient:
    def __init__(self):
        self.api_key = settings.SALESFORCE_API_KEY
        self.base_url = settings.SALESFORCE_API_URL
        if not self.api_key:
            raise ValueError("Salesforce API Key not configured!")

    def get_case_zip_urls(self, case_number: str) -> list:
        """
        Fetches ALL ZIP URLs for a given case number.
        Returns empty list if none found.
        Raises specific errors for other issues.
        """
        url = self.base_url.format(case_number=case_number)
        headers = {
            "x-api-key": self.api_key,
            "Accept": "application/json"
        }
        
        try:
            print(f"   Buscando caso {case_number} na API...")
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                zip_urls = []
                
                # Estrutura real da API Salesforce:
                # {"sucesso": true, "mensagemErro": null, "arquivos": [...]}
                
                # 1. Verificar se é o formato com "arquivos"
                if isinstance(data, dict) and 'arquivos' in data:
                    arquivos = data.get('arquivos', [])
                    if not isinstance(arquivos, list):
                        print(f"   [AVISO] Campo 'arquivos' nao e uma lista. Payload: {data}")
                        return []
                    
                    # Buscar TODOS os ZIPs dentro da lista de arquivos
                    print(f"   Total de arquivos na resposta: {len(arquivos)}")
                    for idx, item in enumerate(arquivos, 1):
                        nome = item.get('nomeArquivo', 'sem nome')
                        tipo = str(item.get('tipoArquivo', '')).strip()
                        url_download = item.get('downloadUrl', '')
                        
                        print(f"   Arquivo {idx}: '{nome}' | Tipo: '{tipo}' | URL: {'OK' if url_download else 'Nao'}")
                        
                        # Case-insensitive comparison
                        if tipo.lower() == 'zip' and url_download:
                            print(f"   [OK] ZIP encontrado: {nome}")
                            zip_urls.append(url_download)
                    
                    if not zip_urls:
                        print(f"   [AVISO] NENHUM ZIP ENCONTRADO neste caso")
                    else:
                        print(f"   [OK] Total de {len(zip_urls)} ZIP(s) encontrado(s)")
                    return zip_urls
                
                # 2. Se for lista direta (formato antigo)
                elif isinstance(data, list):
                    for item in data:
                        tipo = str(item.get('tipoArquivo', '')).lower()
                        if tipo == 'zip' and item.get('downloadUrl'):
                            zip_urls.append(item.get('downloadUrl'))
                    
                    if not zip_urls:
                        print(f"   [AVISO] NENHUM ZIP ENCONTRADO")
                    else:
                        print(f"   [OK] Total de {len(zip_urls)} ZIP(s) encontrado(s)")
                    return zip_urls
                
                # 3. Se for dict simples (fallback)
                elif isinstance(data, dict):
                    url_download = data.get('downloadUrl') or data.get('url') or data.get('link')
                    if url_download:
                        return [url_download]
                    print(f"   [AVISO] Objeto unico sem URL compativel. Payload: {data}")
                    return []
                
                print(f"   [AVISO] Formato de resposta desconhecido: {type(data)}")
                return []

            elif response.status_code == 404:
                print(f"   [ERRO] Caso {case_number} nao encontrado (404).")
                return []
            
            elif response.status_code == 403:
                raise PermissionError(f"Acesso negado (403). Verifique a API Key.")
            
            else:
                raise ConnectionError(f"Erro API Salesforce: {response.status_code} - {response.text}")

        except Exception as e:
            print(f"   [AVISO] Erro de conexao Salesforce: {e}")
            raise e
