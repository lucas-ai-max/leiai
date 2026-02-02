# 🚀 Como Usar o Worker CSV

## Passo a Passo Rápido

### 1. Defina seu Prompt

Copie um dos exemplos para `prompt_custom.txt`:

**Exemplo Simples:**
```bash
copy exemplo_prompt_simples.txt prompt_custom.txt
```

**Exemplo Completo:**
```bash
copy exemplo_prompt_completo.txt prompt_custom.txt
```

**Ou crie o seu próprio:**

Edite `prompt_custom.txt` e defina os campos que você quer:

```
Analise o documento e extraia:

{
  "campo1": "descrição",
  "campo2": "descrição",
  "campo3": "descrição"
}

Retorne APENAS JSON válido.
```

### 2. Execute o Worker

```bash
cd "E:\Projetos Cursor\ProcessIA\processia"
python worker_csv.py
```

### 3. Faça Upload dos PDFs

Use o frontend React (http://localhost:5173) ou faça upload direto no Supabase.

### 4. Resultados

Os resultados aparecem em `resultados_analise.csv` com as colunas que você definiu.

## Estrutura Automática do CSV

O CSV terá:
- **Todos os campos que você definir no JSON**
- `arquivo_original` — nome do arquivo processado
- `data_processamento` — data e hora do processamento
- `tamanho_mb` — tamanho do arquivo em MB

## Exemplos de Prompts por Tipo de Documento

### Contratos
```json
{
  "tipo_contrato": "Tipo",
  "partes": "Partes",
  "valor": "Valor",
  "data": "Data de assinatura",
  "prazo": "Prazo de vigência"
}
```

### Sentenças
```json
{
  "numero_processo": "Número",
  "resultado": "Procedente/Improcedente",
  "valor_condenacao": "Valor",
  "fundamentacao": "Resumo"
}
```

### Petições
```json
{
  "autor": "Nome do autor",
  "tipo_pedido": "Tipo de pedido",
  "valor_pedido": "Valor",
  "argumentos": "Principais argumentos"
}
```

## Customizar Completamente

Você pode definir QUALQUER estrutura. Exemplos:

```json
{
  "meu_campo_especial": "O que você quiser",
  "outro_campo": "Qualquer coisa",
  "tabela_dados": "Até tabelas HTML",
  "lista_itens": "Itens separados por vírgula"
}
```

O Gemini vai tentar preencher os campos conforme você descrever.

## Vantagens

- ✅ Prompt 100% customizável
- ✅ Estrutura flexível (você define)
- ✅ CSV fácil de abrir no Excel/Google Sheets
- ✅ Não precisa mexer no schema do banco
- ✅ Processa qualquer tipo de documento

## Abrir o CSV

O CSV é criado com encoding UTF-8-BOM para compatibilidade com Excel.

- **Excel**: abrir diretamente (double-click)
- **Google Sheets**: Importar → Upload → Abrir
- **Python/Pandas**: `pd.read_csv('resultados_analise.csv')`

## Dica Pro

Teste seu prompt com um arquivo pequeno primeiro para ver se a estrutura está correta:

1. Faça upload de 1 PDF de teste
2. Veja o resultado no CSV
3. Ajuste o prompt se necessário
4. Processe o restante
