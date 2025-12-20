#!/bin/bash
# Setup script para Motor ML de PulseB2B
# Instala dependencias ML y entrena modelo

echo "======================================================================"
echo "🤖 PulseB2B - ML Engine Setup"
echo "======================================================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "✅ Python $python_version detected"
echo ""

# Install ML dependencies
echo "======================================================================"
echo "📦 Installing ML dependencies..."
echo "======================================================================"
echo ""

pip install xgboost>=2.0.3
pip install scikit-learn>=1.4.0
pip install shap>=0.44.0
pip install pandas>=2.1.4
pip install numpy>=1.26.2

echo ""
echo "✅ ML dependencies installed"
echo ""

# Create models directory
echo "======================================================================"
echo "📁 Creating models directory..."
echo "======================================================================"
echo ""

mkdir -p models
mkdir -p data

echo "✅ Directories created"
echo ""

# Train model
echo "======================================================================"
echo "🎯 Training ML model..."
echo "======================================================================"
echo ""
echo "This will generate 2000 synthetic samples and train XGBoost + Random Forest"
echo ""

python scripts/train_model.py

echo ""
echo "======================================================================"
echo "✅ ML Engine Setup Complete!"
echo "======================================================================"
echo ""
echo "Next steps:"
echo "  1. Run predictions: python scripts/run_predictions.py"
echo "  2. View documentation: docs/ML_ENGINE.md"
echo "  3. Try examples: python examples/ml_prediction_example.py"
echo ""
echo "Models saved to:"
echo "  • models/hiring_predictor_xgboost.pkl"
echo "  • models/hiring_predictor_rf.pkl"
echo ""
echo "======================================================================"
