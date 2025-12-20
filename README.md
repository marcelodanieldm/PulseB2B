# 🚀 PulseB2B - Market Intelligence Platform

**Plataforma completa de inteligencia de mercados con arquitectura serverless multi-región.**

Pipeline automatizado que monitorea noticias empresariales, detecta vacantes en tiempo real, predice contrataciones IT y genera lead scoring para LATAM.

## 📋 Descripción

PulseB2B es una solución completa para analistas de mercados que necesitan monitorear el ecosistema de startups y venture capital. El sistema integra cuatro componentes principales:

### 📰 **News Intelligence Pipeline (Python)**
1. **Monitorea** múltiples fuentes de noticias (Google News, TechCrunch, VentureBeat, Crunchbase)
2. **Clasifica** artículos según eventos clave: Funding, Series A/B/C, Layoffs, Expansión, Adquisiciones, IPO
3. **Analiza** el sentimiento de noticias usando modelos BERT
4. **Calcula** Financial Health Scores basándose en:
   - Fecha de última ronda de financiamiento
   - Cantidad total recaudada
   - Tamaño de equipo
   - Eficiencia de capital
   - Sentimiento de noticias recientes

### 💼 **Job Scraping System (Node.js + AWS Lambda)**
1. **Scraping Multi-Región** con AWS Lambda en US, EU y SA
2. **Evasión de Detección** con Playwright Stealth
3. **Rotación de Proxies** gratuita o profesional (SmartProxy/BrightData)
4. **Watchlist Inteligente** para monitorear empresas específicas
5. **Webhooks en Tiempo Real** vía Slack, Discord, Telegram, Email
6. **Persistencia Global** con Supabase (PostgreSQL)

### 🤖 **ML Prediction Engine (XGBoost)**
1. **Predicción de Contratación IT** (0-100%) para próximos 3 meses
2. **Features**: funding_recency, tech_churn, job_post_velocity, region_factor
3. **Explicabilidad SHAP** con justificación de 3 razones por empresa
4. **Batch Processing** para análisis de múltiples empresas
5. **JSON Output** con probabilidades y métricas detalladas

### 🎯 **Lead Scoring System (LATAM)**
1. **Web Scraping** de LinkedIn vía Google Search con BeautifulSoup
2. **Hiring Potential Index (HPI)** - Score 0-100 de probabilidad de contratación
3. **Lógica de Negocio**: Funding reciente + bajo crecimiento = ALTA urgencia
4. **Focus Geográfico**: México y Brasil exclusivamente
5. **Reportes Automáticos**: CSV con rankings y recomendaciones de acción

## 🎯 Características Principales

### � News Intelligence (Python)

#### �🔍 Monitoreo de Noticias Multi-Fuente
- **Google News** vía `pygooglenews`
- **Feeds RSS** de TechCrunch, VentureBeat, Crunchbase
- Extracción completa de contenido con `Newspaper4k`
- Deduplicación automática de artículos

### 🏷️ Clasificación Inteligente
- Detección de **8 categorías** clave de eventos empresariales
- Sistema de scoring basado en palabras clave ponderadas
- Extracción automática de nombres de empresas
- Análisis de sentimiento con **DistilBERT**

#### 💰 Financial Health Score
Algoritmo propietario que evalúa la salud financiera considerando:

| Componente | Peso | Descripción |
|------------|------|-------------|
| **Funding Recency** | 25% | Qué tan reciente fue la última ronda |
| **Funding Amount** | 20% | Total recaudado vs. benchmarks |
| **Team Efficiency** | 20% | Relación funding/empleado |
| **Growth Trajectory** | 15% | Tendencia de crecimiento entre rondas |
| **Funding Velocity** | 10% | Frecuencia óptima de rondas |
| **News Sentiment** | 10% | Análisis de estabilidad en noticias |

