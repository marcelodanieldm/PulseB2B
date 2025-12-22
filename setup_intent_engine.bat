@echo off
REM Setup Script for Intent Classification Engine
REM Installs all required dependencies and downloads NLTK data

echo ============================================================
echo Intent Classification Engine - Setup
echo ============================================================
echo.

echo [1/3] Installing Python dependencies...
pip install sec-edgar-downloader GoogleNews textblob nltk
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [2/3] Downloading NLTK data...
python -c "import nltk; nltk.download('vader_lexicon', quiet=True); nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True); print('NLTK data downloaded successfully')"
if %ERRORLEVEL% NEQ 0 (
    echo Warning: NLTK data download failed. You may need to download manually.
)

echo.
echo [3/3] Creating output directories...
if not exist "data\output\osint_leads" mkdir data\output\osint_leads
if not exist "data\output\form_d_analysis" mkdir data\output\form_d_analysis
if not exist "data\output\market_intelligence" mkdir data\output\market_intelligence
if not exist "data\sec_filings" mkdir data\sec_filings

echo.
echo ============================================================
echo Setup Complete!
echo ============================================================
echo.
echo You can now run:
echo   python examples/run_intent_classification_pipeline.py
echo.
echo Or test individual components:
echo   python src/osint_lead_scorer.py
echo   python src/global_hiring_score.py
echo.

pause
