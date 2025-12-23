@echo off
REM Test Clearbit API
echo ========================================
echo   CLEARBIT API TEST
echo ========================================
echo.

REM Activar entorno virtual si existe
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

REM Ejecutar script de prueba
python test_clearbit_api.py

echo.
pause
