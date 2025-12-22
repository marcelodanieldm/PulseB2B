@echo off
REM Setup script for Ghost Infrastructure (Windows)

echo 🚀 Setting up Ghost Infrastructure...

REM Check Python version
echo 📦 Checking Python version...
python --version || (
    echo ❌ Python 3.9+ required
    exit /b 1
)

REM Create virtual environment
echo 🔧 Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

REM Install Python dependencies
echo 📥 Installing Python dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Download NLTK data
echo 📚 Downloading NLTK data for sentiment analysis...
python -c "import nltk; nltk.download('vader_lexicon'); nltk.download('punkt'); print('✅ NLTK data downloaded')"

REM Check for Supabase CLI
echo 🔍 Checking for Supabase CLI...
where supabase >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  Supabase CLI not found. Installing...
    npm install -g supabase
)

REM Verify installation
echo.
echo ✅ Setup complete!
echo.
echo Next steps:
echo 1. Create Supabase project at https://supabase.com
echo 2. Run database schema: supabase/schema.sql
echo 3. Deploy Edge Functions:
echo    supabase functions deploy news-webhook
echo    supabase functions deploy lead-scoring
echo 4. Add GitHub Secrets (SUPABASE_URL, SUPABASE_KEY)
echo 5. Trigger workflow: Actions → Ghost Pipeline → Run workflow
echo.
echo 📖 Full documentation: docs/QUICK_START_GHOST.md

pause
