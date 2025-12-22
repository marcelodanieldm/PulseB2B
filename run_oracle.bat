@echo off
REM Oracle Quick Test Script for Windows
REM Tests the Oracle Funding Detector with a small sample

echo ============================================================
echo 🔮 ORACLE FUNDING DETECTOR - QUICK TEST
echo ============================================================
echo.

REM Check Python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Python not found. Please install Python 3.8+
    exit /b 1
)

echo ✅ Python found
python --version
echo.

REM Install dependencies
echo 📦 Installing required packages...
pip install feedparser beautifulsoup4 pandas nltk scikit-learn requests lxml --quiet

if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  Some packages may already be installed
)

echo ✅ Dependencies ready
echo.

REM Run Oracle with small sample
echo 🔮 Running Oracle Funding Detector (5 companies)...
echo.

python scripts\oracle_funding_detector.py

echo.
echo ============================================================
echo ✅ Test complete!
echo ============================================================
echo.
echo 📁 Check data/output/oracle/ for results:
echo   - oracle_predictions_YYYYMMDD_HHMMSS.csv
echo   - oracle_predictions_YYYYMMDD_HHMMSS_summary.json
echo.

pause
