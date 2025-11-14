@echo off
REM =============================================================================
REM Start All Services - HF Virtual Stylist (Windows)
REM =============================================================================
echo.
echo ========================================================================
echo   HF Virtual Stylist - Starting All Services
echo ========================================================================
echo.
echo This will open 3 terminal windows:
echo   1. Backend API (port 8000)
echo   2. Worker (processes generation jobs)
echo   3. Frontend (port 3000)
echo.
echo Press Ctrl+C in each window to stop the services.
echo ========================================================================
echo.

REM Get the script directory (project root)
set PROJECT_DIR=%~dp0
cd /d "%PROJECT_DIR%"

REM Start Backend API
echo [1/3] Starting Backend API...
start "HF Virtual Stylist - Backend API" cmd /k "cd /d "%PROJECT_DIR%backend" && call .venv\Scripts\activate && echo. && echo ====================================== && echo   Backend API Starting... && echo ====================================== && echo. && uvicorn app.main:app --reload --port 8000"

REM Wait a bit for backend to start
timeout /t 3 /nobreak >nul

REM Start Worker
echo [2/3] Starting Worker...
start "HF Virtual Stylist - Worker" cmd /k "cd /d "%PROJECT_DIR%backend" && call .venv\Scripts\activate && echo. && echo ====================================== && echo   Worker Starting... && echo ====================================== && echo. && python worker.py"

REM Wait a bit
timeout /t 2 /nobreak >nul

REM Start Frontend
echo [3/3] Starting Frontend...
start "HF Virtual Stylist - Frontend" cmd /k "cd /d "%PROJECT_DIR%frontend" && echo. && echo ====================================== && echo   Frontend Starting... && echo ====================================== && echo. && npm run dev"

echo.
echo ========================================================================
echo   All services started!
echo ========================================================================
echo.
echo   Backend API:  http://localhost:8000/docs
echo   Frontend:     http://localhost:3000
echo.
echo   Check each terminal window for status.
echo   To stop: Close the terminal windows or press Ctrl+C in each.
echo ========================================================================
echo.

pause
