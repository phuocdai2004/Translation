@echo off
cd /d e:\haystack\backend
set PYTHONPATH=e:\haystack\backend
echo.
echo ====================================
echo Machine Translation & Doc Search
echo ====================================
echo.
echo Starting server on http://127.0.0.1:8000
echo Press Ctrl+C to stop
echo.
python -m uvicorn main:app --host 127.0.0.1 --port 8000
pause
