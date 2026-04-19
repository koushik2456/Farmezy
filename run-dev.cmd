@echo off
REM Run from repo root: run-dev.cmd   OR   PowerShell: .\run-dev.ps1
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run-dev.ps1" %*
