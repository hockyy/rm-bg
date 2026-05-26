@echo off
setlocal EnableExtensions

set "APP_DIR=%~dp0"
if "%APP_DIR:~-1%"=="\" set "APP_DIR=%APP_DIR:~0,-1%"

set "PYTHON=%APP_DIR%\.venv\Scripts\python.exe"
set "SCRIPT=%APP_DIR%\remove_bg.py"
set "LOG=%TEMP%\rm-bg-last-run.log"

if not exist "%PYTHON%" (
    >"%LOG%" echo [%DATE% %TIME%] Missing virtual environment: %PYTHON%
    msg "%USERNAME%" "Remove Background: run setup.bat first." 2>nul
    exit /b 1
)

if "%~1"=="" (
    >>"%LOG%" echo [%DATE% %TIME%] No input files received from Explorer.
    >>"%LOG%" echo argv: %*
    msg "%USERNAME%" "Remove Background: no image file was received." 2>nul
    exit /b 1
)

>>"%LOG%" echo [%DATE% %TIME%] Starting: %1
"%PYTHON%" "%SCRIPT%" "%~1" >>"%LOG%" 2>&1
set "ERR=%ERRORLEVEL%"

if not "%ERR%"=="0" (
    msg "%USERNAME%" "Remove Background failed. See %LOG%" 2>nul
    exit /b %ERR%
)

exit /b 0
