# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Backend - Ghost System
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Sistema de scraping distribuido usando GitHub Actions como infraestructura gratuita
# Ejecuta el lead scoring cada hora, almacena en Supabase y notifica leads críticas

## 🏗️ Architecture

```
GitHub Actions (Cron Hourly)
        ↓
Python Lead Scoring Script
        ↓
Node.js/TypeScript Processor
        ↓
    ┌───┴────┐
    ↓        ↓
Supabase   Webhook (Slack/Discord)
(Storage)  (Notifications HPI > 80%)
```

## 📦 Tech Stack

- **Node.js 20** + TypeScript 5.3
- **Supabase** - PostgreSQL cloud database
- **axios-retry** - Network resilience (3 retries, exponential backoff)
- **Zod** - Runtime type validation
- **GitHub Actions** - Free cron infrastructure

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
npm install
```

### 2. Configure Supabase

#### A. Create Supabase Project
1. Go to https://app.supabase.com
2. Create new project
3. Copy **URL** and **Anon Key** from Settings > API

#### B. Run SQL Schema

Go to SQL Editor in Supabase dashboard and run:

```sql
-- Lead Scores Table
CREATE TABLE lead_scores (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_name TEXT NOT NULL,
  country TEXT NOT NULL,
  last_funding_date TEXT NOT NULL,
  funding_stage TEXT,
  last_funding_amount NUMERIC,
  employee_count INTEGER NOT NULL,
  estimated_headcount_delta INTEGER NOT NULL,
  hpi_score NUMERIC NOT NULL CHECK (hpi_score >= 0 AND hpi_score <= 100),
  hpi_category TEXT NOT NULL CHECK (hpi_category IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')),
  urgency_level TEXT NOT NULL,
  funding_recency_score NUMERIC NOT NULL,
  growth_urgency_score NUMERIC NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(company_name, country)
);

CREATE INDEX idx_lead_scores_hpi ON lead_scores(hpi_score DESC);
CREATE INDEX idx_lead_scores_company ON lead_scores(company_name, country);

-- Scraping Cache Table (prevents re-scraping within 7 days)
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

-- Notification Logs Table
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

### 3. Configure Webhooks

#### Option A: Slack Webhook

1. Go to https://api.slack.com/messaging/webhooks
2. Click "Create New App" > "From Scratch"
3. Enable "Incoming Webhooks"
4. Add to workspace and copy webhook URL
5. Format: `https://hooks.slack.com/services/T.../B.../XXX`

#### Option B: Discord Webhook

1. Go to your Discord server
2. Server Settings > Integrations > Webhooks
3. Create webhook
4. Copy webhook URL
5. Format: `https://discord.com/api/webhooks/123456789/abcdefg`

### 4. Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env`:

```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
WEBHOOK_URL=https://hooks.slack.com/services/T.../B.../XXX
CRITICAL_THRESHOLD=80
```

### 5. Test Locally

```bash
# Build TypeScript
npm run build

# Run processor
npm start

# Or run in dev mode
npm run dev
```

Expected output:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 PulseB2B Ghost System - Lead Processor
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏰ Started at: 2025-12-20T12:00:00.000Z

📋 Step 1: Checking scraping cache...
Cache check: 50/50 companies need scraping

📋 Step 2: Running lead scoring script...
[Python output...]

📋 Step 3: Loading results...
✓ Parsed 50 lead scores

📋 Step 4: Saving to Supabase...
✓ Saved: 50 leads

📋 Step 5: Checking for critical leads...
Found 9 critical leads to notify
✓ Notifications sent: 9

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Processing completed successfully
⏱️  Duration: 12.45s
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## 🤖 GitHub Actions Setup

### 1. Configure Secrets

Go to GitHub repository > Settings > Secrets and Variables > Actions

Add these secrets:

```
SUPABASE_URL          = https://xxxxx.supabase.co
SUPABASE_ANON_KEY     = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
WEBHOOK_URL           = https://hooks.slack.com/services/...
CRITICAL_THRESHOLD    = 80
```

### 2. Enable GitHub Actions

Workflow file: `.github/workflows/lead-scraping.yml`

Schedule: **Every hour** (cron: `0 * * * *`)

### 3. Manual Trigger (Testing)

1. Go to Actions tab in GitHub
2. Select "Lead Scoring Automation"
3. Click "Run workflow"

### 4. Monitor Runs

- View logs in Actions tab
- Download CSV/JSON artifacts
- Check Supabase database
- Monitor Slack/Discord for notifications

## 📊 Cache-First Logic

**Business Rule**: Don't re-scrape the same company more than once per week

Implementation:
1. Before scraping, check `scraping_cache` table
2. If `last_scraped_at` < 7 days ago, skip
3. After successful scrape, update cache with timestamp
4. Reduces API calls and avoids rate limits

```typescript
// Example cache check
const sevenDaysAgo = new Date();
sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);

const shouldScrape = lastScrapedAt < sevenDaysAgo;
```

## 🔔 Webhook Notifications

**Trigger**: Any lead with `hpi_score >= 80` (configurable)

**Features**:
- Auto-detects Slack vs Discord from URL
- Rich formatting with company details
- Retry logic (3 attempts with exponential backoff)
- Deduplication (won't notify same company within 24h)

**Slack Example**:
```
🔥 CRITICAL LEAD DETECTED!

Company: Kavak
Country: 🇲🇽 Mexico
HPI Score: 85.20 (CRITICAL)
Urgency: HIGH
Employees: 200
Hiring Delta: +16 (next 6m)
Last Funding: 2024-07-20

💡 Why Critical?
• Funding Recency Score: 92.50
• Growth Urgency Score: 95
```

## 🛠️ Development

### Project Structure

```
backend/
├── src/
│   ├── supabase-client.ts      # Database service + types
│   ├── webhook-notifier.ts     # Slack/Discord notifications
│   └── lead-processor.ts       # Main orchestrator
├── dist/                        # Compiled JS (git ignored)
├── package.json
├── tsconfig.json
└── .env.example
```

### Scripts

```bash
npm run build        # Compile TypeScript
npm start           # Run compiled JS
npm run dev         # Run with ts-node (development)
npm run process-leads  # Alias for dev
```

### Type Safety

All database types are validated with **Zod**:

```typescript
const LeadScoreSchema = z.object({
  company_name: z.string(),
  hpi_score: z.number().min(0).max(100),
  // ...
});

// Runtime validation
LeadScoreSchema.parse(lead); // Throws if invalid
```

## PulseB2B FastAPI Backend - Documentación

### Estructura principal
- `app/main.py`: entrypoint FastAPI
- `app/models/`: modelos SQLAlchemy
- `app/schemas/`: Pydantic schemas
- `app/views/`: routers/controllers (endpoints REST)
- `app/services/`: lógica de scraping, scoring, análisis
- `app/db/`: conexión y utilidades DB
- `app/tasks/`: tareas programadas/background (APScheduler)
- `app/utils/`: utilidades generales
- `tests/`: pruebas automáticas (pytest)

### Endpoints REST principales
- `/companies`: CRUD de compañías
- `/scrape/linkedin-jobs`: Scraping de empleos LinkedIn vía Google
- `/scrape/sec-formd`: Scraping de SEC Form D (funding)
- `/scrape/osint-pipeline`: Orquestador OSINT (POST, lista de compañías)
- `/scrape/linkedin-company`: Buscar LinkedIn de empresa
- `/analyze/intent`: Orquestador de análisis de intención (POST, compañía)
- `/analyze/hpi`: Hiring Potential Index (GET, fecha de funding)
- `/analyze/ghs`: Global Hiring Score (GET, funding y salario)
- `/generate/telegram-teaser`: Generador de resumen para Telegram (POST, compañía)

### Tareas programadas
- Scraping automático de LinkedIn y SEC cada día (ver `app/tasks/scheduler.py`)

### Pruebas automáticas
- Ejecuta `pytest` en la carpeta `backend` para validar servicios y lógica.

### Ejecución local
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Notas
- Personaliza los servicios y endpoints según tus necesidades.
- Integra tu base de datos real en `app/db/session.py`.
- Agrega más tareas programadas en `app/tasks/scheduler.py`.

## 🔍 Monitoring

### 1. Supabase Dashboard

Query leads:
```sql
-- Top 10 leads
SELECT company_name, country, hpi_score, hpi_category
FROM lead_scores
ORDER BY hpi_score DESC
LIMIT 10;

-- Scraping activity
SELECT company_name, last_scraped_at, scrape_count
FROM scraping_cache
ORDER BY last_scraped_at DESC;

-- Notification history
SELECT company_name, hpi_score, status, created_at
FROM notification_logs
ORDER BY created_at DESC
LIMIT 20;
```

### 2. GitHub Actions Logs

- View detailed execution logs
- Download artifacts (CSV/JSON reports)
- Monitor failures and retries

### 3. Webhook Notifications

- Instant alerts in Slack/Discord
- Only for critical leads (HPI >= 80)
- No spam (24h cooldown per company)

## ⚡ Performance

- **Execution Time**: ~10-15 seconds (50 companies, mock data)
- **GitHub Actions**: Free tier = 2,000 minutes/month
- **Cost**: $0 (completely free infrastructure)
- **Reliability**: axios-retry handles network failures
- **Scalability**: Can handle 1,000+ companies with pagination

## 🔐 Security

- ✅ Secrets stored in GitHub Actions (encrypted)
- ✅ Supabase uses Row Level Security (RLS)
- ✅ Webhook URLs are private
- ✅ No credentials in code
- ✅ `.env` file in `.gitignore`

## 🚨 Troubleshooting

### "SUPABASE_URL not defined"
- Check `.env` file exists in `backend/` folder
- Verify secrets are set in GitHub Actions

### "Python script failed"
- Check Python dependencies installed: `pip install -r requirements-scraper.txt`
- Verify `scripts/lead_scoring.py` exists

### "Webhook notification failed"
- Verify webhook URL is correct
- Check Slack/Discord webhook is active
- Review `notification_logs` table for errors

### "No companies need scraping"
- Cache working correctly! Companies scraped < 7 days ago
- Force scrape by clearing cache: `DELETE FROM scraping_cache;`

## 📈 Roadmap

- [ ] Add email notifications (SendGrid)
- [ ] Implement real-time web scraping with proxies
- [ ] Add ML model for HPI prediction improvement
- [ ] Create admin dashboard for cache management
- [ ] Add multiple webhook destinations (Telegram, etc.)
- [ ] Implement A/B testing for notification formats

## 📄 License

MIT

## 👥 Team

Built by PulseB2B Backend Team
