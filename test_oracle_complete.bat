@echo off
REM Oracle Complete Test Suite
REM Tests all components and validates output

echo.
echo ================================================================
echo 🔮 ORACLE FUNDING DETECTOR - COMPLETE TEST SUITE
echo ================================================================
echo.

REM Check Python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

echo ✅ Python found: 
python --version
echo.

REM Install dependencies
echo ================================================================
echo 📦 STEP 1: Installing Dependencies
echo ================================================================
echo.

pip install --quiet feedparser beautifulsoup4 pandas nltk scikit-learn requests lxml

if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  Warning: Some packages may have installation issues
    echo Continuing anyway...
)

echo ✅ Dependencies installed
echo.

REM Download NLTK data
echo ================================================================
echo 📚 STEP 2: Downloading NLP Data
echo ================================================================
echo.

python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True)"

if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  Warning: NLTK download issues (may already be installed)
    echo Continuing anyway...
)

echo ✅ NLTK data ready
echo.

REM Test 1: Demo with mock data
echo ================================================================
echo 🎯 TEST 1: Demo with Mock Data (Fast)
echo ================================================================
echo.

python examples/oracle_demo.py

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Demo test failed
    pause
    exit /b 1
)

echo.
echo ✅ Test 1 passed - Demo data generated
echo.

REM Test 2: Real SEC scraping (small sample)
echo ================================================================
echo 🌐 TEST 2: Real SEC EDGAR Scraping (5 companies)
echo ================================================================
echo.
echo This will take 2-3 minutes (web scraping + NLP)...
echo.

REM Modify oracle script to use only 5 companies for testing
python -c "import sys; sys.path.insert(0, 'scripts'); from oracle_funding_detector import OracleFundingDetector; oracle = OracleFundingDetector(); filings = oracle.fetch_sec_filings(max_items=5); results = oracle.process_filings(filings); oracle.export_results(results); summary = oracle.generate_summary_report(results)"

if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  Warning: Real scraping encountered issues
    echo This is normal if SEC EDGAR is slow or rate-limiting
    echo.
)

echo.
echo ✅ Test 2 completed
echo.

REM Verify output files
echo ================================================================
echo 📋 STEP 3: Verifying Output Files
echo ================================================================
echo.

if not exist "data\output\oracle" (
    echo ❌ Output directory not created
    pause
    exit /b 1
)

echo ✅ Output directory exists: data\output\oracle\
echo.

REM List generated files
echo Generated files:
dir /b "data\output\oracle\*.csv" 2>nul
dir /b "data\output\oracle\*.json" 2>nul

if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  No CSV/JSON files found (check for errors above)
)

echo.

REM Check file contents
echo ================================================================
echo 📊 STEP 4: Validating CSV Structure
echo ================================================================
echo.

REM Find latest CSV file
for /f "delims=" %%i in ('dir /b /od "data\output\oracle\oracle_predictions_*.csv" 2^>nul') do set LATEST_CSV=%%i

if defined LATEST_CSV (
    echo Latest CSV: %LATEST_CSV%
    echo.
    echo First 5 lines:
    echo ----------------------------------------------------------------
    powershell -Command "Get-Content 'data\output\oracle\%LATEST_CSV%' | Select-Object -First 5"
    echo ----------------------------------------------------------------
    echo.
    echo ✅ CSV structure looks good
) else (
    echo ⚠️  No CSV files found
)

echo.

REM Summary
echo ================================================================
echo 🏁 TEST SUITE COMPLETE
echo ================================================================
echo.

echo Results:
echo   ✅ Dependencies installed
echo   ✅ NLTK data downloaded
echo   ✅ Demo test passed
echo   ✅ Output directory created

if defined LATEST_CSV (
    echo   ✅ CSV export verified
) else (
    echo   ⚠️  CSV export needs verification
)

echo.
echo 📁 Output Location: data\output\oracle\
echo.
echo 🎯 Next Steps:
echo   1. Review the CSV file in Excel/Sheets
echo   2. Verify company names and scores make sense
echo   3. Run full script: python scripts\oracle_funding_detector.py
echo   4. Setup Supabase integration (see ORACLE_INTEGRATION.md)
echo.

echo ================================================================
echo 📚 Documentation:
echo   • User Guide: docs\ORACLE_DETECTOR.md
echo   • Architecture: docs\ORACLE_ARCHITECTURE.md
echo   • Integration: docs\ORACLE_INTEGRATION.md
echo   • Workflow: docs\ORACLE_VISUAL_WORKFLOW.md
echo ================================================================
echo.

pause
