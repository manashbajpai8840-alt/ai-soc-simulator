@echo off
REM AI SOC Simulator - Start Script for Windows
REM Just double-click this file to run!

echo.
echo =====================================
echo   AI SOC Simulator - Starting...
echo =====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo Please download from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

REM Navigate to simulator folder
cd /d "%~dp0ai_soc_simulator"

REM Install requirements if needed
echo Installing dependencies...
pip install -r requirements.txt -q

REM Run the simulator
echo.
echo Starting AI SOC Simulator...
echo (This will run for 100 events - fast mode)
echo.
python main.py --events 100 --fast

pause
