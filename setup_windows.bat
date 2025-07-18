@echo off
REM Setup script for Windows
color 0E
echo.
echo ==========================================
echo    Invoice Processing System Setup
echo ==========================================
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [INFO] Python found
python --version

REM Create virtual environment
echo.
echo [INFO] Creating virtual environment...
python -m venv venv_new

if %errorlevel% neq 0 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)

echo [SUCCESS] Virtual environment created

REM Install dependencies
echo.
echo [INFO] Installing dependencies...
venv_new\Scripts\pip.exe install -r requirements.txt

if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo [SUCCESS] Dependencies installed

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo.
    echo [INFO] Creating .env file...
    copy .env.example .env
    echo.
    echo [IMPORTANT] Please edit .env file and add your Anthropic API key
    echo Get your API key from: https://console.anthropic.com/
    echo.
    set /p choice="Would you like to open .env file now? (y/n): "
    if /i "%choice%"=="y" (
        notepad .env
    )
)

REM Create invoice folder if it doesn't exist
if not exist "invoice" (
    echo.
    echo [INFO] Creating invoice folder...
    mkdir invoice
)

echo.
echo ==========================================
echo             Setup Complete!
echo ==========================================
echo.
echo Next steps:
echo 1. Edit .env file and add your API key
echo 2. Add invoice images to the 'invoice' folder
echo 3. Run run_processor.bat to process invoices
echo.
pause