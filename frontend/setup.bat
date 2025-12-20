@echo off
REM PulseB2B Frontend Setup Script for Windows
REM Automatiza la instalación y configuración del dashboard

echo.
echo ============================================
echo   PulseB2B Frontend Setup
echo ============================================
echo.

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js is not installed
    echo Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)

echo [OK] Node.js detected: 
node --version

REM Check if npm is installed
where npm >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] npm is not installed
    pause
    exit /b 1
)

echo [OK] npm detected:
npm --version
echo.

REM Navigate to script directory
cd /d "%~dp0"

REM Install dependencies
echo.
echo Installing dependencies...
echo.
call npm install

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [OK] Dependencies installed successfully
echo.

REM Create .env.local if it doesn't exist
if not exist .env.local (
    echo Creating .env.local...
    copy .env.example .env.local
    echo.
    echo [WARNING] Please edit .env.local with your credentials:
    echo    - NEXT_PUBLIC_MAPBOX_TOKEN (required for map)
    echo    - NEXT_PUBLIC_SUPABASE_URL (optional - uses mock data if not set)
    echo    - NEXT_PUBLIC_SUPABASE_ANON_KEY (optional)
    echo.
) else (
    echo [OK] .env.local already exists
    echo.
)

REM Run type check
echo Running TypeScript type check...
call npm run type-check

if %ERRORLEVEL% EQU 0 (
    echo [OK] Type check passed
) else (
    echo [WARNING] Type check failed (this is okay for initial setup)
)

echo.
echo ============================================
echo   Setup complete!
echo ============================================
echo.
echo Next steps:
echo 1. Edit .env.local with your Mapbox token
echo 2. Run: npm run dev
echo 3. Open: http://localhost:3000
echo.
echo Documentation:
echo    - Quick Start: QUICK_START.md
echo    - Full Docs: README.md
echo.
echo Happy coding! 
echo.
pause
