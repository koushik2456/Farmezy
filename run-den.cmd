@echo off
REM Same as run-dev.cmd (typo-friendly name). PowerShell: .\run-den.ps1
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run-den.ps1" %*
