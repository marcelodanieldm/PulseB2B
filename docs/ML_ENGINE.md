# 🤖 Motor de IA - Predicción de Contratación IT

Sistema de Machine Learning para predecir la probabilidad de contratación IT en empresas tech en los próximos 3 meses.

## 📊 Overview

El motor de IA utiliza **XGBoost** (o Random Forest) para predecir probabilidades de contratación basándose en 4 features principales:

1. **`funding_recency`**: Días desde el último funding
2. **`tech_churn`**: Rotación de desarrolladores (%)
3. **`job_post_velocity`**: Velocidad de publicación de vacantes (ratio mes actual vs. anterior)
4. **`region_factor`**: Coeficiente económico regional

## 🎯 Output

Cada predicción genera un JSON con:

```json
{
  "company_name": "WorkOS",
  "prediction": {
    "probability": 87.5,
    "label": "Alta Probabilidad",
    "confidence": "Very High"
  },
  "reasons": [
    "🔥 Reciente SERIES-B ($80.0M hace 40 días) + 3 bajas de seniors en 1 mes = Alta probabilidad de búsqueda inmediata para reemplazos",
    "🚀 Surge de vacantes tech (3.0x vs. mes anterior) con 83% de roles técnicos. Expansión agresiva del equipo de ingeniería.",
    "🇺🇸 Estados Unidos + stage Growth = Mercado competitivo requiere hiring continuo (factor 1.15)."
  ],
  "features": {
    "funding_recency": 40,
    "tech_churn": 12.3,
    "job_post_velocity": 3.0,
    "region_factor": 1.15,
    "senior_departures": 3,
    "current_month_posts": 6,
    "tech_roles_ratio": 83.3
  }
}
```

## 🚀 Instalación

### 1. Instalar dependencias ML

```bash
pip install xgboost scikit-learn shap pandas numpy
```

### 2. Entrenar el modelo

```bash
python scripts/train_model.py
```

Este script:
- Genera 2000 muestras sintéticas de entrenamiento
- Entrena modelos XGBoost y Random Forest
- Compara métricas (ROC AUC, CV Score)
- Guarda el mejor modelo en `models/`

### 3. Ejecutar predicciones

```bash
python scripts/run_predictions.py
```

Genera:
- `data/predictions.json` - Predicciones individuales
- `data/prediction_report.json` - Reporte completo con estadísticas

## 📈 Features Engineering

### Features Principales

| Feature | Descripción | Rango | Impacto |
|---------|-------------|-------|---------|
| `funding_recency` | Días desde último funding | 0-999 | 🔥 Alto |
| `last_funding_amount` | Millones USD del último round | 0-10000 | ⚡ Medio |
| `tech_churn` | Rotación mensual de devs (%) | 0-100 | 🔥 Alto |
| `senior_departures` | Seniors que salieron (30 días) | 0-10 | 🔥 Alto |
| `job_post_velocity` | Ratio vacantes mes actual/anterior | 0-5 | 🔥 Alto |
| `tech_roles_ratio` | % de vacantes tech vs. total | 0-100 | ⚡ Medio |
| `region_factor` | Coeficiente económico regional | 0.85-1.25 | ⚡ Medio |

### Features Derivadas

- `funding_per_employee`: Total funding / team size
- `is_recent_funding`: Bool (< 180 días)
- `has_high_churn`: Bool (> 15%)
- `has_velocity_surge`: Bool (> 2.0x)
- `has_senior_exodus`: Bool (≥ 3 seniors)

### Coeficientes Regionales

```python
region_coefficients = {
    'us': 1.15,      # Tech boom USA
    'sa': 1.25,      # Brasil tech explosion
    'eu': 0.85,      # Europa estancada post-Brexit
    'ap': 1.10       # Asia-Pacífico crecimiento sólido
}
```

## 🧠 Arquitectura del Modelo

### XGBoost (Recomendado)

```python
model_params = {
    'max_depth': 6,
    'learning_rate': 0.1,
    'n_estimators': 200,
    'objective': 'binary:logistic',
    'eval_metric': 'logloss'
}
```

