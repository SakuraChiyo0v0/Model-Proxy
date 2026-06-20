@echo off
title Model Proxy

echo ============================
echo   Model Proxy Launcher
echo ============================
echo.

cd /d "%~dp0"

echo [0/2] Cleaning up existing services...

REM Kill any process on port 8000 (backend)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)

REM Kill any process on port 5173 (frontend dev server)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)

timeout /t 2 /nobreak >nul

echo [1/2] Starting Backend (FastAPI :8000)...
start "Model-Proxy-Backend" /MIN cmd /c "cd /d %~dp0backend && uvicorn app.main:app --reload --port 8000"

echo [2/2] Starting Frontend (React :5173)...
start "Model-Proxy-Frontend" /MIN cmd /c "cd /d %~dp0frontend && npx vite --port 5173"

echo.
echo   Backend : http://127.0.0.1:8000
echo   Frontend: http://localhost:5173
echo.
echo Started! Press any key to close this window.
pause >nul
