@echo off
REM Machine Translation & Document Search - Complete Run Script
REM Author: Phuoc Dai
REM Created: 2025-11-11

setlocal enabledelayedexpansion

echo.
echo ===============================================
echo Machine Translation & Document Search
echo ===============================================
echo.

REM Set project paths
set HAYSTACK_ROOT=e:\haystack
set BACKEND_DIR=%HAYSTACK_ROOT%\backend
set VENV_PYTHON=%HAYSTACK_ROOT%\venv\Scripts\python.exe
set FRONTEND_URL=http://127.0.0.1:8000

echo [1/3] Checking dependencies...
if not exist "%VENV_PYTHON%" (
    echo ERROR: Virtual environment not found at %VENV_PYTHON%
    echo Please run: python -m venv %HAYSTACK_ROOT%\venv
    pause
    exit /b 1
)

echo [✓] Virtual environment found

echo.
echo [2/3] Installing dependencies...
cd /d "%BACKEND_DIR%"
"%VENV_PYTHON%" -m pip install -q -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo [✓] Dependencies installed

echo.
echo [3/3] Starting FastAPI server...
echo.
echo ===============================================
echo Server Information:
echo ===============================================
echo Backend API: http://127.0.0.1:8000/api
echo API Docs:    http://127.0.0.1:8000/docs
echo Frontend:    http://127.0.0.1:8000
echo ===============================================
echo.
echo Press CTRL+C to stop the server
echo.

REM Kill any existing Python processes on port 8000
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do (
    taskkill /f /pid %%a 2>nul
)

timeout /t 1 /nobreak >nul

REM Start the server
cd /d "%BACKEND_DIR%"
"%VENV_PYTHON%" -m uvicorn main:app --host 127.0.0.1 --port 8000

echo.
echo Server stopped.
pause
