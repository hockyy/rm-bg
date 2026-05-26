@echo off
setlocal EnableExtensions
cd /d "%~dp0"

set "APP_DIR=%~dp0"
if "%APP_DIR:~-1%"=="\" set "APP_DIR=%APP_DIR:~0,-1%"

if exist "%APP_DIR%\.venv\Scripts\python.exe" (
    set "PYTHON=%APP_DIR%\.venv\Scripts\python.exe"
) else (
    where py >nul 2>&1
    if %ERRORLEVEL%==0 (
        set "PYTHON=py -3"
    ) else (
        set "PYTHON=python"
    )
)

set "SCRIPT=%APP_DIR%\remove_bg.py"
set "MENU_KEY=HKCU\Software\Classes\SystemFileAssociations\image\shell\RemoveBackground"
set "MENU_LABEL=Remove Background"
set "MENU_ICON=%SystemRoot%\System32\imageres.dll,67"

if not exist "%SCRIPT%" (
    echo ERROR: remove_bg.py not found in %APP_DIR%
    pause
    exit /b 1
)

reg add "%MENU_KEY%" /ve /d "%MENU_LABEL%" /f >nul
reg add "%MENU_KEY%" /v "Icon" /d "%MENU_ICON%" /f >nul
reg add "%MENU_KEY%" /v "MultiSelectModel" /d "Document" /f >nul
reg add "%MENU_KEY%\command" /ve /d "\"%PYTHON%\" \"%SCRIPT%\" %%*" /f >nul

if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to write registry keys. Try running as your normal user account.
    pause
    exit /b 1
)

echo Registered "Remove Background" for image files.
echo Right-click any image in Explorer to use it.
echo.
echo If the menu does not appear immediately, restart Explorer or sign out/in.
echo.
pause
