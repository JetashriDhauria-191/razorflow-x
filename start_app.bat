@echo off
echo Starting Razorflow X Application Server...
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
pause
