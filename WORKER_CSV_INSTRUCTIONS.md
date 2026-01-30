# 📊 Worker CSV - Instruções

## Visão Geral

Este worker processa PDFs e exporta os resultados para CSV, ao invés de salvar no Supabase.

## Arquivos

- `worker_csv.py` — Worker que exporta para CSV
- `prompt_custom.txt` — Seu prompt personalizado
- `resultados_analise.csv` — Arquivo CSV com os resultados

## Como Usar

### 1. Edite o Prompt (prompt_custom.txt)

Defina qual informação você quer extrair:

```
Analise o documento e extraia:

{
  "campo1": "descrição do campo1",
  "campo2": "descrição do campo2",
  "campo3": "descrição do campo3"
}

Retorne APENAS JSON válido.
```

### 2. Execute o Worker

```bash
cd "E:\Projetos Cursor\ProcessIA\processia"
python worker_csv.py
```

### 3. Faça Upload no Frontend

Use o frontend React para fazer upload dos PDFs.

### 4. Veja os Resultados

Os resultados são salvos em `resultados_analise.csv` com as colunas que você definiu no prompt.

## Exemplo de Prompt Customizado

### Para Análise de Contratos:
```json
{
  "tipo_contrato": "Tipo do contrato",
  "partes": "Partes envolvidas",
  "valor": "Valor do contrato",
  "data_assinatura": "Data de assinatura",
  "vigencia": "Período de vigência",
  "clausulas_principais": "Principais cláusulas"
}
```

### Para Sentenças Judiciais:
```json
{
  "numero_processo": "Número do processo",
  "juiz": "Nome do juiz",
  "resultado": "Procedente/Improcedente",
  "valor_condenacao": "Valor da condenação",
  "fundamentacao": "Resumo da fundamentação"
}
```

### Para Processos Trabalhistas:
```json
{
  "reclamante": "Nome do reclamante",
  "reclamado": "Nome do reclamado",
  "pedidos": "Lista de pedidos",
  "resultado_pedidos": "Resultado de cada pedido",
  "valor_deferido": "Valor total deferido"
}
```

## Estrutura do CSV

O CSV terá automaticamente:
- Todas as colunas que você definir no JSON
- `arquivo_original` — nome do arquivo
- `data_processamento` — data/hora do processamento
- `tamanho_mb` — tamanho do arquivo

## Diferenças do Worker Original

| Recurso | Worker Original | Worker CSV |
|---------|----------------|------------|
| Prompt | Fixo (prompt_analise.txt) | Customizável (prompt_custom.txt) |
| Estrutura | Fixa (schema do banco) | Flexível (você define) |
| Saída | Supabase (tabela analise_jurisprudencial) | CSV (resultados_analise.csv) |
| Atualização | Status + análise completa | Apenas status |

## Vantagens

- ✅ Prompt totalmente customizável
- ✅ Estrutura de dados flexível
- ✅ CSV fácil de abrir no Excel
- ✅ Não depende do schema do Supabase
- ✅ Pode processar qualquer tipo de documento

## Executar

```bash
# Ativar ambiente virtual
.\venv\Scripts\Activate.ps1

# Rodar worker
python worker_csv.py
```

## Troubleshooting

### Erro: "Prompt não configurado"
- Crie o arquivo `prompt_custom.txt` com seu prompt

### CSV com colunas erradas
- Edite o prompt para definir as colunas que você quer
- O CSV é criado baseado nas chaves do JSON retornado

### Resultado em JSON inválido
- Adicione no prompt: "Retorne APENAS JSON válido, sem texto adicional"
- Verifique se o modelo está entendendo a estrutura

## Dica

Se quiser testar seu prompt antes:
```bash
python test_gemini.py
```
