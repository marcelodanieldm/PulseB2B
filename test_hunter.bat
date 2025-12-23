@echo off
REM Test Hunter.io API
echo ========================================
echo   HUNTER.IO API TEST
echo ========================================
echo.

REM Activar entorno virtual si existe
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

REM Ejecutar script de prueba
python test_hunter_api.py

echo.
pause
