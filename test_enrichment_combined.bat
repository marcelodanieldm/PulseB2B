@echo off
REM Test Combined Enrichment: Hunter.io + Clearbit
echo ========================================
echo   SUPER ENRICHMENT TEST
echo   Hunter.io + Clearbit Combined
echo ========================================
echo.

REM Activar entorno virtual si existe
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

REM Ejecutar script de prueba
python test_enrichment_combined.py

echo.
pause
