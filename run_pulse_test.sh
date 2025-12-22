#!/bin/bash
# Pulse Intelligence Quick Test - Linux/Mac
# Run this to validate Pulse Intelligence setup

echo "========================================"
echo "PULSE INTELLIGENCE - QUICK TEST"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed"
    echo ""
    echo "Install Python 3.8+ from: https://www.python.org/downloads/"
    exit 1
fi

echo "[1/3] Checking dependencies..."
python3 -c "import sklearn; import numpy; import pandas" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "[WARN] Missing dependencies. Installing..."
    pip3 install scikit-learn numpy pandas
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to install dependencies"
        exit 1
    fi
fi
echo "      OK - All dependencies installed"
echo ""

echo "[2/3] Running Pulse Intelligence test..."
python3 quick_test_pulse.py
if [ $? -ne 0 ]; then
    echo "[ERROR] Test failed"
    exit 1
fi
echo ""

echo "[3/3] Test complete!"
echo ""
echo "========================================"
echo "NEXT STEPS"
echo "========================================"
echo ""
echo "1. Run full test suite:"
echo "   python3 scripts/test_pulse_intelligence.py"
echo ""
echo "2. Integrate with Oracle detector:"
echo "   python3 scripts/integrate_pulse_intelligence.py --input data/output/oracle_predictions.csv"
echo ""
echo "3. Review documentation:"
echo "   docs/PULSE_INTELLIGENCE.md"
echo ""
echo "========================================"
