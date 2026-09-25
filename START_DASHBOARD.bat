@echo off
REM AI SOC Simulator - Dashboard Launcher for Windows
REM Just double-click this file to see the dashboard!

echo.
echo =====================================
echo   AI SOC Simulator - Dashboard
echo =====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo Please download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Navigate to simulator folder
cd /d "%~dp0ai_soc_simulator"

REM Install requirements if needed
echo Installing dependencies...
pip install -r requirements.txt -q

REM Run the dashboard
echo.
echo Starting Dashboard...
echo Your browser should open automatically.
echo If not, visit: http://localhost:8501
echo.
streamlit run dashboard.py

pause
