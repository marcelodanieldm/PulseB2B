#### Ejemplos de paneles personalizados en Grafana
- **Latencia de endpoints:**
  - Panel tipo heatmap o time series usando la métrica `http_request_duration_seconds_bucket`.
- **Disponibilidad (Uptime):**
  - Panel de gauge o stat con porcentaje de respuestas 2xx vs totales.
- **Errores por endpoint:**
  - Panel de barras apiladas con `http_requests_total{status=~"5.."}` agrupado por endpoint.
- **Tráfico por endpoint:**
  - Panel de líneas con el total de requests por ruta.

#### Ejemplos de alertas específicas
- **Latencia alta:**
  ```yaml
  - alert: HighLatency
    expr: histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, endpoint)) > 1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High latency detected"
      description: "p95 latency > 1s for 5 minutes."
  ```
- **Caída de disponibilidad:**
  ```yaml
  - alert: ServiceDown
    expr: sum(rate(http_requests_total{status!~"2.."}[5m])) by (endpoint) > 0
    for: 3m
    labels:
      severity: critical
    annotations:
      summary: "Service down"
      description: "Non-2xx responses detected."
  ```
- **Errores 5xx recurrentes:**
  ```yaml
  - alert: High5xxErrors
    expr: increase(http_requests_total{status=~"5.."}[10m]) > 10
    for: 10m
    labels:
      severity: critical
    annotations:
      summary: "High 5xx error rate"
      description: "More than 10 errors in 10 minutes."
  ```
### 5. Dashboards y Alertas

#### Dashboards con Grafana
- Conecta Grafana a Prometheus para visualizar métricas de FastAPI:
  1. Agrega Prometheus como datasource en Grafana.
  2. Importa el dashboard oficial de FastAPI/Prometheus o crea uno personalizado.
  3. Ejemplo de panel: latencia de endpoints, errores 5xx, throughput.

#### Alertas con Prometheus Alertmanager
- Define reglas de alerta en `prometheus.yml`:
  ```yaml
  groups:
    - name: fastapi-alerts
      rules:
        - alert: HighErrorRate
          expr: increase(http_requests_total{status=~"5.."}[5m]) > 5
          for: 5m
          labels:
            severity: critical
          annotations:
            summary: "High error rate detected"
            description: "More than 5 errors in 5 minutes."
  ```
- Configura Alertmanager para enviar notificaciones (email, Slack, Telegram, etc.).

---
## Monitoreo y Observabilidad

### 1. Healthcheck básico
Endpoint para verificar que la API está viva:
```bash
curl http://localhost:8000/health
```
Respuesta esperada:
```json
{"status": "ok"}
```

### 2. Logs de aplicación
Por defecto, los logs se imprimen en consola (stdout). Para verlos en tiempo real:
```bash
tail -f backend/logs/app.log
```
O bien, revisa la salida estándar del proceso (útil en Docker/Kubernetes).

