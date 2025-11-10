# Machine Translation & Document Search - PowerShell Run Script
# Usage: .\run.ps1

$ErrorActionPreference = "Stop"

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "Machine Translation & Document Search" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

$HAYSTACK_ROOT = "e:\haystack"
$BACKEND_DIR = "$HAYSTACK_ROOT\backend"
$VENV_PYTHON = "$HAYSTACK_ROOT\venv\Scripts\python.exe"
$FRONTEND_URL = "http://127.0.0.1:8000"

# Check virtual environment
Write-Host "[1/3] Checking dependencies..." -ForegroundColor Yellow
if (-not (Test-Path $VENV_PYTHON)) {
    Write-Host "ERROR: Virtual environment not found at $VENV_PYTHON" -ForegroundColor Red
    Write-Host "Please run: python -m venv $HAYSTACK_ROOT\venv" -ForegroundColor Red
    exit 1
}
Write-Host "[✓] Virtual environment found" -ForegroundColor Green
Write-Host ""

# Install dependencies
Write-Host "[2/3] Installing dependencies..." -ForegroundColor Yellow
Set-Location $BACKEND_DIR
& $VENV_PYTHON -m pip install -q -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "[✓] Dependencies installed" -ForegroundColor Green
Write-Host ""

# Kill existing process on port 8000
Write-Host "[3/3] Cleaning up port 8000..." -ForegroundColor Yellow
$existingProcess = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($existingProcess) {
    Stop-Process -Id $existingProcess.OwningProcess -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
}
Write-Host "[✓] Port 8000 is ready" -ForegroundColor Green
Write-Host ""

# Display server information
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "Server Information:" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "Backend API: http://127.0.0.1:8000/api" -ForegroundColor Green
Write-Host "API Docs:    http://127.0.0.1:8000/docs" -ForegroundColor Green
Write-Host "Frontend:    http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press CTRL+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the server
Set-Location $BACKEND_DIR
& $VENV_PYTHON -m uvicorn main:app --host 127.0.0.1 --port 8000

Write-Host "Server stopped." -ForegroundColor Yellow
