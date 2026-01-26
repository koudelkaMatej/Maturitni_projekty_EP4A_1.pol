@echo off
title Fitness App Game
echo ==========================================
echo       Starting Fitness App Game
echo ==========================================
echo.

if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe main.py
) else (
    echo Virtual environment not found. Preparing one now...
    call install_dependencies.bat
    if exist "venv\Scripts\python.exe" (
        venv\Scripts\python.exe main.py
    ) else (
        echo Could not prepare virtual environment. Attempting to use system python...
        python main.py
    )
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ==========================================
    echo ERROR: The game crashed or could not start.
    echo ==========================================
    echo.
    echo Common fixes:
    echo 1. Ensure you have installed dependencies (run install_dependencies.bat)
    echo 2. If you see "ModuleNotFoundError: No module named 'kivy'", ensure you have a compatible Python version (3.10 - 3.12).
    echo    Python 3.14 is currently NOT fully supported by Kivy.
    echo.
)
pause
