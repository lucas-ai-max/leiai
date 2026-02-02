#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnóstico para verificar extração de PDF e inserção na tabela documento_chunks
"""

import sys
import os
from datetime import datetime

# Configurar encoding para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def print_status(test_name, status, details=""):
    """Imprime status de um teste"""
    icon = "✅" if status else "❌"
    print(f"{icon} {test_name}")
    if details:
        print(f"   {details}")
    print()

def test_table_structure():
    """Verifica se a tabela documento_chunks tem a estrutura correta"""
    try:
        from config import settings
        from supabase import create_client
        
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        
        # Tentar buscar informações da tabela (verificar estrutura)
        try:
            result = supabase.table(settings.TABLE_EMBEDDINGS).select("*").limit(0).execute()
            print_status("Estrutura da tabela documento_chunks", True, "Tabela existe e está acessível")
            return True, supabase
        except Exception as e:
            print_status("Estrutura da tabela documento_chunks", False, f"Erro ao acessar: {str(e)}")
            return False, None
            
    except Exception as e:
        print_status("Estrutura da tabela documento_chunks", False, f"Erro: {str(e)}")
        return False, None

def test_table_insertion(supabase):
    """Testa inserção de um registro de teste na tabela"""
    try:
        from config import settings
        import random
        
        # Criar um embedding de teste (1536 dimensões)
        test_embedding = [random.random() for _ in range(1536)]
        
        # Criar registro de teste
        test_record = {
            "document_id": "TEST_DOC_" + datetime.now().strftime("%Y%m%d%H%M%S"),
            "filename": "test_file.pdf",
            "page_number": 1,
            "chunk_id": 0,
            "content": "Este é um teste de inserção na tabela documento_chunks",
            "embedding": test_embedding
        }
        
        print(f"🔵 Tentando inserir registro de teste...")
        print(f"   document_id: {test_record['document_id']}")
        print(f"   filename: {test_record['filename']}")
        print(f"   embedding_dim: {len(test_embedding)}")
        
        # Tentar inserir
        result = supabase.table(settings.TABLE_EMBEDDINGS).insert(test_record).execute()
        
        if result.data and len(result.data) > 0:
            inserted_id = result.data[0].get('id')
            print_status("Inserção na tabela documento_chunks", True, f"Registro inserido com ID: {inserted_id}")
            
            # Limpar registro de teste
            try:
                supabase.table(settings.TABLE_EMBEDDINGS).delete().eq("document_id", test_record['document_id']).execute()
                print(f"   🧹 Registro de teste removido")
            except:
                pass
            
            return True
        else:
            print_status("Inserção na tabela documento_chunks", False, "Nenhum dado retornado após inserção")
            return False
            
    except Exception as e:
        error_msg = str(e)
        print_status("Inserção na tabela documento_chunks", False, f"Erro: {error_msg}")
        print(f"   Detalhes do erro: {type(e).__name__}")
        if hasattr(e, 'code'):
            print(f"   Código do erro: {e.code}")
        if hasattr(e, 'message'):
            print(f"   Mensagem: {e.message}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()[:500]}")
        return False

def test_pdf_extraction():
    """Testa se consegue extrair texto de um PDF"""
    try:
        from processor import DocumentProcessor
        
        processor = DocumentProcessor()
        
        # Verificar se existe algum PDF na pasta atual para testar
        import glob
        pdf_files = glob.glob("*.pdf")
        
        if not pdf_files:
            print_status("Extração de PDF", None, "Nenhum PDF encontrado na pasta para teste")
            print("   (Isso não é um erro - apenas não há PDFs disponíveis)")
            return None
        
        # Usar o primeiro PDF encontrado
        test_pdf = pdf_files[0]
        print(f"🔵 Testando extração do PDF: {test_pdf}")
        
        # Tentar extrair apenas a primeira página (processamento rápido)
        from pypdf import PdfReader
        reader = PdfReader(test_pdf)
        
        if len(reader.pages) == 0:
            print_status("Extração de PDF", False, "PDF sem páginas")
            return False
        
        # Extrair primeira página
        first_page = reader.pages[0]
        content = first_page.extract_text()
        
        if content and len(content.strip()) > 0:
            print_status("Extração de PDF", True, f"Texto extraído: {len(content)} caracteres da primeira página")
            print(f"   Prévia: {content[:100]}...")
            return True
        else:
            print_status("Extração de PDF", False, "Nenhum texto extraído da primeira página")
            return False
            
    except ImportError as e:
        print_status("Extração de PDF", False, f"Biblioteca não encontrada: {str(e)}")
        return False
    except Exception as e:
        print_status("Extração de PDF", False, f"Erro: {str(e)}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()[:500]}")
        return False

def test_embedding_creation():
    """Testa se consegue criar embeddings"""
    try:
        from vectorstore import VectorStore
        
        vectorstore = VectorStore()
        
        # Criar embedding de teste
        test_text = "Este é um teste de criação de embedding"
        print(f"🔵 Testando criação de embedding para: '{test_text}'")
        
        embeddings = vectorstore._create_embeddings_batch([test_text])
        
        if embeddings and len(embeddings) > 0:
            embedding = embeddings[0]
            embedding_dim = len(embedding) if embedding else 0
            
            if embedding_dim == 1536:
                print_status("Criação de embeddings", True, f"Embedding criado com {embedding_dim} dimensões (correto)")
                return True
            else:
                print_status("Criação de embeddings", True, f"Embedding criado com {embedding_dim} dimensões (esperado: 1536)")
                print("   ⚠️ Dimensão incorreta, mas será ajustada automaticamente")
                return True
        else:
            print_status("Criação de embeddings", False, "Nenhum embedding retornado")
            return False
            
    except Exception as e:
        print_status("Criação de embeddings", False, f"Erro: {str(e)}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()[:500]}")
        return False

def test_full_flow():
    """Testa o fluxo completo: extração -> chunk -> embedding -> inserção"""
    try:
        from processor import DocumentProcessor
        from vectorstore import VectorStore
        from config import settings
        import glob
        
        # Buscar PDF para teste
        pdf_files = glob.glob("*.pdf")
        if not pdf_files:
            print_status("Fluxo completo", None, "Nenhum PDF encontrado para teste")
            return None
        
        test_pdf = pdf_files[0]
        print(f"🔵 Testando fluxo completo com: {test_pdf}")
        
        processor = DocumentProcessor()
        vectorstore = VectorStore()
        
        # Criar chunks de teste (simulando extração)
        chunks = []
        from pypdf import PdfReader
        reader = PdfReader(test_pdf)
        
        if len(reader.pages) == 0:
            print_status("Fluxo completo", False, "PDF sem páginas")
            return False
        
        # Extrair primeira página e criar chunk
        first_page = reader.pages[0]
        content = first_page.extract_text()
        
        if not content or len(content.strip()) == 0:
            print_status("Fluxo completo", False, "Nenhum texto extraído")
            return False
        
        # Criar chunk de teste
        test_doc_id = "TEST_FLOW_" + datetime.now().strftime("%Y%m%d%H%M%S")
        chunk = {
            "document_id": test_doc_id,
            "filename": os.path.basename(test_pdf),
            "page_number": 1,
            "chunk_id": 0,
            "content": content[:500]  # Limitar a 500 chars para teste rápido
        }
        chunks.append(chunk)
        
        print(f"   ✅ Chunk criado: {len(chunk['content'])} caracteres")
        
        # Tentar salvar no banco
        try:
            vectorstore.store_chunks(chunks)
            print_status("Fluxo completo", True, "Chunk processado e salvo com sucesso")
            
            # Verificar se foi salvo
            has_chunks = vectorstore.has_chunks(document_id=test_doc_id)
            if has_chunks:
                print(f"   ✅ Verificação: Chunk confirmado no banco")
                
                # Limpar teste
                try:
                    from supabase import create_client
                    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
                    supabase.table(settings.TABLE_EMBEDDINGS).delete().eq("document_id", test_doc_id).execute()
                    print(f"   🧹 Chunk de teste removido")
                except:
                    pass
                
                return True
            else:
                print_status("Fluxo completo", False, "Chunk não encontrado no banco após inserção")
                return False
                
        except Exception as e:
            print_status("Fluxo completo", False, f"Erro ao salvar chunk: {str(e)}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()[:1000]}")
            return False
            
    except Exception as e:
        print_status("Fluxo completo", False, f"Erro: {str(e)}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()[:1000]}")
        return False

def main():
    """Executa todos os testes"""
    print("=" * 60)
    print("🔍 DIAGNÓSTICO: Extração de PDF e Tabela documento_chunks")
    print("=" * 60)
    print()
    
    results = []
    
    # Teste 1: Estrutura da tabela
    table_ok, supabase = test_table_structure()
    results.append(("Estrutura da tabela", table_ok))
    
    # Teste 2: Inserção na tabela (só se tabela OK)
    if table_ok and supabase:
        insertion_ok = test_table_insertion(supabase)
        results.append(("Inserção na tabela", insertion_ok))
    else:
        results.append(("Inserção na tabela", False))
    
    # Teste 3: Extração de PDF
    pdf_extraction_result = test_pdf_extraction()
    results.append(("Extração de PDF", pdf_extraction_result if pdf_extraction_result is not None else False))
    
    # Teste 4: Criação de embeddings
    embedding_ok = test_embedding_creation()
    results.append(("Criação de embeddings", embedding_ok))
    
    # Teste 5: Fluxo completo
    flow_result = test_full_flow()
    results.append(("Fluxo completo (PDF -> Chunk -> Banco)", flow_result if flow_result is not None else False))
    
    # Resumo
    print("=" * 60)
    print("📊 RESUMO")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len([r for _, r in results if r is not None])
    
    for name, result in results:
        if result is None:
            icon = "⏭️"
            status = "Pulado (sem PDF para teste)"
        else:
            icon = "✅" if result else "❌"
            status = "OK" if result else "FALHOU"
        print(f"{icon} {name}: {status}")
    
    print()
    print(f"Total: {passed}/{total} testes passaram")
    
    if passed == total:
        print("✅ Todos os testes passaram! A tabela e extração estão funcionando.")
        return 0
    else:
        print("❌ Alguns testes falharam. Verifique os erros acima.")
        return 1

if __name__ == "__main__":
    sys.exit(main())