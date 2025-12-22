# Ghost Crawler - Automated Scraping System 🕵️

## Overview

The **Ghost Crawler** is an intelligent, zero-cost automation system that scrapes LinkedIn job data using GitHub Actions, Google Custom Search API, and smart rate limiting to avoid IP bans and proxy costs.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              GITHUB ACTIONS (Every 23 Hours)                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
        ┌───────────────────┴───────────────────┐
        │                                       │
        ↓                                       ↓
┌──────────────────┐                  ┌─────────────────┐
│ Ghost Crawler    │                  │ Pulse Scorer    │
│ (Node.js)        │                  │ (Python)        │
│                  │                  │                 │
│ • Google CSE API │                  │ • TF-IDF        │
│ • LinkedIn Jobs  │ ──────→ CSV ──→  │ • Tech Stack    │
│ • Smart Delays   │                  │ • Red Flags     │
│ • Rate Limiting  │                  │ • Scoring       │
└──────────────────┘                  └─────────────────┘
                                               ↓
                                      ┌─────────────────┐
                                      │ Supabase Sync   │
                                      │ (Node.js)       │
                                      │                 │
                                      │ • Upsert Logic  │
                                      │ • Batch Process │
                                      │ • 40+ Filter    │
                                      └────────┬────────┘
                                               ↓
        ┌──────────────────────────────────────┴──────────────┐
        │                                                      │
        ↓                                                      ↓
┌──────────────────┐                              ┌────────────────────┐
│ Supabase DB      │                              │ Telegram Alerts    │
│                  │                              │                    │
│ • Companies      │                              │ • 90+ Score Only   │
│ • Pulse Scores   │                              │ • 24h Dedupe       │
│ • Timestamps     │                              │ • Max 10/run       │
└──────────────────┘                              └────────────────────┘
```

## Components

### 1. GitHub Actions Workflow (`.github/workflows/daily_scrape.yml`)

**Schedule**: Every 23 hours (not 24 to avoid detection patterns)
**Trigger**: `cron: '17 */23 * * *'` + manual dispatch

**Steps**:
1. Setup Python 3.11 + Node.js 18
2. Install dependencies (cached)
3. Run Ghost Crawler (Google CSE)
4. Run Pulse Intelligence scorer
5. Sync to Supabase (upsert logic)
6. Send Telegram alerts (90+ score)
7. Upload artifacts (7-day retention)
8. Cleanup old artifacts

### 2. Ghost Crawler (`scripts/ghost-crawler.js`)

**Smart Scraping Strategy**:
- ❌ No direct LinkedIn scraping (avoids bans)
- ✅ Google Custom Search API (100 free searches/day)
- ✅ Smart delays (2s + random jitter)
- ✅ Rate limiting (50 max searches per run)

**Search Query Format**:
```
site:linkedin.com/jobs "hiring software engineers" "CompanyName" "United States"
```

**Features**:
- Loads target companies from Oracle predictions
- Rotates search keywords to vary queries
- Extracts job titles and URLs
- Outputs CSV with job counts
- Error handling and retry logic

### 3. Supabase Sync (`scripts/supabase-sync.js`)

**Intelligent Upsert Logic**:

```javascript
if (company exists in DB) {
  // UPDATE only critical fields
  UPDATE:
    - hiring_probability
    - pulse_score
    - desperation_level
    - expansion_density
    - last_seen timestamp
} else {
  // INSERT full record
  INSERT all fields
}
```

**Features**:
- Batch processing (50 companies at a time)
- 40+ score filter (only sync quality leads)
- Prevents duplicates
- Maintains historical tracking
- 1-second delay between batches

### 4. Telegram Alerts (`scripts/telegram-alerts.js`)

**Alert Criteria**:
- 🔥 Pulse score ≥ 90
- ⏰ Not alerted in last 24 hours
- 📊 Max 10 alerts per run

**Alert Format**:
```
🔥🔥 CRITICAL OPPORTUNITY 🔥🔥

TechCorp Inc.
Pulse Score: 95/100
Desperation: CRITICAL