**Ventajas**:
- ⚡ Rápido (tree boosting)
- 🎯 Alta precisión (ROC AUC > 0.85)
- 📊 Feature importance nativa
- 🔍 Compatible con SHAP

### Random Forest (Alternativa)

```python
model_params = {
    'n_estimators': 200,
    'max_depth': 10,
    'min_samples_split': 5
}
```

## 📊 Métricas del Modelo

Ejemplo de entrenamiento con 2000 muestras sintéticas:

```
XGBoost Results:
  Train Accuracy: 0.927
  Test Accuracy: 0.875
  ROC AUC: 0.912
  CV Score: 0.883 (+/- 0.024)

Random Forest Results:
  Train Accuracy: 0.945
  Test Accuracy: 0.868
  ROC AUC: 0.905
  CV Score: 0.876 (+/- 0.031)

🏆 Best Model: XGBoost
```

## 🔍 Explicabilidad (SHAP)

El modelo incluye **SHAP (SHapley Additive exPlanations)** para interpretar predicciones:

```python
prediction = predictor.predict(features, explain=True)

# SHAP explanation
shap_explanation = prediction['shap_explanation']
# [
#   {'feature': 'funding_recency', 'value': 40, 'impact': 0.23},
#   {'feature': 'job_post_velocity', 'value': 3.0, 'impact': 0.18},
#   {'feature': 'senior_departures', 'value': 3, 'impact': 0.15},
#   ...
# ]
```

## 📋 Ejemplo de Uso

### Predicción Individual

```python
from src.ml_predictor import HiringProbabilityPredictor
from src.feature_engineering import FeatureEngineer

# Cargar modelo
predictor = HiringProbabilityPredictor(
    model_path='models/hiring_predictor_xgboost.pkl'
)

# Extraer features
engineer = FeatureEngineer()
features = engineer.extract_features(
    company_data={
        'id': 'workos',
        'name': 'WorkOS',
        'region': 'us',
        'team_size': 85
    },
    jobs_data=[...],
    funding_data=[...],
    linkedin_data={...}
)

# Predecir
prediction = predictor.predict(features)
print(f"Probability: {prediction['prediction']['probability']}%")
print(f"Reasons: {prediction['reasons']}")
```

### Predicción Batch

```python
# Predecir múltiples empresas
predictions = predictor.predict_batch(
    features_list=[features1, features2, features3],
    output_file='data/predictions.json'
)

# Generar reporte
report = predictor.generate_prediction_report(
    predictions,
    output_file='data/report.json'
)
```

## 🎯 Lógica de Razones

Las 3 razones justifican la predicción basándose en:

### Razón 1: Funding + Churn

- **Alta probabilidad**: Funding reciente (<90 días) + ≥3 senior departures
- **Media**: Funding reciente con churn elevado (>10%)
- **Baja**: Funding antiguo (>365 días)

### Razón 2: Velocity + Tech Ratio

- **Alta probabilidad**: Velocity >2.0x + >60% roles tech
- **Media**: Velocity 1.5-2.0x
- **Baja**: Velocity <0.8x (decrecimiento)

### Razón 3: Regional + Growth Stage

- **Alta probabilidad**: Latam (SA) + funding reciente
- **Media**: US + growth/scale stage
- **Baja**: Europa con factor <0.9

## 📁 Estructura de Archivos

```
PulseB2B/
├── src/
│   ├── feature_engineering.py  # Feature extraction
│   ├── ml_predictor.py          # ML model
│   └── main.py                  # Pipeline integration
├── scripts/
│   ├── train_model.py           # Model training
│   └── run_predictions.py       # Run predictions
├── models/
│   ├── hiring_predictor_xgboost.pkl
│   └── hiring_predictor_rf.pkl
├── data/
│   ├── predictions.json
│   └── prediction_report.json
└── docs/
    └── ML_ENGINE.md             # Esta documentación
```

## 🔄 Integración con Pipeline

### Opción 1: CLI

```bash
python src/main.py --ml-predict --watchlist watchlist.csv
```

### Opción 2: Módulo Python

