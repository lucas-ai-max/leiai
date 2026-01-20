from supabase import create_client, Client
from typing import Dict, List, Optional
from config import settings
from datetime import datetime
import json

class ResponseStorage:
    """Armazena análises jurisprudenciais estruturadas"""
    
    def __init__(self):
        self.supabase: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
    
    def save_analysis(self, 
                     numero_processo: str,
                     arquivo_original: str,
                     juiz: Optional[str] = None,
                     vara: str = "5ª Vara do Trabalho de Barueri",
                     tribunal: str = "TRT 2ª Região",
                     tipo_decisao: Optional[str] = None,
                     data_decisao: Optional[str] = None,
                     analisado_por: Optional[str] = None,
                     **kwargs) -> Dict:
        """Salva ou atualiza análise jurisprudencial
        
        Args:
            numero_processo: Número do processo (UNIQUE, obrigatório)
            arquivo_original: Nome do arquivo PDF original
            juiz: Nome do juiz
            vara: Nome da vara (padrão: 5ª Vara do Trabalho de Barueri)
            tribunal: Tribunal (padrão: TRT 2ª Região)
            tipo_decisao: Tipo da decisão (sentença, acórdão, etc.)
            data_decisao: Data da decisão (formato YYYY-MM-DD)
            analisado_por: Nome de quem analisou
            **kwargs: Campos de perguntas (p1_1_resposta, p1_1_justificativa, etc.)
        """
        print(f"🟣 [STORAGE] save_analysis: Iniciando salvamento")
        print(f"🟣 [STORAGE] numero_processo: {numero_processo}")
        print(f"🟣 [STORAGE] arquivo_original: {arquivo_original}")
        print(f"🟣 [STORAGE] Campos extras recebidos: {len(kwargs)} campos")
        
        # Verificar se já existe análise para este processo E arquivo
        print(f"🟣 [STORAGE] Verificando se análise já existe...")
        existing = self.get_by_numero_processo_and_file(numero_processo, arquivo_original)
        
        if existing:
            print(f"🟣 [STORAGE] Análise existente encontrada (ID: {existing.get('id', 'N/A')}), atualizando...")
        else:
            print(f"🟣 [STORAGE] Nenhuma análise existente, criando nova...")
        
        record = {
            "numero_processo": numero_processo,
            "arquivo_original": arquivo_original,
            "juiz": juiz,
            "vara": vara,
            "tribunal": tribunal,
            "tipo_decisao": tipo_decisao,
            "data_decisao": data_decisao,
            "analisado_por": analisado_por,
            "updated_at": datetime.now().isoformat(),
            **kwargs
        }
        
        # Remover None values
        record_before = len(record)
        record = {k: v for k, v in record.items() if v is not None}
        record_after = len(record)
        
        if record_before != record_after:
            print(f"🟣 [STORAGE] Campos None removidos: {record_before} -> {record_after} campos")
        
        print(f"🟣 [STORAGE] Registro preparado com {len(record)} campos")
        
        try:
            if existing:
                # Atualizar registro existente (mesmo processo e arquivo)
                print(f"🟣 [STORAGE] Executando UPDATE na tabela {settings.TABLE_RESPOSTAS}...")
                result = self.supabase.table(settings.TABLE_RESPOSTAS)\
                    .update(record)\
                    .eq("numero_processo", numero_processo)\
                    .eq("arquivo_original", arquivo_original)\
                    .execute()
                
                if result.data:
                    print(f"✅ [STORAGE] Análise atualizada com sucesso: {len(result.data)} registro(s) atualizado(s)")
                    return result.data[0]
                else:
                    print(f"⚠️ [STORAGE] UPDATE executado mas nenhum registro retornado")
                    return None
            else:
                # Criar novo registro
                record["status_analise"] = "CONCLUIDO"
                print(f"🟣 [STORAGE] Executando INSERT na tabela {settings.TABLE_RESPOSTAS}...")
                result = self.supabase.table(settings.TABLE_RESPOSTAS)\
                    .insert(record)\
                    .execute()
                
                if result.data:
                    print(f"✅ [STORAGE] Análise inserida com sucesso: {len(result.data)} registro(s) inserido(s), ID={result.data[0].get('id', 'N/A')}")
                    return result.data[0]
                else:
                    print(f"⚠️ [STORAGE] INSERT executado mas nenhum registro retornado")
                    return None
        except Exception as e:
            print(f"❌ [STORAGE] ERRO ao salvar análise: {str(e)}")
            print(f"❌ [STORAGE] Tipo do erro: {type(e).__name__}")
            import traceback
            print(f"❌ [STORAGE] Traceback: {traceback.format_exc()}")
            raise
    
    def save_question_answer(self,
                            numero_processo: str,
                            pergunta_id: str,  # Ex: "p1_1", "p2_3"
                            resposta: str,
                            justificativa: str = None,
                            referencia: str = None):
        """Salva resposta de uma pergunta específica
        
        Args:
            numero_processo: Número do processo
            pergunta_id: ID da pergunta (ex: "p1_1", "p2_3")
            resposta: Texto da resposta
            justificativa: Justificativa (opcional)
            referencia: Referência (opcional)
        """
        update_data = {
            f"{pergunta_id}_resposta": resposta,
            "updated_at": datetime.now().isoformat()
        }
        
        if justificativa:
            update_data[f"{pergunta_id}_justificativa"] = justificativa
        
        if referencia:
            update_data[f"{pergunta_id}_referencia"] = referencia
        
        result = self.supabase.table(settings.TABLE_RESPOSTAS)\
            .update(update_data)\
            .eq("numero_processo", numero_processo)\
            .execute()
        
        return result.data[0] if result.data else None
    
    def get_by_numero_processo(self, numero_processo: str) -> List[Dict]:
        """Recupera todas as análises de um processo (pode ter múltiplos arquivos)"""
        
        result = self.supabase.table(settings.TABLE_RESPOSTAS)\
            .select("*")\
            .eq("numero_processo", numero_processo)\
            .execute()
        
        return result.data if result.data else []
    
    def get_by_numero_processo_and_file(self, numero_processo: str, arquivo_original: str) -> Optional[Dict]:
        """Recupera análise específica de um processo e arquivo"""
        
        result = self.supabase.table(settings.TABLE_RESPOSTAS)\
            .select("*")\
            .eq("numero_processo", numero_processo)\
            .eq("arquivo_original", arquivo_original)\
            .execute()
        
        return result.data[0] if result.data else None
    
    def get_by_filename(self, filename: str) -> List[Dict]:
        """Recupera análises por nome do arquivo"""
        
        result = self.supabase.table(settings.TABLE_RESPOSTAS)\
            .select("*")\
            .eq("arquivo_original", filename)\
            .order("created_at", desc=True)\
            .execute()
        
        return result.data if result.data else []
    
    def get_all(self, status: Optional[str] = None) -> List[Dict]:
        """Recupera todas análises
        
        Args:
            status: Filtrar por status (PENDENTE, EM_ANALISE, CONCLUIDO, etc.)
        """
        query = self.supabase.table(settings.TABLE_RESPOSTAS).select("*")
        
        if status:
            query = query.eq("status_analise", status)
        
        result = query.order("created_at", desc=True).execute()
        
        return result.data if result.data else []
    
    def update_status(self, numero_processo: str, status: str):
        """Atualiza status da análise"""
        
        result = self.supabase.table(settings.TABLE_RESPOSTAS)\
            .update({
                "status_analise": status,
                "updated_at": datetime.now().isoformat()
            })\
            .eq("numero_processo", numero_processo)\
            .execute()
        
        return result.data[0] if result.data else None
