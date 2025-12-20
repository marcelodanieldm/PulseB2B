# 🎯 Lead Scoring System - LATAM

Sistema de **Lead Scoring Predictivo** para identificar empresas de México y Brasil con alta probabilidad de contratación IT.

## 🚀 Características

### 🔍 Web Scraping Inteligente
- **Google Search** + **LinkedIn** para extraer datos de empleados
- Scraping respetuoso con rate limiting (2-5 segundos entre requests)
- Fallback automático a estimaciones cuando el scraping falla
- Headers realistas para evitar bloqueos

### 📊 Hiring Potential Index (HPI)
Algoritmo propietario que calcula probabilidad de contratación (0-100) basado en:

1. **Funding Recency Score** (40% peso)
   - Último funding < 30 días: 100 pts
   - Último funding < 90 días: 95 pts
   - Último funding < 180 días: 85 pts
   - Decaimiento progresivo después

2. **Growth Urgency Score** (35% peso)
   - < 5% crecimiento en 6m: **95 pts (HIGH urgency)**
   - 5-10% crecimiento: 75 pts (Medium-High)
   - 10-20% crecimiento: 50 pts (Medium)
   - > 20% crecimiento: **20 pts (LOW urgency - saturados)**

3. **Company Size Factor** (15% peso)
   - 50-200 empleados: Prime hiring phase (85 pts)
   - 20-50 empleados: Growing startup (60 pts)
   - 200-500 empleados: Large company (75 pts)

4. **Funding Amount Score** (10% peso)
   - Proporcional al monto de inversión

### 🎯 Lógica de Negocio Clave

**INSIGHT CRÍTICO**: Empresa con funding reciente + crecimiento bajo = **ALTA URGENCIA**
```python
if funding_recency < 6 meses AND employee_growth_6m < 5%:
    HPI = CRITICAL (80-100)
    Razón: "Tienen capital pero no están contratando - necesitan urgente!"
```

### 📈 Categorías de Leads

- **CRITICAL** (HPI ≥ 80): Contactar inmediatamente
- **HIGH** (HPI 65-79): Lead prioritario
- **MEDIUM** (HPI 50-64): Lead calificado
- **LOW** (HPI < 50): Monitorear

## 🛠️ Instalación

### 1. Instalar dependencias

```bash
pip install -r requirements-scraper.txt
```

Librerías principales:
- `beautifulsoup4` - Web scraping
- `requests` - HTTP requests
- `pandas` - Manipulación de datos
- `scikit-learn` - Normalización de scores
- `lxml` - Parsing HTML

### 2. Preparar datos de entrada

Crear CSV con estas columnas:
```csv
company_name,website,country,last_funding_date,last_funding_amount,funding_stage
Clip,https://clip.mx,MX,2024-09-15,75000000,Series C
Nubank,https://nubank.com.br,BR,2024-11-10,500000000,Series G
```

**Columnas requeridas**:
- `company_name`: Nombre de la empresa
- `country`: MX (México) o BR (Brasil)
- `last_funding_date`: Fecha última ronda (YYYY-MM-DD)

**Columnas opcionales**:
- `website`: Sitio web
- `last_funding_amount`: Monto en USD
- `funding_stage`: Seed, Series A, Series B, etc.

## 🚀 Uso

### Modo Testing (con datos mock - SIN web scraping)

```bash
python scripts/lead_scoring.py \
    --input data/input/companies_latam.csv \
    --output data/output/lead_scoring \
    --no-scraper \
    --sample 10
```

**Recomendado para**:
- Probar el sistema rápidamente
- Testing sin consumir APIs
- Desarrollo y debugging

### Modo Producción (con web scraping real)

```bash
python scripts/lead_scoring.py \
    --input data/input/companies_latam.csv \
    --output data/output/lead_scoring
```

**⚠️ Advertencias**:
- Proceso lento (3-6 seg por empresa)
- 50 empresas ≈ 3-5 minutos
- Google puede bloquear tras muchas requests
- Usar con moderación

### Procesar subset de empresas

