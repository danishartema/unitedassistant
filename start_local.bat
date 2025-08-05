@echo off
echo 🚀 Unified Assistant - Local Development
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python is not installed or not in PATH
    echo    Please install Python 3.11+ from https://python.org
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "main.py" (
    echo ❌ Error: main.py not found
    echo    Please run this script from the project directory
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  .env file not found
    echo    Creating template...
    python start_local.py
    pause
    exit /b 0
)

REM Start the application
echo 🚀 Starting Unified Assistant...
echo    The application will be available at: http://localhost:7860
echo    Press Ctrl+C to stop the server
echo.

python main.py

echo.
echo 👋 Server stopped
pause 