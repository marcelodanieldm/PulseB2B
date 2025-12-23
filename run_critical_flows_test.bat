@echo off
REM Test de Flujos Críticos - PulseB2B
REM Ejecuta validación completa del sistema y genera informe para Instagram

echo ========================================
echo 🚀 PULSEB2B - TEST FLUJOS CRÍTICOS
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no instalado
    pause
    exit /b 1
)

echo ✅ Python instalado
echo.

REM Check dependencies
echo 📦 Verificando dependencias...
python -c "import sklearn; import numpy; import pandas" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Instalando dependencias...
    pip install -q scikit-learn numpy pandas
)
echo ✅ Dependencias OK
echo.

echo 🧪 Ejecutando tests de flujos críticos...
echo.

python test_critical_flows.py

if errorlevel 1 (
    echo.
    echo ❌ Algunos tests fallaron
    echo.
) else (
    echo.
    echo ✅ Tests completados exitosamente
    echo.
)

echo ========================================
echo 📱 INFORME PARA TELEGRAM
echo ========================================
echo.

if exist "data\output\telegram_report.txt" (
    type "data\output\telegram_report.txt"
    echo.
    echo ========================================
    echo.
    echo 💡 El informe está en: data\output\telegram_report.txt
    echo 📋 Puedes enviarlo directamente a tu canal de Telegram
    echo.
) else (
    echo ⚠️  No se generó el informe de Telegram
    echo.
)

pause
