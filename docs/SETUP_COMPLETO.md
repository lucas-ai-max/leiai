# 🚀 Setup Completo - ProcessIA Enterprise com Prompt Customizável

## Visão Geral

Sistema completo para análise massiva de documentos com:
- ✅ Prompt customizável na interface
- ✅ Exportação para CSV
- ✅ Estrutura de dados flexível (você define)
- ✅ Interface moderna React
- ✅ Processamento paralelo com Gemini 2.0 Flash

## Passo 1: Configurar Supabase

### 1.1 Criar tabela para o prompt

Execute no SQL Editor do Supabase:

```sql
-- Copie e cole o conteúdo de create_prompt_table.sql
```

### 1.2 Desabilitar RLS

Execute no SQL Editor:

```sql
-- Tabela de gerenciamento
ALTER TABLE documento_gerenciamento DISABLE ROW LEVEL SECURITY;

-- Tabela de prompt
ALTER TABLE prompt_config DISABLE ROW LEVEL SECURITY;
```

### 1.3 Verificar bucket

Certifique-se de que o bucket `processos` existe e está público.

## Passo 2: Configurar Frontend

### 2.1 Variáveis de ambiente

O arquivo `.env` já está configurado em `frontend-processia/.env`

### 2.2 Iniciar frontend

```bash
cd "E:\Projetos Cursor\frontend-processia"
npm run dev
```

Acesse: http://localhost:5173

## Passo 3: Configurar Worker

### 3.1 Usar worker CSV (recomendado)

```bash
cd "E:\Projetos Cursor\ProcessIA\processia"
python worker_csv.py
```

Este worker:
- Lê o prompt do Supabase (atualizado em tempo real)
- Exporta resultados para CSV
- Não salva no Supabase (apenas status)

## Como Usar

### 1. Editar Prompt na Interface

1. Abra o frontend (http://localhost:5173)
2. Clique em "Editor de Prompt" (no topo)
3. Edite o prompt e defina os campos JSON que você quer
4. Clique em "Salvar Prompt"

### 2. Fazer Upload de PDFs

1. Arraste PDFs para a área de upload
2. Ou clique para selecionar
3. Suporta múltiplos arquivos

### 3. Monitorar Processamento

- A tabela mostra o status em tempo real
- PENDENTE → PROCESSANDO → CONCLUIDO

### 4. Exportar Resultados

1. Clique no botão "Exportar CSV" (canto superior direito da tabela)
2. O CSV será baixado com todas as análises concluídas

## Estrutura do CSV

O CSV terá:
- Todas as colunas que você definir no prompt JSON
- `arquivo_original` — nome do arquivo
- `data_processamento` — data/hora
- `tamanho_mb` — tamanho do arquivo

## Exemplo de Uso

### Prompt:
```json
{
  "numero_processo": "Número do processo",
  "resultado": "Procedente ou Improcedente",
  "valor": "Valor da condenação"
}
```

### CSV Gerado:
```csv
numero_processo,resultado,valor,arquivo_original,data_processamento,tamanho_mb
"1234567-89.2023.5.02.0205","Procedente","R$ 50.000,00","processo1.pdf","2026-01-29 18:30:00",2.4
```

## Arquivos Importantes

- `worker_csv.py` — Worker que exporta para CSV
- `create_prompt_table.sql` — Criar tabela no Supabase
- `fix_all_rls.sql` — Desabilitar RLS
- `prompt_custom.txt` — Fallback local (opcional)

## Troubleshooting

### Erro: "Prompt não configurado"
- Execute `create_prompt_table.sql` no Supabase
- Configure o prompt no frontend

### Erro: "Row level security policy"
- Execute `fix_all_rls.sql` no Supabase
- Ou desabilite RLS manualmente

### CSV não é gerado
- Verifique se há arquivos com status CONCLUIDO
- Verifique permissões de escrita na pasta

### Prompt não atualiza
- O worker carrega o prompt a cada arquivo processado
- Reinicie o worker se necessário

## Vantagens

- ✅ Prompt editável na interface (sem mexer em código)
- ✅ CSV pronto para Excel/Google Sheets
- ✅ Estrutura flexível (você define os campos)
- ✅ Processamento paralelo (até 10 arquivos simultâneos)
- ✅ Atualização em tempo real
- ✅ Drag & drop de arquivos

## Pronto para Usar!

1. Execute `create_prompt_table.sql` no Supabase
2. Inicie o frontend: `npm run dev`
3. Inicie o worker: `python worker_csv.py`
4. Configure o prompt na interface
5. Faça upload dos PDFs
6. Exporte o CSV quando concluir
