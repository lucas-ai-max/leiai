"""
Script para verificar/criar o bucket 'processos' no Supabase Storage
"""

from supabase import create_client
from config import settings
import sys
import os
import requests
from dotenv import load_dotenv

# Carregar .env para pegar service_role se existir
load_dotenv()

def check_bucket(supabase):
    """Verifica se o bucket 'processos' existe"""
    try:
        buckets = supabase.storage.list_buckets()
        bucket_exists = any(bucket.name == "processos" for bucket in buckets)
        return bucket_exists
    except Exception as e:
        print(f"[AVISO] Nao foi possivel verificar buckets: {e}")
        return False

def create_bucket_with_service_role():
    """Tenta criar o bucket usando service_role key"""
    service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')
    
    if not service_role_key:
        return False
    
    try:
        storage_url = f"{settings.SUPABASE_URL.rstrip('/')}/storage/v1/bucket"
        
        headers = {
            "apikey": service_role_key,
            "Authorization": f"Bearer {service_role_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "name": "processos",
            "public": True
        }
        
        response = requests.post(storage_url, json=data, headers=headers)
        
        if response.status_code in [200, 201]:
            print("[OK] Bucket 'processos' criado com sucesso!")
            return True
        elif response.status_code == 409:
            print("[OK] Bucket 'processos' ja existe!")
            return True
        else:
            print(f"[ERRO] Falha ao criar: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"[ERRO] Erro ao criar bucket: {e}")
        return False

def main():
    print("Verificando bucket 'processos' no Supabase Storage...\n")
    
    # Conectar com anon key para verificar
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    
    # Verificar se existe
    if check_bucket(supabase):
        print("[OK] Bucket 'processos' ja existe!")
        return True
    
    print("[AVISO] Bucket 'processos' nao encontrado.\n")
    
    # Tentar criar com service_role se disponivel
    service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')
    
    if service_role_key:
        print("Tentando criar bucket com service_role key...")
        if create_bucket_with_service_role():
            return True
        print("\nFalha ao criar com service_role. Tente manualmente.\n")
    else:
        print("Service role key nao encontrada no .env\n")
    
    # Mostrar instrucoes
    print("="*60)
    print("CRIE O BUCKET MANUALMENTE NO SUPABASE DASHBOARD")
    print("="*60)
    print("\n1. Acesse: https://supabase.com/dashboard")
    print("2. Selecione seu projeto")
    print("3. Clique em 'Storage' (menu lateral)")
    print("4. Clique em 'New Bucket'")
    print("5. Configure:")
    print("   - Nome: processos")
    print("   - Public bucket: [X] Marque esta opcao")
    print("6. Clique em 'Create bucket'")
    print("\n" + "="*60)
    print("\nOU adicione no .env e execute novamente:")
    print("SUPABASE_SERVICE_ROLE_KEY=sua-service-role-key")
    print("(Encontre em: Settings > API > service_role)")
    print("="*60 + "\n")
    
    return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