```bash
python scripts/lead_scoring.py \
    --input data/input/companies_latam.csv \
    --sample 20
```

## 📊 Output - Reportes Generados

El sistema genera **4 reportes** en `data/output/lead_scoring/`:

### 1. `lead_scoring_report_YYYYMMDD_HHMMSS.csv`
Reporte completo con todas las empresas:
```csv
lead_rank,company_name,country,last_funding_date,current_employees,growth_6m_pct,estimated_headcount_delta,hiring_probability_score,hpi_category,urgency_level,recommended_action
1,Clip,MX,2024-09-15,245,3.2,15,87.5,CRITICAL,HIGH,Contact immediately - high hiring urgency
2,Nubank,BR,2024-11-10,1250,4.8,75,85.2,CRITICAL,HIGH,Contact immediately - high hiring urgency
```

### 2. `top_leads_YYYYMMDD_HHMMSS.csv`
Solo empresas con HPI ≥ 65 (leads prioritarios)

### 3. `critical_leads_YYYYMMDD_HHMMSS.csv`
Solo empresas con HPI ≥ 80 (máxima urgencia)

### 4. `summary_stats_YYYYMMDD_HHMMSS.json`
Estadísticas agregadas:
```json
{
  "total_companies": 50,
  "critical_leads": 8,
  "high_leads": 12,
  "medium_leads": 18,
  "low_leads": 12,
  "avg_hpi_score": 62.5,
  "avg_growth_6m": 8.3,
  "companies_recent_funding": 15,
  "total_estimated_hires": 450
}
```

## 📋 Ejemplo de Salida

```
================================================================================
LEAD SCORING REPORT SUMMARY
================================================================================

📊 Total Companies Analyzed: 50

🎯 HPI Distribution:
   CRITICAL:   8 companies (≥80 HPI)
   HIGH:      12 companies (65-79 HPI)
   MEDIUM:    18 companies (50-64 HPI)
   LOW:       12 companies (<50 HPI)

📈 Hiring Metrics:
   Average HPI Score: 62.45
   Average Employee Count: 287
   Average 6m Growth: 8.3%
   Estimated Total Hires (6m): 450

🌎 Geographic Distribution:
   MX:  25 companies
   BR:  25 companies

🔥 High Urgency Leads: 15
💰 Recent Funding (<6m): 18

================================================================================

🏆 TOP 10 LEADS TO CONTACT:
--------------------------------------------------------------------------------

 1. Clip (MX)
    HPI: 87.5 | Category: CRITICAL
    Employees: 245 (+3.2% in 6m)
    Est. Hiring: 15 positions
    Action: Contact immediately - high hiring urgency

 2. Nubank (BR)
    HPI: 85.2 | Category: CRITICAL
    Employees: 1250 (+4.8% in 6m)
    Est. Hiring: 75 positions
    Action: Contact immediately - high hiring urgency
```

## 🧮 Algoritmo de Cálculo

### Paso 1: Scoring de Componentes

```python
# 1. Funding Recency Score (0-100)
days_since_funding = (now - last_funding_date).days
if days_since_funding <= 180:
    funding_score = 85-100  # Recent funding

# 2. Growth Urgency Score (0-100)
if growth_6m_pct < 5:
    urgency_score = 95  # HIGH urgency
elif growth_6m_pct > 20:
    urgency_score = 20  # LOW urgency (saturated)

# 3. Size Factor Score (0-100)
if 50 <= employees <= 200:
    size_score = 85  # Prime hiring phase
```

### Paso 2: Weighted HPI

```python
# Caso CRÍTICO: Funding reciente + bajo crecimiento
if funding_score >= 85 and growth_6m_pct < 5:
    raw_hpi = (
        funding_score * 0.40 +      # 40% weight
        urgency_score * 0.35 +      # 35% weight
        size_score * 0.15 +         # 15% weight
        funding_amount_score * 0.10 # 10% weight
    )
    hpi = raw_hpi * 1.2  # Boost by 20%

# Caso NORMAL
else:
    hpi = (
        funding_score * 0.30 +
        urgency_score * 0.30 +
        size_score * 0.25 +
        funding_amount_score * 0.15
    )
```

