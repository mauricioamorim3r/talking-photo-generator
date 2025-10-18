@echo off
echo ========================================
echo Starting Talking Photo Generator
echo ========================================
echo.
echo Starting Backend...
start "Backend Server" cmd /k "cd backend && python -m uvicorn server:app --reload --port 8001"
echo.
timeout /t 3 /nobreak > nul
echo Starting Frontend...
start "Frontend Server" cmd /k "cd frontend && npm start"
echo.
echo ========================================
echo Both servers are starting...
echo Backend: http://localhost:8001
echo Frontend: http://localhost:3000
echo ========================================
