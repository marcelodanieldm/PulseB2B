@echo off
REM Quick Test Script - Lead Scoring System (Windows)
REM Tests with 10 companies using mock data (no web scraping)

echo.
echo ============================================
echo   PulseB2B Lead Scoring - Quick Test
echo ============================================
echo.
echo Testing with 10 companies (MOCK data - no web scraping)
echo.

REM Navigate to project root
cd /d "%~dp0\.."

REM Check if Python is available
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

echo Installing dependencies...
pip install -q -r requirements-scraper.txt

echo.
echo Running lead scoring test...
echo.

python scripts/lead_scoring.py ^
    --input data/input/companies_latam.csv ^
    --output data/output/lead_scoring ^
    --no-scraper ^
    --sample 10

echo.
echo Test complete!
echo.
echo Check results in: data/output/lead_scoring/
echo.
pause
