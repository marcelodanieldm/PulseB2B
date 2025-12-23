@echo off
REM Enviar Informe a Telegram - Windows
REM Ejecuta tests y envía resultados automáticamente a Telegram

echo ========================================
echo 📱 PULSEB2B - ENVIAR A TELEGRAM
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

REM Check if tests were run
if not exist "data\output\telegram_report.txt" (
    echo ⚠️  Ejecutando tests primero...
    echo.
    python test_critical_flows.py
    if errorlevel 1 (
        echo.
        echo ❌ Tests fallaron
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo 📤 ENVIANDO A TELEGRAM
echo ========================================
echo.

REM Ask which version to send
echo ¿Qué versión deseas enviar?
echo.
echo 1. Informe Simple (recomendado)
echo 2. Informe Detallado Completo
echo 3. Ambos
echo.
set /p OPCION="Selecciona (1/2/3): "

if "%OPCION%"=="1" (
    echo.
    echo 📤 Enviando informe simple...
    python send_to_telegram.py
) else if "%OPCION%"=="2" (
    echo.
    echo 📤 Enviando informe detallado...
    python send_to_telegram.py --detailed
) else if "%OPCION%"=="3" (
    echo.
    echo 📤 Enviando informe simple...
    python send_to_telegram.py
    echo.
    echo 📤 Enviando informe detallado...
    timeout /t 2 >nul
    python send_to_telegram.py --detailed
) else (
    echo.
    echo ❌ Opción inválida
    pause
    exit /b 1
)

echo.
echo ========================================
echo.

if errorlevel 1 (
    echo ❌ Error al enviar
    echo.
    echo 💡 Verifica tu configuración:
    echo    - TELEGRAM_BOT_TOKEN
    echo    - TELEGRAM_CHAT_ID
    echo.
    echo 📝 Edita send_to_telegram.py con tus datos
    echo    o configura variables de entorno:
    echo.
    echo    set TELEGRAM_BOT_TOKEN=tu-token
    echo    set TELEGRAM_CHAT_ID=tu-chat-id
    echo.
) else (
    echo ✅ Informe enviado exitosamente
    echo.
    echo 📱 Revisa tu Telegram para ver el mensaje
    echo.
)

pause
