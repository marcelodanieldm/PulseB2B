# 👻 Ghost System - Arquitectura Técnica

## 🎯 Visión General

Sistema de scraping distribuido que usa **GitHub Actions como infraestructura gratuita** para ejecutar análisis de leads cada hora, almacenar resultados en Supabase y notificar leads críticas vía webhooks.

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Actions (Cron)                    │
│                 Ejecuta cada hora (0 * * * *)                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Python Lead Scoring Script                     │
│         (scripts/lead_scoring.py --no-scraper)               │
│  • Lee companies_latam.csv (50 empresas)                    │
│  • Genera mock employee data                                │
│  • Calcula HPI scores (0-100)                               │
│  • Output: CSV + JSON reports                               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│            Node.js/TypeScript Processor                     │
│              (backend/src/lead-processor.ts)                 │
│                                                              │
│  1. Cache Check (scraping_cache table)                      │
│  2. Parse CSV results                                       │
│  3. Save to Supabase (lead_scores table)                    │
│  4. Identify critical leads (HPI ≥ 80)                      │
│  5. Send webhook notifications                              │
└─────────────┬──────────────────────┬─────────────────────────┘
              │                      │
              ▼                      ▼
┌──────────────────────┐  ┌──────────────────────────────────┐
│   Supabase Cloud     │  │   Webhook Notifier               │
│   (PostgreSQL)       │  │   (Slack/Discord)                │
│                      │  │                                  │
│  • lead_scores       │  │  • Auto-detect webhook type      │
│  • scraping_cache    │  │  • Rich formatting               │
│  • notification_logs │  │  • axios-retry (3 attempts)      │
│                      │  │  • 24h cooldown (no spam)        │
└──────────────────────┘  └──────────────────────────────────┘
```

## 📊 Data Flow

### 1. Input (CSV)
```
data/input/companies_latam.csv
├── company_name: "Kavak"
├── country: "MX"
├── last_funding_date: "2024-07-20"
├── funding_stage: "Series E"
└── last_funding_amount: 700000000
```

### 2. Processing (Python + HPI Algorithm)
```python
# Funding Recency Score (0-100)
if days_since_funding <= 180:
    score = 100 - (days/180) * 15  # 85-100

# Growth Urgency Score
if growth_6m < 5%:
    urgency = 95  # HIGH - necesita contratar YA
elif growth_6m > 20%:
    urgency = 20  # LOW - saturado

# Weighted HPI
hpi = (funding*0.40 + urgency*0.35 + size*0.15 + amount*0.10)

# BOOST: Fresh funding + low growth
if funding_score >= 85 and growth < 5%:
    hpi *= 1.2  # +20%
```

### 3. Storage (Supabase)
```typescript
interface LeadScore {
  company_name: string;
  country: 'MX' | 'BR';
  hpi_score: number;        // 0-100
  hpi_category: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  urgency_level: string;
  estimated_headcount_delta: number;
  // ... more fields
}
```

### 4. Notification (Webhook)
```json
{
  "blocks": [
    {
      "type": "header",
      "text": "🔥 CRITICAL LEAD DETECTED!"
    },
    {
      "type": "section",
      "fields": [
        { "text": "*Company:* Kavak" },
        { "text": "*HPI Score:* 85.20" },
        { "text": "*Urgency:* HIGH" }
      ]
    }
  ]
}
```

## 🔄 Cache-First Strategy

### Problema
Re-scrapear las mismas empresas cada hora desperdicia:
- ✗ API calls (rate limits)
- ✗ Tiempo de ejecución
- ✗ GitHub Actions minutos

### Solución
**Cache de 7 días** en tabla `scraping_cache`

```typescript
// Check before scraping
const sevenDaysAgo = new Date();
sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);

const { data } = await supabase
  .from('scraping_cache')
  .select('last_scraped_at')
  .eq('company_name', 'Kavak')
  .single();

if (data && new Date(data.last_scraped_at) > sevenDaysAgo) {
  console.log('✓ Using cached data');
  return; // Skip scraping
}

