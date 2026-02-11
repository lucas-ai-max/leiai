# 🚀 Frontend ProcessIA

Interface React moderna para upload e monitoramento de documentos jurídicos.

## 📋 Pré-requisitos

- Node.js 18+ instalado
- Conta Supabase configurada
- Bucket `processos` criado no Supabase Storage

## ⚙️ Configuração

### 1. Configure as credenciais do Supabase

Edite `src/supabaseClient.js` e substitua:

```javascript
const supabaseUrl = 'SUA_URL_SUPABASE'  // Ex: https://xxxxx.supabase.co
const supabaseKey = 'SUA_CHAVE_ANON_PUBLICA'  // Chave pública (anon key)
```

**Onde encontrar:**
- Acesse seu projeto no Supabase
- Vá em **Settings** → **API**
- Copie a **URL** e a **anon public** key

### 2. Instale as dependências (já feito)

```bash
npm install
```

### 3. Execute o projeto

```bash
npm run dev
```

A aplicação estará disponível em `http://localhost:5173`

## 🎯 Funcionalidades

- ✅ **Upload em lote** de PDFs
- ✅ **Upload direto** para Supabase Storage
- ✅ **Atualização em tempo real** via Supabase Realtime
- ✅ **Status visual** (PENDENTE, PROCESSANDO, CONCLUIDO, ERRO)
- ✅ **Interface moderna** com Tailwind CSS

## 📁 Estrutura

```
frontend-processia/
├── src/
│   ├── App.jsx              # Componente principal
│   ├── supabaseClient.js    # Cliente Supabase
│   ├── index.css            # Estilos Tailwind
│   └── main.jsx             # Entry point
├── tailwind.config.js       # Configuração Tailwind
└── postcss.config.js        # Configuração PostCSS
```

## 🔄 Fluxo de Dados

1. Usuário faz upload de PDFs
2. Arquivos são enviados para Supabase Storage (bucket `processos`)
3. Registro criado na tabela `documento_gerenciamento` com status `PENDENTE`
4. Worker Python detecta o novo registro e processa
5. Frontend atualiza automaticamente via Realtime quando status muda

## 🛠️ Build para Produção

```bash
npm run build
```

Os arquivos otimizados estarão em `dist/`
