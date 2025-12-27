#### Custom Grafana Panel Examples
- **Endpoint latency:**
	- Heatmap or time series panel using `http_request_duration_seconds_bucket` metric.
- **Availability (Uptime):**
	- Gauge or stat panel with percentage of 2xx responses vs total.
- **Errors per endpoint:**
	- Stacked bar panel with `http_requests_total{status=~"5.."}` grouped by endpoint.
- **Traffic per endpoint:**
	- Line panel with total requests per route.

#### Specific Alert Examples
- **High latency:**
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
- **Service down:**
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
- **Recurring 5xx errors:**
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
### 5. Dashboards & Alerts

#### Grafana Dashboards
- Connect Grafana to Prometheus to visualize FastAPI metrics:
	1. Add Prometheus as a datasource in Grafana.
	2. Import the official FastAPI/Prometheus dashboard or create a custom one.
	3. Example panels: endpoint latency, 5xx errors, throughput.

#### Prometheus Alertmanager Alerts
- Define alert rules in `prometheus.yml`:
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
- Configure Alertmanager to send notifications (email, Slack, Telegram, etc.).

---
## Monitoring & Observability

### 1. Basic Healthcheck
Endpoint to verify API is alive:
```bash
curl http://localhost:8000/health
```
Expected response:
```json
{"status": "ok"}
```

### 2. Application Logs
Logs are printed to stdout by default. To view in real time:
```bash
tail -f backend/logs/app.log
```
Or check the process output (useful in Docker/Kubernetes).

### 3. Prometheus Integration (metrics)
Expose metrics for Prometheus using [prometheus_fastapi_instrumentator](https://github.com/trallard/prometheus-fastapi-instrumentator):
```python
from prometheus_fastapi_instrumentator import Instrumentator
from app.main import app
Instrumentator().instrument(app).expose(app)
```
Then access:
```
http://localhost:8000/metrics
```

### 4. Sentry Integration (errors)
For error monitoring in production:
```python
import sentry_sdk
sentry_sdk.init(dsn="YOUR_SENTRY_DSN", traces_sample_rate=1.0)
```
Place this at the top of `app/main.py`.

---
# PulseB2B Backend - System Overview

## Overview

The PulseB2B backend is a modular, production-grade FastAPI application designed for scalable market intelligence, lead scoring, and global hiring analytics. It integrates legacy scrapers, ML models, and business logic into a unified, testable, and maintainable architecture.

---

## Key Components

### Services (app/services/)
- **global_hiring_score_service.py**: Calculates global hiring urgency and cost savings.
- **regional_economic_analyzer_service.py**: Detects regional arbitrage opportunities for cross-border hiring.
- **pulse_intelligence_engine_service.py**: Advanced NLP/ML engine for expansion and talent signals.
- **osint_lead_scorer.py**: Public signals and news-based lead scoring.
- **sec_rss_scraper.py / sec_edgar_scraper.py**: SEC Form D and RSS scraping.
- **ghost_supabase_client_service.py**: Secure Supabase client with mock mode.

### Utilities (app/utils/)
- **common.py**: Logging setup, safe dict access.
- **text.py**: Text cleaning and normalization.
- **lead_scoring_helpers.py**: HPI, report generation, headcount delta.

### Tasks (app/tasks/)
- **scheduler.py**: Background jobs and periodic tasks.

---


## API Endpoints

- `/intent-engine/analyze-company` : Multi-source company analysis (hiring, OSINT, SEC, news)
- `/scrapers/sec-formd` : SEC Form D scraping endpoint
- `/scrapers/osint-lead` : OSINT lead scoring endpoint
- `/regional/arbitrage` : Regional arbitrage calculation


### Endpoint Usage Examples

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
Expected response:
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
Expected response:
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
Expected response:
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
Expected response:
```json
{
	"source_country": "US",
	"target_country": "MX",
	"arbitrage_opportunity": true,
	"savings_estimate": 32000
}
```

---

## Deployment & CI/CD

- **Local development:**
	```bash
	cd backend
	uvicorn app.main:app --reload
	```
- **Automated tests:**
	```bash
	pytest tests --maxfail=1 --disable-warnings -q
	```
- **Continuous Integration:**
	- Recommended: GitHub Actions with jobs for lint, test, and build
	- Example workflow: `.github/workflows/backend-ci.yml`

### Production Deployment

- **Gunicorn + Uvicorn Workers (recommended):**
	```bash
	cd backend
	gunicorn app.main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --workers 4
	```
- **Environment variables:**
	- Set sensitive variables (.env) and credentials in the server environment.
- **Reverse Proxy:**
	- Use Nginx or similar for HTTPS and load balancing.
- **Scaling:**
	- Deploy with Docker/Kubernetes for high availability.

---

## Deployment & CI/CD

- **Local development:**
	```bash
	cd backend
	uvicorn app.main:app --reload
	```
- **Automated tests:**
	```bash
	pytest tests --maxfail=1 --disable-warnings -q
	```
- **Continuous Integration:**
	- Recommended: GitHub Actions with jobs for lint, test, and build
	- Example workflow: `.github/workflows/backend-ci.yml`

---

---

## Testing & Quality

- **Pytest**: All business logic, endpoints, and helpers covered
- **tests/conftest.py**: Ensures import paths for modular structure
- **Mocking**: All external dependencies (Supabase, APIs) support mock mode for safe testing

---

## Developer Notes

- All services are singletons for easy import and DI
- Logging is centralized and configurable
- All endpoints and services are ready for extension and background jobs

---

For diagrams, data flows, and extended documentation, see:
- `docs/GHOST_ARCHITECTURE.md`
- `docs/LEAD_ENRICHMENT_ARCHITECTURE.md`
- `README.md` (root)

**Last updated:** 2025-12-26
