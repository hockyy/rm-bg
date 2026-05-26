@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo Installing Remove Background tool...
echo.

where py >nul 2>&1
if %ERRORLEVEL%==0 (
    py -3.12 -m venv .venv 2>nul
    if not exist ".venv\Scripts\python.exe" (
        py -3.13 -m venv .venv 2>nul
    )
    if not exist ".venv\Scripts\python.exe" (
        py -3.11 -m venv .venv 2>nul
    )
    if not exist ".venv\Scripts\python.exe" (
        py -3 -m venv .venv
    )
) else (
    python -m venv .venv
)

if not exist ".venv\Scripts\python.exe" (
    echo ERROR: Could not create a virtual environment.
    echo Install Python 3.11+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
pip install -r requirements.txt

if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: Dependency installation failed.
    pause
    exit /b 1
)

echo.
echo Setup complete.
echo Run register_context_menu.bat to add the right-click menu entry.
echo.
pause
