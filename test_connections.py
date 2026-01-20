#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnóstico para verificar conexões com APIs e banco de dados
"""

import sys
import os
from datetime import datetime

# Configurar encoding para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Adicionar logs de debug
LOG_PATH = r"c:\Users\TRIA 2026\Downloads\ProcessIA\.cursor\debug.log"

def debug_log(location, message, data, hypothesis_id="CONN", session_id="test-connections", run_id="run1"):
    """Debug logging helper"""
    try:
        log_entry = {
            "sessionId": session_id,
            "runId": run_id,
            "hypothesisId": hypothesis_id,
            "location": location,
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            import json
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    except Exception as e:
        pass

def print_status(test_name, status, details=""):
    """Imprime status de um teste"""
    icon = "✅" if status else "❌"
    print(f"{icon} {test_name}")
    if details:
        print(f"   {details}")
    print()

def test_env_file():
    """Testa se o arquivo .env existe e tem as variáveis necessárias"""
    # #region agent log
    debug_log("test_connections.py:test_env_file", "INICIO_TESTE_ENV", {}, "A")
    # #endregion
    
    env_path = ".env"
    if not os.path.exists(env_path):
        print_status("Arquivo .env", False, "Arquivo .env não encontrado!")
        return False
    
    # #region agent log
    debug_log("test_connections.py:test_env_file", "ENV_EXISTE", {"path": env_path}, "A")
    # #endregion
    
    required_vars = ["OPENAI_API_KEY", "SUPABASE_URL", "SUPABASE_KEY"]
    missing = []
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        for var in required_vars:
            value = os.getenv(var)
            if not value:
                missing.append(var)
            else:
                # Verificar se não está vazio (apenas espaços)
                if not value.strip():
                    missing.append(f"{var} (vazio)")
        
        # #region agent log
        debug_log("test_connections.py:test_env_file", "VARIAVEIS_VERIFICADAS", {"missing": missing, "found": len(required_vars) - len(missing)}, "A")
        # #endregion
        
        if missing:
            print_status("Variáveis de ambiente", False, f"Variáveis faltando: {', '.join(missing)}")
            return False
        
        print_status("Arquivo .env", True, "Todas as variáveis necessárias encontradas")
        return True
    except Exception as e:
        # #region agent log
        debug_log("test_connections.py:test_env_file", "ERRO_ENV", {"error": str(e)}, "A")
        # #endregion
        print_status("Arquivo .env", False, f"Erro ao carregar: {str(e)}")
        return False

def test_openai_connection():
    """Testa conexão com OpenAI API"""
    # #region agent log
    debug_log("test_connections.py:test_openai_connection", "INICIO_TESTE_OPENAI", {}, "B")
    # #endregion
    
    try:
        from config import settings
        from openai import OpenAI
        
        # #region agent log
        debug_log("test_connections.py:test_openai_connection", "CRIANDO_CLIENTE", {"api_key_prefix": settings.OPENAI_API_KEY[:10] + "..." if settings.OPENAI_API_KEY else None}, "B")
        # #endregion
        
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Teste simples: listar modelos (requisição leve)
        # #region agent log
        debug_log("test_connections.py:test_openai_connection", "TESTANDO_LIST_MODELS", {}, "B")
        # #endregion
        
        models = client.models.list()
        
        # #region agent log
        debug_log("test_connections.py:test_openai_connection", "MODELS_LIST_OK", {"count": len(list(models.data)) if models else 0}, "B")
        # #endregion
        
        # Teste de embedding (mais relevante para o uso)
        # #region agent log
        debug_log("test_connections.py:test_openai_connection", "TESTANDO_EMBEDDING", {"model": settings.MODEL_EMBEDDING}, "B")
        # #endregion
        
        response = client.embeddings.create(
            model=settings.MODEL_EMBEDDING,
            input="teste de conexão"
        )
        
        # #region agent log
        debug_log("test_connections.py:test_openai_connection", "EMBEDDING_OK", {"embedding_dim": len(response.data[0].embedding) if response.data else 0}, "B")
        # #endregion
        
        embedding_dim = len(response.data[0].embedding) if response.data else 0
        print_status("OpenAI API", True, f"Conexão OK. Embedding dimension: {embedding_dim}")
        return True
        
    except Exception as e:
        # #region agent log
        debug_log("test_connections.py:test_openai_connection", "ERRO_OPENAI", {"error": str(e), "error_type": type(e).__name__}, "B")
        # #endregion
        print_status("OpenAI API", False, f"Erro: {str(e)}")
        return False

def test_supabase_connection():
    """Testa conexão com Supabase"""
    # #region agent log
    debug_log("test_connections.py:test_supabase_connection", "INICIO_TESTE_SUPABASE", {}, "C")
    # #endregion
    
    try:
        from config import settings
        from supabase import create_client
        
        # #region agent log
        debug_log("test_connections.py:test_supabase_connection", "CRIANDO_CLIENTE", {"url": settings.SUPABASE_URL[:30] + "..." if settings.SUPABASE_URL else None}, "C")
        # #endregion
        
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        
        # Teste simples: fazer uma query vazia para verificar conexão
        # #region agent log
        debug_log("test_connections.py:test_supabase_connection", "TESTANDO_QUERY", {}, "C")
        # #endregion
        
        # Tentar acessar uma tabela (mesmo que vazia)
        try:
            result = supabase.table("documento_chunks").select("id").limit(1).execute()
            # #region agent log
            debug_log("test_connections.py:test_supabase_connection", "QUERY_OK", {"has_data": len(result.data) > 0 if result.data else False}, "C")
            # #endregion
        except Exception as table_error:
            # Se a tabela não existir, ainda assim a conexão pode estar OK
            # #region agent log
            debug_log("test_connections.py:test_supabase_connection", "QUERY_TABLE_ERROR", {"error": str(table_error)}, "C")
            # #endregion
            pass
        
        print_status("Supabase", True, f"Conexão OK. URL: {settings.SUPABASE_URL[:50]}...")
        return True
        
    except Exception as e:
        # #region agent log
        debug_log("test_connections.py:test_supabase_connection", "ERRO_SUPABASE", {"error": str(e), "error_type": type(e).__name__}, "C")
        # #endregion
        print_status("Supabase", False, f"Erro: {str(e)}")
        return False

def test_supabase_tables():
    """Testa se as tabelas necessárias existem no Supabase"""
    # #region agent log
    debug_log("test_connections.py:test_supabase_tables", "INICIO_TESTE_TABELAS", {}, "D")
    # #endregion
    
    try:
        from config import settings
        from supabase import create_client
        
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        
        required_tables = [
            settings.TABLE_EMBEDDINGS,
            settings.TABLE_RESPOSTAS,
            settings.TABLE_GERENCIAMENTO
        ]
        
        # #region agent log
        debug_log("test_connections.py:test_supabase_tables", "TABELAS_REQUERIDAS", {"tables": required_tables}, "D")
        # #endregion
        
        all_ok = True
        for table in required_tables:
            try:
                # Tentar fazer uma query simples na tabela
                result = supabase.table(table).select("*").limit(1).execute()
                # #region agent log
                debug_log("test_connections.py:test_supabase_tables", "TABELA_OK", {"table": table, "has_data": len(result.data) > 0 if result.data else False}, "D")
                # #endregion
                print_status(f"Tabela: {table}", True, f"Tabela existe e está acessível")
            except Exception as e:
                # #region agent log
                debug_log("test_connections.py:test_supabase_tables", "TABELA_ERRO", {"table": table, "error": str(e)}, "D")
                # #endregion
                print_status(f"Tabela: {table}", False, f"Erro: {str(e)}")
                all_ok = False
        
        return all_ok
        
    except Exception as e:
        # #region agent log
        debug_log("test_connections.py:test_supabase_tables", "ERRO_GERAL", {"error": str(e)}, "D")
        # #endregion
        print_status("Tabelas Supabase", False, f"Erro ao verificar tabelas: {str(e)}")
        return False

def test_vectorstore_operations():
    """Testa operações básicas do VectorStore"""
    # #region agent log
    debug_log("test_connections.py:test_vectorstore_operations", "INICIO_TESTE_VECTORSTORE", {}, "E")
    # #endregion
    
    try:
        from vectorstore import VectorStore
        
        # #region agent log
        debug_log("test_connections.py:test_vectorstore_operations", "CRIANDO_VECTORSTORE", {}, "E")
        # #endregion
        
        vectorstore = VectorStore()
        
        # Teste: verificar se consegue criar embedding
        # #region agent log
        debug_log("test_connections.py:test_vectorstore_operations", "TESTANDO_HAS_CHUNKS", {}, "E")
        # #endregion
        
        # Teste simples: verificar se o método has_chunks funciona
        test_result = vectorstore.has_chunks(document_id="test_doc_12345")
        
        # #region agent log
        debug_log("test_connections.py:test_vectorstore_operations", "HAS_CHUNKS_OK", {"result": test_result}, "E")
        # #endregion
        
        print_status("VectorStore", True, "Operações básicas funcionando")
        return True
        
    except Exception as e:
        # #region agent log
        debug_log("test_connections.py:test_vectorstore_operations", "ERRO_VECTORSTORE", {"error": str(e), "error_type": type(e).__name__}, "E")
        # #endregion
        print_status("VectorStore", False, f"Erro: {str(e)}")
        return False

def test_storage_operations():
    """Testa operações básicas do Storage"""
    # #region agent log
    debug_log("test_connections.py:test_storage_operations", "INICIO_TESTE_STORAGE", {}, "F")
    # #endregion
    
    try:
        from storage import ResponseStorage
        
        # #region agent log
        debug_log("test_connections.py:test_storage_operations", "CRIANDO_STORAGE", {}, "F")
        # #endregion
        
        storage = ResponseStorage()
        
        # Teste: verificar se consegue buscar análises
        # #region agent log
        debug_log("test_connections.py:test_storage_operations", "TESTANDO_GET_ALL", {}, "F")
        # #endregion
        
        all_analyses = storage.get_all()
        
        # #region agent log
        debug_log("test_connections.py:test_storage_operations", "GET_ALL_OK", {"count": len(all_analyses) if all_analyses else 0}, "F")
        # #endregion
        
        count = len(all_analyses) if all_analyses else 0
        print_status("ResponseStorage", True, f"Operações básicas funcionando. {count} análises encontradas")
        return True
        
    except Exception as e:
        # #region agent log
        debug_log("test_connections.py:test_storage_operations", "ERRO_STORAGE", {"error": str(e), "error_type": type(e).__name__}, "F")
        # #endregion
        print_status("ResponseStorage", False, f"Erro: {str(e)}")
        return False

def main():
    """Executa todos os testes"""
    print("=" * 60)
    print("🔍 DIAGNÓSTICO DE CONEXÕES - ProcessIA")
    print("=" * 60)
    print()
    
    # #region agent log
    debug_log("test_connections.py:main", "INICIO_DIAGNOSTICO", {}, "ALL")
    # #endregion
    
    results = []
    
    # Teste 1: Arquivo .env
    results.append(("Arquivo .env", test_env_file()))
    
    if not results[0][1]:
        print("⚠️  Arquivo .env não configurado corretamente. Testes seguintes podem falhar.")
        print()
    
    # Teste 2: OpenAI
    results.append(("OpenAI API", test_openai_connection()))
    
    # Teste 3: Supabase
    results.append(("Supabase", test_supabase_connection()))
    
    # Teste 4: Tabelas
    results.append(("Tabelas Supabase", test_supabase_tables()))
    
    # Teste 5: VectorStore
    results.append(("VectorStore", test_vectorstore_operations()))
    
    # Teste 6: Storage
    results.append(("ResponseStorage", test_storage_operations()))
    
    # Resumo
    print("=" * 60)
    print("📊 RESUMO")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        icon = "✅" if result else "❌"
        print(f"{icon} {name}")
    
    print()
    print(f"Total: {passed}/{total} testes passaram")
    
    # #region agent log
    debug_log("test_connections.py:main", "FIM_DIAGNOSTICO", {"passed": passed, "total": total}, "ALL")
    # #endregion
    
    if passed == total:
        print("✅ Todas as conexões estão funcionando corretamente!")
        return 0
    else:
        print("❌ Algumas conexões falharam. Verifique os erros acima.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