📊 Signals:
• Expansion Density: 72%
• Tech Stack: 15 technologies
• Hiring Probability: 88%

💡 Contact immediately - Company is desperately hiring

🔗 https://techcorp.com

⏰ Detected: Dec 21, 2025 3:45 PM ET
```

## Setup Instructions

### 1. Google Custom Search API (Free Tier)

**Step 1**: Create Custom Search Engine
1. Go to: https://programmablesearchengine.google.com/
2. Click "Add" → "Create new search engine"
3. Sites to search: `linkedin.com/jobs/*`
4. Name: `LinkedIn Jobs Search`
5. Copy **Search Engine ID** (cx parameter)

**Step 2**: Get API Key
1. Go to: https://console.cloud.google.com/apis/credentials
2. Create API Key
3. Restrict to Custom Search API
4. Copy **API Key**

**Free Tier Limits**: 100 searches/day (our script uses 50)

### 2. GitHub Secrets Configuration

Add 6 secrets to repository (Settings → Secrets → Actions):

```bash
# Google Custom Search
GOOGLE_CSE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXX
GOOGLE_CSE_ID=a1b2c3d4e5f6g7h8i

# Supabase
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Telegram
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

### 3. Supabase Schema Update

Add new columns to `oracle_predictions` table:

```sql
-- Pulse Intelligence columns
ALTER TABLE oracle_predictions ADD COLUMN IF NOT EXISTS pulse_score DECIMAL(5,2);
ALTER TABLE oracle_predictions ADD COLUMN IF NOT EXISTS desperation_level VARCHAR(20);
ALTER TABLE oracle_predictions ADD COLUMN IF NOT EXISTS urgency VARCHAR(20);
ALTER TABLE oracle_predictions ADD COLUMN IF NOT EXISTS expansion_density DECIMAL(5,2);
ALTER TABLE oracle_predictions ADD COLUMN IF NOT EXISTS tech_diversity_score INTEGER;
ALTER TABLE oracle_predictions ADD COLUMN IF NOT EXISTS has_red_flags BOOLEAN DEFAULT FALSE;
ALTER TABLE oracle_predictions ADD COLUMN IF NOT EXISTS recommendation TEXT;
ALTER TABLE oracle_predictions ADD COLUMN IF NOT EXISTS pulse_full_analysis JSONB;

-- Tracking columns
ALTER TABLE oracle_predictions ADD COLUMN IF NOT EXISTS last_seen TIMESTAMP DEFAULT NOW();
ALTER TABLE oracle_predictions ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT NOW();

-- Unique constraint for upsert
CREATE UNIQUE INDEX IF NOT EXISTS idx_company_name_unique 
ON oracle_predictions(company_name);
```

## Usage

### Manual Trigger (Testing)

1. Go to: `https://github.com/YOUR_USERNAME/PulseB2B/actions`
2. Select "Ghost Crawler - Daily Scrape"
3. Click "Run workflow" → "Run workflow"
4. Monitor execution (~5-10 minutes)

### Automatic Execution

Runs automatically every 23 hours at minute 17:
- First run: Today 12:17 AM
- Second run: Tomorrow 11:17 PM
- Third run: Day after 10:17 PM
- etc.

### Check Results

**GitHub Artifacts**:
```
Actions → Latest run → Artifacts
└── ghost-crawler-results-XXX/
    ├── scraped_companies.csv
    ├── pulse_scored.csv
    └── pulse_reports/
        ├── critical_opportunities_*.csv
        ├── high_priority_*.csv
        └── pulse_summary_*.json
```

**Supabase Dashboard**:
```sql
SELECT company_name, pulse_score, desperation_level, last_seen
FROM oracle_predictions
WHERE pulse_score >= 90
ORDER BY pulse_score DESC
LIMIT 10;
```

**Telegram**:
Check your bot chat for real-time alerts

## Cost Breakdown

| Service | Tier | Monthly Cost | Usage |
|---------|------|--------------|-------|
| **GitHub Actions** | Free | $0 | 2,000 min/month |
| **Google CSE** | Free | $0 | 100 searches/day |
| **Supabase** | Free | $0 | 500MB DB, 2GB transfer |
| **Telegram Bot** | Free | $0 | Unlimited messages |
| **Total** | | **$0/month** | 🎉 |

## Performance

- **Scraping Time**: ~2-3 minutes (50 companies)
- **Scoring Time**: ~1-2 minutes (Pulse Intelligence)
- **Sync Time**: ~30 seconds (Supabase upsert)
- **Total Workflow**: ~5-10 minutes
- **Daily Searches**: 50 (under 100 limit)
- **Daily Companies**: ~20-30 with jobs found

## Rate Limits & Smart Delays

### Google Custom Search API
- **Limit**: 100 searches/day
- **Our usage**: 50 searches/run
- **Safety margin**: 50% buffer
- **Delay**: 2 seconds + 0-500ms jitter

### Supabase
- **Free tier**: 500MB database
- **Batch size**: 50 records
- **Delay**: 1 second between batches
- **Upsert**: Prevents duplicates

### Telegram
- **Limit**: 30 messages/second
- **Our usage**: Max 10 alerts/run
- **Delay**: 1 second between alerts
- **Dedupe**: 24-hour tracking

## Troubleshooting

### "Google CSE API Error"
```bash
# Check secrets are configured
gh secret list

# Test API key
curl "https://www.googleapis.com/customsearch/v1?key=YOUR_KEY&cx=YOUR_CX&q=test"
```

### "Supabase Connection Failed"
```bash
# Verify credentials
node -e "const {createClient} = require('@supabase/supabase-js'); const s = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_KEY); console.log('✅ Connected')"
```

### "No Jobs Found"
- Check Google CSE site restrictions (should be `linkedin.com/jobs/*`)
- Verify companies exist on LinkedIn
- Try different search keywords

### "Telegram Alerts Not Sending"
```bash
# Test bot connection
curl "https://api.telegram.org/botYOUR_TOKEN/getMe"

# Test message
curl -X POST "https://api.telegram.org/botYOUR_TOKEN/sendMessage" \
  -d "chat_id=YOUR_CHAT_ID" \
  -d "text=Test message"
```

## Advanced Configuration

### Increase Search Frequency
Edit `.github/workflows/daily_scrape.yml`:
```yaml
schedule:
  - cron: '17 */12 * * *'  # Every 12 hours
