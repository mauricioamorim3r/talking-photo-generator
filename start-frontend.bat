@echo off
echo ========================================
echo 🎨 Starting Frontend - Talking Photo Generator
echo ========================================
echo.
echo 📍 Frontend will start on: http://localhost:3000
echo 🔗 Backend API: http://localhost:8000
echo.

cd frontend

REM Verificar se .env.local existe
if not exist ".env.local" (
    echo ⚙️ Creating .env.local...
    echo REACT_APP_API_URL=http://localhost:8000 > .env.local
    echo ✅ Created .env.local
    echo.
)

echo ✅ Configuration ready
echo.
echo 🚀 Starting React app...
echo    (Browser will open automatically)
echo.
npm start
