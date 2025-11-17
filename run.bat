@echo off
title Haystack
cd /d %~dp0backend

echo Starting server...
timeout /t 2 /nobreak >nul

start http://localhost:8000

python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

pause
