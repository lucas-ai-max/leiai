# 🚀 Início Rápido - Frontend ProcessIA

## ✅ Configuração Concluída!

O arquivo `.env` foi criado com suas credenciais do Supabase.

## 🎯 Como Iniciar

1. **Inicie o servidor de desenvolvimento:**
   ```bash
   cd "E:\Projetos Cursor\frontend-processia"
   npm run dev
   ```

2. **Abra no navegador:**
   - URL: `http://localhost:5173`
   - (A porta pode variar - veja no terminal)

3. **O que você deve ver:**
   - ✅ Interface completa carregando
   - ✅ Área de upload funcionando
   - ✅ Lista de documentos (se houver)

## ⚠️ Importante

- **Reinicie o servidor** se você mudar o arquivo `.env`
- O Vite só carrega variáveis de ambiente na inicialização
- Use `Ctrl+C` para parar o servidor

## 🔧 Se não funcionar

1. Verifique se o servidor está rodando
2. Abra o Console do navegador (F12) e veja se há erros
3. Verifique se o arquivo `.env` está na pasta `frontend-processia`
4. Certifique-se de que as variáveis começam com `VITE_`

## 📝 Variáveis no .env

```
VITE_SUPABASE_URL=https://kyrvxikgtifklibusxwf.supabase.co
VITE_SUPABASE_KEY=sua-chave-aqui
```

**Nota:** As variáveis no frontend precisam ter o prefixo `VITE_` para serem acessíveis no código do cliente.
