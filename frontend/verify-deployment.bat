@echo off
REM PulseB2B - Pre-Deployment Verification Script (Windows)
REM Run this before deploying to Vercel to catch issues early

setlocal enabledelayedexpansion

echo ========================================
echo    PulseB2B Pre-Deployment Verification
echo ========================================
echo.

set ERRORS=0
set WARNINGS=0
set PASSED=0

REM Check if we're in frontend directory
if not exist "package.json" (
    echo [ERROR] package.json not found
    echo Please run this script from the frontend directory
    exit /b 1
)

echo ======== Step 1: Checking Dependencies ========
echo.

REM Check Node version
for /f "tokens=1 delims=v" %%a in ('node -v') do set NODE_VERSION=%%a
echo [OK] Node.js version: %NODE_VERSION%
set /a PASSED+=1

REM Check npm version
for /f %%a in ('npm -v') do set NPM_VERSION=%%a
echo [OK] npm version: %NPM_VERSION%
set /a PASSED+=1

REM Check if node_modules exists
if exist "node_modules" (
    echo [OK] node_modules directory exists
    set /a PASSED+=1
) else (
    echo [ERROR] node_modules not found. Run: npm install
    set /a ERRORS+=1
)

echo.
echo ======== Step 2: Checking Environment Variables ========
echo.

REM Check .env.local exists
if exist ".env.local" (
    echo [OK] .env.local file found
    set /a PASSED+=1
    
    REM Read environment variables
    for /f "usebackq tokens=1,2 delims==" %%a in (".env.local") do (
        if "%%a"=="NEXT_PUBLIC_SUPABASE_URL" (
            echo [OK] NEXT_PUBLIC_SUPABASE_URL is set
            set /a PASSED+=1
        )
        if "%%a"=="NEXT_PUBLIC_SUPABASE_ANON_KEY" (
            echo [OK] NEXT_PUBLIC_SUPABASE_ANON_KEY is set
            set /a PASSED+=1
        )
        if "%%a"=="NEXT_PUBLIC_MAPBOX_TOKEN" (
            echo [OK] NEXT_PUBLIC_MAPBOX_TOKEN is set
            set /a PASSED+=1
        )
        if "%%a"=="NEXT_PUBLIC_STRIPE_PAYMENT_LINK" (
            echo [OK] NEXT_PUBLIC_STRIPE_PAYMENT_LINK is set
            set /a PASSED+=1
        )
    )
) else (
    echo [ERROR] .env.local file not found
    echo    Copy .env.example to .env.local and fill in your values
    set /a ERRORS+=1
)

echo.
echo ======== Step 3: TypeScript Type Checking ========
echo.

npm run type-check >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo [OK] TypeScript compilation successful
    set /a PASSED+=1
) else (
    echo [ERROR] TypeScript compilation failed
    echo    Run: npm run type-check to see errors
    set /a ERRORS+=1
)

echo.
echo ======== Step 4: Build Test ========
echo.

echo Building production bundle... (this may take 30-60 seconds)
npm run build >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo [OK] Production build successful
    set /a PASSED+=1
) else (
    echo [ERROR] Production build failed
    echo    Run: npm run build to see errors
    set /a ERRORS+=1
)

echo.
echo ======== Step 5: Required Files Check ========
echo.

REM Check critical files
set FILES=src\app\page.tsx src\app\layout.tsx src\components\GlobalSignalMap.tsx src\components\PremiumPaywall.tsx src\lib\supabase.ts src\lib\utils.ts src\types\index.ts next.config.js tailwind.config.ts tsconfig.json vercel.json

for %%f in (%FILES%) do (
    if exist "%%f" (
        echo [OK] %%f
        set /a PASSED+=1
    ) else (
        echo [ERROR] %%f is missing
        set /a ERRORS+=1
    )
)

echo.
echo ======== Step 6: Configuration Validation ========
echo.

REM Check vercel.json exists
if exist "vercel.json" (
    echo [OK] vercel.json exists
    set /a PASSED+=1
) else (
    echo [WARNING] vercel.json not found (optional)
    set /a WARNINGS+=1
)

REM Check package.json scripts
findstr /C:"\"build\": \"next build\"" package.json >nul
if %ERRORLEVEL% equ 0 (
    echo [OK] Build script configured
    set /a PASSED+=1
) else (
    echo [WARNING] Build script may not be standard
    set /a WARNINGS+=1
)

findstr /C:"\"start\": \"next start\"" package.json >nul
if %ERRORLEVEL% equ 0 (
    echo [OK] Start script configured
    set /a PASSED+=1
) else (
    echo [WARNING] Start script may not be standard
    set /a WARNINGS+=1
)

echo.
echo ========================================
echo     Verification Summary
echo ========================================
echo Passed: %PASSED%
echo Warnings: %WARNINGS%
echo Errors: %ERRORS%
echo.

if %ERRORS% equ 0 (
    echo [SUCCESS] All critical checks passed!
    echo.
    echo Ready to deploy to Vercel!
    echo.
    echo Next steps:
    echo 1. Commit your changes: git add . ^&^& git commit -m "feat: Premium dashboard ready"
    echo 2. Push to GitHub: git push origin main
    echo 3. Deploy to Vercel:
    echo    - Option A: Connect GitHub repo in Vercel Dashboard
    echo    - Option B: Run 'vercel --prod' (requires Vercel CLI)
    echo.
    echo Don't forget to add environment variables in Vercel Dashboard!
    echo.
    exit /b 0
) else (
    echo [FAILED] Deployment blocked due to %ERRORS% error(s)
    echo.
    echo Please fix the errors above before deploying.
    echo.
    echo Common fixes:
    echo - Missing environment variables? Copy .env.example to .env.local
    echo - TypeScript errors? Run: npm run type-check
    echo - Build errors? Run: npm run build
    echo - Missing dependencies? Run: npm install
    echo.
    exit /b 1
)
