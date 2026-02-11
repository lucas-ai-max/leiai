# 🔧 Troubleshooting - Frontend não carrega

## Verificações Rápidas

### 1. Servidor está rodando?

```bash
cd "E:\Projetos Cursor\frontend-processia"
npm run dev
```

Você deve ver algo como:
```
  VITE v7.2.4  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### 2. Abra o navegador no endereço correto

- URL: `http://localhost:5173`
- Se a porta estiver diferente, use a que aparecer no terminal

### 3. Verifique o Console do Navegador

1. Pressione `F12` no navegador
2. Vá na aba **Console**
3. Procure por erros em vermelho

**Erros comuns:**

#### Erro: "Failed to fetch" ou "Network error"
- **Causa**: Supabase não configurado ou credenciais inválidas
- **Solução**: Configure `src/supabaseClient.js` ou crie `.env` com `VITE_SUPABASE_URL` e `VITE_SUPABASE_KEY`

#### Erro: "Cannot read property 'from' of null"
- **Causa**: Supabase client não inicializado
- **Solução**: Verifique se as credenciais estão corretas em `src/supabaseClient.js`

#### Erro: "Module not found"
- **Causa**: Dependências não instaladas
- **Solução**: Execute `npm install`

### 4. Limpe o cache e reinstale

```bash
# Parar o servidor (Ctrl+C)

# Limpar cache
rm -rf node_modules
rm package-lock.json

# Reinstalar
npm install

# Rodar novamente
npm run dev
```

### 5. Verifique se a porta está livre

Se a porta 5173 estiver ocupada:

```bash
# Windows PowerShell
netstat -ano | findstr :5173

# Matar processo se necessário
taskkill /PID <numero_do_pid> /F
```

Ou use outra porta:
```bash
npm run dev -- --port 3000
```

## Problemas Específicos

### Frontend carrega mas mostra erro amarelo
✅ **Isso é normal!** Significa que o frontend está funcionando, mas as credenciais do Supabase não estão configuradas. Configure-as para usar o sistema.

### Tela em branco
1. Abra o Console (F12)
2. Verifique se há erros JavaScript
3. Verifique se o arquivo `index.html` está carregando
4. Tente acessar `http://localhost:5173/src/main.jsx` (deve mostrar código)

### Estilos não aparecem (sem CSS)
- Verifique se `src/index.css` existe e tem `@tailwind` directives
- Verifique se `postcss.config.js` está configurado corretamente
- Tente rebuild: `npm run build`

## Teste Rápido

Crie um arquivo `test.html` na raiz do projeto:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Teste</title>
</head>
<body>
    <h1>Se você vê isso, o servidor está funcionando!</h1>
    <script>
        console.log('JavaScript funcionando!')
    </script>
</body>
</html>
```

Acesse `http://localhost:5173/test.html` - se funcionar, o problema é no React/JSX.

## Ainda não funciona?

1. Verifique a versão do Node.js: `node --version` (deve ser 18+)
2. Verifique a versão do npm: `npm --version`
3. Tente criar um projeto Vite novo para comparar:
   ```bash
   npm create vite@latest test-app -- --template react
   cd test-app
   npm install
   npm run dev
   ```

Se o projeto de teste funcionar, o problema é específico do `frontend-processia`.
