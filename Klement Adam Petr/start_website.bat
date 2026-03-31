@echo off
title Fitness App Website
echo ==========================================
echo      Starting Fitness App Website
echo ==========================================
echo.
echo The website will be available at: http://localhost:5000
echo Keep this window open to keep the server running.
echo.
if not exist "venv\Scripts\python.exe" (
    echo Virtual environment not found. Preparing one now with Python 3.12...
    call install_dependencies.bat
)
if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe web_app.py
) else (
    echo ERROR: venv not available. Please install Python 3.12 and run install_dependencies.bat
)
