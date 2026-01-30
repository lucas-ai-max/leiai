# 🚀 Guia de Migração para Nova Arquitetura

## Visão Geral da Nova Arquitetura

### Componentes:
1. **Frontend (React + Vite)**: Interface moderna para upload de PDFs
2. **Supabase Storage**: Armazena os arquivos PDF na nuvem
3. **Supabase Database**: Gerencia fila de processamento
4. **Worker Python**: Processa arquivos em background usando Gemini 1.5 Flash

---

## 📋 Passo 1: Preparar o Supabase

### 1.1 Criar Bucket no Storage

1. Acesse seu projeto no Supabase Dashboard
2. Vá em **Storage** (ícone de pasta) → **New Bucket**
3. Configure:
   - **Nome**: `processos`
   - **Public bucket**: ✅ Marque esta opção
4. Clique em **Save**

### 1.2 Atualizar Tabela no Banco

Execute o script SQL no **SQL Editor** do Supabase:

```sql
-- Execute o arquivo migration_storage.sql
-- Ou copie e cole o conteúdo no SQL Editor
```

O script adiciona a coluna `storage_path` na tabela `documento_gerenciamento`.

---

## 📋 Passo 2: Configurar Variáveis de Ambiente

Atualize o arquivo `.env` com as novas credenciais:

```env
# Supabase (obrigatório)
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua-chave-anonima-aqui

# Google/Gemini (obrigatório para nova arquitetura)
GOOGLE_API_KEY=sua-chave-google-aqui

# OpenAI (opcional - apenas se usar embeddings OpenAI)
OPENAI_API_KEY=sk-proj-sua-chave-aqui
```

**Como obter a chave do Gemini:**
1. Acesse: https://aistudio.google.com/app/apikey
2. Crie uma nova API Key
3. Cole no `.env`

---

## 📋 Passo 3: Instalar Dependências do Worker

O worker precisa da biblioteca do Google Gemini:

```bash
# Ativar ambiente virtual
.\venv\Scripts\Activate.ps1

# Instalar dependência
pip install google-generativeai
```

---

## 📋 Passo 4: Executar o Worker

O worker fica rodando em background processando arquivos:

```bash
# Ativar ambiente virtual
.\venv\Scripts\Activate.ps1

# Executar worker
python worker.py
```

O worker:
- ✅ Verifica o banco a cada 5 segundos
- ✅ Busca arquivos com status "PENDENTE" que tenham `storage_path`
- ✅ Baixa o arquivo do Supabase Storage
- ✅ Processa o PDF
- ✅ Atualiza status no banco

---

## 📋 Passo 5: Criar Frontend (React + Vite)

### Estrutura sugerida:

```
frontend/
├── src/
│   ├── components/
│   │   ├── FileUpload.tsx
│   │   └── FileList.tsx
│   ├── services/
│   │   └── supabase.ts
│   └── App.tsx
├── package.json
└── vite.config.ts
```

### Exemplo de upload para Supabase Storage:

```typescript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY)

async function uploadFile(file: File) {
  // 1. Upload para Storage
  const fileName = `${Date.now()}_${file.name}`
  const { data, error } = await supabase.storage
    .from('processos')
    .upload(fileName, file)
  
  if (error) throw error
  
  // 2. Criar registro na fila
  const { error: dbError } = await supabase
    .from('documento_gerenciamento')
    .insert({
      filename: file.name,
      status: 'PENDENTE',
      storage_path: data.path,
      file_size_mb: file.size / (1024 * 1024)
    })
  
  if (dbError) throw dbError
}
```

---

## 🔄 Fluxo Completo

1. **Usuário faz upload** → Frontend envia PDF para Supabase Storage
2. **Frontend cria registro** → Insere na tabela `documento_gerenciamento` com `storage_path`
3. **Worker detecta** → Busca arquivos com status "PENDENTE"
4. **Worker processa** → Baixa do Storage, processa PDF, analisa com Gemini
5. **Worker atualiza** → Muda status para "CONCLUIDO" ou "ERRO"
6. **Frontend exibe** → Mostra status atualizado em tempo real

---

## 📝 Arquivos Criados

- ✅ `migration_storage.sql` - Script para atualizar banco
- ✅ `worker.py` - Worker Python para processamento
- ✅ `MIGRATION_GUIDE.md` - Este guia

---

## ⚠️ Próximos Passos

1. ✅ Executar `migration_storage.sql` no Supabase
2. ✅ Criar bucket `processos` no Storage
3. ✅ Configurar `.env` com `GEMINI_API_KEY`
4. ✅ Instalar `google-generativeai`: `pip install google-generativeai`
5. ✅ Testar worker: `python worker.py`
6. 🔲 Criar frontend React + Vite
7. 🔲 Integrar frontend com Supabase

---

## 🐛 Troubleshooting

### Worker não encontra arquivos:
- Verifique se `storage_path` está sendo salvo no banco
- Confirme que o bucket `processos` existe e é público

### Erro ao baixar do Storage:
- Verifique permissões do bucket
- Confirme que `storage_path` está correto

### Erro com Gemini:
- Verifique se `GOOGLE_API_KEY` está no `.env`
- Confirme que a chave está válida
- Instale a biblioteca: `pip install google-generativeai>=0.5.0`
