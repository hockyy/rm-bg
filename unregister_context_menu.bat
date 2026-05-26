@echo off
setlocal EnableExtensions

set "REMOVED=0"

for %%E in (.avif .bmp .gif .jpeg .jpg .png .tif .tiff .webp image) do call :UnregisterExtension %%E

if "%REMOVED%"=="0" (
    echo Context menu entry is not registered.
) else (
    echo Removed "Remove Background" from the image context menu.
)
pause
exit /b 0

:UnregisterExtension
set "MENU_KEY=HKCU\Software\Classes\SystemFileAssociations\%~1\shell\RemoveBackground"
reg query "%MENU_KEY%" >nul 2>&1
if %ERRORLEVEL% neq 0 exit /b 0
reg delete "%MENU_KEY%" /f >nul
if %ERRORLEVEL%==0 set "REMOVED=1"
exit /b 0
