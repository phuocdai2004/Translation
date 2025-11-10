@echo off
REM Run project with Docker Compose

setlocal enabledelayedexpansion

echo.
echo ===============================================
echo Running with Docker Compose
echo ===============================================
echo.

set HAYSTACK_ROOT=e:\haystack

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not installed or not in PATH
    echo Please install Docker Desktop from https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo [✓] Docker found

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker Compose is not installed or not in PATH
    pause
    exit /b 1
)

echo [✓] Docker Compose found
echo.

REM Start Docker Compose
cd /d "%HAYSTACK_ROOT%"

echo [1/2] Building images...
docker-compose build

if errorlevel 1 (
    echo ERROR: Failed to build Docker images
    pause
    exit /b 1
)

echo.
echo [2/2] Starting containers...
docker-compose up

echo.
echo.
echo ===============================================
echo Services Information:
echo ===============================================
echo Frontend:  http://localhost
echo API:       http://localhost/api
echo Docs:      http://localhost/docs
echo ===============================================
echo.
echo Press CTRL+C to stop containers
echo.

pause
