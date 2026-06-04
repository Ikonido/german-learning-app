@echo off
setlocal

set "PROJECT_ROOT=%~dp0"
if "%PROJECT_ROOT:~-1%"=="\" set "PROJECT_ROOT=%PROJECT_ROOT:~0,-1%"

set "BACKEND_VENV=%PROJECT_ROOT%\.venv\Scripts\activate.bat"
set "FRONTEND_DIR=%PROJECT_ROOT%\frontend"
set "FRONTEND_URL=http://localhost:5173"

echo Starting Deutsch Lernen project...

if not exist "%BACKEND_VENV%" (
    echo ERROR: Virtual environment was not found:
    echo %BACKEND_VENV%
    echo.
    echo Create it first with:
    echo python -m venv .venv
    echo .venv\Scripts\activate
    echo pip install -r requirements.txt
    pause
    exit /b 1
)

if not exist "%FRONTEND_DIR%" (
    echo ERROR: Frontend directory was not found:
    echo %FRONTEND_DIR%
    pause
    exit /b 1
)

start "Backend - FastAPI" cmd /k "cd /d ""%PROJECT_ROOT%"" && call ""%BACKEND_VENV%"" && uvicorn app.main:app --reload"
start "Frontend - Vite" cmd /k "cd /d ""%FRONTEND_DIR%"" && npm run dev"

timeout /t 3 /nobreak >nul
start "" "%FRONTEND_URL%"

echo Backend:  http://localhost:8000
echo Frontend: %FRONTEND_URL%

endlocal
