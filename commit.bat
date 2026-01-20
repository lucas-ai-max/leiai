@echo off
REM Script para fazer commit no GitHub
REM Execute este arquivo após instalar o Git

echo ========================================
echo  COMMIT PARA GITHUB - PROCESSIA
echo ========================================
echo.

REM Verificar se Git está instalado
git --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Git nao esta instalado!
    echo Baixe em: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo [1/6] Inicializando repositorio Git...
if not exist .git (
    git init
)

echo [2/6] Configurando remote do GitHub...
git remote remove origin 2>nul
git remote add origin https://github.com/lucas-ai-max/processia.git

echo [3/6] Adicionando arquivos...
git add .

echo [4/6] Status dos arquivos:
git status

echo.
echo [5/6] Fazendo commit...
git commit -m "feat: Processamento completo com PyMuPDF - Extração de PDFs, geração de embeddings e salvamento em chunks funcionando corretamente"

if errorlevel 1 (
    echo.
    echo AVISO: Nenhuma mudanca para commitar, ou erro no commit.
    echo Verifique o status acima.
    pause
    exit /b 1
)

echo.
echo [6/6] Enviando para o GitHub...
git branch -M main 2>nul
git push -u origin main

if errorlevel 1 (
    echo.
    echo Tentando com branch 'master'...
    git push -u origin master
)

echo.
echo ========================================
echo  CONCLUIDO!
echo ========================================
echo.
echo Verifique em: https://github.com/lucas-ai-max/processia
pause
