@echo off
title Fitness App Website
echo ==========================================
echo      Starting Fitness App Website
echo ==========================================
echo.
echo The website will be available at: http://localhost:5000
echo Keep this window open to keep the server running.
echo.

if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe web_app.py
) else (
    echo Virtual environment not found. Preparing one now...
    call install_dependencies.bat
    if exist "venv\Scripts\python.exe" (
        venv\Scripts\python.exe web_app.py
    ) else (
        echo Could not prepare virtual environment. Attempting to use system python...
        python web_app.py
    )
)

pause
