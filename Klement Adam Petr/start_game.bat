@echo off
title Fitness App Game
echo ==========================================
echo       Starting Fitness App Game
echo ==========================================
echo.

if not exist "venv\Scripts\python.exe" (
    echo Virtual environment not found. Preparing one now with Python 3.12...
    call install_dependencies.bat
)
if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe main.py
) else (
    echo ERROR: venv not available. Please install Python 3.12 and run install_dependencies.bat
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ==========================================
    echo ERROR: The game crashed or could not start.
    echo ==========================================
    echo.
    echo 1. Ensure you have Python 3.12 installed and venv created (install_dependencies.bat)
    echo 2. If you see "ModuleNotFoundError: No module named 'kivy'", run install_dependencies.bat
    echo.
)
pause
