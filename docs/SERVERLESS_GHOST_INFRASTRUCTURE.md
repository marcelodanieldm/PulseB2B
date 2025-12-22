# 👻 Serverless Ghost Infrastructure

**Automated Market Intelligence Pipeline for US Tech → LATAM Offshore Hiring**

Complete serverless solution using GitHub Actions + Supabase to detect US tech companies expanding to Brazil/LATAM through free OSINT sources.

---

## 🎯 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│              GitHub Actions (Every 6 Hours)                  │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ SEC.gov RSS  │  │ LinkedIn via │  │  OSINT News  │     │
│  │  Form D      │  │ Google Search│  │  Scraping    │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                  │                  │             │
│         └──────────────────┴──────────────────┘             │
│                            │                                │
│                  ┌─────────▼─────────┐                     │
│                  │  Consolidate &    │                     │
│                  │  Push to Supabase │                     │
│                  └─────────┬─────────┘                     │
└────────────────────────────┼─────────────────────────────┘
                             │
                             ▼
              ┌──────────────────────────┐
              │    Supabase (Postgres)   │
              │                          │
              │  - companies             │
              │  - funding_rounds        │
              │  - job_postings          │
              │  - news_articles         │
              │  - lead_scores           │
              │                          │
              │  Edge Functions:         │
              │  - news-webhook          │
              │  - lead-scoring          │
              └──────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Supabase Setup

