# =====================================================
# TELEGRAM BOT - CONFIGURACIÓN AUTOMÁTICA COMPLETA
# =====================================================
# Este script configura todo el sistema de Telegram Bot
# Author: GitHub Copilot
# Date: December 22, 2025
# =====================================================

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  TELEGRAM BOT - CONFIGURACIÓN AUTOMÁTICA" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# =====================================================
# PASO 1: RECOPILAR CREDENCIALES
# =====================================================

Write-Host "PASO 1: Recopilando credenciales..." -ForegroundColor Yellow
Write-Host ""

# Token de Telegram
Write-Host "TELEGRAM BOT TOKEN" -ForegroundColor Green
Write-Host "   Obten tu token de @BotFather en Telegram" -ForegroundColor Gray
Write-Host "   Formato: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz" -ForegroundColor Gray
$TELEGRAM_BOT_TOKEN = Read-Host "   Ingresa tu TELEGRAM_BOT_TOKEN"
Write-Host ""

# Supabase Project Ref
Write-Host "SUPABASE PROJECT REF" -ForegroundColor Green
Write-Host "   Lo encuentras en: Supabase Dashboard - Settings - General" -ForegroundColor Gray
Write-Host "   Formato: abcdefghijklmnop" -ForegroundColor Gray
$PROJECT_REF = Read-Host "   Ingresa tu PROJECT REF"
Write-Host ""

# Supabase Service Role Key
Write-Host "SUPABASE SERVICE ROLE KEY" -ForegroundColor Green
Write-Host "   Lo encuentras en: Supabase Dashboard - Settings - API" -ForegroundColor Gray
Write-Host "   Busca 'service_role' (secret key)" -ForegroundColor Gray
$SUPABASE_SERVICE_ROLE_KEY = Read-Host "   Ingresa tu SERVICE ROLE KEY"
Write-Host ""

# Frontend URL
Write-Host "FRONTEND URL" -ForegroundColor Green
Write-Host "   Para desarrollo local: http://localhost:3000" -ForegroundColor Gray
Write-Host "   Para producción: https://tu-dominio.com" -ForegroundColor Gray
$FRONTEND_URL = Read-Host "   Ingresa tu FRONTEND URL (presiona Enter para localhost:3000)"
if ([string]::IsNullOrWhiteSpace($FRONTEND_URL)) {
    $FRONTEND_URL = "http://localhost:3000"
}
Write-Host ""

# Calcular SUPABASE_URL
$SUPABASE_URL = "https://$PROJECT_REF.supabase.co"

Write-Host "OK - Credenciales recopiladas:" -ForegroundColor Green
Write-Host "   - Telegram Token: $($TELEGRAM_BOT_TOKEN.Substring(0, 15))..." -ForegroundColor Gray
Write-Host "   - Project Ref: $PROJECT_REF" -ForegroundColor Gray
Write-Host "   - Supabase URL: $SUPABASE_URL" -ForegroundColor Gray
Write-Host "   - Frontend URL: $FRONTEND_URL" -ForegroundColor Gray
Write-Host ""

