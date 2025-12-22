@echo off
REM Setup script for PulseB2B Global Dashboard (Windows)

echo 🚀 Setting up PulseB2B Global Dashboard...

REM Check Node.js
echo 📦 Checking Node.js version...
node --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Node.js not found. Please install Node.js 18+ from https://nodejs.org
    exit /b 1
)

echo ✅ Node.js version OK
node --version

REM Navigate to frontend
cd frontend
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Frontend directory not found
    exit /b 1
)

REM Install dependencies
echo 📥 Installing dependencies...
call npm install

REM Create .env.local
if not exist .env.local (
    echo 📝 Creating .env.local from template...
    copy .env.example .env.local
    echo.
    echo ⚠️  IMPORTANT: Edit .env.local with your Supabase credentials!
    echo.
    echo You need to add:
    echo   - NEXT_PUBLIC_SUPABASE_URL (from Supabase Settings → API)
    echo   - NEXT_PUBLIC_SUPABASE_ANON_KEY (from Supabase Settings → API)
    echo.
)

REM Ask about Vercel CLI
echo.
set /p INSTALL_VERCEL="📦 Install Vercel CLI for deployment? (y/n): "
if /i "%INSTALL_VERCEL%"=="y" (
    call npm install -g vercel
    echo ✅ Vercel CLI installed
)

echo.
echo ✅ Setup complete!
echo.
echo Next steps:
echo 1. Edit frontend\.env.local with your Supabase credentials
echo 2. Run 'cd frontend && npm run dev' to start development server
echo 3. Visit http://localhost:3000/dashboard
echo.
echo 📖 Documentation:
echo   - Dashboard README: frontend\README_DASHBOARD.md
echo   - Deployment guide: frontend\DEPLOYMENT.md
echo   - Complete guide: frontend\IMPLEMENTATION_COMPLETE.md
echo.
echo 🚀 Ready to deploy? Run 'cd frontend && vercel --prod'

pause
