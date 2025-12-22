@echo off
REM Gated Content Setup Script for Windows
REM Installs dependencies and configures environment

echo ================================
echo 🔐 PulseB2B Gated Content Setup
echo ================================
echo.

REM Navigate to frontend directory
cd frontend

echo 📦 Installing dependencies...
call npm install lucide-react @supabase/supabase-js framer-motion

echo.
echo ✅ Dependencies installed!
echo.

echo 🔧 Setup Instructions:
echo.
echo 1. Configure Environment Variables:
echo    Copy .env.example to .env.local and add:
echo    - NEXT_PUBLIC_SUPABASE_URL
echo    - NEXT_PUBLIC_SUPABASE_ANON_KEY
echo    - NEXT_PUBLIC_STRIPE_PAYMENT_LINK
echo.

echo 2. Update Supabase Schema:
echo    Run this SQL in Supabase SQL Editor:
echo    ALTER TABLE users ADD COLUMN IF NOT EXISTS is_premium BOOLEAN DEFAULT FALSE;
echo.

echo 3. Create Stripe Payment Link:
echo    - Go to Stripe Dashboard → Payment Links
echo    - Create product: 'PulseB2B Premium' at $99/month
echo    - Copy link to NEXT_PUBLIC_STRIPE_PAYMENT_LINK
echo.

echo 4. Start Development Server:
echo    npm run dev
echo.

echo 5. Test Gated Content:
echo    - Visit: http://localhost:3000/continental
echo    - Toggle premium in Supabase: UPDATE users SET is_premium = true WHERE email = 'your@email.com'
echo.

echo 🎉 Setup complete! Read GATED_CONTENT_IMPLEMENTATION.md for full documentation.

pause
