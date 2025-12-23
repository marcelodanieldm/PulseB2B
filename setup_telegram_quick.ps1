# TELEGRAM BOT - CONFIGURACION AUTOMATICA
# =======================================

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  TELEGRAM BOT - CONFIGURACION AUTOMATICA" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# PASO 1: RECOPILAR CREDENCIALES
Write-Host "PASO 1: Recopilando credenciales..." -ForegroundColor Yellow
Write-Host ""

Write-Host "TELEGRAM BOT TOKEN" -ForegroundColor Green
Write-Host "   Obten tu token de @BotFather en Telegram" -ForegroundColor Gray
$TELEGRAM_BOT_TOKEN = Read-Host "   Ingresa tu TELEGRAM_BOT_TOKEN"
Write-Host ""

Write-Host "SUPABASE PROJECT REF" -ForegroundColor Green
Write-Host "   Lo encuentras en: Supabase Dashboard - Settings - General" -ForegroundColor Gray
$PROJECT_REF = Read-Host "   Ingresa tu PROJECT REF"
Write-Host ""

Write-Host "SUPABASE SERVICE ROLE KEY" -ForegroundColor Green
Write-Host "   Lo encuentras en: Supabase Dashboard - Settings - API" -ForegroundColor Gray
$SUPABASE_SERVICE_ROLE_KEY = Read-Host "   Ingresa tu SERVICE ROLE KEY"
Write-Host ""

Write-Host "FRONTEND URL" -ForegroundColor Green
Write-Host "   Para desarrollo: http://localhost:3000" -ForegroundColor Gray
$FRONTEND_URL = Read-Host "   Ingresa tu FRONTEND URL (Enter = localhost:3000)"
if ([string]::IsNullOrWhiteSpace($FRONTEND_URL)) {
    $FRONTEND_URL = "http://localhost:3000"
}
Write-Host ""

$SUPABASE_URL = "https://$PROJECT_REF.supabase.co"

Write-Host "[OK] Credenciales recopiladas:" -ForegroundColor Green
Write-Host "   - Telegram Token: $($TELEGRAM_BOT_TOKEN.Substring(0, 15))..." -ForegroundColor Gray
Write-Host "   - Project Ref: $PROJECT_REF" -ForegroundColor Gray
Write-Host "   - Supabase URL: $SUPABASE_URL" -ForegroundColor Gray
Write-Host "   - Frontend URL: $FRONTEND_URL" -ForegroundColor Gray
Write-Host ""

$confirm = Read-Host "Son correctos estos datos? (s/n)"
if ($confirm -ne "s" -and $confirm -ne "S") {
    Write-Host "[ERROR] Configuracion cancelada" -ForegroundColor Red
    exit 1
}

Write-Host ""

# PASO 2: CONFIGURAR WEBHOOK DE TELEGRAM
Write-Host "PASO 2: Configurando webhook de Telegram..." -ForegroundColor Yellow
Write-Host ""

$webhookUrl = "https://$PROJECT_REF.supabase.co/functions/v1/telegram-webhook"
$telegramApiUrl = "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setWebhook"

$body = @{
    url = $webhookUrl
    allowed_updates = @("message", "callback_query")
    drop_pending_updates = $true
} | ConvertTo-Json

Write-Host "URL del webhook: $webhookUrl" -ForegroundColor Gray

try {
    $response = Invoke-RestMethod -Method Post -Uri $telegramApiUrl -ContentType "application/json" -Body $body
    
    if ($response.ok) {
        Write-Host "[OK] Webhook configurado exitosamente" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Error al configurar webhook: $($response.description)" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "[ERROR] Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Verificar webhook
Write-Host "Verificando webhook..." -ForegroundColor Gray
$verifyUrl = "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getWebhookInfo"
$webhookInfo = Invoke-RestMethod -Uri $verifyUrl

Write-Host "[OK] Webhook activo:" -ForegroundColor Green
Write-Host "   URL: $($webhookInfo.result.url)" -ForegroundColor Gray
Write-Host "   Updates pendientes: $($webhookInfo.result.pending_update_count)" -ForegroundColor Gray

Write-Host ""

# PASO 3: GUARDAR CONFIGURACION
Write-Host "PASO 3: Guardando configuracion..." -ForegroundColor Yellow
Write-Host ""

$configContent = @"
TELEGRAM BOT CONFIGURATION
===========================

Bot Token: $TELEGRAM_BOT_TOKEN
Project Ref: $PROJECT_REF
Supabase URL: $SUPABASE_URL
Frontend URL: $FRONTEND_URL
Webhook URL: $webhookUrl

GITHUB SECRETS
==============
Configura estos secretos en GitHub:
Settings - Secrets and variables - Actions

TELEGRAM_BOT_TOKEN = $TELEGRAM_BOT_TOKEN
SUPABASE_URL = $SUPABASE_URL
SUPABASE_SERVICE_ROLE_KEY = $SUPABASE_SERVICE_ROLE_KEY
FRONTEND_URL = $FRONTEND_URL

SUPABASE SECRETS
================
Ejecuta estos comandos:

supabase secrets set TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN --project-ref $PROJECT_REF
supabase secrets set FRONTEND_URL=$FRONTEND_URL --project-ref $PROJECT_REF

DEPLOYMENT COMMANDS
===================

# Conectar proyecto
supabase link --project-ref $PROJECT_REF

# Aplicar migracion
supabase db push

# Desplegar Edge Function
supabase functions deploy telegram-webhook --no-verify-jwt --project-ref $PROJECT_REF

===========================
ELIMINA ESTE ARCHIVO DESPUES DE USAR
"@

$configFile = ".\telegram_config.txt"
Set-Content -Path $configFile -Value $configContent

Write-Host "[OK] Configuracion guardada en: telegram_config.txt" -ForegroundColor Green
Write-Host ""

# RESUMEN FINAL
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  CONFIGURACION COMPLETADA" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "PROXIMOS PASOS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Instalar Supabase CLI (si no lo tienes):" -ForegroundColor White
Write-Host "   npm install -g supabase" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Conectar proyecto:" -ForegroundColor White
Write-Host "   supabase link --project-ref $PROJECT_REF" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Aplicar migracion:" -ForegroundColor White
Write-Host "   supabase db push" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Configurar secretos en Supabase:" -ForegroundColor White
Write-Host "   supabase secrets set TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN --project-ref $PROJECT_REF" -ForegroundColor Gray
Write-Host "   supabase secrets set FRONTEND_URL=$FRONTEND_URL --project-ref $PROJECT_REF" -ForegroundColor Gray
Write-Host ""
Write-Host "5. Desplegar Edge Function:" -ForegroundColor White
Write-Host "   supabase functions deploy telegram-webhook --no-verify-jwt --project-ref $PROJECT_REF" -ForegroundColor Gray
Write-Host ""
Write-Host "6. Configurar GitHub Secrets (ver telegram_config.txt)" -ForegroundColor White
Write-Host ""
Write-Host "7. Probar el bot en Telegram:" -ForegroundColor White
Write-Host "   - Busca tu bot" -ForegroundColor Gray
Write-Host "   - Envia: /start" -ForegroundColor Gray
Write-Host "   - Envia: /latest" -ForegroundColor Gray
Write-Host ""

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Webhook configurado y listo!" -ForegroundColor Green
Write-Host "Revisa telegram_config.txt para los siguientes pasos" -ForegroundColor Green
Write-Host ""
