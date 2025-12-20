#!/bin/bash

# Quick Test Script - Lead Scoring System
# Tests with 10 companies using mock data (no web scraping)

echo "🚀 PulseB2B Lead Scoring - Quick Test"
echo "====================================="
echo ""
echo "Testing with 10 companies (MOCK data - no web scraping)"
echo ""

# Navigate to project root
cd "$(dirname "$0")/.."

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.8+"
    exit 1
fi

echo "📦 Installing dependencies..."
pip install -q -r requirements-scraper.txt

echo ""
echo "🏃 Running lead scoring test..."
echo ""

python scripts/lead_scoring.py \
    --input data/input/companies_latam.csv \
    --output data/output/lead_scoring \
    --no-scraper \
    --sample 10

echo ""
echo "✅ Test complete!"
echo ""
echo "📊 Check results in: data/output/lead_scoring/"
