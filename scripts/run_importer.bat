@echo off
cd /d "e:\Projetos Cursor\Leiai -Antigravity\leiai"
call venv\Scripts\activate
echo Starting Salesforce Pipeline Manager...
python src/pipeline_manager.py
pause
