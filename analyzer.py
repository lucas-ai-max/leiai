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
        if not self.vectorstore:
            raise ValueError("VectorStore não inicializado. Passe vectorstore no __init__")
        
        # Carregar prompt
        try:
            with open(prompt_file, "r", encoding="utf-8") as f:
                full_prompt_template = f.read()
        except FileNotFoundError:
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
        all_relevant_chunks = []
        seen_chunk_ids = set()
        
        # Buscar chunks para cada query temática
        for query in rag_queries:
            chunks = self.vectorstore.search(query, document_id=document_id, limit=10)
            
            for chunk in chunks:
                chunk_id = chunk.get('id')
                if chunk_id and chunk_id not in seen_chunk_ids:
                    all_relevant_chunks.append(chunk)
                    seen_chunk_ids.add(chunk_id)
        
        # Se não encontrou chunks suficientes, buscar mais genericamente
        if len(all_relevant_chunks) < 50:
            generic_queries = [
                "sentença decisão acórdão",
                "juiz desembargador vara trabalho",
                "processo número decisão",
                "fundamentação jurídica artigo lei"
            ]
            
            for query in generic_queries:
                chunks = self.vectorstore.search(query, document_id=document_id, limit=20)
                for chunk in chunks:
                    chunk_id = chunk.get('id')
                    if chunk_id and chunk_id not in seen_chunk_ids:
                        all_relevant_chunks.append(chunk)
                        seen_chunk_ids.add(chunk_id)
                        if len(all_relevant_chunks) >= 100:  # Limite razoável
                            break
                if len(all_relevant_chunks) >= 100:
                    break
        
        if not all_relevant_chunks:
            raise ValueError(f"Nenhum chunk encontrado para documento {document_id}")
        
        # Ordenar chunks por página para manter ordem lógica
        all_relevant_chunks.sort(key=lambda x: (x.get('page_number', 0), x.get('chunk_id', 0)))
        
        # Construir contexto com chunks relevantes
        context = self._build_context(all_relevant_chunks)
        
        # Montar prompt final
        prompt_with_context = f"""{full_prompt_template}

# DOCUMENTO PARA ANÁLISE

{context}

---

Agora analise o documento acima e forneça as respostas no formato especificado."""
        
        # Chamar GPT-4.1
        response = self.client.chat.completions.create(
            model=settings.MODEL_O1,
            messages=[
                {"role": "user", "content": prompt_with_context}
            ]
        )
        
        answer = response.choices[0].message.content
        
        # Parsear resposta estruturada
        parsed_data = self._parse_analysis_response(answer, filename, all_relevant_chunks)
        
        if return_raw_response:
            return parsed_data, answer
        return parsed_data
    
    def _parse_analysis_response(self, response_text: str, filename: str, chunks: List[Dict]) -> Dict:
        """Extrai dados estruturados da resposta do o1"""
        import re
        
        data = {
            "arquivo_original": filename,
            "analisado_por": "Sistema IA (o1)",
            "status_analise": "CONCLUIDO"
        }
        
        # Extrair identificação
        juiz_match = re.search(r'\*\*JUIZ:\*\*\s*(.+)', response_text)
        if juiz_match:
            data["juiz"] = juiz_match.group(1).strip()
        
        num_proc_match = re.search(r'\*\*NUMERO_PROCESSO:\*\*\s*(\d{7}-\d{2}\.\d{4}\.\d{1}\.\d{2}\.\d{4})', response_text)
        if num_proc_match:
            data["numero_processo"] = num_proc_match.group(1).strip()
        
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
        # Padrão CORRIGIDO: usar p literal (não [p]), e múltiplas estratégias
        # Estratégia 1: padrão específico com lookahead para próximo campo
        pattern = r'\*\*(p\d+_\d+_(?:resposta|justificativa|referencia)):\*\*\s*\n(.*?)(?=\n\*\*p\d+_\d+_|\n---|\n##|\Z)'
        matches = list(re.finditer(pattern, response_text, re.DOTALL | re.MULTILINE))
        
        extracted_fields = []
        for match in matches:
            campo = match.group(1).strip()
            valor = match.group(2).strip()
            
            # Validar se é um campo válido da tabela
            if campo.startswith('p') and ('_resposta' in campo or '_justificativa' in campo or '_referencia' in campo):
                data[campo] = valor
                extracted_fields.append(campo)
        
        # Se não encontrou suficientes, tentar padrão mais flexível
        if len(extracted_fields) < 30:
            # Estratégia 2: padrão sem lookahead específico
            pattern2 = r'\*\*(p\d+_\d+_(?:resposta|justificativa|referencia)):\*\*\s*\n?(.*?)(?=\n\*\*p\d+_|\n\*\*[A-Z]|\n---|\n##|\Z)'
            matches2 = list(re.finditer(pattern2, response_text, re.DOTALL | re.MULTILINE))
            
            # Se ainda não encontrou, tentar padrão ainda mais flexível
            if len(extracted_fields) < 20:
                # Estratégia 3: qualquer campo que comece com **p e tenha números
                pattern3 = r'\*\*(p\d+_\d+_(?:resposta|justificativa|referencia)):\*\*\s*\n?(.*?)(?=\n\*\*[a-zA-Z]|\n---|\n##|\Z)'
                matches3 = list(re.finditer(pattern3, response_text, re.DOTALL | re.MULTILINE))
                matches2.extend(matches3)
            
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
        
        return data