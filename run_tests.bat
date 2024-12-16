@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

:menu
cls
echo ===================================
echo    Menu zapuska testov
echo ===================================
echo 1. Zapustit testy
echo 2. Vyhod
echo.
choice /c 12 /n /m "Vyberite deystvie (1-2): "

if errorlevel 2 goto :eof
if errorlevel 1 (
    call .venv\Scripts\activate
    pytest -n 10 ^
        --dist=loadfile ^
        --tb=short ^
        --durations=10 ^
        --cov=pyui_automation ^
        --cov-report=html ^
        --cov-report=term-missing ^
        --html=report.html ^
        --self-contained-html ^
        --junitxml=tests/.pytest_results/test_results.xml ^
        --log-file=test.log ^
        --log-file-level=DEBUG ^
        --color=yes ^
        -c pytest-html.ini ^
        --basetemp=./pytest_temp ^
        tests/
    echo.
    echo Testy zaversheny. Nazhmite lubuyu klavishu dlya vozvrata v menu...
    pause > nul
    goto menu
)
