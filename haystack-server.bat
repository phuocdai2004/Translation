@echo off
cd /d e:\haystack\backend
set PYTHONPATH=e:\haystack\backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000
