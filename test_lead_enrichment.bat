@echo off
REM Quick test script for Lead Enrichment System
REM Tests all 3 core services with mock data

echo.
echo ============================================================
echo  LEAD ENRICHMENT SYSTEM - QUICK TEST
echo ============================================================
echo.

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js is not installed!
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist .env (
    echo [WARNING] .env file not found!
    echo Create .env file with Supabase and API credentials
    echo.
    pause
)

echo [1/3] Testing Company Enrichment Service...
echo ============================================================
echo.
echo Testing with domain: stripe.com
echo.
node scripts\lead_enrichment_service.js domain stripe.com
echo.
echo Press any key to continue to scoring test...
pause >nul

echo.
echo.
echo [2/3] Testing Lead Scoring Engine...
echo ============================================================
echo.
echo Testing with mock user data
echo.
node scripts\lead_scoring_engine.js test
echo.
echo Press any key to continue to alert test...
pause >nul

echo.
echo.
echo [3/3] Testing Telegram Alert Service...
echo ============================================================
echo.
echo Testing with mock high-value prospect
echo.
node scripts\telegram_alert_service.js test
echo.

echo.
echo ============================================================
echo  TEST COMPLETE!
echo ============================================================
echo.
echo Next Steps:
echo   1. Configure .env file with API keys
echo   2. Run database migration: supabase db push
echo   3. Enrich real user: node scripts\lead_enrichment_service.js enrich USER_ID EMAIL
echo   4. Start webhook server: node scripts\signup_webhook.js
echo.
echo Documentation: LEAD_ENRICHMENT_SYSTEM.md
echo.
pause
