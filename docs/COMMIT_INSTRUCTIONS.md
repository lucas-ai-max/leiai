# Instruções para fazer Commit no GitHub

## 📋 Pré-requisitos

1. **Instalar Git** (se ainda não tiver):
   - Baixe em: https://git-scm.com/download/win
   - Instale com as configurações padrão
   - Reinicie o terminal após instalar

## 🚀 Passos para fazer o Commit

### 1. Abra o terminal na pasta do projeto:
```powershell
cd "C:\Users\TRIA 2026\Downloads\ProcessIA\processia-main\processia-main"
```

### 2. Inicialize o repositório Git (se ainda não estiver inicializado):
```bash
git init
```

### 3. Configure o remote do GitHub:
```bash
git remote add origin https://github.com/lucas-ai-max/processia.git
```

Ou se já existir, atualize:
```bash
git remote set-url origin https://github.com/lucas-ai-max/processia.git
```

### 4. Adicione todos os arquivos:
```bash
git add .
```

### 5. Faça o commit:
```bash
git commit -m "feat: Processamento completo com PyMuPDF - Extração de PDFs, geração de embeddings e salvamento em chunks funcionando corretamente"
```

### 6. Envie para o GitHub:
```bash
git branch -M main
git push -u origin main
```

Se der erro na branch, tente:
```bash
git push -u origin master
```

## 🔐 Autenticação

Se pedir credenciais, você pode:

1. **Usar Personal Access Token** (recomendado):
   - Vá em: GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Crie um token com permissão `repo`
   - Use o token como senha quando pedir

2. **Ou use GitHub CLI**:
   ```bash
   gh auth login
   ```

## ✅ Verificar

Depois do push, verifique em:
https://github.com/lucas-ai-max/processia

## 📝 Mensagem do Commit

A mensagem do commit atual inclui:
- Migração completa de `pypdf` para `PyMuPDF` (fitz)
- Correção de erros "I/O operation on closed file"
- Correção de estrutura de chunks (document_id e filename na raiz)
- Processamento sequencial funcionando
- Extração e salvamento de chunks funcionando corretamente
