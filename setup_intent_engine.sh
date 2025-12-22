#!/bin/bash
# Setup Script for Intent Classification Engine
# Installs all required dependencies and downloads NLTK data

echo "============================================================"
echo "Intent Classification Engine - Setup"
echo "============================================================"
echo ""

echo "[1/3] Installing Python dependencies..."
pip install sec-edgar-downloader GoogleNews textblob nltk
if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
fi

echo ""
echo "[2/3] Downloading NLTK data..."
python3 -c "import nltk; nltk.download('vader_lexicon', quiet=True); nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True); print('NLTK data downloaded successfully')"
if [ $? -ne 0 ]; then
    echo "Warning: NLTK data download failed. You may need to download manually."
fi

echo ""
echo "[3/3] Creating output directories..."
mkdir -p data/output/osint_leads
mkdir -p data/output/form_d_analysis
mkdir -p data/output/market_intelligence
mkdir -p data/sec_filings

echo ""
echo "============================================================"
echo "Setup Complete!"
echo "============================================================"
echo ""
echo "You can now run:"
echo "  python examples/run_intent_classification_pipeline.py"
echo ""
echo "Or test individual components:"
echo "  python src/osint_lead_scorer.py"
echo "  python src/global_hiring_score.py"
echo ""
