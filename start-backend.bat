@echo off
echo ========================================
echo 🚀 Starting Backend - Talking Photo Generator
echo ========================================
echo.
echo 📍 Backend will start on: http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo 💊 Health: http://localhost:8000/health
echo.
echo ⚙️ Checking providers...
cd backend

REM Verificar se .env existe
if not exist ".env" (
    echo ❌ ERROR: .env file not found!
    echo.
    echo 📝 Please create .env file:
    echo    1. Copy .env.example to .env
    echo    2. Add your API keys
    echo.
    pause
    exit /b 1
)

echo ✅ Configuration found
echo.
echo 🎬 Starting server...
python -m uvicorn server:app --reload --host 0.0.0.0 --port 8000
