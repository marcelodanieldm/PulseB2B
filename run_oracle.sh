#!/bin/bash
# Oracle Quick Test Script for Linux/Mac
# Tests the Oracle Funding Detector with a small sample

echo "============================================================"
echo "🔮 ORACLE FUNDING DETECTOR - QUICK TEST"
echo "============================================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.8+"
    exit 1
fi

echo "✅ Python found"
python3 --version
echo ""

# Install dependencies
echo "📦 Installing required packages..."
pip3 install feedparser beautifulsoup4 pandas nltk scikit-learn requests lxml --quiet

if [ $? -ne 0 ]; then
    echo "⚠️  Some packages may already be installed"
fi

echo "✅ Dependencies ready"
echo ""

# Run Oracle with small sample
echo "🔮 Running Oracle Funding Detector (5 companies)..."
echo ""

python3 scripts/oracle_funding_detector.py

echo ""
echo "============================================================"
echo "✅ Test complete!"
echo "============================================================"
echo ""
echo "📁 Check data/output/oracle/ for results:"
echo "   - oracle_predictions_YYYYMMDD_HHMMSS.csv"
echo "   - oracle_predictions_YYYYMMDD_HHMMSS_summary.json"
echo ""
