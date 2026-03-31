@echo off
setlocal
title Install Dependencies
echo ==========================================
echo      Installing Dependencies (Python 3.12)
echo ==========================================
echo.

if not exist "venv\Scripts\python.exe" (
    echo Creating Virtual Environment with Python 3.12...
    py -3.12 -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Python 3.12 not found. Please install Python 3.12 and try again.
        echo Download: https://www.python.org/downloads/release/python-3120/
        goto :end
    )
)

echo Using Virtual Environment...
venv\Scripts\python.exe -m pip install --upgrade pip
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: pip upgrade failed.
    goto :end
)
venv\Scripts\python.exe -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Installation finished with errors.
    echo Note: Kivy requires Python 3.10–3.12 on Windows. Ensure 3.12 is installed.
) else (
    echo.
    echo Installation finished successfully!
)

:end
pause
endlocal
