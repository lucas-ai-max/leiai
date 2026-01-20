from openai import OpenAI
from typing import List, Dict, Optional
from config import settings
import json

class DocumentAnalyzer:
    """Analisador com o1 (GPT-4.1) para máxima qualidade usando RAG"""
    
    def __init__(self, vectorstore=None):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.vectorstore = vectorstore  # Para buscar chunks via RAG
    
    def analyze(self, 
                question: str, 
                chunks: List[Dict],
                custom_prompt: str = None) -> Dict:
        """Analisa documento com o1 e retorna resposta com referências"""
        
        # Construir contexto com referências de página
        context = self._build_context(chunks)
        
        # Prompt base (será customizado depois)
        base_prompt = custom_prompt or """Analise o processo jurídico e responda à pergunta.

INSTRUÇÕES:
- Responda apenas com base no contexto fornecido
- Cite sempre a página e arquivo de origem
- Use formato: "...conforme página X do arquivo Y..."
- Seja preciso e direto
- Se não souber, diga claramente"""

        full_prompt = f"""{base_prompt}

CONTEXTO:
{context}

PERGUNTA: {question}

RESPOSTA:"""

        # Chamar GPT-4.1
        response = self.client.chat.completions.create(
            model=settings.MODEL_O1,
            messages=[
                {"role": "user", "content": full_prompt}
            ]
        )
        
        answer = response.choices[0].message.content
        
        # Extrair referências automaticamente
        references = self._extract_references(chunks)
        
        return {
            "answer": answer,
            "references": references,
            "chunks_used": len(chunks),
            "model": settings.MODEL_O1
        }
    
    def _build_context(self, chunks: List[Dict]) -> str:
        """Constrói contexto com referências claras"""
        context_parts = []
        
        for chunk in chunks:
            part = f"""[Arquivo: {chunk['filename']} | Página: {chunk['page_number']}]
{chunk['content']}
---"""
            context_parts.append(part)
        
        return "\n\n".join(context_parts)
    
    def _extract_references(self, chunks: List[Dict]) -> List[Dict]:
        """Extrai referências estruturadas"""
        refs = []
        seen = set()
        
        for chunk in chunks:
            key = (chunk['filename'], chunk['page_number'])
            if key not in seen:
                refs.append({
                    "filename": chunk['filename'],
                    "page": chunk['page_number']
                })
                seen.add(key)
        
        return refs
    
    def analyze_full_document_rag(self, document_id: str, filename: str, prompt_file: str = "prompt_analise.txt", return_raw_response: bool = False) -> Dict:
        """Analisa documento completo usando RAG - busca chunks relevantes por embeddings
        
        Args:
            document_id: ID do documento
            filename: Nome do arquivo
            prompt_file: Caminho para arquivo com prompt completo
        """
        print(f"🟡 [ANALYZER] analyze_full_document_rag: Iniciando análise RAG")
        print(f"🟡 [ANALYZER] document_id: {document_id}")
        print(f"🟡 [ANALYZER] filename: {filename}")
        print(f"🟡 [ANALYZER] prompt_file: {prompt_file}")
        print(f"🟡 [ANALYZER] return_raw_response: {return_raw_response}")
        
        if not self.vectorstore:
            print(f"❌ [ANALYZER] ERRO: VectorStore não inicializado")
            raise ValueError("VectorStore não inicializado. Passe vectorstore no __init__")
        
        # Carregar prompt
        print(f"🟡 [ANALYZER] Carregando prompt do arquivo {prompt_file}...")
        try:
            with open(prompt_file, "r", encoding="utf-8") as f:
                full_prompt_template = f.read()
            prompt_len = len(full_prompt_template)
            print(f"✅ [ANALYZER] Prompt carregado: {prompt_len} caracteres")
        except FileNotFoundError:
            print(f"❌ [ANALYZER] ERRO: Arquivo {prompt_file} não encontrado")
            raise FileNotFoundError(f"Arquivo {prompt_file} não encontrado")
        
        # Queries para busca RAG - cobrem todos os temas das perguntas
        rag_queries = [
            "desconsideração da personalidade jurídica procedência improcedência",
            "desconsideração liminar contraditório produção de provas",
            "artigo 50 CC artigo 28 CDC artigo 795 CLT fundamentação jurídica",
            "desconsideração patrimônio proporcional bloqueio integral bens",
            "grau de prova exigido indícios graves presunção desconsideração",
            "prova documental pericial testemunhal indiciária desconsideração",
            "prova outros processos inventário falência processo cível",
            "inversão ônus da prova terceiro boa-fé desconsideração",
            "terceiro de boa-fé proteção adquirente bens executado",
            "requisitos boa-fé terceiro desconhecimento preço mercado registro público",
            "boa-fé momento contratação pagamentos conhecimento ações judiciais",
            "consultas prévias certidões pesquisas processos órgãos crédito boa-fé",
            "operações familiares cônjuges presunção fraude desconsideração",
            "pagamentos terceiros vinculados dívidas imóvel acordos trabalhistas",
            "rastreabilidade valores pagos comprovação credores finais",
            "cláusulas contratuais direcionamento pagamentos terceiros simulação fraude",
            "aquisição antes depois ajuizamento trânsito julgado desconsideração",
            "prazo decadencial prescricional desconsideração personalidade jurídica",
            "efeitos retroativos prospectivos desconsideração operações passadas",
            "Tema 1232 STF suspensão processos desconsideração",
            "preço vil laudo pericial avaliatório subavaliação bem",
            "percentual deságio valor mercado negociações aceitável",
            "condições imóvel conservação ocupação ônus urgência venda",
            "valor mercado data transação data atual perícia preço vil",
            "descumprimento ordem judicial multa presunção má-fé inversão ônus",
            "ordens judiciais outros processos vinculam terceiros trabalhistas",
            "excludente responsabilidade descumprimento ordem obrigações contratuais conflitantes",
            "confusão patrimonial contas bancárias contabilidade separada uso promíscuo bens",
            "confusão patrimonial pessoas jurídicas grupo econômico sócios",
            "confusão patrimonial contemporânea execução histórica regularizada",
            "desvio finalidade social pessoa jurídica ultra vires objeto social",
            "grupo econômico informal fato estrutura societária formal",
            "grupo econômico direção única coordenação administrativa solidariedade interesses",
            "prova grupo econômico documentos societários demonstrações financeiras contratos",
            "fraude execução art 792 CPC fraude contra credores art 158 CC",
            "fraude execução bem imóvel penhora registrada matrícula alienação",
            "conhecimento demanda trabalhista vendedor ciência inequívoca adquirente",
            "alienação tornou devedor insolvente presunção insolvência dívidas trabalhistas",
            "terceiro assume acordos trabalhistas vendedor preço aquisição fraude",
            "esgotamento bens executado principal desconsiderar personalidade jurídica terceiros",
            "ônus provar insuficiência patrimonial executado exequente terceiro",
            "pesquisas patrimoniais RENAJUD BACENJUD INFOJUD SISBAJUD desconsideração",
            "garantias alternativas seguro garantia fiança bancária caução substituir penhora",
            "limitação penhora valor necessário garantir execução liberar excesso",
            "intimação prévia terceiro Tema 916 STJ desconsideração liminar urgência",
            "prazo manifestação terceiro incluído 15 dias urgência complexidade",
            "dilação probatória perícias testemunhas documentos incidente desconsideração",
            "soluções conciliatórias desconsideração audiências acordos",
            "acordos desconsideração parcelamento débito dação bem divisão proporcional",
            "momento adequado propostas acordo fase processual negociação",
            "decisões desconsideração reformadas TRT-2 agravo petição",
            "fundamentos TRT-2 reformar desconsideração contraditório insuficiência probatória",
            "efeito suspensivo agravo petição decisões desconsideração execução imediata",
            "tempo médio agravo petição julgamento TRT-2 casos similares",
            "nulidade negócio jurídico imobiliário vício origem procuração suspensa competência",
            "nulidade título origem terceiro boa-fé proteção terceiro invalidade ato",
            "nulidade negócio jurídico restituição status quo confiança enriquecimento",
            "decisões inventário vinculantes relevantes processos independentes",
            "direitos espólio inventariante terceiro adquirente boa-fé conflito",
            "alienação bem empresa indenização cotas sociais herdeiro fraude",
            "fraude fiscal pagamentos contabilização fundamento desconsideração irregularidade",
            "irregularidades contábeis tributárias perícia contábil alegações genéricas",
            "competência analisar questões tributárias complexas prejudicial Justiça Federal"
        ]
        
        # Buscar chunks relevantes usando RAG (múltiplas queries para cobrir todos os temas)
        print(f"🟡 [ANALYZER] Iniciando busca RAG com {len(rag_queries)} queries temáticas")
        all_relevant_chunks = []
        seen_chunk_ids = set()
        
        # Buscar chunks para cada query temática
        for query_idx, query in enumerate(rag_queries, 1):
            if query_idx <= 5 or query_idx % 10 == 0:  # Log a cada 10 queries para não poluir
                print(f"🟡 [ANALYZER] Buscando chunks para query {query_idx}/{len(rag_queries)}: '{query[:50]}...'")
            
            chunks = self.vectorstore.search(query, document_id=document_id, limit=10)
            
            if query_idx <= 5 or query_idx % 10 == 0:
                print(f"🟡 [ANALYZER] Query {query_idx}: {len(chunks)} chunks encontrados")
            
            new_chunks_count = 0
            for chunk in chunks:
                chunk_id = chunk.get('id')
                if chunk_id and chunk_id not in seen_chunk_ids:
                    all_relevant_chunks.append(chunk)
                    seen_chunk_ids.add(chunk_id)
                    new_chunks_count += 1
            
            if query_idx <= 5 or query_idx % 10 == 0 and new_chunks_count > 0:
                print(f"🟡 [ANALYZER] Query {query_idx}: {new_chunks_count} novos chunks adicionados (total acumulado: {len(all_relevant_chunks)})")
        
        print(f"🟡 [ANALYZER] Após queries temáticas: {len(all_relevant_chunks)} chunks únicos encontrados")
        
        # Se não encontrou chunks suficientes, buscar mais genericamente
        if len(all_relevant_chunks) < 50:
            print(f"⚠️ [ANALYZER] Poucos chunks encontrados ({len(all_relevant_chunks)} < 50), buscando genericamente...")
            generic_queries = [
                "sentença decisão acórdão",
                "juiz desembargador vara trabalho",
                "processo número decisão",
                "fundamentação jurídica artigo lei"
            ]
            
            for gen_query_idx, query in enumerate(generic_queries, 1):
                print(f"🟡 [ANALYZER] Busca genérica {gen_query_idx}/{len(generic_queries)}: '{query}'")
                chunks = self.vectorstore.search(query, document_id=document_id, limit=20)
                print(f"🟡 [ANALYZER] Busca genérica {gen_query_idx}: {len(chunks)} chunks retornados")
                
                new_chunks = 0
                for chunk in chunks:
                    chunk_id = chunk.get('id')
                    if chunk_id and chunk_id not in seen_chunk_ids:
                        all_relevant_chunks.append(chunk)
                        seen_chunk_ids.add(chunk_id)
                        new_chunks += 1
                        if len(all_relevant_chunks) >= 100:  # Limite razoável
                            break
                
                print(f"🟡 [ANALYZER] Busca genérica {gen_query_idx}: {new_chunks} novos chunks (total: {len(all_relevant_chunks)})")
                
                if len(all_relevant_chunks) >= 100:
                    print(f"🟡 [ANALYZER] Limite de 100 chunks atingido, parando busca")
                    break
        
        print(f"✅ [ANALYZER] Total de chunks únicos coletados: {len(all_relevant_chunks)}")
        
        if not all_relevant_chunks:
            print(f"❌ [ANALYZER] ERRO: Nenhum chunk encontrado para documento {document_id}")
            raise ValueError(f"Nenhum chunk encontrado para documento {document_id}")
        
        # Ordenar chunks por página para manter ordem lógica
        print(f"🟡 [ANALYZER] Ordenando chunks por página e chunk_id...")
        all_relevant_chunks.sort(key=lambda x: (x.get('page_number', 0), x.get('chunk_id', 0)))
        print(f"✅ [ANALYZER] Chunks ordenados")
        
        # Construir contexto com chunks relevantes
        print(f"🟡 [ANALYZER] Construindo contexto com {len(all_relevant_chunks)} chunks...")
        context = self._build_context(all_relevant_chunks)
        context_len = len(context)
        print(f"✅ [ANALYZER] Contexto construído: {context_len} caracteres")
        
        # Montar prompt final
        print(f"🟡 [ANALYZER] Montando prompt final...")
        prompt_with_context = f"""{full_prompt_template}

# DOCUMENTO PARA ANÁLISE

{context}

---

Agora analise o documento acima e forneça as respostas no formato especificado."""
        
        final_prompt_len = len(prompt_with_context)
        print(f"✅ [ANALYZER] Prompt final montado: {final_prompt_len} caracteres ({final_prompt_len/1000:.2f}K chars)")
        
        # Chamar GPT-4.1
        print(f"🟡 [ANALYZER] Chamando GPT-4.1 ({settings.MODEL_O1}) para análise...")
        print(f"🟡 [ANALYZER] Aguardando resposta da API...")
        
        try:
            response = self.client.chat.completions.create(
                model=settings.MODEL_O1,
                messages=[
                    {"role": "user", "content": prompt_with_context}
                ]
            )
            
            answer = response.choices[0].message.content
            answer_len = len(answer) if answer else 0
            print(f"✅ [ANALYZER] Resposta GPT-4.1 recebida: {answer_len} caracteres ({answer_len/1000:.2f}K chars)")
            
            if hasattr(response, 'usage'):
                usage = response.usage
                print(f"🟡 [ANALYZER] Uso de tokens: prompt_tokens={getattr(usage, 'prompt_tokens', 'N/A')}, completion_tokens={getattr(usage, 'completion_tokens', 'N/A')}, total_tokens={getattr(usage, 'total_tokens', 'N/A')}")
        except Exception as e:
            print(f"❌ [ANALYZER] ERRO ao chamar GPT-4.1: {str(e)}")
            print(f"❌ [ANALYZER] Tipo do erro: {type(e).__name__}")
            import traceback
            print(f"❌ [ANALYZER] Traceback: {traceback.format_exc()}")
            raise
        
        # Parsear resposta estruturada
        print(f"🟡 [ANALYZER] Parseando resposta da análise...")
        parsed_data = self._parse_analysis_response(answer, filename, all_relevant_chunks)
        
        result_keys = len(parsed_data.keys()) if parsed_data else 0
        print(f"✅ [ANALYZER] Resposta parseada: {result_keys} campos extraídos")
        if parsed_data:
            print(f"🟡 [ANALYZER] Campos extraídos: {list(parsed_data.keys())[:10]}... (mostrando primeiros 10)")
            if 'numero_processo' in parsed_data:
                print(f"🟡 [ANALYZER] Número do processo: {parsed_data['numero_processo']}")
        
        if return_raw_response:
            print(f"🟡 [ANALYZER] Retornando resultado parseado + resposta bruta")
            return parsed_data, answer
        else:
            print(f"🟡 [ANALYZER] Retornando apenas resultado parseado")
            return parsed_data
    
    def _parse_analysis_response(self, response_text: str, filename: str, chunks: List[Dict]) -> Dict:
        """Extrai dados estruturados da resposta do o1"""
        print(f"🟡 [ANALYZER] _parse_analysis_response: Iniciando parseamento")
        print(f"🟡 [ANALYZER] response_text length: {len(response_text)} caracteres")
        print(f"🟡 [ANALYZER] filename: {filename}")
        print(f"🟡 [ANALYZER] chunks disponíveis: {len(chunks)}")
        
        import re
        
        data = {
            "arquivo_original": filename,
            "analisado_por": "Sistema IA (o1)",
            "status_analise": "CONCLUIDO"
        }
        
        # Extrair identificação
        print(f"🟡 [ANALYZER] Extraindo identificação (JUIZ, NUMERO_PROCESSO, etc.)...")
        juiz_match = re.search(r'\*\*JUIZ:\*\*\s*(.+)', response_text)
        if juiz_match:
            data["juiz"] = juiz_match.group(1).strip()
            print(f"✅ [ANALYZER] JUIZ extraído: {data['juiz']}")
        else:
            print(f"⚠️ [ANALYZER] JUIZ não encontrado na resposta")
        
        num_proc_match = re.search(r'\*\*NUMERO_PROCESSO:\*\*\s*(\d{7}-\d{2}\.\d{4}\.\d{1}\.\d{2}\.\d{4})', response_text)
        if num_proc_match:
            data["numero_processo"] = num_proc_match.group(1).strip()
            print(f"✅ [ANALYZER] NUMERO_PROCESSO extraído: {data['numero_processo']}")
        else:
            print(f"⚠️ [ANALYZER] NUMERO_PROCESSO não encontrado na resposta")
        
        data_dec_match = re.search(r'\*\*DATA_DECISAO:\*\*\s*(\d{4}-\d{2}-\d{2})', response_text)
        if data_dec_match:
            data["data_decisao"] = data_dec_match.group(1).strip()
        
        tipo_match = re.search(r'\*\*TIPO_DECISAO:\*\*\s*(.+?)(?:\n|$)', response_text)
        if tipo_match:
            data["tipo_decisao"] = tipo_match.group(1).strip()
        
        grau_match = re.search(r'\*\*GRAU:\*\*\s*(1º\s*Grau|2º\s*Grau)', response_text)
        if grau_match:
            data["grau"] = grau_match.group(1).strip()
        
        vara_match = re.search(r'\*\*VARA:\*\*\s*(.+?)(?:\n|$)', response_text)
        if vara_match:
            data["vara"] = vara_match.group(1).strip()
        else:
            data["vara"] = "5ª Vara do Trabalho de Barueri"  # Default
        
        tribunal_match = re.search(r'\*\*TRIBUNAL:\*\*\s*(.+?)(?:\n|$)', response_text)
        if tribunal_match:
            data["tribunal"] = tribunal_match.group(1).strip()
        else:
            data["tribunal"] = "TRT 2ª Região"  # Default
        
        # Extrair campos de decisão (decisao_resposta, decisao_justificativa, decisao_referencia)
        decisao_resposta_match = re.search(r'\*\*decisao_resposta:\*\*\s*\n?(.*?)(?=\n\*\*decisao_|\n\*\*p\d+_|\n---|\n##|\Z)', response_text, re.DOTALL)
        if decisao_resposta_match:
            data["decisao_resposta"] = decisao_resposta_match.group(1).strip()
        
        decisao_justificativa_match = re.search(r'\*\*decisao_justificativa:\*\*\s*\n?(.*?)(?=\n\*\*decisao_|\n\*\*p\d+_|\n---|\n##|\Z)', response_text, re.DOTALL)
        if decisao_justificativa_match:
            data["decisao_justificativa"] = decisao_justificativa_match.group(1).strip()
        
        decisao_referencia_match = re.search(r'\*\*decisao_referencia:\*\*\s*\n?(.*?)(?=\n\*\*decisao_|\n\*\*p\d+_|\n---|\n##|\Z)', response_text, re.DOTALL)
        if decisao_referencia_match:
            data["decisao_referencia"] = decisao_referencia_match.group(1).strip()
        
        # Extrair todas as respostas (p1_1_resposta, p1_1_justificativa, etc.)
        print(f"🟡 [ANALYZER] Extraindo campos de perguntas (p1_1_resposta, p1_1_justificativa, etc.)...")
        # Padrão CORRIGIDO: usar p literal (não [p]), e múltiplas estratégias
        # Estratégia 1: padrão específico com lookahead para próximo campo
        pattern = r'\*\*(p\d+_\d+_(?:resposta|justificativa|referencia)):\*\*\s*\n(.*?)(?=\n\*\*p\d+_\d+_|\n---|\n##|\Z)'
        matches = list(re.finditer(pattern, response_text, re.DOTALL | re.MULTILINE))
        
        print(f"🟡 [ANALYZER] Estratégia 1: {len(matches)} matches encontrados")
        
        extracted_fields = []
        for match in matches:
            campo = match.group(1).strip()
            valor = match.group(2).strip()
            
            # Validar se é um campo válido da tabela
            if campo.startswith('p') and ('_resposta' in campo or '_justificativa' in campo or '_referencia' in campo):
                data[campo] = valor
                extracted_fields.append(campo)
                if len(extracted_fields) <= 5:  # Log apenas os primeiros 5
                    print(f"✅ [ANALYZER] Campo extraído: {campo} (valor: {len(valor)} chars)")
        
        print(f"✅ [ANALYZER] Estratégia 1: {len(extracted_fields)} campos extraídos")
        
        # Se não encontrou suficientes, tentar padrão mais flexível
        if len(extracted_fields) < 30:
            print(f"⚠️ [ANALYZER] Poucos campos extraídos ({len(extracted_fields)} < 30), tentando estratégia 2...")
            # Estratégia 2: padrão sem lookahead específico
            pattern2 = r'\*\*(p\d+_\d+_(?:resposta|justificativa|referencia)):\*\*\s*\n?(.*?)(?=\n\*\*p\d+_|\n\*\*[A-Z]|\n---|\n##|\Z)'
            matches2 = list(re.finditer(pattern2, response_text, re.DOTALL | re.MULTILINE))
            print(f"🟡 [ANALYZER] Estratégia 2: {len(matches2)} matches encontrados")
            
            # Se ainda não encontrou, tentar padrão ainda mais flexível
            if len(extracted_fields) < 20:
                print(f"⚠️ [ANALYZER] Ainda poucos campos ({len(extracted_fields)} < 20), tentando estratégia 3...")
                # Estratégia 3: qualquer campo que comece com **p e tenha números
                pattern3 = r'\*\*(p\d+_\d+_(?:resposta|justificativa|referencia)):\*\*\s*\n?(.*?)(?=\n\*\*[a-zA-Z]|\n---|\n##|\Z)'
                matches3 = list(re.finditer(pattern3, response_text, re.DOTALL | re.MULTILINE))
                print(f"🟡 [ANALYZER] Estratégia 3: {len(matches3)} matches encontrados")
                matches2.extend(matches3)
            
            new_fields_count = 0
            for match in matches2:
                campo = match.group(1).strip()
                valor = match.group(2).strip()
                
                # Validar campo e evitar duplicatas
                if campo.startswith('p') and campo not in extracted_fields:
                    if '_resposta' in campo or '_justificativa' in campo or '_referencia' in campo:
                        # Limpar valor de espaços em branco excessivos
                        valor_limpo = re.sub(r'\s+', ' ', valor).strip()
                        if valor_limpo and valor_limpo != "Não foi possível obter parâmetros para resposta":
                            data[campo] = valor_limpo
                            extracted_fields.append(campo)
                            new_fields_count += 1
                            if new_fields_count <= 5:  # Log apenas os primeiros 5 novos
                                print(f"✅ [ANALYZER] Campo extraído (estratégia 2/3): {campo} (valor: {len(valor_limpo)} chars)")
            
            print(f"✅ [ANALYZER] Estratégias 2/3: {new_fields_count} novos campos extraídos")
        
        total_fields = len(extracted_fields)
        total_data_keys = len(data.keys())
        print(f"✅ [ANALYZER] Parseamento concluído: {total_fields} campos de perguntas extraídos, {total_data_keys} campos totais no resultado")
        print(f"🟡 [ANALYZER] Campos totais no data: {list(data.keys())[:15]}... (mostrando primeiros 15)")
        
        return data