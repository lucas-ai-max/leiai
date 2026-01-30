#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
from typing import Dict, List, Callable, Optional
import hashlib
import re
import os

class DocumentProcessor:
    """Processador usando pypdf (leve e rápido)"""
    
    def __init__(self):
        # Verificar se pypdf está disponível
        try:
            from pypdf import PdfReader
        except ImportError:
            raise ImportError(
                "Instale pypdf: pip install pypdf"
            )
    
    def _fix_unicode_text(self, text: str) -> str:
        """Converte códigos Unicode /uniXXXX para caracteres legíveis"""
        if not text or '/uni' not in text:
            return text
        
        # Padrão para encontrar /uniXXXX
        pattern = r'/uni([0-9A-Fa-f]{4})'
        
        def replace_unicode(match):
            try:
                # Converter código hexadecimal para caractere
                code = int(match.group(1), 16)
                return chr(code)
            except (ValueError, OverflowError):
                # Se falhar, retornar o código original
                return match.group(0)
        
        # Substituir todos os códigos Unicode
        fixed_text = re.sub(pattern, replace_unicode, text)
        
        # Limpar apenas espaços horizontais múltiplos (preservar quebras de linha)
        fixed_text = re.sub(r'[ \t]+', ' ', fixed_text)
        # Normalizar apenas múltiplas quebras de linha consecutivas (3+ vira 2)
        fixed_text = re.sub(r'\n\n\n+', '\n\n', fixed_text)
        
        return fixed_text.strip()
    
    def process(self, pdf_path: str, filename: str = None) -> Dict:
        """Extrai documento usando pypdf
        
        Args:
            pdf_path: Caminho do arquivo PDF
            filename: Nome original do arquivo (se não fornecido, usa o nome do caminho)
        """
        from pypdf import PdfReader
        
        reader = PdfReader(pdf_path)
        if filename is None:
            filename = Path(pdf_path).name
        doc_id = self._generate_id(pdf_path)
        
        pages_text = []
        full_text_parts = []
        
        for page_num, page in enumerate(reader.pages, 1):
            try:
                content = page.extract_text()
                content = self._fix_unicode_text(content)
            except Exception as e:
                content = f"[Erro ao extrair texto da página {page_num}: {str(e)}]"
            
            full_text_parts.append(content)
            pages_text.append({
                "page_number": page_num,
                "content": content,
                "char_count": len(content)
            })
        
        full_text = "\n\n".join(full_text_parts)
        
        return {
            "document_id": doc_id,
            "filename": filename,
            "full_text": full_text,
            "pages": pages_text,
            "metadata": {
                "document_id": doc_id,
                "filename": filename,
                "total_pages": len(pages_text),
                "numero_processo": self._extract_numero_processo(full_text)
            }
        }
    
    def chunk_with_pages(self, document: Dict) -> List[Dict]:
        """Cria chunks mantendo referência de página"""
        from config import settings
        
        chunks = []
        chunk_id = 0
        
        for page_info in document["pages"]:
            page_num = page_info["page_number"]
            content = page_info["content"]
            
            if len(content) > settings.CHUNK_SIZE:
                page_chunks = self._split_text(content, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
                
                for sub_chunk in page_chunks:
                    chunks.append({
                        "chunk_id": chunk_id,
                        "content": sub_chunk,
                        "page_number": page_num,
                        "document_id": document["document_id"],
                        "filename": document["filename"]
                    })
                    chunk_id += 1
            else:
                chunks.append({
                    "chunk_id": chunk_id,
                    "content": content,
                    "page_number": page_num,
                    "document_id": document["document_id"],
                    "filename": document["filename"]
                })
                chunk_id += 1
        
        return chunks
    
    def _generate_id(self, pdf_path: str) -> str:
        """Gera ID único baseado no hash do arquivo"""
        try:
            hash_obj = hashlib.sha256()
            with open(pdf_path, 'rb') as f:
                while chunk := f.read(65536):
                    hash_obj.update(chunk)
            file_hash = hash_obj.hexdigest()
            return f"doc_{file_hash[:12]}"
        except Exception as e:
            path_hash = hashlib.sha256(pdf_path.encode()).hexdigest()
            return f"doc_{path_hash[:12]}"
    
    def process_incremental(self, pdf_path: str, filename: str, 
                           chunk_callback: Optional[Callable] = None, 
                           batch_size: int = 50) -> Dict:
        """Processa PDF página por página e chama callback para cada batch de chunks
        
        Args:
            pdf_path: Caminho do arquivo PDF
            filename: Nome original do arquivo
            chunk_callback: Função(chunks_batch) chamada a cada batch
            batch_size: Número de chunks por batch
        """
        from pypdf import PdfReader
        from config import settings
        
        reader = PdfReader(pdf_path)
        doc_id = self._generate_id(pdf_path)
        total_pages = len(reader.pages)
        
        pages_text = []
        full_text_parts = []
        all_chunks = []
        chunk_id = 0
        
        MAX_PAGE_SIZE = 5 * 1024 * 1024  # 5MB por página
        numero_processo = None
        
        for page_num, page in enumerate(reader.pages, 1):
            try:
                content = page.extract_text()
                content = self._fix_unicode_text(content)
                
                if len(content) > MAX_PAGE_SIZE:
                    content = content[:MAX_PAGE_SIZE] + "\n\n[Conteúdo truncado - página muito grande]"
                    
            except MemoryError:
                content = f"[Erro de memória ao extrair texto da página {page_num}]"
            except Exception as e:
                content = f"[Erro ao extrair texto da página {page_num}: {str(e)}]"
            
            # Extrair número do processo das primeiras páginas
            if page_num <= 10 and not numero_processo:
                numero_processo = self._extract_numero_processo(content)
            
            # Guardar página (metadata limitada)
            pages_text.append({
                "page_number": page_num,
                "content": content[:1000] if len(content) > 1000 else content,
                "char_count": len(content)
            })
            
            # Criar chunks desta página
            if not content or not content.strip():
                continue
            
            content = content.strip()
            
            if not content:
                continue
            
            # Verificar se este conteúdo não é duplicado da página anterior
            if all_chunks:
                last_chunk_content = all_chunks[-1].get("content", "")
                if len(content) >= 100 and len(last_chunk_content) >= 100:
                    last_100 = last_chunk_content[-100:]
                    first_100 = content[:100]
                    if first_100 == last_100:
                        overlap_pos = last_chunk_content.rfind(content[:50])
                        if overlap_pos > 0:
                            skip_chars = len(last_chunk_content) - overlap_pos
                            if skip_chars < len(content):
                                content = content[skip_chars:].strip()
                            if not content or len(content) < 10:
                                continue
            
            # Criar chunks desta página
            if len(content) > settings.CHUNK_SIZE:
                page_chunks_texts = self._split_text(content, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
            else:
                page_chunks_texts = [content] if content.strip() else []
            
            # Criar objetos chunk, evitando duplicatas
            seen_chunk_contents = set()
            for chunk_text in page_chunks_texts:
                chunk_text = chunk_text.strip()
                if not chunk_text:
                    continue
                
                if chunk_text in seen_chunk_contents:
                    continue
                
                seen_chunk_contents.add(chunk_text)
                
                all_chunks.append({
                    "chunk_id": chunk_id,
                    "content": chunk_text,
                    "page_number": page_num,
                    "document_id": doc_id,
                    "filename": filename
                })
                chunk_id += 1
            
            # Processar e salvar em batches
            if len(all_chunks) >= batch_size and chunk_callback:
                chunk_callback(all_chunks)
                all_chunks = []
            
            # Acumular texto apenas para metadata (limitado)
            if len(full_text_parts) < 100:
                full_text_parts.append(content[:10000])
        
        # Processar chunks restantes
        if all_chunks and chunk_callback:
            chunk_callback(all_chunks)
        
        # Construir metadata
        full_text = "\n\n".join(full_text_parts) if full_text_parts else ""
        
        return {
            "document_id": doc_id,
            "filename": filename,
            "full_text": full_text,
            "pages": pages_text,
            "metadata": {
                "document_id": doc_id,
                "filename": filename,
                "total_pages": total_pages,
                "numero_processo": numero_processo
            }
        }
    
    def _split_text(self, text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        """Divide texto em chunks com overlap"""
        if len(text) <= chunk_size:
            return [text.strip()] if text.strip() else []
        
        if len(text) > chunk_size * 100:
            chunks = []
            block_size = chunk_size * 20
            
            for i in range(0, len(text), block_size):
                block = text[i:i + block_size]
                if block.strip():
                    block_chunks = self._split_text_small(block, chunk_size, chunk_overlap)
                    chunks.extend(block_chunks)
            
            return chunks
        
        return self._split_text_small(text, chunk_size, chunk_overlap)
    
    def _split_text_small(self, text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        """Divide texto pequeno/médio em chunks"""
        if len(text) <= chunk_size:
            return [text.strip()] if text.strip() else []
        
        chunks = []
        start = 0
        min_chunk_size = max(100, chunk_size // 10)
        
        while start < len(text):
            end = min(start + chunk_size, len(text))
            
            if end < len(text):
                last_para = text.rfind('\n\n', start, end)
                if last_para > start:
                    end = last_para + 2
                else:
                    last_newline = text.rfind('\n', start, end)
                    if last_newline > start:
                        end = last_newline + 1
                    else:
                        last_period = text.rfind('. ', start, end)
                        if last_period > start:
                            end = last_period + 2
            
            chunk = text[start:end]
            stripped = chunk.strip()
            
            if stripped and len(stripped) >= min_chunk_size:
                if not chunks or not self._is_mostly_overlapping(stripped, chunks[-1]):
                    chunks.append(stripped)
            
            if end < len(text):
                if chunk_overlap > 0:
                    start = max(end - chunk_overlap, start + 1)
                else:
                    start = end
            else:
                break
            
            if start >= len(text) or start == end:
                break
        
        return chunks
    
    def _is_mostly_overlapping(self, text1: str, text2: str, threshold: float = 0.8) -> bool:
        """Verifica se dois textos têm mais de threshold% de sobreposição"""
        if not text1 or not text2:
            return False
        
        min_len = min(len(text1), len(text2))
        overlap_len = 0
        
        for i in range(min(200, min_len), 0, -1):
            if text1[-i:] == text2[:i]:
                overlap_len = i
                break
        
        if overlap_len > 0:
            overlap_ratio = overlap_len / min_len
            return overlap_ratio >= threshold
        
        return False
    
    def _extract_numero_processo(self, text: str) -> Optional[str]:
        """Extrai número do processo"""
        if not text:
            return None
        
        pattern = r'\b(\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})\b'
        match = re.search(pattern, text[:3000])
        return match.group(1) if match else None
