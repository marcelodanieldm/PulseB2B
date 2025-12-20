## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                        PulseB2B Platform                         │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────┐         ┌──────────────────────────────┐
│  NEWS INTELLIGENCE   │         │    JOB SCRAPING SYSTEM       │
│     (Python)         │         │       (Node.js)              │
└──────────────────────┘         └──────────────────────────────┘
         │                                    │
         │                                    │
    ┌────▼─────┐                         ┌───▼────────────┐
    │ Scrapers │                         │  AWS Lambda    │
    │  - Google│                         │  Multi-Region  │
    │  - RSS   │                         │  ┌──────────┐  │
    │  - News4k│                         │  │ US-East  │  │
    └────┬─────┘                         │  │ EU-West  │  │
         │                                │  │ SA-East  │  │
    ┌────▼──────┐                        │  └──────────┘  │
    │Classifier │                        └───┬────────────┘
    │  - Keywords                            │
    │  - BERT    │                      ┌────▼────────┐
    │  - Sentiment│                     │ Playwright  │
    └────┬───────┘                      │  Stealth    │
         │                               │  ┌────────┐ │
    ┌────▼────────┐                     │  │Browser │ │
    │ Financial   │                     │  │Context │ │
    │  Analyzer   │                     │  └────────┘ │
    │  - Score    │                     └────┬────────┘
    │  - Insights │                          │
    └────┬────────┘                     ┌────▼─────────┐
         │                               │ Proxy Router │
         │                               │  - Free APIs │
         │                               │  - SmartProxy│
    ┌────▼────────┐                     │  - BrightData│
    │   Output    │                     └────┬─────────┘
    │  - JSON     │                          │
    │  - Markdown │                     ┌────▼──────────┐
    │  - Reports  │                     │  Watchlist    │
    └─────────────┘                     │   Manager     │
                                        └────┬──────────┘
                                             │
                                        ┌────▼──────────┐
                                        │   Supabase    │
                                        │  PostgreSQL   │
                                        │  ┌──────────┐ │
                                        │  │watchlist │ │
                                        │  │jobs      │ │
                                        │  │logs      │ │
                                        │  └──────────┘ │
                                        └────┬──────────┘
                                             │
                                        ┌────▼──────────┐
                                        │   Webhooks    │
                                        │  ┌──────────┐ │
                                        │  │ Slack    │ │
                                        │  │ Discord  │ │
                                        │  │ Telegram │ │
                                        │  │ Email    │ │
                                        │  └──────────┘ │
                                        └───────────────┘
```

### Flujo de Datos

#### News Pipeline:
1. **Scraping** → Obtiene artículos de múltiples fuentes
2. **Classification** → Categoriza por tipo de evento + sentimiento
3. **Analysis** → Calcula Financial Health Score
4. **Output** → Genera reportes consolidados

#### Job Scraping:
1. **Orchestrator** → Distribuye empresas por región
2. **Lambda Functions** → Ejecutan scraping en paralelo
3. **Playwright** → Navega sitios con evasión de detección
4. **Proxy Rotation** → Evita bloqueos geográficos
5. **Supabase** → Persiste vacantes y detecta nuevas
6. **Webhooks** → Notifica en tiempo real

### Costos Estimados (Free Tier)

| Servicio | Free Tier | Costo después |
|----------|-----------|---------------|
| **AWS Lambda** | 1M requests/mes | $0.20 por 1M requests |
| **Supabase** | 500MB DB, 1GB storage | $25/mes Pro |
| **Proxies Free** | Ilimitado | N/A |
| **SmartProxy** | N/A | $75/mes (5GB) |
| **BrightData** | N/A | $500/mes (20GB) |

**Total Free Tier:** $0/mes para ~10,000 scrapers/mes ✅

## 📊 Salidas

### News Pipeline

El pipeline genera varios archivos en el directorio `data/`:

#### 1. `raw_articles_YYYYMMDD_HHMMSS.json`
Artículos sin procesar con metadata completa.

#### 2. `classified_articles_YYYYMMDD_HHMMSS.json`
Artículos clasificados con:
- Categoría principal y score
- Análisis de sentimiento
- Empresas mencionadas

#### 3. `company_insights_YYYYMMDD_HHMMSS.json`
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

#### 4. `financial_scores_YYYYMMDD_HHMMSS.json`
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

#### 5. `report_YYYYMMDD_HHMMSS.md`
Reporte consolidado en Markdown con:
- Resumen ejecutivo
- Distribución por categoría
- Top empresas por menciones
- Financial Health Scores
- Artículos destacados

### Job Scraping System

Los datos se persisten en **Supabase** con acceso en tiempo real:

#### Tablas Principales:

**`watchlist`** - Empresas monitoreadas
```sql
id | name | careers_url | scraper_type | region | priority | active
```

**`jobs`** - Vacantes detectadas
```sql
id | company_id | title | link | location | department | scraped_at
```

**`notifications`** - Historial de webhooks
```sql
id | company_id | job_count | channels | sent_at | status
```

**`scrape_logs`** - Logs de ejecución
```sql
id | company_id | region | proxy_used | jobs_found | success | scraped_at
```

#### Consultas Útiles:

```sql
-- Jobs recientes (últimos 7 días)
SELECT * FROM recent_jobs LIMIT 50;

-- Estadísticas por empresa
SELECT * FROM company_stats;

-- Búsqueda full-text
SELECT * FROM search_jobs('machine learning');

-- Empresas que necesitan scraping
SELECT * FROM get_companies_needing_scrape(24);
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

Edita las categorías en [src/news_classifier.py](src/news_classifier.py):

```python
self.categories = {
    'Mi Categoria': {
        'keywords': ['palabra1', 'palabra2'],
        'weight': 1.2
    }
}
```

### Ajustar Pesos del Financial Health Score

En [config/config.yaml](config/config.yaml):

```yaml
financial_health:
  weights:
    funding_recency: 0.30  # Aumentar importancia
    funding_amount: 0.15
    # ...
```

### Configurar Scraper Personalizado para Empresa

```javascript
// En Supabase o via API
await watchlistManager.addCompany({
  name: 'CustomCompany',
  careers_url: 'https://company.com/jobs',
  scraper_type: 'custom',
  job_selector: '.job-card', // Selector CSS personalizado
  region: 'us',
  priority: 8
});
```

### Configurar Proxies Profesionales

#### SmartProxy

```bash
# En .env
PROXY_MODE=smartproxy
SMARTPROXY_USERNAME=user-spXXXXXX
SMARTPROXY_PASSWORD=your-password
```

#### BrightData

```bash
# En .env
PROXY_MODE=brightdata
BRIGHTDATA_USERNAME=brd-customer-xxx
BRIGHTDATA_PASSWORD=your-password
```

### Ajustar Frecuencia de Scraping

Edita [template.yaml](template.yaml):

```yaml
Events:
  ScheduledEvent:
    Type: Schedule
    Properties:
      Schedule: rate(2 hours)  # Cambiar a 2 horas
      Enabled: true
```

Redeploy:
```bash
sam deploy
```
