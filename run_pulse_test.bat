@echo off
REM Pulse Intelligence Quick Test - Windows
REM Run this to validate Pulse Intelligence setup

echo ========================================
echo PULSE INTELLIGENCE - QUICK TEST
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] Checking dependencies...
python -c "import sklearn; import numpy; import pandas" >nul 2>&1
if errorlevel 1 (
    echo [WARN] Missing dependencies. Installing...
    pip install scikit-learn numpy pandas
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
)
echo       OK - All dependencies installed
echo.

echo [2/3] Running Pulse Intelligence test...
python quick_test_pulse.py
if errorlevel 1 (
    echo [ERROR] Test failed
    pause
    exit /b 1
)
echo.

echo [3/3] Test complete!
echo.
echo ========================================
echo NEXT STEPS
echo ========================================
echo.
echo 1. Run full test suite:
echo    python scripts\test_pulse_intelligence.py
echo.
echo 2. Integrate with Oracle detector:
echo    python scripts\integrate_pulse_intelligence.py --input data\output\oracle_predictions.csv
echo.
echo 3. Review documentation:
echo    docs\PULSE_INTELLIGENCE.md
echo.
echo ========================================

pause
