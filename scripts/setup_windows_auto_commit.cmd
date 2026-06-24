@echo off
setlocal

powershell.exe -ExecutionPolicy Bypass -File "%~dp0setup_windows_auto_commit.ps1" %*
exit /b %ERRORLEVEL%
