@echo off
echo ========================================
echo 🚀 Starting Talking Photo Generator
echo ========================================
echo.
echo 📦 This will start BOTH backend and frontend
echo.

REM Verificar se backend/.env existe
if not exist "backend\.env" (
    echo ❌ ERROR: backend/.env not found!
    echo.
    echo 📝 Setup required:
    echo    1. Copy .env.example to backend/.env
    echo    2. Add your API keys
    echo.
    pause
    exit /b 1
)

echo ✅ Configuration found
echo.
echo 🔧 Starting Backend Server...
start "🔧 Backend (Port 8000)" cmd /k "cd backend && python -m uvicorn server:app --reload --host 0.0.0.0 --port 8000"

echo ⏳ Waiting for backend to initialize...
timeout /t 5 /nobreak > nul

echo.
echo 🎨 Starting Frontend Server...
start "🎨 Frontend (Port 3000)" cmd /k "cd frontend && npm start"

echo.
echo ========================================
echo ✅ Both servers are starting!
echo ========================================
echo.
echo 📍 URLs:
echo    Backend:  http://localhost:8000
echo    Frontend: http://localhost:3000
echo    API Docs: http://localhost:8000/docs
echo.
echo 💡 TIP: Close this window will NOT stop the servers
echo    To stop, close each terminal window individually
echo.
echo ========================================
