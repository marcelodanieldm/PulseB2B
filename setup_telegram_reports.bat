@echo off
REM Configurador Interactivo de Telegram Bot
REM Guía paso a paso para configurar y probar el bot

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  🤖 CONFIGURADOR DE BOT DE TELEGRAM - PULSEB2B            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no instalado
    echo.
    echo Instalar desde: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python instalado
echo.

REM Step 1: Create Bot
echo ════════════════════════════════════════════════════════════
echo PASO 1: CREAR BOT DE TELEGRAM
echo ════════════════════════════════════════════════════════════
echo.
echo 📱 Abre Telegram en tu móvil/PC y sigue estos pasos:
echo.
echo    1. Busca el contacto: @BotFather
echo    2. Envía el comando: /newbot
echo    3. Responde con el nombre del bot: PulseB2B Reports
echo    4. Responde con el username: pulseb2b_reports_bot
echo       (o el que prefieras, debe terminar en _bot)
echo.
echo 🔑 @BotFather te dará un TOKEN como este:
echo    123456789:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890
echo.
set /p BOT_TOKEN="📋 Pega aquí el TOKEN del bot: "

if "%BOT_TOKEN%"=="" (
    echo.
    echo ❌ Error: No ingresaste el token
    pause
    exit /b 1
)

echo.
echo ✅ Token guardado temporalmente
echo.

REM Step 2: Get Chat ID
echo ════════════════════════════════════════════════════════════
echo PASO 2: OBTENER TU CHAT ID
echo ════════════════════════════════════════════════════════════
echo.
echo 📱 En Telegram:
echo.
echo    1. Busca el contacto: @userinfobot
echo    2. Envía el comando: /start
echo    3. El bot te responderá con tu ID (número de 9-10 dígitos)
echo.
echo 💡 Si quieres enviar a un GRUPO/CANAL:
echo    1. Agrega tu bot al grupo/canal
echo    2. Busca @myidbot y agrégalo también
echo    3. El bot te dará el ID del grupo (número negativo)
echo.
set /p CHAT_ID="📋 Pega aquí tu CHAT ID: "

if "%CHAT_ID%"=="" (
    echo.
    echo ❌ Error: No ingresaste el chat ID
    pause
    exit /b 1
)

echo.
echo ✅ Chat ID guardado
echo.

REM Step 3: Install dependencies
echo ════════════════════════════════════════════════════════════
echo PASO 3: INSTALAR DEPENDENCIAS
echo ════════════════════════════════════════════════════════════
echo.
echo 📦 Instalando python-telegram-bot...
echo.

pip install python-telegram-bot >nul 2>&1

if errorlevel 1 (
    echo ⚠️  Instalación con warnings, intentando sin caché...
    pip install --no-cache-dir python-telegram-bot
)

echo.
echo ✅ Dependencias instaladas
echo.

REM Step 4: Save configuration
echo ════════════════════════════════════════════════════════════
echo PASO 4: GUARDAR CONFIGURACIÓN
echo ════════════════════════════════════════════════════════════
echo.

REM Create .env file
echo TELEGRAM_BOT_TOKEN=%BOT_TOKEN% > .env
echo TELEGRAM_CHAT_ID=%CHAT_ID% >> .env

echo ✅ Configuración guardada en .env
echo.

REM Create PowerShell profile configuration
echo # Telegram Bot Configuration - PulseB2B > telegram_config.ps1
echo $env:TELEGRAM_BOT_TOKEN="%BOT_TOKEN%" >> telegram_config.ps1
echo $env:TELEGRAM_CHAT_ID="%CHAT_ID%" >> telegram_config.ps1

echo ✅ Script de configuración creado: telegram_config.ps1
echo.

REM Create batch configuration
echo @echo off > set_telegram_env.bat
echo REM Configurar variables de entorno de Telegram >> set_telegram_env.bat
echo set TELEGRAM_BOT_TOKEN=%BOT_TOKEN% >> set_telegram_env.bat
echo set TELEGRAM_CHAT_ID=%CHAT_ID% >> set_telegram_env.bat
echo echo ✅ Variables de entorno configuradas >> set_telegram_env.bat

echo ✅ Script de configuración creado: set_telegram_env.bat
echo.

REM Step 5: Test connection
echo ════════════════════════════════════════════════════════════
echo PASO 5: PROBAR CONEXIÓN
echo ════════════════════════════════════════════════════════════
echo.

set /p TEST_SEND="¿Deseas enviar un mensaje de prueba ahora? (S/N): "

if /i "%TEST_SEND%"=="S" (
    echo.
    echo 📤 Enviando mensaje de prueba...
    echo.
    
    REM Set environment variables for this session
    set TELEGRAM_BOT_TOKEN=%BOT_TOKEN%
    set TELEGRAM_CHAT_ID=%CHAT_ID%
    
    REM Create test script
    echo import asyncio > test_telegram_connection.py
    echo from telegram import Bot >> test_telegram_connection.py
    echo import os >> test_telegram_connection.py
    echo. >> test_telegram_connection.py
    echo async def test(): >> test_telegram_connection.py
    echo     bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN')) >> test_telegram_connection.py
    echo     await bot.send_message( >> test_telegram_connection.py
    echo         chat_id=os.getenv('TELEGRAM_CHAT_ID'), >> test_telegram_connection.py
    echo         text='🤖 ^<b^>Conexión exitosa!^</b^>\n\nTu bot de PulseB2B está configurado correctamente.\n\n✅ Listo para recibir informes automáticos.', >> test_telegram_connection.py
    echo         parse_mode='HTML' >> test_telegram_connection.py
    echo     ) >> test_telegram_connection.py
    echo     print('✅ Mensaje enviado con éxito!') >> test_telegram_connection.py
    echo. >> test_telegram_connection.py
    echo asyncio.run(test()) >> test_telegram_connection.py
    
    python test_telegram_connection.py
    
    if errorlevel 1 (
        echo.
        echo ❌ Error al enviar mensaje
        echo.
        echo 💡 Verifica:
        echo    - Token correcto
        echo    - Chat ID correcto
        echo    - Bot iniciado con /start
        echo.
    ) else (
        echo.
        echo ✅ ¡Mensaje enviado! Revisa tu Telegram
        echo.
    )
    
    del test_telegram_connection.py >nul 2>&1
)

echo.
echo ════════════════════════════════════════════════════════════
echo ✅ CONFIGURACIÓN COMPLETA
echo ════════════════════════════════════════════════════════════
echo.
echo 📋 Archivos creados:
echo    • .env - Variables de entorno
echo    • telegram_config.ps1 - Para PowerShell
echo    • set_telegram_env.bat - Para CMD
echo.
echo 🚀 Próximos pasos:
echo.
echo    1. Ejecutar tests y enviar informe:
echo       ^> send_telegram_report.bat
echo.
echo    2. O enviar directamente:
echo       ^> python send_to_telegram.py
echo.
echo    3. Enviar informe detallado:
echo       ^> python send_to_telegram.py --detailed
echo.
echo 💡 Para usar en nuevas sesiones:
echo    CMD: call set_telegram_env.bat
echo    PowerShell: . .\telegram_config.ps1
echo.
pause
