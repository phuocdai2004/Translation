# Machine Translation & Document Search - Quick Start# Machine Translation & Document Search - Quick Start# Machine Translation & Document Search - Quick Start

Write-Host "Starting FastAPI server..." -ForegroundColor Cyan

Write-Host "http://127.0.0.1:8000" -ForegroundColor Green# Usage: .\run.ps1# Usage: .\run.ps1

Write-Host ""



Set-Location e:\haystack\backend

$env:PYTHONPATH = 'e:\haystack\backend'Write-Host "========================================" -ForegroundColor CyanWrite-Host "========================================" -ForegroundColor Cyan



python -c @"Write-Host "Machine Translation & Document Search" -ForegroundColor CyanWrite-Host "Machine Translation & Document Search" -ForegroundColor Cyan

import sys

sys.path.insert(0, r'e:\haystack\backend')Write-Host "========================================" -ForegroundColor CyanWrite-Host "========================================" -ForegroundColor Cyan

from main import app

import uvicornWrite-Host ""Write-Host ""

uvicorn.run(app, host='127.0.0.1', port=8000, log_level='info')

"@


$BACKEND_DIR = "e:\haystack\backend"$BACKEND_DIR = "e:\haystack\backend"

$FRONTEND_URL = "http://127.0.0.1:8000"

Write-Host "[*] Starting FastAPI server..." -ForegroundColor Yellow

Write-Host "[*] Frontend: http://127.0.0.1:8000" -ForegroundColor GreenWrite-Host "[*] Starting server..." -ForegroundColor Yellow

Write-Host "[*] API Docs: http://127.0.0.1:8000/docs" -ForegroundColor GreenWrite-Host "[*] Frontend: $FRONTEND_URL" -ForegroundColor Green

Write-Host "[*] Press Ctrl+C to stop" -ForegroundColor YellowWrite-Host "[*] Press Ctrl+C to stop" -ForegroundColor Yellow

Write-Host ""Write-Host ""



$env:PYTHONPATH = 'e:\haystack\backend'$env:PYTHONPATH = 'e:\haystack\backend'



# Kill existing process on port 8000 if neededtry {

$existingProcess = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object -First 1    python -c "import sys; sys.path.insert(0, r'e:\haystack\backend'); from main import app; import uvicorn; uvicorn.run(app, host='127.0.0.1', port=8000)"

if ($existingProcess) {}

    Write-Host "[*] Port 8000 already in use, stopping existing process..." -ForegroundColor Yellowcatch {

    Stop-Process -Id $existingProcess.OwningProcess -Force -ErrorAction SilentlyContinue    Write-Host "ERROR: Failed to start server" -ForegroundColor Red

    Start-Sleep -Seconds 1    Write-Host $_.Exception.Message -ForegroundColor Red

}    exit 1

}

Write-Host ""Write-Host "[✓] Virtual environment found" -ForegroundColor Green

Write-Host "===============================================" -ForegroundColor CyanWrite-Host ""

Write-Host "Server ready. Open browser at:" -ForegroundColor Cyan

Write-Host "http://127.0.0.1:8000" -ForegroundColor Green# Install dependencies

Write-Host "===============================================" -ForegroundColor CyanWrite-Host "[2/3] Installing dependencies..." -ForegroundColor Yellow

Write-Host ""Set-Location $BACKEND_DIR

& $VENV_PYTHON -m pip install -q -r requirements.txt

# Start the serverif ($LASTEXITCODE -ne 0) {

Set-Location $BACKEND_DIR    Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red

# Start the server
Set-Location $BACKEND_DIR
$pythonCmd = @"
import sys
sys.path.insert(0, r'e:\haystack\backend')
from main import app
import uvicorn
uvicorn.run(app, host='127.0.0.1', port=8000, log_level='info')
"@
python -c $pythonCmd    exit 1

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
# e:\haystack\start.bat