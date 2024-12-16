@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

:menu
cls
echo ===================================
echo    Menu zapuska servera
echo ===================================
echo 1. Zapustit server s avtoobnovleniem
echo 2. Zapustit server bez avtoobnovleniya
echo 3. Vyhod
echo.
choice /c 123 /n /m "Vyberite deystvie (1-3): "

if errorlevel 3 goto :eof
if errorlevel 2 (
    call .venv\Scripts\activate
    python -c "from pyui_automation.server import run_server; run_server()"
    goto menu
)
if errorlevel 1 (
    call .venv\Scripts\activate
    python -m pyui_automation.server.run_server
    timeout /t 5
    goto menu
)
