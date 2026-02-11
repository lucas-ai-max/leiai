# ⚙️ Configuração do Frontend

## Configurar Credenciais do Supabase

Você tem duas opções para configurar as credenciais:

### Opção 1: Variáveis de Ambiente (Recomendado)

Crie um arquivo `.env` na raiz do projeto `frontend-processia`:

```env
VITE_SUPABASE_URL=https://seu-projeto.supabase.co
VITE_SUPABASE_KEY=sua-chave-anon-publica-aqui
```

**Onde encontrar:**
1. Acesse seu projeto no Supabase Dashboard
2. Vá em **Settings** → **API**
3. Copie a **URL** (Project URL)
4. Copie a **anon public** key (Project API keys → anon public)

### Opção 2: Editar Arquivo Diretamente

Edite `src/supabaseClient.js` e substitua:

```javascript
const supabaseUrl = 'https://seu-projeto.supabase.co'
const supabaseKey = 'sua-chave-anon-publica-aqui'
```

## Executar o Projeto

```bash
cd "E:\Projetos Cursor\frontend-processia"
npm run dev
```

O servidor estará disponível em `http://localhost:5173`

## Troubleshooting

### Frontend não carrega
- Verifique se as credenciais estão configuradas
- Verifique o console do navegador (F12) para erros
- Certifique-se de que o servidor está rodando (`npm run dev`)

### Erro de conexão com Supabase
- Verifique se a URL está correta (sem barra no final)
- Verifique se a chave anon está correta
- Verifique se o bucket `processos` existe no Storage
