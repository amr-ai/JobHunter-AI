@echo off
echo ============================================
echo Starting JobFinder AI with Virtual Environment
echo ============================================
echo.
echo Using Python from venv...
.\venv\Scripts\python.exe --version
echo.
echo Starting Flask server...
.\venv\Scripts\python.exe run.py
pause
