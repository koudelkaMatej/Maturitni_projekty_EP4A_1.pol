@echo off
title Install Dependencies
echo ==========================================
echo      Installing Dependencies
echo ==========================================
echo.

if exist "venv\Scripts\python.exe" (
    echo Using Virtual Environment (Recommended)...
    venv\Scripts\python.exe -m pip install -r requirements.txt
) else (
    echo Creating Virtual Environment with Python 3.12...
    py -3.12 -m venv venv
    if %ERRORLEVEL% NEQ 0 (
         echo Could not find Python 3.12. Using system default python...
         python -m pip install -r requirements.txt
    ) else (
         echo Virtual Environment created. Installing dependencies...
         venv\Scripts\python.exe -m pip install -r requirements.txt
    )
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Installation finished with errors.
    echo Note: Kivy may fail to install on Python 3.14. Please use Python 3.10-3.12 if possible.
) else (
    echo.
    echo Installation finished successfully!
)
pause