// Scrape and update cache
await scrapeCompany('Kavak');
await supabase.from('scraping_cache').upsert({
  company_name: 'Kavak',
  last_scraped_at: new Date().toISOString(),
  scrape_count: existingCount + 1
});
```

### Beneficios
- ✅ Reduce 86% de scrapes (7 días / 24 horas = ~86%)
- ✅ Evita rate limits
- ✅ Mantiene datos frescos (1 semana)

## 🔔 Webhook Notification System

### Arquitectura

```typescript
class WebhookNotifier {
  private axiosInstance: AxiosInstance;
  
  constructor() {
    // axios-retry configuration
    axiosRetry(this.axiosInstance, {
      retries: 3,
      retryDelay: exponentialDelay, // 1s, 2s, 4s
      retryCondition: (error) => {
        return error.response?.status >= 500 ||
               isNetworkError(error);
      }
    });
  }
}
```

### Flujo de Notificación

```
Lead HPI ≥ 80
    ↓
Check notification_logs
    ↓
Already notified in last 24h?
    ├─ YES → Skip (avoid spam)
    └─ NO  → Continue
         ↓
    Detect webhook type
         ↓
    ┌────┴────┐
    ↓         ↓
  Slack    Discord
    │         │
    └────┬────┘
         ↓
   Send POST request
    (with 3 retries)
         ↓
    Log result in
  notification_logs
```

### Retry Logic

```typescript
// Attempt 1: Immediate
POST /webhook → Error 503

// Attempt 2: Wait 1s
setTimeout(1000)
POST /webhook → Error 503

// Attempt 3: Wait 2s
setTimeout(2000)
POST /webhook → Error 503

// Attempt 4: Wait 4s (final)
setTimeout(4000)
POST /webhook → Success ✓
```

## 🗄️ Database Schema

### Table: `lead_scores`

```sql
CREATE TABLE lead_scores (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_name TEXT NOT NULL,
  country TEXT NOT NULL CHECK (country IN ('MX', 'BR')),
  hpi_score NUMERIC NOT NULL CHECK (hpi_score BETWEEN 0 AND 100),
  hpi_category TEXT NOT NULL CHECK (hpi_category IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')),
  urgency_level TEXT NOT NULL,
  employee_count INTEGER NOT NULL,
  estimated_headcount_delta INTEGER NOT NULL,
  funding_recency_score NUMERIC NOT NULL,
  growth_urgency_score NUMERIC NOT NULL,
  last_funding_date TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(company_name, country)
);

-- Indexes for performance
CREATE INDEX idx_lead_scores_hpi ON lead_scores(hpi_score DESC);
CREATE INDEX idx_lead_scores_company ON lead_scores(company_name, country);
```

### Table: `scraping_cache`

```sql
CREATE TABLE scraping_cache (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_name TEXT NOT NULL,
  country TEXT NOT NULL,
  last_scraped_at TIMESTAMPTZ NOT NULL,
  scrape_count INTEGER DEFAULT 1,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(company_name, country)
);

CREATE INDEX idx_scraping_cache_last_scraped ON scraping_cache(last_scraped_at);
```

### Table: `notification_logs`

```sql
CREATE TABLE notification_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_name TEXT NOT NULL,
  hpi_score NUMERIC NOT NULL,
  webhook_url TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('success', 'failed', 'retrying')),
  retry_count INTEGER DEFAULT 0,
  error_message TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_notification_logs_company ON notification_logs(company_name, created_at DESC);
CREATE INDEX idx_notification_logs_status ON notification_logs(status, created_at DESC);
```

## ⚡ Performance Optimization

### 1. Parallel Processing
```typescript
// Process leads in batches
const BATCH_SIZE = 10;
for (let i = 0; i < leads.length; i += BATCH_SIZE) {
  const batch = leads.slice(i, i + BATCH_SIZE);
  await Promise.all(batch.map(lead => saveToSupabase(lead)));
}
```

### 2. Connection Pooling
```typescript
// Supabase client reuses connections
const client = createClient(url, key); // Singleton
```

### 3. CSV Streaming (future)
```typescript
// For large files (1000+ companies)
import { parse } from 'csv-parse';

