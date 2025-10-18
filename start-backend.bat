@echo off
echo ========================================
echo Starting Talking Photo Generator Backend
echo ========================================
cd backend
python -m uvicorn server:app --reload --port 8001
