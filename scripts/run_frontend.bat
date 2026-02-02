@echo off
cd /d "E:\Projetos Cursor\frontend-processia"
echo Installing dependencies...
call npm install
if %errorlevel% neq 0 exit /b %errorlevel%
echo Starting Frontend...
call npm run dev
