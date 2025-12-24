# GitHub Actions Secrets Configuration
# Execute este script en PowerShell para configurar variables de entorno localmente

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   GitHub Actions Secrets Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# CRITICAL SECRETS (Requeridos)
Write-Host "CRITICAL SECRETS (Required):" -ForegroundColor Red

# CRITICAL SECRETS
Write-Host "CRITICAL SECRETS:" -ForegroundColor Yellow

# Token del bot de Telegram
$env:TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"
Write-Host "  Set: TELEGRAM_BOT_TOKEN" -ForegroundColor Green

# ID del chat de Telegram
$env:TELEGRAM_CHAT_ID = "YOUR_TELEGRAM_CHAT_ID_HERE"
Write-Host "  Set: TELEGRAM_CHAT_ID" -ForegroundColor Green

# URL de tu proyecto Supabase
$env:SUPABASE_URL = "YOUR_SUPABASE_URL_HERE"
Write-Host "  Set: SUPABASE_URL" -ForegroundColor Green

# Service key de Supabase
$env:SUPABASE_SERVICE_KEY = "YOUR_SUPABASE_SERVICE_KEY_HERE"
Write-Host "  Set: SUPABASE_SERVICE_KEY" -ForegroundColor Green

# IMPORTANT SECRETS
Write-Host "IMPORTANT SECRETS:" -ForegroundColor Yellow

# API key de Google Custom Search
$env:GOOGLE_CSE_API_KEY = "YOUR_GOOGLE_CSE_API_KEY_HERE"
Write-Host "  Set: GOOGLE_CSE_API_KEY" -ForegroundColor Green

# ID del Custom Search Engine
$env:GOOGLE_CSE_ID = "YOUR_GOOGLE_CSE_ID_HERE"
Write-Host "  Set: GOOGLE_CSE_ID" -ForegroundColor Green

# API key de SendGrid
$env:SENDGRID_API_KEY = "YOUR_SENDGRID_API_KEY_HERE"
Write-Host "  Set: SENDGRID_API_KEY" -ForegroundColor Green

# Usuario de email
$env:EMAIL_USERNAME = "YOUR_EMAIL_USERNAME_HERE"
Write-Host "  Set: EMAIL_USERNAME" -ForegroundColor Green

# Contraseña de email
$env:EMAIL_PASSWORD = "YOUR_EMAIL_PASSWORD_HERE"
Write-Host "  Set: EMAIL_PASSWORD" -ForegroundColor Green

# OPTIONAL SECRETS
Write-Host "OPTIONAL SECRETS:" -ForegroundColor Yellow

# API key de Clearbit
$env:CLEARBIT_API_KEY = "YOUR_CLEARBIT_API_KEY_HERE"
Write-Host "  Set: CLEARBIT_API_KEY" -ForegroundColor Green

# Webhook de Slack
$env:SLACK_WEBHOOK_URL = "YOUR_SLACK_WEBHOOK_URL_HERE"
Write-Host "  Set: SLACK_WEBHOOK_URL" -ForegroundColor Green

# Webhook de Discord
$env:DISCORD_WEBHOOK_URL = "YOUR_DISCORD_WEBHOOK_URL_HERE"
Write-Host "  Set: DISCORD_WEBHOOK_URL" -ForegroundColor Green

# Chat ID para alertas
$env:TELEGRAM_ALERT_CHAT_ID = "YOUR_TELEGRAM_ALERT_CHAT_ID_HERE"
Write-Host "  Set: TELEGRAM_ALERT_CHAT_ID" -ForegroundColor Green

# Anon key de Supabase
$env:SUPABASE_ANON_KEY = "YOUR_SUPABASE_ANON_KEY_HERE"
Write-Host "  Set: SUPABASE_ANON_KEY" -ForegroundColor Green

# Key alternativa de Supabase
$env:SUPABASE_KEY = "YOUR_SUPABASE_KEY_HERE"
Write-Host "  Set: SUPABASE_KEY" -ForegroundColor Green

# Service role key
$env:SUPABASE_SERVICE_ROLE_KEY = "YOUR_SUPABASE_SERVICE_ROLE_KEY_HERE"
Write-Host "  Set: SUPABASE_SERVICE_ROLE_KEY" -ForegroundColor Green

# Webhook URL genérico
$env:WEBHOOK_URL = "YOUR_WEBHOOK_URL_HERE"
Write-Host "  Set: WEBHOOK_URL" -ForegroundColor Green

# Email para alertas
$env:ALERT_EMAIL = "YOUR_ALERT_EMAIL_HERE"
Write-Host "  Set: ALERT_EMAIL" -ForegroundColor Green

# Email remitente
$env:FROM_EMAIL = "YOUR_FROM_EMAIL_HERE"
Write-Host "  Set: FROM_EMAIL" -ForegroundColor Green

# URL base de la aplicación
$env:BASE_URL = "YOUR_BASE_URL_HERE"
Write-Host "  Set: BASE_URL" -ForegroundColor Green

# URL del frontend
$env:FRONTEND_URL = "YOUR_FRONTEND_URL_HERE"
Write-Host "  Set: FRONTEND_URL" -ForegroundColor Green

# API key alternativa de Google
$env:GOOGLE_SEARCH_API_KEY = "YOUR_GOOGLE_SEARCH_API_KEY_HERE"
Write-Host "  Set: GOOGLE_SEARCH_API_KEY" -ForegroundColor Green

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   Configuration Complete!" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 Verify configuration:" -ForegroundColor Yellow
Write-Host "   python check_workflow_status.py" -ForegroundColor White
Write-Host ""
Write-Host "📚 Next steps:" -ForegroundColor Yellow
Write-Host "   1. Replace 'YOUR_*_HERE' with actual values" -ForegroundColor White
Write-Host "   2. Run this script: .\configure_secrets.ps1" -ForegroundColor White
Write-Host "   3. Configure same secrets in GitHub:" -ForegroundColor White
Write-Host "      Settings > Secrets and variables > Actions" -ForegroundColor White
