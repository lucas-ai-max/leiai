from pathlib import Path
from typing import Dict, List, Callable, Optional
import hashlib
import re

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
    
    def process(self, pdf_path: str, filename: str = None) -> Dict:
        """Extrai documento usando pypdf
        
        Args:
            pdf_path: Caminho do arquivo PDF
            filename: Nome original do arquivo (se não fornecido, usa o nome do caminho)
        """
        from pypdf import PdfReader
        
        reader = PdfReader(pdf_path)
        # Usa o filename fornecido ou o nome do arquivo do caminho
        if filename is None:
            filename = Path(pdf_path).name
        doc_id = self._generate_id(pdf_path)
        
        pages_text = []
        full_text_parts = []
        
        for page_num, page in enumerate(reader.pages, 1):
            try:
                content = page.extract_text()
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
        
        # Processar página por página
        for page_info in document["pages"]:
            page_num = page_info["page_number"]
            content = page_info["content"]
            
            # Se página muito grande, dividir
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
                # Página inteira é um chunk
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
        """Gera ID único"""
        with open(pdf_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        return f"doc_{file_hash[:12]}"
    
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
                
                # Limitar tamanho de páginas muito grandes
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
                "content": content[:1000] if len(content) > 1000 else content,  # Guardar só início
                "char_count": len(content)
            })
            
            # Criar chunks desta página
            if len(content) > settings.CHUNK_SIZE:
                page_chunks_texts = self._split_text(content, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
            else:
                page_chunks_texts = [content] if content.strip() else []
            
            # Criar objetos chunk
            for chunk_text in page_chunks_texts:
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
                all_chunks = []  # Liberar memória após salvar
            
            # Acumular texto apenas para metadata (limitado)
            if len(full_text_parts) < 100:  # Guardar apenas primeiras 100 páginas
                full_text_parts.append(content[:10000])  # 10KB por página
        
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
        """Divide texto em chunks com overlap - otimizado para grandes textos"""
        if len(text) <= chunk_size:
            return [text.strip()] if text.strip() else []
        
        # Se o texto for muito grande, processar de forma mais conservadora
        if len(text) > chunk_size * 100:  # Mais de 100x o chunk_size
            # Dividir em blocos intermediários primeiro
            chunks = []
            block_size = chunk_size * 20  # Blocos de 20x o chunk_size
            
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
        
        while start < len(text):
            end = min(start + chunk_size, len(text))
            
            # Tentar dividir em quebras naturais
            if end < len(text):
                # Procurar por quebra de parágrafo (\n\n)
                last_para = text.rfind('\n\n', start, end)
                if last_para > start:
                    end = last_para + 2
                else:
                    # Procurar por quebra de linha
                    last_newline = text.rfind('\n', start, end)
                    if last_newline > start:
                        end = last_newline + 1
                    else:
                        # Procurar por ponto seguido de espaço
                        last_period = text.rfind('. ', start, end)
                        if last_period > start:
                            end = last_period + 2
            
            # Extrair chunk
            chunk = text[start:end]
            stripped = chunk.strip()
            
            if stripped:  # Só adicionar se não estiver vazio
                chunks.append(stripped)
            
            # Mover start considerando overlap
            if end < len(text):
                start = max(end - chunk_overlap, start + 1)
            else:
                break
            
            # Prevenir loop infinito
            if start >= len(text):
                break
        
        return chunks
    
    def _extract_numero_processo(self, text: str) -> str:
        """Extrai número do processo"""
        pattern = r'\d{7}-\d{2}\.\d{4}\.\d{1}\.\d{2}\.\d{4}'
        match = re.search(pattern, text[:3000])
        return match.group(0) if match else None