**Score Final:** 0-100
- **80-100:** Excelente
- **65-79:** Buena
- **50-64:** Moderada
- **35-49:** Preocupante
- **0-34:** Pobre

### 💼 Job Scraping System (Node.js)

#### 🌍 Scraping Multi-Región Serverless
- **AWS Lambda** en 3 regiones (US-East-1, EU-West-1, SA-East-1)
- **Costo casi cero** con Free Tier de AWS
- **Ejecución programada** cada 4-6 horas
- **Escalamiento automático** según demanda

#### 🎭 Evasión de Detección Avanzada
- **Playwright Stealth** con anti-detección
- **Rotación de User-Agents** y fingerprints
- **Simulación de comportamiento humano**
- **Delays aleatorios** y movimientos de mouse

#### 🔄 Rotación de Proxies Inteligente
- **Proxies gratuitos** desde APIs públicas
- **SmartProxy** integration (residencial)
- **BrightData** integration (Luminati)
- **Rotación automática** por región y tiempo

#### 📋 Watchlist & Monitoring
- **Empresas personalizadas** para monitorear
- **Priorización** por importancia (1-10)
- **Scrapers especializados**: Greenhouse, Lever, Workday
- **Detección automática** de sistemas de careers

#### 🚨 Webhooks en Tiempo Real
- **Notificaciones instantáneas** de nuevas vacantes
- **Múltiples canales**: Slack, Discord, Telegram, Email
- **Payloads personalizados** por empresa
- **Deduplicación** automática de vacantes

#### 💾 Persistencia Global con Supabase
- **PostgreSQL** serverless con sync en tiempo real
- **Full-text search** de vacantes
- **Logs de scraping** detallados
- **Estadísticas** por empresa y región

## 🛠️ Tecnologías

### Backend (Python - News Pipeline)
- **Python 3.8+**
- **pygooglenews** - Acceso a Google News
- **Newspaper4k** - Extracción de contenido web
- **Transformers (HuggingFace)** - Análisis de sentimiento BERT
- **PyTorch** - Backend de ML
- **feedparser** - Procesamiento de RSS
- **PyYAML** - Configuración

### Backend (Node.js - Job Scraping)
- **Node.js 18+**
- **Playwright Stealth** - Scraping con evasión
- **AWS Lambda** - Serverless computing
- **Supabase** - PostgreSQL + Auth + Storage
- **Axios** - HTTP requests para webhooks

## 📦 Instalación

### Prerequisitos
- **Python 3.8+** (para News Pipeline)
- **Node.js 18+** (para Job Scraping)
- **AWS CLI** configurado (para deployment)
- **AWS SAM CLI** (para serverless)
- **Cuenta Supabase** (gratis)

### 1. Clonar repositorio

```bash
git clone https://github.com/tu-usuario/PulseB2B.git
cd PulseB2B
```

### 2. Configurar Python (News Pipeline)

```bash
# Crear entorno virtual
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Descargar modelo BERT (primera vez)
python -c "from transformers import pipeline; pipeline('sentiment-analysis')"
```

### 3. Entrenar Modelo ML (Predicción de Contratación)

```bash
# Entrenar XGBoost con datos sintéticos
python scripts/train_model.py

# Genera:
# - models/hiring_predictor_xgboost.pkl
# - models/hiring_predictor_rf.pkl
```

### 4. Configurar Node.js (Job Scraping)

```bash
# Instalar dependencias de Node
npm install

# Instalar Playwright browsers
npx playwright install chromium
```

### 4. Configurar Supabase

