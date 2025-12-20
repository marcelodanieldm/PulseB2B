# Setup script para Motor ML de PulseB2B (Windows)
# Instala dependencias ML y entrena modelo

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "🤖 PulseB2B - ML Engine Setup" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
Write-Host "✅ $pythonVersion detected" -ForegroundColor Green
Write-Host ""

# Install ML dependencies
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "📦 Installing ML dependencies..." -ForegroundColor Yellow
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

pip install xgboost>=2.0.3
pip install scikit-learn>=1.4.0
pip install shap>=0.44.0
pip install pandas>=2.1.4
pip install numpy>=1.26.2

Write-Host ""
Write-Host "✅ ML dependencies installed" -ForegroundColor Green
Write-Host ""

# Create models directory
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "📁 Creating models directory..." -ForegroundColor Yellow
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

New-Item -ItemType Directory -Force -Path models | Out-Null
New-Item -ItemType Directory -Force -Path data | Out-Null

Write-Host "✅ Directories created" -ForegroundColor Green
Write-Host ""

# Train model
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "🎯 Training ML model..." -ForegroundColor Yellow
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This will generate 2000 synthetic samples and train XGBoost + Random Forest" -ForegroundColor White
Write-Host ""

python scripts/train_model.py

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "✅ ML Engine Setup Complete!" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Run predictions: python scripts/run_predictions.py" -ForegroundColor White
Write-Host "  2. View documentation: docs/ML_ENGINE.md" -ForegroundColor White
Write-Host "  3. Try examples: python examples/ml_prediction_example.py" -ForegroundColor White
Write-Host ""
Write-Host "Models saved to:" -ForegroundColor Yellow
Write-Host "  • models/hiring_predictor_xgboost.pkl" -ForegroundColor White
Write-Host "  • models/hiring_predictor_rf.pkl" -ForegroundColor White
Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