#### Create Supabase Project
1. Go to [supabase.com](https://supabase.com)
2. Create new project
3. Note your **Project URL** and **Service Role Key**

#### Run Database Schema
```bash
# Copy the SQL from supabase/schema.sql
# Paste into Supabase SQL Editor and execute
# This creates all tables, indexes, views, and triggers
```

#### Deploy Edge Functions
```bash
# Install Supabase CLI
npm install -g supabase

# Login
supabase login

# Link your project
supabase link --project-ref YOUR_PROJECT_REF

# Deploy Edge Functions
supabase functions deploy news-webhook
supabase functions deploy lead-scoring
```

### 2. GitHub Secrets Configuration

Add these secrets to your GitHub repository:

```
Settings → Secrets and variables → Actions → New repository secret
```

**Required Secrets:**
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Your Supabase service role key (NOT anon key)
- `SLACK_WEBHOOK_URL` - (Optional) For notifications

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- `googlenews` - Free news scraping
- `feedparser` - SEC.gov RSS parsing
- `beautifulsoup4` - HTML parsing
- `requests` - HTTP requests
- `textblob` - Sentiment analysis
- `nltk` - NLP processing

### 4. Enable GitHub Actions

The workflow at `.github/workflows/serverless-ghost-pipeline.yml` runs automatically every 6 hours (00:00, 06:00, 12:00, 18:00 UTC).

To trigger manually:
```bash
# Go to Actions tab in GitHub
# Select "Ghost Pipeline - Market Intelligence"
# Click "Run workflow"
```

---

## 📊 Data Sources (All Free)

### 1. SEC.gov RSS Feed
- **What**: Form D filings (private securities offerings)
- **Why**: Detect US tech company funding rounds
- **URL**: `https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=D&company=&dateb=&owner=include&count=100&output=atom`
- **Rate Limit**: None (RSS feed)
- **Script**: `src/ghost_sec_rss_scraper.py`

### 2. LinkedIn Jobs via Google Search
- **What**: LATAM job postings from US tech companies
- **Why**: Detect offshore hiring expansion
- **Query**: `site:linkedin.com/jobs/view "São Paulo" OR "Rio de Janeiro" software engineer`
- **Rate Limit**: Use random delays (2-5 seconds)
- **Script**: `src/ghost_linkedin_google_scraper.py`

### 3. Google News (OSINT)
- **What**: Company news for lead scoring
- **Why**: Detect expansion, layoffs, funding announcements
- **Library**: `googlenews` (no API key needed)
- **Rate Limit**: None
- **Script**: `src/osint_lead_scorer.py`

---

## 🔧 Components

### Python Scripts

#### 1. **ghost_supabase_client.py**
REST API client for Supabase PostgreSQL
```python
from ghost_supabase_client import GhostSupabaseClient

client = GhostSupabaseClient(url, key)
client.insert_companies([{...}])
client.insert_funding_rounds([{...}])
```

#### 2. **ghost_sec_rss_scraper.py**
Scrapes SEC.gov RSS feed for Form D filings
```python
from ghost_sec_rss_scraper import SECRSSScraper

scraper = SECRSSScraper()
filings = scraper.scrape_form_d_feed(max_entries=100)
scraper.push_to_supabase(filings)
```

#### 3. **ghost_linkedin_google_scraper.py**
Scrapes LinkedIn jobs via Google Search (no API needed)
```python
from ghost_linkedin_google_scraper import LinkedInGoogleScraper

scraper = LinkedInGoogleScraper()
jobs = scraper.scrape_latam_jobs(
    keywords=["software engineer", "backend developer"],
    locations=["São Paulo", "Rio de Janeiro"]
)
```

#### 4. **ghost_osint_pipeline.py**
Orchestrates OSINT lead scoring and pushes to Supabase
```python
from ghost_osint_pipeline import GhostOSINTPipeline

pipeline = GhostOSINTPipeline()
results = pipeline.run_market_scan(
    company_names=["OpenAI", "Anthropic", ...],
    days_lookback=30
)
```

#### 5. **ghost_supabase_pusher.py**
Consolidates GitHub Actions artifacts and batch inserts
```bash
python src/ghost_supabase_pusher.py artifacts/
```

### Supabase Edge Functions (TypeScript/Deno)

#### 1. **news-webhook** (`supabase/functions/news-webhook/index.ts`)
Handles incoming news webhooks from external sources
- Validates payload
- Detects duplicates
- Inserts news articles
- Creates funding records if detected
- Returns status

**Invoke:**
```bash
curl -X POST https://YOUR_PROJECT.supabase.co/functions/v1/news-webhook \
  -H "Authorization: Bearer YOUR_ANON_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "OpenAI",
    "title": "OpenAI raises $10B Series C",
    "url": "https://...",
    "published": "2024-01-15T10:00:00Z"
  }'
```

#### 2. **lead-scoring** (`supabase/functions/lead-scoring/index.ts`)
Calculates lead score for a company based on signals
- Funding recency (+50 points if < 90 days)
- Large funding rounds (+30 points if > $50M)
- Job postings (+5 points each, max +50)
- Positive news (+15 points each)
- Negative news (-30 points each)
- Priority: critical (80+), high (60+), medium (40+), low (<40)

**Invoke:**
```bash
curl -X POST https://YOUR_PROJECT.supabase.co/functions/v1/lead-scoring \
  -H "Authorization: Bearer YOUR_ANON_KEY" \
  -H "Content-Type: application/json" \
  -d '{"company_name": "OpenAI"}'
```

---

## 🗄️ Database Schema

### Tables

#### `companies`
Market intelligence company profiles
- `company_name` - Unique identifier
- `industry`, `country`, `city`
- `funding_amount`, `funding_stage`
- `sec_cik` - SEC Central Index Key
- `linkedin_url`

#### `funding_rounds`
SEC Form D filings and funding announcements
- `company_name` - Foreign key (soft)
- `funding_type` - "Series A", "Series B", etc.
- `amount_usd` - Funding amount
- `announced_date` - Filing date
- `sec_accession_number` - Unique SEC identifier

#### `job_postings`
LinkedIn jobs scraped via Google Search
- `job_id` - Unique LinkedIn job ID
- `company_name` - Employer
- `title`, `description`, `location`
- `remote_allowed` - Boolean
- `posted_date` - Job posting date

#### `news_articles`
OSINT news for lead scoring
- `company_name` - Subject company
- `title`, `description`
- `event_type` - "funding", "expansion", "layoffs", etc.
- `sentiment_score` - -1.0 to +1.0

#### `lead_scores`
Automated lead scoring results
- `company_name` - Scored company
- `score` - 0-100 integer
- `priority` - "critical", "high", "medium", "low"
- `factors` - Array of scoring reasons
- `calculated_at` - Timestamp

#### `pipeline_runs`
GitHub Actions execution logs
- `pipeline_type` - Job name
- `status` - "running", "completed", "failed"
- `records_processed`, `records_inserted`
- `error_message`

### Views

#### `high_priority_leads`
Companies with critical/high priority scores + metrics
```sql
SELECT * FROM high_priority_leads
WHERE score >= 80
ORDER BY score DESC;
```

#### `recent_activity`
Combined view of funding + jobs + news (last 30 days)
```sql
SELECT * FROM recent_activity
WHERE activity_type = 'funding'
AND activity_date > NOW() - INTERVAL '7 days';
```

---

## ⚙️ GitHub Actions Workflow

### Schedule
Runs every 6 hours: **00:00, 06:00, 12:00, 18:00 UTC**

Cron: `0 */6 * * *`

### Jobs

#### 1. **sec-funding-scraper**
- Scrapes SEC.gov RSS for Form D filings
- Saves to `artifacts/sec_funding.json`
- Runtime: ~2 minutes

#### 2. **linkedin-jobs-scraper**
- Searches LinkedIn via Google for LATAM jobs
- Targets: Brazil (São Paulo, Rio), Mexico (CDMX, Guadalajara)
- Saves to `artifacts/linkedin_jobs.json`
- Runtime: ~5 minutes

#### 3. **osint-lead-scoring**
- Scrapes Google News for company intel
- Calculates heuristic lead scores
- Saves to `artifacts/osint_news.json` + `artifacts/lead_scores.json`
- Runtime: ~3 minutes

#### 4. **news-intelligence**
- Runs full OSINT pipeline via `ghost_osint_pipeline.py`
- Directly pushes to Supabase (no artifacts)
- Runtime: ~4 minutes

#### 5. **push-to-supabase**
- Consolidates all JSON artifacts
- Batch inserts to Supabase tables
- Uses `ghost_supabase_pusher.py`
- Runtime: ~1 minute

#### 6. **notify**
- Sends Slack notification with stats
- Includes success/failure status
- Runtime: ~30 seconds

**Total Pipeline Runtime:** ~15 minutes

---

## 🎯 Lead Scoring Algorithm

### Scoring Factors

| Signal | Points | Description |
|--------|--------|-------------|
| **Funding Round (< 90 days)** | +50 | Recent funding = hiring budget |
| **Large Round (> $50M)** | +30 | More capital = aggressive growth |
| **Job Posting** | +5 each | Max +50 total |
| **Expansion News** | +50 | "Opens LATAM office" |
| **Hiring News** | +50 | "Plans to hire 100 engineers" |
| **Positive News** | +15 | General positive sentiment |
| **Layoff News** | -100 | Cost-cutting mode |
| **Bankruptcy News** | -150 | Company in trouble |
| **Negative News** | -30 | General negative sentiment |

### Priority Levels
- **Critical** (80-100): Immediate outreach
- **High** (60-79): Priority follow-up
- **Medium** (40-59): Monitor closely
- **Low** (0-39): Keep on radar

### Example Calculation
```
Company: "Stripe"
- Recent Series H ($50M) → +50 points
- Large round → +30 points
- 8 job postings in Brazil → +40 points
- Expansion news ("Opens São Paulo office") → +50 points
- Total: 170 points → Capped at 100 → CRITICAL
```

---

## 🔒 Security & Best Practices

### API Keys
- ✅ Store in GitHub Secrets (never commit)
- ✅ Use Supabase **service_role** key for GitHub Actions
- ✅ Use Supabase **anon** key for frontend/public access
- ❌ Never expose service_role key in client-side code

### Rate Limiting
- SEC.gov RSS: No limits (official feed)
- Google Search: Random 2-5 second delays between requests
- Google News: Batch requests, max 10 companies/minute
- Supabase: Batch inserts (50 records/query)

### Error Handling
- All scripts have try/catch with graceful degradation
- Pipeline continues even if one job fails
- Duplicate detection on insert (unique constraints)
- Logs stored in `pipeline_runs` table

### Privacy
- Only public data sources used
- No personal data collected
- Company-level intelligence only
- GDPR compliant (public business information)

---

## 📈 Monitoring & Debugging

### Check Pipeline Status

**Via Supabase:**
```sql
SELECT *
FROM pipeline_runs
ORDER BY started_at DESC
LIMIT 10;
```

**Via GitHub Actions:**
1. Go to "Actions" tab
2. Select latest "Ghost Pipeline" run
3. View job logs

### Check Lead Scores
```sql
SELECT 
  company_name,
  score,
  priority,
  factors,
  calculated_at
FROM lead_scores
WHERE priority IN ('critical', 'high')
ORDER BY score DESC;
```

### Check Recent Activity
```sql
SELECT *
FROM recent_activity
WHERE activity_date > NOW() - INTERVAL '7 days'
ORDER BY activity_date DESC;
```

### Common Issues

**"Supabase connection failed"**
- Check `SUPABASE_URL` and `SUPABASE_KEY` in GitHub Secrets
- Verify service_role key (not anon key)
- Ensure Supabase project is not paused

**"Google Search blocked"**
- Add random user agents to `ghost_linkedin_google_scraper.py`
- Increase delay between requests (5-10 seconds)
- Use residential proxy (optional, paid)

**"SEC scraper returns no results"**
- Check SEC.gov is accessible (not under maintenance)
- Verify RSS feed URL is correct
- Check firewall/network restrictions

---

## 🚀 Advanced Usage

### Custom Company List
Edit `.github/workflows/serverless-ghost-pipeline.yml`:
```yaml
env:
  TARGET_COMPANIES: "OpenAI,Anthropic,Scale AI,Perplexity,Databricks"
```

### Change Schedule
Edit cron expression in workflow file:
```yaml
schedule:
  - cron: '0 */12 * * *'  # Every 12 hours instead of 6
```

### Add Slack Notifications
1. Create Slack Incoming Webhook
2. Add `SLACK_WEBHOOK_URL` to GitHub Secrets
3. Webhook will receive pipeline stats after each run

### Extend Lead Scoring
Edit `supabase/functions/lead-scoring/index.ts`:
```typescript
// Add custom scoring factors
if (company_data.employee_count > 1000) {
  score += 20;
  factors.push("Large company (+20)");
}
```

---

## 📚 Related Documentation

- [OSINT Lead Scoring](./OSINT_LEAD_SCORING.md) - Free news-based lead scoring
- [Intent Classification Engine](./INTENT_CLASSIFICATION_ENGINE.md) - NLP for outsourcing intent
- [ML Engine](./ML_ENGINE.md) - Advanced predictive models
- [Ghost Architecture](./GHOST_ARCHITECTURE.md) - Technical deep dive

---

## 🤝 Contributing

This is a production-ready market intelligence system. To extend:

1. **Add new data sources**: Create new scraper in `src/ghost_*.py`
2. **Improve scoring**: Modify `lead-scoring` Edge Function
3. **Add regions**: Extend `ghost_linkedin_google_scraper.py` with new locations
4. **Enhance notifications**: Add Discord, Telegram, or email integrations

---

## ⚖️ License

MIT License - Free for commercial use

---

## 🎓 Learn More

Built for B2B sales teams targeting US tech companies expanding to LATAM. Uses only free, public data sources to maintain zero operational costs (except Supabase hosting).

**Questions?** Check the [QUICK_START_GHOST.md](./QUICK_START_GHOST.md) guide.
