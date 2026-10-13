@echo off
chcp 65001 >nul
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0render.ps1" %*
set "render_status=%ERRORLEVEL%"
if not "%render_status%"=="0" pause
if "%~1"=="" pause
exit /b %render_status%
