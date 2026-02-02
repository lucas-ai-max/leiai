# 🎯 Como Usar a Interface ProcessIA Enterprise

## Visão Geral

Sistema completo com:
- ✨ **Gerador de Estrutura com IA** (você descreve, a IA cria)
- 📝 **Editor de Prompt** integrado
- 📊 **Exportação para CSV**
- 🔄 **Atualização em tempo real**

## Passo a Passo

### 1. Configurar Estrutura de Dados (Primeira Vez)

#### Opção A: Gerar com IA (Recomendado)

1. Abra o frontend: http://localhost:5173
2. Clique em "Editor de Prompt" (expande)
3. Na caixa roxa "Gerar Estrutura com IA", digite o que você quer extrair:

**Exemplos:**
```
"Quero extrair número do processo, nome das partes e resultado da decisão"

"Preciso do nome do juiz, valor da causa, data da decisão e fundamentação"

"Extrair tipo de contrato, partes envolvidas, valor e prazo de vigência"
```

4. Clique em "Gerar Estrutura com IA"
5. A IA criará automaticamente o JSON com os campos
6. Revise o prompt gerado abaixo
7. Clique em "Salvar Prompt"

#### Opção B: Criar Manualmente

1. Edite o campo "Prompt Personalizado" diretamente
2. Defina a estrutura JSON que você quer
3. Clique em "Salvar Prompt"

### 2. Fazer Upload de PDFs

1. Arraste os PDFs para a área de upload
2. Ou clique para selecionar (suporta múltiplos arquivos)
3. Os arquivos aparecerão na tabela com status PENDENTE

### 3. Processamento Automático

O worker processará automaticamente:
- Status muda de PENDENTE → PROCESSANDO → CONCLUIDO
- Atualização em tempo real (não precisa recarregar)

### 4. Exportar Resultados

1. Aguarde os arquivos serem processados (status CONCLUIDO)
2. Clique no botão verde "Exportar CSV" (canto superior direito)
3. O CSV será baixado com todas as análises

## Exemplos de Uso

### Exemplo 1: Análise de Sentenças

**Digite:**
```
Quero analisar sentenças judiciais e extrair número do processo, nome do juiz, partes envolvidas, resultado da decisão, valor da condenação e fundamentos legais
```

**IA Gera:**
```json
{
  "numero_processo": "Número do processo",
  "nome_juiz": "Nome do juiz",
  "partes": "Partes envolvidas",
  "resultado": "Resultado da decisão",
  "valor_condenacao": "Valor da condenação",
  "fundamentos": "Fundamentos legais"
}
```

### Exemplo 2: Análise de Contratos

**Digite:**
```
Preciso extrair tipo de contrato, partes contratantes, valor, data de assinatura, prazo de vigência e principais obrigações
```

**IA Gera:**
```json
{
  "tipo_contrato": "Tipo do contrato",
  "partes": "Partes contratantes",
  "valor": "Valor do contrato",
  "data_assinatura": "Data de assinatura",
  "prazo_vigencia": "Prazo de vigência",
  "obrigacoes": "Principais obrigações"
}
```

## Funcionalidades

### Editor de Prompt
- ✨ Gerador automático com IA
- 📝 Editor de texto para ajustes
- 💾 Salvar no Supabase
- 📥 Baixar como .txt
- 🔄 Restaurar padrão

### Área de Upload
- 📎 Drag & drop de arquivos
- 📚 Upload múltiplo (em lote)
- ✅ Validação de PDF
- 🔄 Feedback visual

### Tabela de Monitoramento
- 📊 Status em tempo real
- 🎨 Badges coloridos (PENDENTE, PROCESSANDO, CONCLUIDO, ERRO)
- 📥 Exportar CSV
- 🔍 Informações detalhadas

## Dicas

### Descreva Claramente
Quanto mais específico, melhor a estrutura gerada:
- ❌ "Quero extrair dados"
- ✅ "Quero extrair número do processo, nome do juiz e valor da causa"

### Revise o Prompt
Após a IA gerar, você pode:
- Adicionar/remover campos
- Ajustar descrições
- Modificar instruções

### Teste com 1 Arquivo Primeiro
- Faça upload de 1 PDF
- Veja o resultado no CSV
- Ajuste o prompt se necessário
- Depois processe em lote

## Troubleshooting

### "Gerar Estrutura" não funciona
- Verifique se VITE_GOOGLE_API_KEY está no .env do frontend
- Reinicie o servidor frontend

### CSV vem em branco
- Verifique se há arquivos com status CONCLUIDO
- O botão só funciona se houver arquivos processados

### Estrutura JSON errada
- Refaça o prompt sendo mais específico
- Ou edite manualmente o JSON gerado

## Fluxo Completo

```
1. Usuário descreve o que quer extrair (linguagem natural)
2. IA gera a estrutura JSON automaticamente
3. Usuário revisa e salva o prompt
4. Usuário faz upload dos PDFs
5. Worker processa usando o prompt customizado
6. Usuário exporta os resultados em CSV
```

## Pronto!

Você tem um sistema completo onde pode:
- Definir campos em linguagem natural
- A IA criar a estrutura automaticamente
- Processar documentos em massa
- Exportar para CSV
