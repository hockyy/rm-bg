@echo off
setlocal EnableExtensions

set "MENU_KEY=HKCU\Software\Classes\SystemFileAssociations\image\shell\RemoveBackground"

reg query "%MENU_KEY%" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Context menu entry is not registered.
    pause
    exit /b 0
)

reg delete "%MENU_KEY%" /f >nul

if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to remove registry keys.
    pause
    exit /b 1
)

echo Removed "Remove Background" from the image context menu.
pause
