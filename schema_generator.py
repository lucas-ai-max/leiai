"""
Gerador de Schema JSON baseado em prompt do usuário
Usa Gemini para criar automaticamente a estrutura de dados
"""

import google.generativeai as genai
from config import settings
import json

genai.configure(api_key=settings.GOOGLE_API_KEY)

class SchemaGenerator:
    def __init__(self):
        self.model = genai.GenerativeModel(settings.MODEL_FAST)
    
    def generate_schema(self, user_prompt: str) -> dict:
        """
        Gera um schema JSON baseado no prompt do usuário
        
        Args:
            user_prompt: Descrição em linguagem natural do que o usuário quer extrair
            
        Returns:
            dict: Schema JSON com campos e descrições
        """
        
        system_prompt = f"""Você é um assistente especializado em criar estruturas JSON para análise de documentos.

O usuário quer analisar documentos e extrair informações específicas. Baseado na descrição dele, crie uma estrutura JSON apropriada.

PROMPT DO USUÁRIO:
{user_prompt}

INSTRUÇÕES:
1. Crie um objeto JSON com campos relevantes baseados no que o usuário pediu
2. Cada campo deve ter uma descrição clara
3. Use nomes de campos em snake_case (ex: numero_processo, data_decisao)
4. Inclua campos obrigatórios para contexto jurídico se aplicável
5. Seja inteligente e adicione campos relacionados que o usuário pode ter esquecido
6. Retorne APENAS o JSON, sem texto adicional

FORMATO DE SAÍDA (exemplo):
{{
  "campo1": "Descrição do campo 1",
  "campo2": "Descrição do campo 2",
  "campo3": "Descrição do campo 3"
}}

Agora crie o JSON baseado no prompt do usuário:"""

        try:
            response = self.model.generate_content(
                system_prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            
            schema = json.loads(response.text)
            return schema
            
        except Exception as e:
            print(f"Erro ao gerar schema: {e}")
            raise
    
    def generate_full_prompt(self, user_prompt: str, schema: dict) -> str:
        """
        Gera o prompt completo para análise de documentos
        
        Args:
            user_prompt: Descrição original do usuário
            schema: Schema JSON gerado
            
        Returns:
            str: Prompt completo formatado
        """
        
        schema_formatted = json.dumps(schema, indent=2, ensure_ascii=False)
        
        full_prompt = f"""Você é um assistente especializado em análise de documentos jurídicos.

OBJETIVO: {user_prompt}

Analise o documento fornecido e extraia as seguintes informações em formato JSON:

{schema_formatted}

INSTRUÇÕES IMPORTANTES:
- Retorne APENAS o JSON válido, sem texto antes ou depois
- Use "N/A" para campos não encontrados no documento
- Seja preciso e objetivo nas extrações
- Mantenha a formatação consistente
- Para listas, separe itens com vírgula
- Para valores monetários, use formato "R$ X.XXX,XX"
- Para datas, use formato DD/MM/AAAA quando possível

Analise o documento e retorne o JSON com os dados extraídos:"""

        return full_prompt


# Função auxiliar para CLI
def generate_from_cli():
    """Gera schema via linha de comando"""
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python schema_generator.py 'seu prompt aqui'")
        print("\nExemplo:")
        print('  python schema_generator.py "Quero extrair nome do juiz, número do processo e valor da causa"')
        sys.exit(1)
    
    user_prompt = sys.argv[1]
    
    print(f"\nGerando schema para: {user_prompt}\n")
    
    generator = SchemaGenerator()
    
    try:
        schema = generator.generate_schema(user_prompt)
        
        print("[OK] Schema gerado:\n")
        print(json.dumps(schema, indent=2, ensure_ascii=False))
        
        print("\n" + "="*60)
        print("PROMPT COMPLETO:")
        print("="*60)
        
        full_prompt = generator.generate_full_prompt(user_prompt, schema)
        print(full_prompt)
        
        # Salvar em arquivo
        with open("prompt_generated.txt", "w", encoding="utf-8") as f:
            f.write(full_prompt)
        
        print("\n" + "="*60)
        print("[OK] Prompt salvo em: prompt_generated.txt")
        print("="*60)
        
    except Exception as e:
        print(f"[ERRO] Erro: {e}")
        sys.exit(1)


if __name__ == "__main__":
    generate_from_cli()
