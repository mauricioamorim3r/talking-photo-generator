@echo off
REM ========================================
REM 🧪 Quick Test - Providers Check
REM ========================================

echo.
echo 🧪 Testing Video Providers Configuration
echo ========================================
echo.

cd backend

REM Check if .env exists
if not exist ".env" (
    echo ❌ backend/.env not found!
    echo.
    echo Please run: copy .env.example .env
    echo Then add your API keys
    echo.
    pause
    exit /b 1
)

echo ✅ .env found
echo.
echo 🔍 Checking providers...
echo.

python -c "import sys; sys.path.insert(0, '.'); from video_providers import video_manager; providers = video_manager.get_available_providers(); print('\n📋 Available Providers:'); [print(f'  - {k}: {"✅ YES" if v else "❌ NO"}') for k, v in providers.items()]; print('\n💰 Estimated Costs (8s video):'); from video_providers import VideoProvider; [(print(f'  {k}:'), print(f'    Without audio: ${video_manager.estimate_cost(VideoProvider[k.upper()], 8, False):.2f}'), print(f'    With audio: ${video_manager.estimate_cost(VideoProvider[k.upper()], 8, True):.2f}')) for k in ['FAL_VEO3', 'GOOGLE_VEO3_DIRECT'] if providers.get(VideoProvider[k])] if providers else print('  No providers available')"

echo.
echo ========================================
echo.
pause