### 3. Integración con Prometheus (métricas)
Puedes exponer métricas para Prometheus usando [prometheus_fastapi_instrumentator](https://github.com/trallard/prometheus-fastapi-instrumentator):
```python
from prometheus_fastapi_instrumentator import Instrumentator
from app.main import app
Instrumentator().instrument(app).expose(app)
```
Luego accede a:
```
http://localhost:8000/metrics
```

### 4. Integración con Sentry (errores)
Para monitoreo de errores en producción:
```python
import sentry_sdk
sentry_sdk.init(dsn="TU_SENTRY_DSN", traces_sample_rate=1.0)
```
Coloca esto al inicio de `app/main.py`.

---
# PulseB2B Backend - FastAPI Modular Architecture

## Arquitectura General

- **Framework:** FastAPI (Python 3.10+)
- **Patrón:** Modular MVC (services, routers, utils, tasks)
- **Persistencia:** Supabase (PostgreSQL, REST API)
- **Scrapers:** Integrados como servicios y endpoints
- **Tests:** Pytest, cobertura para endpoints y lógica de negocio

## Estructura de Carpetas

```
backend/
  app/
    services/      # Lógica de negocio, scrapers, ML, integración
    utils/         # Utilidades y helpers
    tasks/         # Tareas background y schedulers
    views/         # Routers y endpoints FastAPI
  tests/           # Pruebas automáticas (pytest)
```

## Servicios y Utilidades Clave

- **global_hiring_score_service.py**: Cálculo de urgencia y ahorro por contratación global
- **regional_economic_analyzer_service.py**: Detección de oportunidades de arbitraje regional
- **pulse_intelligence_engine_service.py**: Análisis avanzado de señales de expansión y talento
- **osint_lead_scorer.py**: Scoring OSINT de leads y noticias
- **sec_rss_scraper.py / sec_edgar_scraper.py**: Scraping de Form D y RSS de la SEC
- **ghost_supabase_client_service.py**: Cliente seguro para Supabase (mock incluido)
- **lead_scoring_helpers.py**: Utilidades para HPI, generación de reportes y headcount


## Endpoints y Flujos Principales

- `/intent-engine/analyze-company` : Orquestador de análisis multi-fuente (contratación, OSINT, SEC, noticias)
- `/scrapers/sec-formd` : Scraping de Form D (SEC)
- `/scrapers/osint-lead` : Scoring de leads por señales públicas
- `/regional/arbitrage` : Cálculo de oportunidades de arbitraje regional


### Ejemplos de uso de endpoints

#### 1. /intent-engine/analyze-company
```bash
curl -X POST "http://localhost:8000/intent-engine/analyze-company" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Acme Corp",
    "company_description": "SaaS startup expanding globally",
    "funding_amount": 10000000,
    "funding_stage": "series_a"
  }'
```
Respuesta esperada:
```json
{
  "company_name": "Acme Corp",
  "global_hiring_score": { ... },
  "recommendation": { ... },
  ...
}
```

#### 2. /scrapers/sec-formd
```bash
curl -X POST "http://localhost:8000/scrapers/sec-formd" \
  -H "Content-Type: application/json" \
  -d '{
    "cik": "0001234567",
    "year": 2024
  }'
```
Respuesta esperada:
```json
{
  "cik": "0001234567",
  "forms": [ { ... }, ... ]
}
```

#### 3. /scrapers/osint-lead
```bash
curl -X POST "http://localhost:8000/scrapers/osint-lead" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Acme Corp",
    "domain": "acme.com"
  }'
```
Respuesta esperada:
```json
{
  "company_name": "Acme Corp",
  "osint_score": 0.87,
  "signals": [ ... ]
}
```

#### 4. /regional/arbitrage
```bash
curl -X POST "http://localhost:8000/regional/arbitrage" \
  -H "Content-Type: application/json" \
  -d '{
    "source_country": "US",
    "target_country": "MX",
    "role": "Software Engineer"
  }'
```
Respuesta esperada:
```json
{
  "source_country": "US",
  "target_country": "MX",
  "arbitrage_opportunity": true,
  "savings_estimate": 32000
}
```

---

## Despliegue y CI/CD

- **Desarrollo local:**
  ```bash
  cd backend
  uvicorn app.main:app --reload
  ```
- **Pruebas automáticas:**
  ```bash
  pytest tests --maxfail=1 --disable-warnings -q
  ```
- **Integración continua:**
  - Recomendado: GitHub Actions con jobs para lint, test y build
  - Ejemplo de workflow: `.github/workflows/backend-ci.yml`

### Despliegue en producción

- **Gunicorn + Uvicorn Workers (recomendado):**
  ```bash
  cd backend
  gunicorn app.main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --workers 4
  ```
- **Variables de entorno:**
  - Configura variables sensibles (.env) y credenciales en el entorno del servidor.
- **Reverse Proxy:**
  - Usa Nginx o similar para servir HTTPS y balancear carga.
- **Escalado:**
  - Despliegue en Docker/Kubernetes recomendado para alta disponibilidad.

---

## Despliegue y CI/CD

- **Desarrollo local:**
  ```bash
  cd backend
  uvicorn app.main:app --reload
  ```
- **Pruebas automáticas:**
  ```bash
  pytest tests --maxfail=1 --disable-warnings -q
  ```
- **Integración continua:**
  - Recomendado: GitHub Actions con jobs para lint, test y build
  - Ejemplo de workflow: `.github/workflows/backend-ci.yml`

---

## Pruebas Automáticas

- Ejecutar todos los tests:
  ```bash
  cd backend
  pytest tests --maxfail=1 --disable-warnings -q
  ```
- Cobertura: endpoints, lógica de negocio, utilidades y helpers
- Configuración de imports asegurada vía `tests/conftest.py`

## Mocking y Seguridad

- Todos los servicios críticos soportan modo mock para ambientes sin credenciales (ej: Supabase)
- Logging centralizado y helpers para acceso seguro a datos

## Documentación Extendida

- Ver docs/ y archivos markdown raíz para diagramas, flujos y detalles de integración
- Ejemplo: `docs/GHOST_ARCHITECTURE.md`, `LEAD_ENRICHMENT_SYSTEM.md`, `ORACLE_IMPLEMENTATION_SUMMARY.md`

---

**Actualizado:** 26/12/2025