```

### Change Score Threshold
Edit `scripts/telegram-alerts.js`:
```javascript
SCORE_THRESHOLD: 85,  // Lower to 85 for more alerts
```

### Add More Target Companies
Edit `scripts/ghost-crawler.js`:
```javascript
const TARGET_COMPANIES = [
  'YourCompany1',
  'YourCompany2',
  // ...
];
```

## Monitoring

### GitHub Actions Dashboard
- View workflow runs
- Check execution logs
- Download artifacts

### Supabase Dashboard
- Monitor database size
- View API usage
- Check error logs

### Telegram Bot
- Real-time alerts
- Failure notifications
- Weekly summaries

## Security Best Practices

1. ✅ **Never commit secrets** to repository
2. ✅ Use GitHub Secrets for all credentials
3. ✅ Rotate API keys every 90 days
4. ✅ Use Supabase service_role key (not anon key)
5. ✅ Restrict Google API key to CSE only
6. ✅ Monitor workflow logs for anomalies

## Next Steps

1. ✅ Configure GitHub Secrets
2. ✅ Setup Google Custom Search API
3. ✅ Update Supabase schema
4. ✅ Test manual workflow trigger
5. ✅ Verify Telegram alerts
6. ✅ Monitor first automated run

## Documentation

- [Ghost Crawler Source](../scripts/ghost-crawler.js)
- [Supabase Sync Source](../scripts/supabase-sync.js)
- [Telegram Alerts Source](../scripts/telegram-alerts.js)
- [Workflow Configuration](../.github/workflows/daily_scrape.yml)
- [Pulse Intelligence](PULSE_INTELLIGENCE.md)

---

**Status**: ✅ Production Ready  
**Cost**: $0/month (100% free tier)  
**Version**: 1.0.0  
**Last Updated**: December 21, 2025