```python
from src.main import PulseB2BPipeline

pipeline = PulseB2BPipeline()
pipeline.run_with_ml_prediction(
    watchlist=['OpenAI', 'Stripe', 'Nubank'],
    output_file='data/ml_predictions.json'
)
```

### Opción 3: Lambda Function

```javascript
// lambda/ml_predictor.js
const { spawn } = require('child_process');

exports.handler = async (event) => {
  const { companyId } = event;
  
  // Llamar a Python ML predictor
  const result = await runPythonPredictor(companyId);
  
  // Guardar en Supabase
  await supabase.from('hiring_predictions').insert({
    company_id: companyId,
    probability: result.prediction.probability,
    reasons: result.reasons,
    predicted_at: new Date()
  });
  
  return result;
};
```

## 📊 Dashboard de Resultados

### Distribución de Probabilidades

```
🔥 High Probability (≥70%):   12 companies (24%)
⚡ Medium Probability (40-70%): 28 companies (56%)
❄️ Low Probability (<40%):     10 companies (20%)

Average Probability: 58.3%
```

### Top 5 Hiring Candidates

```
1. WorkOS - 87.5% 🔥
   Reciente Series B + 3 senior departures + 3.0x velocity

2. Nubank - 82.3% 🔥
   Brasil tech boom + 5 departures + alta actividad de hiring

3. OpenAI - 76.8% 🔥
   Post-funding masivo + expansión agresiva

4. Stripe - 65.2% ⚡
   Funding reciente + hiring constante

5. Revolut - 38.5% ❄️
   Funding antiguo + alta rotación sin reemplazo visible
```

## 🛠️ Troubleshooting

### Error: "Model not found"

```bash
# Entrenar modelo primero
python scripts/train_model.py
```

### Error: "SHAP not available"

```bash
# Instalar SHAP
pip install shap

# O desactivar explicabilidad
prediction = predictor.predict(features, explain=False)
```

### Bajo ROC AUC (<0.80)

- ✅ Aumentar `n_estimators` (200 → 500)
- ✅ Ajustar `max_depth` (6 → 8)
- ✅ Generar más muestras de entrenamiento (2000 → 5000)
- ✅ Recolectar datos reales (mejor que sintéticos)

## 🚀 Próximos Pasos

### 1. Recolectar Datos Reales

Reemplazar datos sintéticos con histórico real:

```python
# Formato esperado
training_data = [
    {
        'features': {...},
        'label': 1,  # 1 = contrató en 3 meses, 0 = no contrató
        'company': 'Example Inc'
    }
]
```

### 2. Fine-tuning

Optimizar hiperparámetros con GridSearch:

```python
from sklearn.model_selection import GridSearchCV

param_grid = {
    'max_depth': [4, 6, 8],
    'learning_rate': [0.05, 0.1, 0.15],
    'n_estimators': [100, 200, 300]
}

grid_search = GridSearchCV(xgb_model, param_grid, cv=5)
grid_search.fit(X_train, y_train)
```

### 3. Monitoreo en Producción

Trackear drift de modelo:

```python
# Guardar predicciones
predictions_log = {
    'predicted_at': datetime.now(),
    'probability': 87.5,
    'actual_outcome': None  # Actualizar después de 3 meses
}

# Después de 3 meses
actual_hired = True
model_accuracy = calculate_accuracy(predictions_log)
```

### 4. Features Adicionales

- 🔹 Glassdoor rating (señal de cultura)
- 🔹 GitHub activity (repos, commits)
- 🔹 Social media hiring signals
- 🔹 Job board presence (LinkedIn, Indeed)
- 🔹 Tech stack changes (nuevas tecnologías)

## 📞 Soporte

Para problemas o preguntas sobre el motor de IA:

- 📧 Email: support@pulseb2b.com
- 📚 Docs: [docs/ML_ENGINE.md](ML_ENGINE.md)
- 🐛 Issues: GitHub Issues

## 📄 Licencia

MIT License - Ver [LICENSE](../LICENSE)

---

**Powered by XGBoost + SHAP** 🚀
