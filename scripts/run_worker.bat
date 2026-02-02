@echo off
cd /d "E:\Projetos Cursor\Leiai -Antigravity\leiai"
call venv\Scripts\activate
echo Starting Worker...
python src/worker.py
