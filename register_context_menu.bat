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

set "SCRIPT=%APP_DIR%\remove_bg_menu.bat"
set "MENU_LABEL=Remove Background"
set "MENU_ICON=%SystemRoot%\System32\imageres.dll,67"

if not exist "%APP_DIR%\remove_bg.py" (
    echo ERROR: remove_bg.py not found in %APP_DIR%
    pause
    exit /b 1
)

for %%E in (.avif .bmp .gif .jpeg .jpg .png .tif .tiff .webp image) do call :RegisterExtension %%E

echo Registered "Remove Background" for image files.
echo Extensions: .avif .bmp .gif .jpeg .jpg .png .tif .tiff .webp
echo Right-click any image in Explorer to use it.
echo.
echo If the menu does not appear immediately, restart Explorer or sign out/in.
echo.
pause
exit /b 0

:RegisterExtension
set "MENU_KEY=HKCU\Software\Classes\SystemFileAssociations\%~1\shell\RemoveBackground"
reg add "%MENU_KEY%" /ve /d "%MENU_LABEL%" /f >nul
reg add "%MENU_KEY%" /v "Icon" /d "%MENU_ICON%" /f >nul
reg add "%MENU_KEY%" /v "MultiSelectModel" /d "Player" /f >nul
reg add "%MENU_KEY%\command" /ve /d "\"%SCRIPT%\" \"%%1\"" /f >nul
exit /b 0