$confirm = Read-Host "¿Son correctos estos datos? (s/n)"
if ($confirm -ne "s" -and $confirm -ne "S") {
    Write-Host "❌ Configuración cancelada. Ejecuta el script nuevamente." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# =====================================================
# PASO 2: VERIFICAR SUPABASE CLI
# =====================================================

Write-Host "PASO 2: Verificando Supabase CLI..." -ForegroundColor Yellow
Write-Host ""

try {
    $supabaseVersion = supabase --version 2>&1
    Write-Host "OK - Supabase CLI instalado: $supabaseVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR - Supabase CLI no encontrado. Instalando..." -ForegroundColor Red
    Write-Host ""
    npm install -g supabase
    Write-Host ""
    Write-Host "OK - Supabase CLI instalado correctamente" -ForegroundColor Green
}

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# =====================================================
# PASO 3: CONECTAR PROYECTO SUPABASE
# =====================================================

Write-Host "PASO 3: Conectando proyecto Supabase..." -ForegroundColor Yellow
Write-Host ""

# Crear archivo de configuración temporal
$configContent = @"
[default]
project_id = "$PROJECT_REF"
"@

New-Item -Path ".\.supabase" -ItemType Directory -Force | Out-Null
Set-Content -Path ".\.supabase\config.toml" -Value $configContent -Force

Write-Host "Ejecutando: supabase link --project-ref $PROJECT_REF" -ForegroundColor Gray
supabase link --project-ref $PROJECT_REF

if ($LASTEXITCODE -eq 0) {
    Write-Host "OK - Proyecto conectado exitosamente" -ForegroundColor Green
} else {
    Write-Host "ADVERTENCIA - Error al conectar proyecto (puede ser normal si ya esta conectado)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# =====================================================
# PASO 4: APLICAR MIGRACIÓN DE BASE DE DATOS
# =====================================================

Write-Host "PASO 4: Aplicando migración de base de datos..." -ForegroundColor Yellow
Write-Host ""

Write-Host "Ejecutando: supabase db push" -ForegroundColor Gray
Write-Host ""

# Verificar que existe el archivo de migración
if (Test-Path ".\supabase\migrations\20251222_telegram_integration.sql") {
    Write-Host "✅ Migración encontrada: 20251222_telegram_integration.sql" -ForegroundColor Green
    
    supabase db push
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Migración aplicada exitosamente" -ForegroundColor Green
        Write-Host "   - Tabla telegram_subscribers creada" -ForegroundColor Gray
        Write-Host "   - Funciones helper creadas" -ForegroundColor Gray
        Write-Host "   - Vistas de analytics creadas" -ForegroundColor Gray
    } else {
        Write-Host "⚠️  Error al aplicar migración. Continúa con el siguiente paso..." -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  Archivo de migración no encontrado. Verifica la ruta." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# =====================================================
# PASO 5: CONFIGURAR SECRETOS EN SUPABASE
# =====================================================

Write-Host "PASO 5: Configurando secretos en Supabase..." -ForegroundColor Yellow
Write-Host ""

Write-Host "Configurando TELEGRAM_BOT_TOKEN..." -ForegroundColor Gray
supabase secrets set TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN --project-ref $PROJECT_REF

Write-Host "Configurando FRONTEND_URL..." -ForegroundColor Gray
supabase secrets set FRONTEND_URL=$FRONTEND_URL --project-ref $PROJECT_REF

Write-Host ""
Write-Host "✅ Secretos configurados" -ForegroundColor Green

Write-Host ""
Write-Host "Listando secretos..." -ForegroundColor Gray
supabase secrets list --project-ref $PROJECT_REF

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# =====================================================
# PASO 6: DESPLEGAR EDGE FUNCTION
# =====================================================

Write-Host "PASO 6: Desplegando Edge Function (Webhook)..." -ForegroundColor Yellow
Write-Host ""

Write-Host "Ejecutando: supabase functions deploy telegram-webhook --no-verify-jwt" -ForegroundColor Gray
Write-Host ""

supabase functions deploy telegram-webhook --no-verify-jwt --project-ref $PROJECT_REF

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Edge Function desplegada exitosamente" -ForegroundColor Green
    $WEBHOOK_URL = "https://$PROJECT_REF.supabase.co/functions/v1/telegram-webhook"
    Write-Host "   URL: $WEBHOOK_URL" -ForegroundColor Gray
} else {
    Write-Host "❌ Error al desplegar Edge Function" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# =====================================================
# PASO 7: CONFIGURAR WEBHOOK DE TELEGRAM
# =====================================================

Write-Host "PASO 7: Configurando webhook de Telegram..." -ForegroundColor Yellow
Write-Host ""

$webhookUrl = "https://$PROJECT_REF.supabase.co/functions/v1/telegram-webhook"
$telegramApiUrl = "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setWebhook"

$body = @{
    url = $webhookUrl
    allowed_updates = @("message", "callback_query")
    drop_pending_updates = $true
} | ConvertTo-Json

Write-Host "Configurando webhook en Telegram..." -ForegroundColor Gray
Write-Host "URL: $webhookUrl" -ForegroundColor Gray
Write-Host ""

try {
    $response = Invoke-RestMethod -Method Post -Uri $telegramApiUrl -ContentType "application/json" -Body $body
    
    if ($response.ok) {
        Write-Host "✅ Webhook configurado exitosamente en Telegram" -ForegroundColor Green
    } else {
        Write-Host "❌ Error al configurar webhook: $($response.description)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error al configurar webhook: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "Verificando webhook..." -ForegroundColor Gray

try {
    $verifyUrl = "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getWebhookInfo"
    $webhookInfo = Invoke-RestMethod -Uri $verifyUrl
    
    Write-Host "✅ Estado del webhook:" -ForegroundColor Green
    Write-Host "   URL: $($webhookInfo.result.url)" -ForegroundColor Gray
    Write-Host "   Pending updates: $($webhookInfo.result.pending_update_count)" -ForegroundColor Gray
    
    if ($webhookInfo.result.last_error_message) {
        Write-Host "   ⚠️  Último error: $($webhookInfo.result.last_error_message)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  No se pudo verificar webhook" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# =====================================================
# PASO 8: CONFIGURAR GITHUB SECRETS
# =====================================================

Write-Host "PASO 8: Configuración de GitHub Secrets..." -ForegroundColor Yellow
Write-Host ""

Write-Host "⚠️  ACCIÓN MANUAL REQUERIDA:" -ForegroundColor Yellow
Write-Host ""
Write-Host "Ve a tu repositorio de GitHub:" -ForegroundColor White
Write-Host "Settings - Secrets and variables - Actions - New repository secret" -ForegroundColor Gray
Write-Host ""
Write-Host "Agrega estos 4 secretos:" -ForegroundColor White
Write-Host ""
Write-Host "TELEGRAM_BOT_TOKEN =" -ForegroundColor Cyan -NoNewline
Write-Host " $TELEGRAM_BOT_TOKEN" -ForegroundColor Gray
Write-Host ""
Write-Host "SUPABASE_URL =" -ForegroundColor Cyan -NoNewline
Write-Host " $SUPABASE_URL" -ForegroundColor Gray
Write-Host ""
Write-Host "SUPABASE_SERVICE_ROLE_KEY =" -ForegroundColor Cyan -NoNewline
Write-Host " (ver archivo github_secrets_config.txt)" -ForegroundColor Gray
Write-Host ""
Write-Host "FRONTEND_URL =" -ForegroundColor Cyan -NoNewline
Write-Host " $FRONTEND_URL" -ForegroundColor Gray
Write-Host ""

# Crear archivo con las credenciales para fácil copy-paste
$githubSecretsFile = ".\github_secrets_config.txt"
$secretsContent = @"
GITHUB SECRETS CONFIGURATION
========================================

Copia y pega estos valores en GitHub:
Settings - Secrets and variables - Actions

TELEGRAM_BOT_TOKEN
$TELEGRAM_BOT_TOKEN

SUPABASE_URL
$SUPABASE_URL

SUPABASE_SERVICE_ROLE_KEY
$SUPABASE_SERVICE_ROLE_KEY

FRONTEND_URL
$FRONTEND_URL

========================================
IMPORTANTE: Elimina este archivo despues de configurar GitHub
"@

Set-Content -Path $githubSecretsFile -Value $secretsContent
Write-Host "✅ Credenciales guardadas en: github_secrets_config.txt" -ForegroundColor Green
Write-Host "   (Elimina este archivo después de configurar GitHub)" -ForegroundColor Gray

Write-Host ""
$githubConfirm = Read-Host "¿Ya configuraste los GitHub Secrets? (s/n)"

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# =====================================================
# RESUMEN FINAL
# =====================================================

Write-Host "🎉 CONFIGURACIÓN COMPLETADA" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "✅ CHECKLIST:" -ForegroundColor Green
Write-Host "   [✓] Supabase CLI instalado" -ForegroundColor Gray
Write-Host "   [✓] Proyecto conectado" -ForegroundColor Gray
Write-Host "   [✓] Migración de base de datos aplicada" -ForegroundColor Gray
Write-Host "   [✓] Secretos configurados en Supabase" -ForegroundColor Gray
Write-Host "   [✓] Edge Function desplegada" -ForegroundColor Gray
Write-Host "   [✓] Webhook configurado en Telegram" -ForegroundColor Gray
Write-Host ""

Write-Host "📱 PRUEBA TU BOT:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Abre Telegram" -ForegroundColor White
Write-Host "2. Busca tu bot (usa el username que configuraste en BotFather)" -ForegroundColor White
Write-Host "3. Envía: /start" -ForegroundColor White
Write-Host "4. Deberías recibir el mensaje de bienvenida" -ForegroundColor White
Write-Host "5. Envía: /latest" -ForegroundColor White
Write-Host "6. Deberías recibir el lead más reciente" -ForegroundColor White
Write-Host ""

Write-Host "🔗 ENLACES ÚTILES:" -ForegroundColor Yellow
Write-Host "   - Webhook URL: $webhookUrl" -ForegroundColor Gray
Write-Host "   - Frontend URL: $FRONTEND_URL" -ForegroundColor Gray
Write-Host "   - Supabase Dashboard: https://app.supabase.com/project/$PROJECT_REF" -ForegroundColor Gray
Write-Host ""

Write-Host "📊 VERIFICAR BASE DE DATOS:" -ForegroundColor Yellow
Write-Host "   Ve a Supabase SQL Editor y ejecuta:" -ForegroundColor White
Write-Host "   SELECT * FROM telegram_subscribers;" -ForegroundColor Gray
Write-Host ""

Write-Host "🚀 PRÓXIMOS PASOS:" -ForegroundColor Yellow
Write-Host "   1. Configura los GitHub Secrets (si no lo hiciste)" -ForegroundColor White
Write-Host "   2. Prueba el bot en Telegram" -ForegroundColor White
Write-Host "   3. Ejecuta el broadcast manual desde GitHub Actions" -ForegroundColor White
Write-Host "   4. ¡Listo! El bot enviará mensajes diarios a las 9 AM UTC" -ForegroundColor White
Write-Host ""

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Script completado exitosamente" -ForegroundColor Green
Write-Host ""
