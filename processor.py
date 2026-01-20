#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
from typing import Dict, List, Callable, Optional
import hashlib
import re
import os
import sys
import json

# Configurar encoding UTF-8 para Windows (evita erro com emojis)
# NOTA: Removido para evitar conflitos durante importação
# if sys.platform == 'win32':
#     import io
#     try:
#         if hasattr(sys.stdout, 'buffer'):
#             sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
#         if hasattr(sys.stderr, 'buffer'):
#             sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
#     except:
#         pass  # Ignorar se já estiver configurado

def _debug_log_processor(location, message, data, hypothesis_id="A"):
    """Debug logging helper para processor"""
    log_path = r'c:\Users\TRIA 2026\Downloads\ProcessIA\.cursor\debug.log'
    try:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        log_entry = {
            "sessionId": "debug-session",
            "runId": "run1",
            "hypothesisId": hypothesis_id,
            "location": location,
            "message": message,
            "data": data,
            "timestamp": int(__import__('time').time()*1000)
        }
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    except Exception:
        pass

class DocumentProcessor:
    """Processador usando PyMuPDF (fitz) - muito mais robusto que pypdf"""
    
    def __init__(self):
        # Verificar se PyMuPDF está disponível
        try:
            import fitz
            # #region agent log
            _debug_log_processor("processor.py:__init__", "PyMuPDF importado", {"fitz_version": getattr(fitz, '__version__', 'unknown')}, "A")
            # #endregion
            print("✅ [PROCESSOR] PyMuPDF (fitz) carregado com sucesso")
        except ImportError as e:
            # #region agent log
            _debug_log_processor("processor.py:__init__", "PyMuPDF import ERROR", {"error": str(e)}, "A,E")
            # #endregion
            raise ImportError(
                "Instale PyMuPDF: pip install PyMuPDF"
            )
    
    def _fix_unicode_text(self, text: str) -> str:
        """Corrige problemas de encoding Unicode no texto extraído"""
        if not text:
            return ""
        
        # Remover caracteres de controle problemáticos, mas manter quebras de linha
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', text)
        
        # Normalizar espaços em branco múltiplos (mas preservar quebras de linha)
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        return text.strip()
    
    def _split_text(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """Divide texto em chunks com overlap"""
        if not text or not text.strip():
            return []
        
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = start + chunk_size
            
            # Se não é o último chunk, tentar quebrar em parágrafo ou frase
            if end < text_len:
                # Procurar quebra de parágrafo
                last_para = text.rfind('\n\n', start, end)
                if last_para > start + chunk_size // 2:
                    end = last_para + 2
                else:
                    # Procurar quebra de frase
                    last_sentence = max(
                        text.rfind('. ', start, end),
                        text.rfind('.\n', start, end),
                        text.rfind('! ', start, end),
                        text.rfind('? ', start, end)
                    )
                    if last_sentence > start + chunk_size // 2:
                        end = last_sentence + 2
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Próximo chunk com overlap
            start = end - overlap if end < text_len else text_len
        
        return chunks
    
    def _split_text_small(self, text: str, max_size: int = 1000) -> List[str]:
        """Divide texto pequeno em chunks menores se necessário"""
        if len(text) <= max_size:
            return [text]
        return self._split_text(text, max_size, 100)
    
    def _is_mostly_overlapping(self, text1: str, text2: str, threshold: float = 0.8) -> bool:
        """Verifica se dois textos têm overlap significativo"""
        if not text1 or not text2:
            return False
        
        # Comparar primeiros e últimos 200 caracteres
        sample_size = min(200, len(text1), len(text2))
        
        # Verificar se início de text2 está no final de text1
        text1_end = text1[-sample_size:]
        text2_start = text2[:sample_size]
        
        # Contar caracteres em comum
        common = sum(1 for a, b in zip(text1_end, text2_start) if a == b)
        similarity = common / sample_size if sample_size > 0 else 0
        
        return similarity >= threshold
    
    def _extract_numero_processo(self, text: str) -> Optional[str]:
        """Extrai número do processo do texto"""
        if not text:
            return None
        
        # Padrão: 0000000-00.0000.0.00.0000
        pattern = r'\b(\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})\b'
        match = re.search(pattern, text)
        
        if match:
            return match.group(1)
        
        return None
    
    def _generate_id(self, pdf_path: str) -> str:
        """Gera ID único baseado no hash do arquivo"""
        try:
            # Ler arquivo em blocos para não carregar tudo na memória
            hash_obj = hashlib.sha256()
            with open(pdf_path, 'rb') as f:
                # Ler em blocos de 64KB
                while chunk := f.read(65536):
                    hash_obj.update(chunk)
            file_hash = hash_obj.hexdigest()
            return f"doc_{file_hash[:12]}"
        except Exception as e:
            # Fallback: usar hash do caminho do arquivo
            print(f"⚠️ [PROCESSOR] Erro ao gerar hash do arquivo: {str(e)}, usando hash do caminho")
            path_hash = hashlib.sha256(pdf_path.encode()).hexdigest()
            return f"doc_{path_hash[:12]}"
    
    def process_incremental(self, pdf_path: str, filename: str, 
                           chunk_callback: Optional[Callable] = None, 
                           batch_size: int = 50) -> Dict:
        """Processa PDF página por página e chama callback para cada batch de chunks
        
        Args:
            pdf_path: Caminho do arquivo PDF
            filename: Nome do arquivo
            chunk_callback: Função chamada para cada batch de chunks
            batch_size: Número de chunks por batch
        """
        # #region agent log
        _debug_log_processor("processor.py:137", "process_incremental ENTRY", {
            "pdf_path": pdf_path,
            "filename": filename,
            "batch_size": batch_size,
            "chunk_callback_provided": chunk_callback is not None,
            "pdf_exists": os.path.exists(pdf_path),
            "pdf_size": os.path.getsize(pdf_path) if os.path.exists(pdf_path) else 0
        }, "A,B,G")
        # #endregion
        
        print(f"🟢 [PROCESSOR] process_incremental: Iniciando processamento")
        print(f"🟢 [PROCESSOR] PDF: {pdf_path}")
        print(f"🟢 [PROCESSOR] Filename: {filename}")
        print(f"🟢 [PROCESSOR] Batch size: {batch_size}")
        print(f"🟢 [PROCESSOR] Chunk callback: {'Fornecido' if chunk_callback else 'Não fornecido'}")
        
        import fitz  # PyMuPDF
        from config import settings
        
        # #region agent log
        _debug_log_processor("processor.py:177", "ANTES de abrir PDF", {"pdf_path": pdf_path, "exists": os.path.exists(pdf_path)}, "B")
        # #endregion
        
        print(f"=" * 80)
        print(f"🔵 [PROCESSOR] USANDO PyMuPDF (FITZ) - BIBLIOTECA ROBUSTA")
        print(f"=" * 80)
        print(f"🟢 [PROCESSOR] Abrindo PDF com PyMuPDF...")
        
        # #region agent log
        doc = None
        try:
            # PyMuPDF é muito mais robusto e não tem problemas com arquivos fechados
            # #region agent log
            _debug_log_processor("processor.py:187", "CHAMANDO fitz.open", {"pdf_path": pdf_path}, "B")
            # #endregion
            
            # Abrir documento e garantir que permanece aberto durante toda a extração
            print(f"🟢 [PROCESSOR] Abrindo documento PyMuPDF...")
            doc = fitz.open(pdf_path)
            
            # #region agent log
            _debug_log_processor("processor.py:189", "fitz.open SUCESSO", {
                "doc_type": str(type(doc)),
                "is_closed": doc.is_closed,
                "page_count": doc.page_count
            }, "B")
            # #endregion
            
            if doc.is_closed:
                raise ValueError("Documento foi fechado imediatamente após abrir!")
            
            total_pages = len(doc)
            
            if total_pages == 0:
                raise ValueError("PDF não tem páginas!")
            
            print(f"✅ [PROCESSOR] PDF aberto: {total_pages} páginas")
            
            # Gerar ID do documento (antes de qualquer operação que possa fechar)
            doc_id = self._generate_id(pdf_path)
            
            _debug_log_processor("processor.py:159", "PyMuPDF SUCCESS", {
                "total_pages": total_pages,
                "doc_id": doc_id,
                "is_encrypted": doc.is_encrypted,
                "page_count": doc.page_count,
                "is_closed": doc.is_closed
            }, "B,C")
            
            print(f"✅ [PROCESSOR] doc_id={doc_id}")
            print(f"🟢 [PROCESSOR] Extraindo texto de todas as páginas...")
            
            # Verificar se documento está aberto antes de extrair
            if doc.is_closed:
                raise ValueError("Documento já está fechado antes da extração!")
            
            # Extrair texto de todas as páginas ANTES de fechar o documento
            pages_content = []
            for page_num in range(total_pages):
                try:
                    # Verificar se documento ainda está aberto antes de cada página
                    if doc.is_closed:
                        raise ValueError(f"Documento foi fechado durante extração (página {page_num + 1})")
                    
                    # Carregar página primeiro e manter referência durante extração
                    page = doc[page_num]
                    if page is None:
                        raise ValueError(f"Página {page_num + 1} é None")
                    
                    # Extrair texto da página
                    content = page.get_text("text")
                    content_str = str(content) if content else ""
                    
                    # Limpar referência à página após extrair texto
                    del page
                    
                    pages_content.append({
                        "page_num": page_num + 1,  # 1-indexed
                        "content": content_str,
                    })
                    print(f"🟢 [PROCESSOR] Página {page_num + 1}/{total_pages}: {len(content_str)} caracteres extraídos")
                except RuntimeError as e:
                    # PyMuPDF pode lançar RuntimeError quando documento está fechado
                    error_msg = str(e)
                    if "closed" in error_msg.lower() or "document" in error_msg.lower():
                        raise ValueError(f"Documento fechado ao acessar página {page_num + 1}: {error_msg}")
                    raise
                except Exception as e:
                    error_msg = str(e)
                    error_type = type(e).__name__
                    print(f"⚠️ [PROCESSOR] Erro ao extrair página {page_num + 1}: {error_type}: {error_msg}")
                    import traceback
                    print(f"⚠️ [PROCESSOR] Traceback: {traceback.format_exc()[:500]}")
                    pages_content.append({
                        "page_num": page_num + 1,
                        "content": f"[Erro ao extrair texto da página {page_num + 1}: {error_msg}]",
                    })
                    # Se o documento foi fechado, não continuar
                    if "closed" in error_msg.lower() or "document closed" in error_msg.lower():
                        raise ValueError(f"Documento fechado durante extração: {error_msg}")
            
            print(f"✅ [PROCESSOR] {len(pages_content)} páginas extraídas com sucesso")
            
            # NÃO fechar o documento aqui - será fechado no finally após TODOS os callbacks
            # O documento precisa ficar "aberto" até que todos os chunks finais sejam processados
            
            # AGORA processar o texto extraído
            pages_text = []
            full_text_parts = []
            all_chunks = []
            chunk_id = 0
            
            MAX_PAGE_SIZE = 5 * 1024 * 1024  # 5MB por página
            numero_processo = None
            
            for page_data in pages_content:
                page_num = page_data["page_num"]
                content = page_data["content"]
                
                # #region agent log
                _debug_log_processor("processor.py:172", "LOOP ITERATION", {"page_num": page_num, "total_pages": total_pages}, "C")
                # #endregion
                
                print(f"🟢 [PROCESSOR] Processando página {page_num}/{total_pages}...")
                original_len = len(content) if content else 0
                print(f"🟢 [PROCESSOR] Página {page_num}: {original_len} caracteres extraídos")
                
                try:
                    # #region agent log
                    _debug_log_processor("processor.py:176", "PROCESSING EXTRACTED TEXT", {
                        "page_num": page_num,
                        "content_len": original_len,
                        "content_is_none": content is None,
                        "content_is_empty": not content or not content.strip()
                    }, "D")
                    # #endregion
                    
                    # Corrigir códigos Unicode
                    print(f"🟢 [PROCESSOR] Corrigindo Unicode da página {page_num}...")
                    content = self._fix_unicode_text(content)
                    fixed_len = len(content) if content else 0
                    if original_len != fixed_len:
                        print(f"🟢 [PROCESSOR] Página {page_num}: Unicode corrigido ({original_len} -> {fixed_len} chars)")
                    
                    # Limitar tamanho de páginas muito grandes
                    if len(content) > MAX_PAGE_SIZE:
                        print(f"⚠️ [PROCESSOR] Página {page_num} muito grande ({len(content)} chars), truncando para {MAX_PAGE_SIZE}...")
                        content = content[:MAX_PAGE_SIZE] + "\n\n[Conteúdo truncado - página muito grande]"
                        print(f"🟢 [PROCESSOR] Página {page_num} truncada: {len(content)} chars")
                        
                except MemoryError:
                    # #region agent log
                    _debug_log_processor("processor.py:193", "MemoryError CAUGHT", {"page_num": page_num}, "E")
                    # #endregion
                    print(f"❌ [PROCESSOR] ERRO DE MEMÓRIA na página {page_num}")
                    content = f"[Erro de memória ao processar página {page_num}]"
                except Exception as e:
                    # #region agent log
                    _debug_log_processor("processor.py:196", "EXCEPTION CAUGHT", {
                        "page_num": page_num,
                        "error": str(e),
                        "error_type": type(e).__name__
                    }, "E")
                    # #endregion
                    print(f"❌ [PROCESSOR] ERRO ao processar página {page_num}: {str(e)}")
                    content = f"[Erro ao processar página {page_num}: {str(e)}]"
                    
                # Extrair número do processo das primeiras páginas
                if page_num <= 10 and not numero_processo:
                    print(f"🟢 [PROCESSOR] Tentando extrair número do processo da página {page_num}...")
                    numero_processo = self._extract_numero_processo(content)
                    if numero_processo:
                        print(f"✅ [PROCESSOR] Número do processo encontrado na página {page_num}: {numero_processo}")
                    else:
                        print(f"🟢 [PROCESSOR] Número do processo não encontrado na página {page_num}")
                
                # Guardar página (metadata limitada)
                page_metadata_content = content[:1000] if len(content) > 1000 else content
                pages_text.append({
                    "page_number": page_num,
                    "content": page_metadata_content,  # Guardar só início
                    "char_count": len(content)
                })
                
                # Criar chunks desta página
                if not content or not content.strip():
                    print(f"⚠️ [PROCESSOR] Página {page_num} vazia, pulando...")
                    continue  # Pular páginas vazias
                
                content = content.strip()
                
                if not content:  # Se após normalização ficou vazio, pular
                    print(f"⚠️ [PROCESSOR] Página {page_num} ficou vazia após normalização, pulando...")
                    continue
                
                print(f"🟢 [PROCESSOR] Página {page_num} pronta para chunking: {len(content)} caracteres")
                
                # Verificar se este conteúdo não é duplicado da página anterior
                if all_chunks:
                    last_chunk_content = all_chunks[-1].get("content", "")
                    # Se o conteúdo começar com os últimos 100 chars do chunk anterior, pode ser duplicata
                    if len(content) >= 100 and len(last_chunk_content) >= 100:
                        last_100 = last_chunk_content[-100:]
                        first_100 = content[:100]
                        # Verificar sobreposição
                        if first_100 == last_100:
                            print(f"Aviso: Página {page_num} parece duplicar final da anterior. Removendo sobreposição...")
                            # Tentar encontrar onde começa o conteúdo novo
                            overlap_pos = last_chunk_content.rfind(content[:50])
                            if overlap_pos > 0:
                                # Pular a parte duplicada
                                skip_chars = len(last_chunk_content) - overlap_pos
                                if skip_chars < len(content):
                                    content = content[skip_chars:].strip()
                                if not content or len(content) < 10:
                                    print(f"Aviso: Página {page_num} completamente duplicada, ignorando...")
                                    continue
                
                # Criar chunks desta página
                if len(content) > settings.CHUNK_SIZE:
                    print(f"🟢 [PROCESSOR] Página {page_num}: Texto grande ({len(content)} chars), dividindo em chunks (CHUNK_SIZE={settings.CHUNK_SIZE}, OVERLAP={settings.CHUNK_OVERLAP})...")
                    page_chunks_texts = self._split_text(content, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
                    print(f"✅ [PROCESSOR] Página {page_num}: Dividida em {len(page_chunks_texts)} chunks")
                else:
                    print(f"🟢 [PROCESSOR] Página {page_num}: Texto pequeno ({len(content)} chars), criando 1 chunk único")
                    page_chunks_texts = [content] if content.strip() else []
                
                # Criar objetos chunk, evitando duplicatas
                seen_chunk_contents = set()
                page_chunks_count = 0
                for chunk_idx, chunk_text in enumerate(page_chunks_texts, 1):
                    chunk_text = chunk_text.strip()
                    if not chunk_text:
                        print(f"⚠️ [PROCESSOR] Página {page_num}, chunk {chunk_idx}: Vazio, pulando")
                        continue
                    
                    # Verificar se este chunk não é duplicata (mesmo conteúdo exato)
                    chunk_hash = hashlib.md5(chunk_text.encode()).hexdigest()
                    if chunk_hash in seen_chunk_contents:
                        print(f"⚠️ [PROCESSOR] Página {page_num}, chunk {chunk_idx}: Duplicata detectada, pulando")
                        continue
                    seen_chunk_contents.add(chunk_hash)
                    
                    chunk_obj = {
                        "chunk_id": chunk_id,
                        "document_id": doc_id,  # Na raiz para vectorstore
                        "filename": filename,  # Na raiz para vectorstore
                        "content": chunk_text,
                        "page_number": page_num,
                        "char_count": len(chunk_text),
                        "metadata": {
                            "page": page_num,
                            "chunk_index": chunk_idx,
                            "total_pages": total_pages,
                            "filename": filename,
                            "document_id": doc_id
                        }
                    }
                    all_chunks.append(chunk_obj)
                    chunk_id += 1
                    page_chunks_count += 1
                    print(f"✅ [PROCESSOR] Página {page_num}, chunk {chunk_idx}: Criado (ID global: {chunk_id-1}, {len(chunk_text)} chars)")
                
                print(f"✅ [PROCESSOR] Página {page_num}: {page_chunks_count} chunks criados")
                
                # Chamar callback se tivermos chunks suficientes
                if chunk_callback and len(all_chunks) >= batch_size:
                    print(f"🟢 [PROCESSOR] Chamando callback com batch de {len(all_chunks)} chunks...")
                    try:
                        chunk_callback(all_chunks, doc_id, filename)
                        print(f"✅ [PROCESSOR] Callback executado com sucesso para {len(all_chunks)} chunks")
                        all_chunks = []  # Limpar após salvar
                    except Exception as e:
                        print(f"❌ [PROCESSOR] ERRO no callback: {str(e)}")
                        import traceback
                        print(f"❌ [PROCESSOR] Traceback: {traceback.format_exc()[:1000]}")
                        raise
            
            # Processar chunks restantes
            if chunk_callback and all_chunks:
                print(f"🟢 [PROCESSOR] Processando chunks finais ({len(all_chunks)} restantes)...")
                try:
                    chunk_callback(all_chunks, doc_id, filename)
                    print(f"✅ [PROCESSOR] Chunks finais processados")
                except Exception as e:
                    print(f"❌ [PROCESSOR] ERRO ao processar chunks finais: {str(e)}")
                    import traceback
                    print(f"❌ [PROCESSOR] Traceback: {traceback.format_exc()[:1000]}")
                    raise
            
            # #region agent log
            _debug_log_processor("processor.py:309", "process_incremental EXIT", {
                "total_chunks_created": chunk_id,
                "total_pages": total_pages,
                "doc_id": doc_id,
                "numero_processo": numero_processo
            }, "A")
            # #endregion
            
            # Retornar resultado
            result = {
                "document_id": doc_id,
                "filename": filename,
                "metadata": {
                    "total_pages": total_pages,
                    "total_chunks": chunk_id,
                    "numero_processo": numero_processo,
                    "pages": pages_text
                }
            }
            
            print(f"✅ [PROCESSOR] process_incremental concluído: doc_id={doc_id}, total_pages={total_pages}, numero_processo={numero_processo}")
            return result
        except Exception as e:
            _debug_log_processor("processor.py:159", "PyMuPDF ERROR", {
                "error": str(e),
                "error_type": type(e).__name__
            }, "B,E")
            raise
        finally:
            # GARANTIR que o documento seja fechado sempre, mesmo se houver erro
            if doc and not doc.is_closed:
                try:
                    doc.close()
                    print(f"✅ [PROCESSOR] Documento PyMuPDF fechado no finally")
                except Exception as close_error:
                    print(f"⚠️ [PROCESSOR] Aviso ao fechar documento no finally: {str(close_error)}")
        # #endregion
