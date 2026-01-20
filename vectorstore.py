<<<<<<< HEAD
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
=======
>>>>>>> b5e15dc0d9832b696102fc7e6f8c4b6f2b1f24cf
from openai import OpenAI
from supabase import create_client, Client
from typing import List, Dict
from config import settings
from concurrent.futures import ThreadPoolExecutor
from postgrest.exceptions import APIError
import json
import re
import time
<<<<<<< HEAD
import sys

# Configurar encoding UTF-8 para Windows (evita erro com emojis)
if sys.platform == 'win32':
    import io
    try:
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'buffer'):
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass  # Ignorar se já estiver configurado
=======
>>>>>>> b5e15dc0d9832b696102fc7e6f8c4b6f2b1f24cf

class VectorStore:
    """Gerenciador de embeddings otimizado"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.supabase: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
    
    def _clean_text(self, text: str) -> str:
        """Remove caracteres Unicode inválidos que causam erro no PostgreSQL"""
        if not text:
            return ""
        
        # Substituir null bytes por espaço
        text = text.replace('\x00', ' ')
        text = text.replace('\u0000', ' ')
        
        # Remover outros caracteres de controle não imprimíveis
        # Mas manter \n, \r, \t (quebras de linha e tab)
        cleaned = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F-\x9F]', ' ', text)
        
        # Normalizar espaços múltiplos
        cleaned = re.sub(r' +', ' ', cleaned)
        
        # Normalizar quebras de linha múltiplas
        cleaned = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned)
        
        return cleaned.strip()
    
    def store_chunks(self, chunks: List[Dict]):
        """Armazena chunks com embeddings em paralelo"""
<<<<<<< HEAD
        print(f"🔵 [VECTORSTORE] ════════════════════════════════════════════════════════")
        print(f"🔵 [VECTORSTORE] store_chunks CHAMADO! Recebidos {len(chunks)} chunks")
        if chunks:
            first_chunk_sample = str(chunks[0])[:200] if chunks[0] else 'VAZIO'
            print(f"🔵 [VECTORSTORE] Primeiro chunk sample: {first_chunk_sample}")
        else:
            print(f"🔵 [VECTORSTORE] ⚠️ AVISO: Lista de chunks está VAZIA!")
        print(f"🔵 [VECTORSTORE] ════════════════════════════════════════════════════════")
        
        # Limpar conteúdo de cada chunk e filtrar vazios
        cleaned_chunks = []
        for idx, chunk in enumerate(chunks):
            print(f"🔵 [VECTORSTORE] Limpando chunk {idx+1}/{len(chunks)}: doc_id={chunk.get('document_id')}, page={chunk.get('page_number')}, chunk_id={chunk.get('chunk_id')}")
            cleaned_chunk = chunk.copy()
            original_content_len = len(chunk.get("content", ""))
            cleaned_content = self._clean_text(chunk["content"])
            cleaned_content_len = len(cleaned_content)
            
            if original_content_len != cleaned_content_len:
                print(f"🔵 [VECTORSTORE] Conteúdo limpo: {original_content_len} -> {cleaned_content_len} caracteres")
=======
        
        # Limpar conteúdo de cada chunk e filtrar vazios
        cleaned_chunks = []
        for chunk in chunks:
            cleaned_chunk = chunk.copy()
            cleaned_content = self._clean_text(chunk["content"])
>>>>>>> b5e15dc0d9832b696102fc7e6f8c4b6f2b1f24cf
            
            # Só incluir chunks com conteúdo válido
            if cleaned_content and cleaned_content.strip():
                cleaned_chunk["content"] = cleaned_content
                cleaned_chunks.append(cleaned_chunk)
<<<<<<< HEAD
                print(f"✅ [VECTORSTORE] Chunk {idx+1} válido: {cleaned_content_len} chars")
            else:
                print(f"⚠️ [VECTORSTORE] Chunk {idx+1} descartado: conteúdo vazio ou inválido")
        
        print(f"🔵 [VECTORSTORE] Após limpeza: {len(cleaned_chunks)} chunks válidos de {len(chunks)} originais")
        
        if not cleaned_chunks:
            print("❌ [VECTORSTORE] Aviso: Nenhum chunk válido para processar")
            return
        
        # Criar embeddings em batch (rápido)
        print(f"🔵 [VECTORSTORE] Extraindo textos de {len(cleaned_chunks)} chunks para criar embeddings")
        texts = [chunk["content"] for chunk in cleaned_chunks]
        print(f"🔵 [VECTORSTORE] Chamando _create_embeddings_batch com {len(texts)} textos (total chars: {sum(len(t) for t in texts)})")
        
        embeddings = self._create_embeddings_batch(texts)
        
        print(f"🔵 [VECTORSTORE] Embeddings criados: {len(embeddings)} embeddings retornados")
        
        # Preparar registros
        records = []
        valid_embeddings_count = 0
        invalid_embeddings_count = 0
        
        for idx, (chunk, embedding) in enumerate(zip(cleaned_chunks, embeddings)):
            # Só incluir se tiver embedding válido
            if embedding:
                valid_embeddings_count += 1
                # VERIFICAR E AJUSTAR DIMENSÃO (tabela espera 1536)
                embedding_dim = len(embedding)
                if embedding_dim != 1536:
                    # Truncar se maior, ou preencher se menor
                    if embedding_dim > 1536:
                        print(f"⚠️ [VECTORSTORE] Chunk {idx+1}: Embedding truncado de {embedding_dim} para 1536 dimensões")
                        embedding = embedding[:1536]
                    elif embedding_dim < 1536:
                        print(f"⚠️ [VECTORSTORE] Chunk {idx+1}: Embedding preenchido de {embedding_dim} para 1536 dimensões")
                        embedding = embedding + [0.0] * (1536 - embedding_dim)
                else:
                    print(f"✅ [VECTORSTORE] Chunk {idx+1}: Embedding com dimensão correta (1536)")
                
                record = {
=======
        
        if not cleaned_chunks:
            print("Aviso: Nenhum chunk válido para processar")
            return
        
        # Criar embeddings em batch (rápido)
        texts = [chunk["content"] for chunk in cleaned_chunks]
        embeddings = self._create_embeddings_batch(texts)
        
        # Preparar registros
        records = []
        for chunk, embedding in zip(cleaned_chunks, embeddings):
            # Só incluir se tiver embedding válido
            if embedding:
                records.append({
>>>>>>> b5e15dc0d9832b696102fc7e6f8c4b6f2b1f24cf
                    "document_id": chunk["document_id"],
                    "filename": chunk["filename"],
                    "page_number": chunk["page_number"],
                    "chunk_id": chunk["chunk_id"],
                    "content": chunk["content"],  # Já limpo
                    "embedding": embedding
<<<<<<< HEAD
                }
                records.append(record)
                print(f"✅ [VECTORSTORE] Chunk {idx+1} preparado: doc_id={record['document_id']}, filename={record['filename']}, page={record['page_number']}, chunk_id={record['chunk_id']}, content_len={len(record['content'])}, embedding_dim={len(embedding)}")
            else:
                invalid_embeddings_count += 1
                print(f"❌ [VECTORSTORE] Chunk {idx+1}: Embedding inválido (None ou vazio)")
        
        print(f"🔵 [VECTORSTORE] Resumo preparação: {valid_embeddings_count} embeddings válidos, {invalid_embeddings_count} inválidos, {len(records)} registros preparados")
        
        # Inserir em batch com delay antes para não sobrecarregar o banco
        if records:
            print(f"🔵 [VECTORSTORE] Preparando para inserir {len(records)} registros na tabela documento_chunks")
            print(f"🔵 [VECTORSTORE] Aguardando 0.5s antes de inserir...")
            # Pequeno delay antes de inserir para evitar sobrecarga
            time.sleep(0.5)
            print(f"🔵 [VECTORSTORE] Chamando _insert_batch com {len(records)} registros")
            self._insert_batch(records)
            print(f"✅ [VECTORSTORE] _insert_batch concluído")
        else:
            print("❌ [VECTORSTORE] AVISO: Nenhum registro válido para inserir após processamento")
    
    def _create_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Cria embeddings em batch (econômico e rápido)"""
        print(f"🔵 [VECTORSTORE] _create_embeddings_batch: Iniciando com {len(texts)} textos")
        all_embeddings = []
        batch_size = 100
        print(f"🔵 [VECTORSTORE] Configuração: batch_size={batch_size}, model={settings.MODEL_EMBEDDING}")