1. Crear proyecto en [supabase.com](https://supabase.com)
2. Ejecutar el schema SQL:
   ```bash
   # En Supabase Dashboard > SQL Editor
   # Copiar y ejecutar: supabase/schema.sql
   ```
3. Obtener credenciales:
   - **Project URL**: Settings > API
   - **Service Role Key**: Settings > API (secret key)

### 5. Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus credenciales
# SUPABASE_URL=https://tu-proyecto.supabase.co
# SUPABASE_KEY=tu-service-role-key
```

### 6. Deploy a AWS Lambda (Opcional)

```bash
# Build con SAM
sam build

# Deploy (primera vez)
sam deploy --guided

# Deploy subsecuentes
sam deploy
```

**Nota:** El deploy inicial solicitará parámetros:
- Supabase URL y Key
- Modo de proxy (free, smartproxy, brightdata, none)
- Webhooks de Slack/Discord (opcional)

## 🚀 Uso

### 📰 News Intelligence Pipeline (Python)

#### Ejecutar Pipeline Completo

```bash
cd src
python main.py
```

#### Con Opciones Personalizadas

```bash
# Monitorear últimas 24 horas
python main.py --days 1

# Sin análisis de sentimiento (más rápido)
python main.py --no-sentiment

# Con archivo de configuración personalizado
python main.py --config ../config/mi_config.yaml
```

### 🤖 ML Prediction Engine

#### Ejecutar Predicciones

```bash
# Predecir probabilidades de contratación
python scripts/run_predictions.py

# Genera:
# - data/predictions.json (predicciones individuales)
# - data/prediction_report.json (reporte completo)
```

#### Output Ejemplo

```json
{
  "company_name": "WorkOS",
  "prediction": {
    "probability": 87.5,
    "label": "Alta Probabilidad",
    "confidence": "Very High"
  },
  "reasons": [
    "🔥 Reciente SERIES-B ($80M hace 40 días) + 3 seniors salieron = Alta probabilidad inmediata",
    "🚀 Surge de vacantes (3.0x vs. mes anterior) con 83% de roles tech",
    "🇺🇸 Estados Unidos + stage Growth = Mercado competitivo (factor 1.15)"
  ],
  "features": {
    "funding_recency": 40,
    "tech_churn": 12.3,
    "job_post_velocity": 3.0,
    "region_factor": 1.15
  }
}
```

#### API Programática

```python
from src.ml_predictor import HiringProbabilityPredictor
from src.feature_engineering import FeatureEngineer

# Cargar modelo
predictor = HiringProbabilityPredictor()

# Extraer features
engineer = FeatureEngineer()
features = engineer.extract_features(
    company_data={...},
    jobs_data=[...],
    funding_data=[...],
    linkedin_data={...}
)

# Predecir
prediction = predictor.predict(features)
print(f"Probability: {prediction['prediction']['probability']}%")
```

### 💼 Job Scraping System (Node.js)

#### Test Local (Sin Lambda)

```bash
# Test del scraper
node scrapers/jobScraper.js

# Test de watchlist manager
node -e "const WM = require('./webhooks/watchlistManager'); new WM().getActiveCompanies().then(console.log)"
```

#### Invocar Lambda Localmente (SAM)

```bash
# Iniciar API local
sam local start-api

# En otra terminal, hacer request
curl -X POST http://localhost:3000/scrape/us-east-1 \
  -H "Content-Type: application/json" \
  -d '{"maxCompanies": 5}'
```

#### Invocar Lambda en AWS

```bash
# Via AWS CLI
aws lambda invoke \
  --function-name pulseb2b-scraper-us-east-1 \
  --payload '{"region":"us-east-1","maxCompanies":10}' \
  response.json

# Via API Gateway (después del deploy)
curl -X POST https://your-api-id.execute-api.us-east-1.amazonaws.com/Prod/scrape/us-east-1 \
  -H "Content-Type: application/json" \
  -d '{"maxCompanies": 10}'
```

#### Agregar Empresa a Watchlist

```javascript
// addCompanyToWatchlist.js
const WatchlistManager = require('./webhooks/watchlistManager');

async function main() {
  const manager = new WatchlistManager();
  
  await manager.addCompany({
    name: 'Anthropic',
    careers_url: 'https://www.anthropic.com/careers',
    scraper_type: 'greenhouse',
    region: 'us',
    priority: 10,
    webhook_url: 'https://your-webhook.com/endpoint',
    notification_channels: ['webhook', 'slack']
  });
  
  console.log('✓ Company added to watchlist');
}

main();
```

```bash
node addCompanyToWatchlist.js
```

### 🔔 Configurar Webhooks

#### 1. Webhook Personalizado

```javascript
// Tu endpoint debe aceptar POST con este payload:
{
  "event": "new_jobs_detected",
  "timestamp": "2025-12-20T10:30:00Z",
  "company": {
    "id": "uuid",
    "name": "Anthropic",
    "careers_url": "https://..."
  },
  "jobs": [
    {
      "title": "Senior ML Engineer",
      "link": "https://...",
      "location": "San Francisco, CA",
      "department": "Engineering"
    }
  ],
  "summary": {
    "total_new_jobs": 5,
    "locations": ["San Francisco", "Remote"],
    "departments": ["Engineering", "Product"]
  }
}
```

#### 2. Slack Webhook

```bash
# En .env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

Recibirás notificaciones formateadas:
```
🚀 5 New Jobs at Anthropic
• Senior ML Engineer (San Francisco, CA)
• Product Manager (Remote)
...
[View All Jobs] → https://anthropic.com/careers
```

#### 3. Discord Webhook

```bash
# En .env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR/WEBHOOK
```

#### 4. Telegram Bot

```bash
# Crear bot con @BotFather
# En .env
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
TELEGRAM_CHAT_ID=your-chat-id
```

### Usar Módulos Individualmente

#### 1. Solo Scraping de Noticias

```python
from news_scraper import NewsMonitor

monitor = NewsMonitor()
articles = monitor.fetch_all_news(
    queries=["startup funding", "Series A"],
    days=7,
    extract_content=True
)

print(f"Artículos obtenidos: {len(articles)}")
```

#### 2. Solo Clasificación

```python
from news_classifier import NewsClassifier

classifier = NewsClassifier(load_sentiment_model=True)
result = classifier.classify_article(article)

print(f"Categoría: {result['primary_category']}")
print(f"Sentimiento: {result['sentiment']['sentiment']}")
```

#### 3. Solo Análisis Financiero

```python
from financial_analyzer import FinancialHealthCalculator, CompanyData, FundingRound
from datetime import datetime

company = CompanyData(
    name="MiStartup",
    team_size=50,
    funding_rounds=[
        FundingRound("seed", 2.5, datetime(2023, 1, 15), ["Angel Investors"]),
        FundingRound("series-a", 12.0, datetime(2024, 6, 1), ["Sequoia Capital"])
    ]
)

calculator = FinancialHealthCalculator()
score = calculator.calculate_health_score(company)

print(f"Financial Health Score: {score['overall_score']}/100")
print(f"Estado: {score['health_status']}")
```

## 📊 Salidas

El pipeline genera varios archivos en el directorio `data/`:

### 1. `raw_articles_YYYYMMDD_HHMMSS.json`
Artículos sin procesar con metadata completa.

### 2. `classified_articles_YYYYMMDD_HHMMSS.json`
Artículos clasificados con:
- Categoría principal y score
- Análisis de sentimiento
- Empresas mencionadas

### 3. `company_insights_YYYYMMDD_HHMMSS.json`
Insights agregados por empresa:
```json
{
  "Anthropic": {
    "articles": [...],
    "categories": {"Funding": 3, "Expansion": 1},
    "avg_sentiment": {
      "positive": 0.78,
      "negative": 0.22,
      "overall": "positive"
    }
  }
}
```

### 4. `financial_scores_YYYYMMDD_HHMMSS.json`
Scores financieros detallados:
```json
{
  "company": "Anthropic",
  "health_score": {
    "overall_score": 82.5,
    "health_status": "excellent",
    "components": {...},
    "metrics": {
      "total_funding": 1154.0,
      "team_size": 150,
      "estimated_burn_rate": 1.5,
      "estimated_runway_months": 24.3
    },
    "insights": [
      "✓ Financiamiento muy reciente (3.2 meses).",
      "✓ Salud financiera sólida en general."
    ]
  }
}
```

### 5. `report_YYYYMMDD_HHMMSS.md`
Reporte consolidado en Markdown con:
- Resumen ejecutivo
- Distribución por categoría
- Top empresas por menciones
- Financial Health Scores
- Artículos destacados

### 6. `predictions.json` (ML Engine)
Predicciones de contratación IT:
```json
{
  "company_name": "Anthropic",
  "prediction": {
    "probability": 85.2,
    "label": "Alta Probabilidad",
    "confidence": "Very High"
  },
  "reasons": [
    "🔥 Reciente SERIES-C ($450M hace 65 días) indica expansión inminente",
    "📈 Velocity de vacantes 2.8x vs. mes anterior con 78% roles tech",
    "🇺🇸 Estados Unidos + stage Scale = Hiring continuo (factor 1.15)"
  ],
  "features": {
    "funding_recency": 65,
    "tech_churn": 8.5,
    "job_post_velocity": 2.8,
    "region_factor": 1.15
  }
}
```

### 7. `prediction_report.json` (ML Engine)
Reporte agregado con estadísticas:
```json
{
  "summary": {
    "total_companies": 50,
    "high_probability": 12,
    "medium_probability": 28,
    "low_probability": 10,
    "average_probability": 58.3
  },
  "top_candidates": [...],
  "predictions": [...]
}
```

## 🔧 Configuración Avanzada

### Agregar Fuentes RSS Personalizadas

```python
from news_scraper import RSSFeedSource

# En tu código
monitor.add_source(RSSFeedSource(
    "Mi Fuente",
    "https://mifuente.com/rss"
))
```

### Personalizar Palabras Clave

Edita las categorías en `src/news_classifier.py`:

```python
self.categories = {
    'Mi Categoria': {
        'keywords': ['palabra1', 'palabra2'],
        'weight': 1.2
    }
}
```

### Ajustar Pesos del Financial Health Score

En `config/config.yaml`:

```yaml
financial_health:
  weights:
    funding_recency: 0.30  # Aumentar importancia
    funding_amount: 0.15
    # ...
```

## 📈 Ejemplos de Uso Real

### Caso 1: Monitoreo de Portafolio VC

```python
from main import PulseB2BPipeline
from financial_analyzer import CompanyData, FundingRound

# Mis inversiones
portfolio = [
    CompanyData(name="Startup1", team_size=45, funding_rounds=[...]),
    CompanyData(name="Startup2", team_size=120, funding_rounds=[...]),
]

pipeline = PulseB2BPipeline()
pipeline.run_full_pipeline(company_data=portfolio)
```

### Caso 2: Alertas de Riesgo

```python
# Identificar empresas en riesgo
for result in financial_scores:
    score = result['health_score']
    if score['overall_score'] < 50:
        print(f"⚠️ ALERTA: {result['company']}")
        print(f"Score: {score['overall_score']}")
        print(f"Runway: {score['metrics']['estimated_runway_months']} meses")
```

### Caso 3: Análisis de Competencia

```python
# Monitorear categoría específica
classified = pipeline.run_classification(articles)
funding_news = [a for a in classified if a['primary_category'] == 'Funding']

for article in funding_news:
    print(f"{article['title']} - {article['companies_mentioned']}")
```

## 🎓 Casos de Uso

- **Venture Capital:** Monitoreo de portafolio y pipeline de inversión
- **M&A:** Identificación de targets de adquisición
- **Análisis Competitivo:** Tracking de competidores y mercado
- **Business Development:** Detección de oportunidades de partnership
- **Sales Intelligence:** Identificación de empresas en expansión

## 🐛 Troubleshooting

### Error: "No module named 'torch'"

```bash
pip install torch==2.1.2 --index-url https://download.pytorch.org/whl/cpu
```

### Error: "Article Download Failed"

Algunos sitios bloquean scraping. Reduce `extract_full_content: false` en config.

### Warning: "Could not load sentiment model"

El modelo descarga ~250MB la primera vez. Verifica tu conexión a internet.

### Lentitud en clasificación

Desactiva análisis de sentimiento:
```bash
python main.py --no-sentiment
```

## 🔐 Consideraciones

- **Rate Limiting:** El scraper incluye delays para respetar sitios web
- **Legal:** Verifica términos de uso de cada fuente de noticias
- **Privacidad:** No almacena datos personales
- **API Keys:** No requiere API keys para funcionalidad básica

## 📝 Roadmap

### ✅ Completado

- [x] News Intelligence Pipeline con clasificación
- [x] Financial Health Score calculator
- [x] Multi-region serverless scraping
- [x] Webhook notifications (5 canales)
- [x] Supabase integration
- [x] **ML Prediction Engine (XGBoost + SHAP)**
- [x] **Feature engineering con 4 features principales**
- [x] **Batch predictions con reportes JSON**

### 🚧 En Progreso

- [ ] Integración LinkedIn para churn real (actualmente estimado)
- [ ] Dashboard web para visualización de predicciones
- [ ] Fine-tuning con datos históricos reales

### 📋 Futuro

- [ ] Integración con APIs de Crunchbase y PitchBook
- [ ] Notificaciones por email/Slack para predicciones ML
- [ ] Exportación a Google Sheets
- [ ] Análisis de tendencias temporales
- [ ] Named Entity Recognition mejorado con spaCy
- [ ] Soporte para múltiples idiomas
- [ ] API REST para predicciones ML
- [ ] Integración con CRMs (Salesforce, HubSpot)

## 📚 Documentación

- [📖 README Principal](README.md) - Overview y setup
- [🏗️ ARCHITECTURE.md](docs/ARCHITECTURE.md) - Arquitectura del sistema
- [🚀 DEPLOYMENT.md](docs/DEPLOYMENT.md) - Guía de deployment AWS
- [🤖 ML_ENGINE.md](docs/ML_ENGINE.md) - Motor de predicción ML con XGBoost
- [🎯 LEAD_SCORING.md](docs/LEAD_SCORING.md) - **Sistema de Lead Scoring para LATAM**
- [💻 Frontend README](frontend/README.md) - Dashboard Next.js con Mapbox

## 🎓 Casos de Uso

- **Venture Capital:** Monitoreo de portafolio y pipeline de inversión
- **Recruiting Tech:** Predicción de empresas que contratarán en 3 meses
- **Lead Generation LATAM:** Identificación de empresas en México/Brasil con alta urgencia de hiring
- **M&A:** Identificación de targets de adquisición
- **Análisis Competitivo:** Tracking de competidores y mercado
- **Business Development:** Detección de oportunidades de partnership
- **Sales Intelligence:** Identificación de empresas en expansión

## 🤝 Contribuir

1. Fork el proyecto
2. Crea un branch (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 👥 Autores

- **Tu Nombre** - *Desarrollo Inicial* - [GitHub](https://github.com/tu-usuario)

## 🙏 Agradecimientos

- HuggingFace por los modelos Transformers
- Comunidad de Python por las excelentes librerías
- Todas las fuentes de noticias open-source

## 📞 Contacto

Para preguntas o soporte:
- **Email:** tu-email@ejemplo.com
- **LinkedIn:** [Tu Perfil](https://linkedin.com/in/tu-perfil)
- **Issues:** [GitHub Issues](https://github.com/tu-usuario/PulseB2B/issues)

---

**Made with ❤️ for Market Intelligence Professionals**