### Paso 3: Estimated Headcount Delta

```python
if hpi >= 80:
    estimated_growth = max(15%, past_growth * 1.5)
elif hpi >= 65:
    estimated_growth = max(10%, past_growth * 1.2)
else:
    estimated_growth = past_growth

headcount_delta = current_employees * estimated_growth / 100
```

## 🔧 Configuración Avanzada

### Ajustar rate limiting

```python
# En src/web_scraper.py
scraper = LinkedInScraper(delay_range=(5, 10))  # Más conservador
```

### Modificar pesos del HPI

```python
# En src/hpi_calculator.py, método calculate_hpi()
raw_hpi = (
    funding_score * 0.50 +      # Aumentar peso funding
    urgency_score * 0.25 +      # Reducir peso urgency
    size_score * 0.15 +
    funding_amount_score * 0.10
)
```

### Cambiar umbrales de urgencia

```python
# En src/hpi_calculator.py, método calculate_growth_urgency_score()
if growth_6m_pct < 3:  # Más estricto (antes 5%)
    return {'urgency_score': 95.0, 'urgency_level': 'HIGH'}
```

## 🎯 Casos de Uso

### 1. Identificar leads hot para sales
```bash
# Generar lista de empresas CRITICAL
python scripts/lead_scoring.py \
    --input data/input/companies_latam.csv \
    --output data/output/lead_scoring

# Output: critical_leads_*.csv con empresas HPI ≥ 80
```

### 2. Priorizar pipeline de prospección
```bash
# Todos los leads ordenados por HPI
# Output: lead_scoring_report_*.csv con ranking
```

### 3. Estimar demanda de mercado
```bash
# Ver summary_stats_*.json
# Campo: "total_estimated_hires": 450
```

### 4. Segmentar por geografía
```bash
# Filtrar reporte por country column
import pandas as pd
df = pd.read_csv('lead_scoring_report_*.csv')
mx_leads = df[df['country'] == 'MX']
```

## 📈 Métricas de Validación

### Success Rate del Scraper
- **Real scraping**: 40-60% (depende de Google)
- **Fallback estimations**: 100% (siempre genera datos)

### Precisión del HPI
Validar contra conversiones reales:
```python
# Calcular correlación HPI vs conversión
from scipy.stats import pearsonr
correlation = pearsonr(df['hiring_probability_score'], df['converted'])
```

### Performance
- **50 empresas** con scraping: ~5 minutos
- **50 empresas** sin scraping: <10 segundos
- **500 empresas** con scraping: ~50 minutos (usar batches)

## 🚨 Troubleshooting

### Error: "No LinkedIn found"
→ Scraping bloqueado por Google
→ Solución: Aumentar delay_range o usar VPN

### Error: "Rate limit exceeded"
→ Demasiadas requests rápidas
→ Solución: Aumentar delay_range=(10, 15)

### Datos de empleados inexactos
→ LinkedIn requiere autenticación
→ Solución: Usar estimaciones (--no-scraper) o APIs pagadas

### CSV mal formateado
→ Verificar columnas requeridas
→ Solución: Validar con pandas antes de ejecutar

## 🔗 Integración con PulseB2B ML Engine

Los reportes son compatibles con el ML engine existente:

```python
# 1. Generar lead scoring
python scripts/lead_scoring.py --input companies.csv

# 2. Usar como input para ML predictions
python scripts/run_predictions.py \
    --input data/output/lead_scoring/lead_scoring_report_*.csv
```

## 📚 Referencias

- **BeautifulSoup Docs**: https://www.crummy.com/software/BeautifulSoup/
- **Pandas Docs**: https://pandas.pydata.org/docs/
- **Scikit-learn**: https://scikit-learn.org/stable/

## 👥 Autor

**Lead Data Scientist** - PulseB2B Team

---

**Built with Python, BeautifulSoup, and Data Science 📊**