=======
                })
        
        # Inserir em batch com delay antes para não sobrecarregar o banco
        if records:
            # Pequeno delay antes de inserir para evitar sobrecarga
            time.sleep(0.5)
            self._insert_batch(records)
    
    def _create_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Cria embeddings em batch (econômico e rápido)"""
        all_embeddings = []
        batch_size = 100
>>>>>>> b5e15dc0d9832b696102fc7e6f8c4b6f2b1f24cf
        
        # Filtrar textos vazios ou inválidos
        valid_texts = []
        text_indices = []  # Mapear índices válidos para índices originais
        
<<<<<<< HEAD
        print(f"🔵 [VECTORSTORE] Filtrando textos válidos de {len(texts)} textos")
=======
>>>>>>> b5e15dc0d9832b696102fc7e6f8c4b6f2b1f24cf
        for idx, text in enumerate(texts):
            if text and isinstance(text, str) and text.strip():
                valid_texts.append(text)
                text_indices.append(idx)
<<<<<<< HEAD
                print(f"✅ [VECTORSTORE] Texto {idx+1} válido: {len(text)} chars")
            else:
                print(f"⚠️ [VECTORSTORE] Texto {idx+1} inválido: type={type(text)}, empty={not text if text else True}")
        
        print(f"🔵 [VECTORSTORE] Após filtro: {len(valid_texts)} textos válidos de {len(texts)} originais")
        
        if not valid_texts:
            # Retornar embeddings vazios se não houver textos válidos
            print("❌ [VECTORSTORE] Nenhum texto válido, retornando embeddings vazios")
            return [[] for _ in texts]
        
        # Criar embeddings apenas para textos válidos
        total_batches = (len(valid_texts) + batch_size - 1) // batch_size
        print(f"🔵 [VECTORSTORE] Processando {total_batches} batches de embeddings")
        
        for batch_num, i in enumerate(range(0, len(valid_texts), batch_size), 1):
=======
        
        if not valid_texts:
            # Retornar embeddings vazios se não houver textos válidos
            return [[] for _ in texts]
        
        # Criar embeddings apenas para textos válidos
        for i in range(0, len(valid_texts), batch_size):
>>>>>>> b5e15dc0d9832b696102fc7e6f8c4b6f2b1f24cf
            batch = valid_texts[i:i + batch_size]
            
            # Validar que batch não está vazio
            if not batch:
<<<<<<< HEAD
                print(f"⚠️ [VECTORSTORE] Batch {batch_num} vazio, pulando")
                continue
            
            print(f"🔵 [VECTORSTORE] Processando batch {batch_num}/{total_batches}: {len(batch)} textos (índices {i} a {i+len(batch)-1})")
            print(f"🔵 [VECTORSTORE] Tamanhos dos textos: {[len(t) for t in batch[:3]]}... (mostrando primeiros 3)")
            
=======
                continue
            
>>>>>>> b5e15dc0d9832b696102fc7e6f8c4b6f2b1f24cf
            # Usar dimensions=1536 para compatibilidade com Supabase (limite de 2000)
            embedding_params = {
                "model": settings.MODEL_EMBEDDING,
                "input": batch
            }
            
            # Se usar text-embedding-3-large, reduzir para 1536 dimensões
            if "3-large" in settings.MODEL_EMBEDDING:
                embedding_params["dimensions"] = 1536
<<<<<<< HEAD
                print(f"🔵 [VECTORSTORE] Usando dimensions=1536 para model {settings.MODEL_EMBEDDING}")
            
            print(f"🔵 [VECTORSTORE] Chamando OpenAI API para criar embeddings...")
            try:
                response = self.client.embeddings.create(**embedding_params)
                batch_embeddings = [item.embedding for item in response.data]
                
                if batch_embeddings:
                    first_embedding_dim = len(batch_embeddings[0])
                    print(f"✅ [VECTORSTORE] Batch {batch_num}: {len(batch_embeddings)} embeddings criados, dimensão={first_embedding_dim}")
                else:
                    print(f"⚠️ [VECTORSTORE] Batch {batch_num}: API retornou lista vazia de embeddings")
                
=======
            
            try:
                response = self.client.embeddings.create(**embedding_params)
                batch_embeddings = [item.embedding for item in response.data]
>>>>>>> b5e15dc0d9832b696102fc7e6f8c4b6f2b1f24cf
                all_embeddings.extend(batch_embeddings)
                
                # Pequeno delay entre batches de embeddings para não sobrecarregar a API
                if i + batch_size < len(valid_texts):
<<<<<<< HEAD
                    print(f"🔵 [VECTORSTORE] Aguardando 0.2s antes do próximo batch...")
                    time.sleep(0.2)  # 200ms entre batches de embeddings
            except Exception as e:
                # Log do erro e dados do batch para debug
                print(f"❌ [VECTORSTORE] ERRO ao criar embeddings para batch {batch_num}: {e}")
                print(f"❌ [VECTORSTORE] Tipo do erro: {type(e).__name__}")
                print(f"❌ [VECTORSTORE] Tamanho do batch: {len(batch)}")
                print(f"❌ [VECTORSTORE] Primeiros caracteres do primeiro texto: {batch[0][:100] if batch else 'N/A'}")
                import traceback
                print(f"❌ [VECTORSTORE] Traceback: {traceback.format_exc()}")
                raise
        
        # Mapear embeddings de volta para os índices originais
        print(f"🔵 [VECTORSTORE] Mapeando {len(all_embeddings)} embeddings para {len(texts)} índices originais")
        result = [[] for _ in texts]  # Inicializar com listas vazias
        embedding_idx = 0
        mapped_count = 0
        for valid_idx, original_idx in enumerate(text_indices):
            if embedding_idx < len(all_embeddings):
                embedding = all_embeddings[embedding_idx]
                result[original_idx] = embedding
                mapped_count += 1
                if mapped_count <= 3:  # Log apenas os primeiros 3 para não poluir
                    print(f"✅ [VECTORSTORE] Mapeado embedding {mapped_count}: índice original={original_idx}, dimensão={len(embedding)}")
                embedding_idx += 1
        
        print(f"✅ [VECTORSTORE] Mapeamento concluído: {mapped_count} embeddings mapeados, {len(result)} slots no resultado final")
=======
                    time.sleep(0.2)  # 200ms entre batches de embeddings
            except Exception as e:
                # Log do erro e dados do batch para debug
                print(f"Erro ao criar embeddings para batch: {e}")
                print(f"Tamanho do batch: {len(batch)}")
                print(f"Primeiros caracteres do primeiro texto: {batch[0][:100] if batch else 'N/A'}")
                raise
        
        # Mapear embeddings de volta para os índices originais
        result = [[] for _ in texts]  # Inicializar com listas vazias
        embedding_idx = 0
        for valid_idx, original_idx in enumerate(text_indices):
            if embedding_idx < len(all_embeddings):
                result[original_idx] = all_embeddings[embedding_idx]
                embedding_idx += 1
        
>>>>>>> b5e15dc0d9832b696102fc7e6f8c4b6f2b1f24cf
        return result
    
    def _insert_batch(self, records: List[Dict]):
        """Insere em batch no Supabase com retry e batches menores"""
<<<<<<< HEAD
        print(f"🔵 [VECTORSTORE] ════════════════════════════════════════════════════════")
        print(f"🔵 [VECTORSTORE] _insert_batch CHAMADO! {len(records)} registros")
        print(f"🔵 [VECTORSTORE] Vou inserir na tabela: {settings.TABLE_EMBEDDINGS}")
        if records:
            first_record = records[0]
            print(f"🔵 [VECTORSTORE] Primeiro registro sample: doc_id={first_record.get('document_id')}, filename={first_record.get('filename')}")
        print(f"🔵 [VECTORSTORE] ════════════════════════════════════════════════════════")
        batch_size = 3  # Reduzir para 3 registros para evitar timeout e reduzir carga
        delay_between_batches = 1.0  # Aumentar delay entre batches para 1s
        total_batches = (len(records) + batch_size - 1) // batch_size
        print(f"🔵 [VECTORSTORE] Configuração: batch_size={batch_size}, total_batches={total_batches}, delay={delay_between_batches}s")
        
        for batch_idx, i in enumerate(range(0, len(records), batch_size), 1):
            batch = records[i:i + batch_size]
            print(f"🔵 [VECTORSTORE] Processando batch {batch_idx}/{total_batches}: {len(batch)} registros (índices {i} a {i+len(batch)-1})")
            
            # Log detalhes do primeiro registro do batch
            if batch:
                first_record = batch[0]
                print(f"🔵 [VECTORSTORE] Primeiro registro do batch: doc_id={first_record.get('document_id')}, filename={first_record.get('filename')}, page={first_record.get('page_number')}, chunk_id={first_record.get('chunk_id')}, content_len={len(first_record.get('content', ''))}, embedding_dim={len(first_record.get('embedding', []))}")
            
=======
        batch_size = 3  # Reduzir para 3 registros para evitar timeout e reduzir carga
        delay_between_batches = 1.0  # Aumentar delay entre batches para 1s
        
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
>>>>>>> b5e15dc0d9832b696102fc7e6f8c4b6f2b1f24cf
            max_retries = 3
            retry_delay = 3  # Aumentar delay inicial para 3s para dar mais tempo ao banco
            inserted = False
            
            for attempt in range(max_retries):
                try:
<<<<<<< HEAD
                    print(f"🔵 [VECTORSTORE] Tentativa {attempt+1}/{max_retries} de inserir batch {batch_idx}")
                    print(f"🔵 [VECTORSTORE] Inserindo {len(batch)} registros na tabela {settings.TABLE_EMBEDDINGS}...")
                    print(f"🔵 [VECTORSTORE] 🔴 CHAMANDO SUPABASE.INSERT AGORA...")
                    print(f"🔵 [VECTORSTORE] Tabela: {settings.TABLE_EMBEDDINGS}")
                    print(f"🔵 [VECTORSTORE] Registros no batch: {len(batch)}")
                    result = self.supabase.table(settings.TABLE_EMBEDDINGS).insert(batch).execute()
                    print(f"🔵 [VECTORSTORE] ✅ SUPABASE.INSERT RETORNOU: result.data={len(result.data) if result.data else 0} registros")
                    print(f"🔵 [VECTORSTORE] Resultado completo: {str(result)[:500]}")
                    inserted = True
                    inserted_count = len(result.data) if result.data else 0
                    print(f"✅ [VECTORSTORE] Batch {batch_idx}: {inserted_count} registros inseridos com sucesso na tabela documento_chunks")
                    if inserted_count != len(batch):
                        print(f"⚠️ [VECTORSTORE] AVISO: Inseridos {inserted_count} mas esperados {len(batch)} registros")
                    
                    # Pequeno delay após inserção bem-sucedida
                    if i + batch_size < len(records):
                        print(f"🔵 [VECTORSTORE] Aguardando {delay_between_batches}s antes do próximo batch...")
=======
                    self.supabase.table(settings.TABLE_EMBEDDINGS).insert(batch).execute()
                    inserted = True
                    # Pequeno delay após inserção bem-sucedida
                    if i + batch_size < len(records):
>>>>>>> b5e15dc0d9832b696102fc7e6f8c4b6f2b1f24cf
                        time.sleep(delay_between_batches)
                    break  # Sucesso, sair do loop de retry
                except APIError as e:
                    error_code = e.code if hasattr(e, 'code') else str(getattr(e, 'message', {}))
                    
                    # Se for timeout (57014) e ainda houver tentativas
                    if error_code == '57014' and attempt < max_retries - 1:
<<<<<<< HEAD
                        wait_time = retry_delay * (2 ** attempt)  # Backoff exponencial (3s, 6s, 12s)
                        print(f"⚠️ [VECTORSTORE] Timeout (57014) ao inserir batch {batch_idx} ({len(batch)} registros)")
                        print(f"🔵 [VECTORSTORE] Tentando novamente em {wait_time}s... (tentativa {attempt + 1}/{max_retries})")
                        print(f"🔵 [VECTORSTORE] Erro completo: {e}")
=======
                        wait_time = retry_delay * (2 ** attempt)  # Backoff exponencial (2s, 4s, 8s)
                        print(f"Timeout ao inserir batch ({len(batch)} registros), tentando novamente em {wait_time}s... (tentativa {attempt + 1}/{max_retries})")
>>>>>>> b5e15dc0d9832b696102fc7e6f8c4b6f2b1f24cf
                        time.sleep(wait_time)
                        
                        # Reduzir batch na primeira tentativa falha
                        if attempt == 0 and len(batch) > 2:
                            mid = len(batch) // 2
                            first_half = batch[:mid]
                            second_half = batch[mid:]
                            
                            # Tentar inserir a primeira metade
                            try:
                                self.supabase.table(settings.TABLE_EMBEDDINGS).insert(first_half).execute()
                                print(f"Primeira metade ({len(first_half)} registros) inserida com sucesso")
                                time.sleep(delay_between_batches)
                                
                                # Tentar a segunda metade
                                try:
                                    self.supabase.table(settings.TABLE_EMBEDDINGS).insert(second_half).execute()
                                    print(f"Segunda metade ({len(second_half)} registros) inserida com sucesso")
                                    inserted = True
                                    break
                                except APIError as e3:
                                    print(f"Erro ao inserir segunda metade: {e3}")
                                    batch = second_half  # Continuar tentando com a segunda metade
                            except APIError as e2:
                                print(f"Erro ao inserir primeira metade: {e2}")
                                # Tentar a segunda metade mesmo se a primeira falhou
                                if len(second_half) > 0:
                                    batch = second_half
                    else:
                        # Outro erro ou esgotou tentativas
                        print(f"Erro ao inserir batch: {e}")
                        if error_code == '57014':
                            print("Timeout persistente. Tentando inserir registros individualmente com delay...")
                            # Inserir registros um por um com delay entre cada
                            success_count = 0
                            for idx, record in enumerate(batch):
                                try:
                                    self.supabase.table(settings.TABLE_EMBEDDINGS).insert(record).execute()
                                    success_count += 1
                                    # Delay entre inserções individuais
                                    if idx < len(batch) - 1:
                                        time.sleep(1.0)  # 1s entre cada registro para reduzir carga
                                except Exception as e3:
                                    print(f"Erro ao inserir registro individual {idx+1}/{len(batch)}: {e3}")
                                    # Continuar tentando os próximos
                                    time.sleep(2.0)  # Delay maior após erro (2s)
                            
                            if success_count > 0:
                                print(f"Inseridos {success_count}/{len(batch)} registros individualmente")
                            inserted = True  # Considerar como inserido mesmo se alguns falharam
                            break
                        else:
                            raise
                except Exception as e:
                    print(f"Erro inesperado ao inserir batch: {e}")
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(retry_delay)
            
            if not inserted:
<<<<<<< HEAD
                print(f"❌ [VECTORSTORE] ERRO CRÍTICO: Não foi possível inserir batch {batch_idx} de {len(batch)} registros após {max_retries} tentativas")
                print(f"❌ [VECTORSTORE] Registros que falharam: {[(r.get('document_id'), r.get('chunk_id')) for r in batch]}")
            else:
                print(f"✅ [VECTORSTORE] Batch {batch_idx} concluído com sucesso")
                # Delay entre batches para não sobrecarregar o banco
                if i + batch_size < len(records):
                    print(f"🔵 [VECTORSTORE] Aguardando {delay_between_batches}s antes do próximo batch...")
                    time.sleep(delay_between_batches)
        
        print(f"✅ [VECTORSTORE] _insert_batch concluído: processados {total_batches} batches")
=======
                print(f"Aviso: Não foi possível inserir batch de {len(batch)} registros após {max_retries} tentativas")
            else:
                # Delay entre batches para não sobrecarregar o banco
                if i + batch_size < len(records):
                    time.sleep(delay_between_batches)
>>>>>>> b5e15dc0d9832b696102fc7e6f8c4b6f2b1f24cf
    
    def search(self, query: str, document_id: str = None, limit: int = 8) -> List[Dict]:
        """Busca rápida com pgvector"""
        
        # Embedding da query
        query_embedding = self._create_embeddings_batch([query])[0]
        
        # Buscar
        params = {
            "query_embedding": query_embedding,
            "match_count": limit
        }
        
        if document_id:
            params["filter_document_id"] = document_id
        
        try:
            results = self.supabase.rpc("match_chunks", params).execute()
            return results.data if results.data else []
        except Exception as e:
            # Fallback: busca simples sem RPC
            print(f"Erro na busca RPC: {e}")
            return self._fallback_search(query, document_id, limit)
    
    def _fallback_search(self, query: str, document_id: str = None, limit: int = 8) -> List[Dict]:
        """Busca alternativa caso RPC não esteja disponível"""
        query_obj = self.supabase.table(settings.TABLE_EMBEDDINGS).select("*")
        
        if document_id:
            query_obj = query_obj.eq("document_id", document_id)
        
        results = query_obj.limit(limit).execute()
        return results.data if results.data else []
    
    def has_chunks(self, document_id: str = None, filename: str = None) -> bool:
        """Verifica se já existem chunks para um documento"""
        try:
            query = self.supabase.table(settings.TABLE_EMBEDDINGS).select("id", count="exact")
            
            if document_id:
                query = query.eq("document_id", document_id)
            elif filename:
                query = query.eq("filename", filename)
            else:
                return False
            
            result = query.limit(1).execute()
            return result.count > 0 if hasattr(result, 'count') else len(result.data) > 0
        except Exception as e:
            print(f"Erro ao verificar chunks: {e}")
            return False
    
    def get_document_id_by_filename(self, filename: str) -> str:
        """Retorna o document_id associado a um filename (se existir)"""
        try:
            result = self.supabase.table(settings.TABLE_EMBEDDINGS)\
                .select("document_id")\
                .eq("filename", filename)\
                .limit(1)\
                .execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]["document_id"]
            return None
        except Exception as e:
            print(f"Erro ao buscar document_id: {e}")
            return None
    
    def delete_chunks_by_document_id(self, document_id: str) -> int:
        """Deleta todos os chunks de um documento específico"""
        try:
            result = self.supabase.table(settings.TABLE_EMBEDDINGS)\
                .delete()\
                .eq("document_id", document_id)\
                .execute()
            
            deleted_count = len(result.data) if result.data else 0
            print(f"✅ Deletados {deleted_count} chunks do documento {document_id}")
            return deleted_count
        except Exception as e:
            print(f"⚠️ Erro ao deletar chunks do documento {document_id}: {e}")
            return 0
    
    def delete_chunks_by_filename(self, filename: str) -> int:
        """Deleta todos os chunks de um arquivo específico"""
        try:
            result = self.supabase.table(settings.TABLE_EMBEDDINGS)\
                .delete()\
                .eq("filename", filename)\
                .execute()
            
            deleted_count = len(result.data) if result.data else 0
            print(f"✅ Deletados {deleted_count} chunks do arquivo {filename}")
            return deleted_count
        except Exception as e:
            print(f"⚠️ Erro ao deletar chunks do arquivo {filename}: {e}")
            return 0