fs.createReadStream('large.csv')
  .pipe(parse())
  .on('data', (row) => processLead(row));
```

## 🔐 Security Best Practices

### 1. Environment Variables
```bash
# Never commit these!
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGc...
WEBHOOK_URL=https://hooks.slack.com/...
```

### 2. GitHub Secrets
```yaml
# Encrypted in GitHub
env:
  SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
  SUPABASE_ANON_KEY: ${{ secrets.SUPABASE_ANON_KEY }}
```

### 3. Supabase RLS (Row Level Security)
```sql
-- Only allow inserts/updates from service role
ALTER TABLE lead_scores ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow service role all" ON lead_scores
  FOR ALL USING (auth.role() = 'service_role');
```

### 4. Webhook Validation
```typescript
// Validate webhook URL format
if (!url.match(/^https:\/\/(hooks\.slack\.com|discord\.com)/)) {
  throw new Error('Invalid webhook URL');
}
```

## 📊 Monitoring & Observability

### 1. GitHub Actions Logs
```yaml
- name: 📊 Summary
  run: |
    echo "⏰ Executed at: $(date)"
    echo "🔄 Run number: ${{ github.run_number }}"
    echo "📈 Leads processed: $LEAD_COUNT"
```

### 2. Supabase Dashboard Queries
```sql
-- Top leads this week
SELECT company_name, hpi_score, created_at
FROM lead_scores
WHERE created_at > NOW() - INTERVAL '7 days'
ORDER BY hpi_score DESC;

-- Notification success rate
SELECT 
  status,
  COUNT(*) as count,
  ROUND(AVG(retry_count), 2) as avg_retries
FROM notification_logs
GROUP BY status;

-- Cache hit rate
SELECT 
  COUNT(*) as total_checks,
  SUM(CASE WHEN scrape_count > 1 THEN 1 ELSE 0 END) as cache_hits
FROM scraping_cache;
```

### 3. Webhook Logs
```typescript
console.log(`Sending notification for ${lead.company_name}`);
console.log(`HPI: ${lead.hpi_score} | Urgency: ${lead.urgency_level}`);
console.log(`Webhook type: ${webhookType}`);
console.log(`Retry count: ${retryCount}`);
```

## 🚀 Deployment Checklist

- [ ] Create Supabase project
- [ ] Run SQL schema migrations
- [ ] Create Slack/Discord webhook
- [ ] Configure GitHub Secrets
- [ ] Test workflow manually (workflow_dispatch)
- [ ] Verify logs in Actions tab
- [ ] Check data in Supabase dashboard
- [ ] Confirm webhook notifications received
- [ ] Enable hourly cron schedule
- [ ] Monitor first 24 hours

## 📈 Scaling Considerations

### Current Limits (Free Tier)
- GitHub Actions: 2,000 minutes/month
- Supabase: 500 MB storage, 2 GB bandwidth
- Execution time: ~15 seconds per run

### Capacity
- **50 companies** × **24 runs/day** = 1,200 checks/day
- **30 days** × **~10 minutes/day** = 300 minutes/month (15% of free tier)
- Can scale to **500+ companies** without hitting limits

### Future Optimizations
1. **Conditional execution**: Only run if CSV changed
2. **Multi-region**: Separate jobs for MX and BR
3. **Incremental processing**: Delta updates only
4. **Parallel workflows**: Multiple jobs for different company segments

## 🔮 Future Enhancements

- [ ] Real-time web scraping with Playwright
- [ ] Multiple webhook destinations (Telegram, Email)
- [ ] Admin dashboard for cache management
- [ ] A/B testing for notification formats
- [ ] ML model integration for HPI improvement
- [ ] Historical trend analysis
- [ ] API endpoints for external integrations

---

**Última actualización**: Diciembre 2025  
**Versión**: 1.0.0  
**Autor**: PulseB2B Backend Team
