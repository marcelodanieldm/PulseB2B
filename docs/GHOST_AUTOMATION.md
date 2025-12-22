# 👻 Ghost Infrastructure - GitHub Actions Automation

## 🎯 Overview

Fully automated **zero-cost** lead detection system that runs every 12 hours using GitHub Actions. No servers, no cloud costs - just pure automation! 💰

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ GITHUB ACTIONS (Free Tier - 2000 min/month)                 │
│ Runs every 12 hours (00:00 and 12:00 UTC)                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: Oracle Funding Detector                             │
│ • Parse SEC EDGAR RSS Feed (Form D filings)                 │
│ • Scrape company websites (Google Cache bypass)             │
│ • Detect tech stacks with NLP                               │
│ • Calculate hiring probability (ML scoring)                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: Data Validation                                     │
│ • Check CSV structure (required columns)                    │
│ • Validate data quality (nulls, ranges, formats)            │
│ • Business logic checks (scoring consistency)               │
│ • Generate validation report                                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: Supabase Upload                                     │
│ • Transform CSV → JSON records                              │
│ • Batch upload (50 records/batch)                           │
│ • Upsert (prevents duplicates)                              │
│ • Generate upload summary                                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: Telegram Alerts                                     │
│ • Find critical leads (≥85% probability)                    │
│ • Send individual alerts (max 5)                            │
│ • Send daily summary                                        │
│ • Log notifications                                         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ ARTIFACTS & LOGS                                             │
│ • CSV files (30 days retention)                             │
│ • JSON summaries                                            │
│ • Validation reports                                        │
│ • GitHub Actions logs                                       │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Setup (15 Minutes)

### 1. Create Telegram Bot (5 min)

```bash
# Windows
setup_telegram_bot.bat

# Linux/Mac
chmod +x setup_telegram_bot.sh
./setup_telegram_bot.sh
```

**What it does:**
- Creates Telegram bot via @BotFather
- Gets your Chat ID
- Tests connection
- Saves to `.env` file

### 2. Setup Supabase (5 min)

Create database table:

```sql
-- Run in Supabase SQL Editor
CREATE TABLE oracle_predictions (
    id BIGSERIAL PRIMARY KEY,
    company_name TEXT NOT NULL,
    funding_date DATE NOT NULL,
    days_since_filing INTEGER,
    estimated_amount_millions NUMERIC(10, 2),
    funding_source TEXT,
    tech_stack TEXT[],
    tech_count INTEGER,
    hiring_signals INTEGER,
    hiring_probability NUMERIC(5, 2),
    website TEXT,
    description TEXT,
    cik TEXT,
    filing_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_name, funding_date)
);

-- Indexes for performance
CREATE INDEX idx_hiring_prob ON oracle_predictions(hiring_probability DESC);
CREATE INDEX idx_funding_date ON oracle_predictions(funding_date DESC);
CREATE INDEX idx_company_name ON oracle_predictions(company_name);

-- View for hot opportunities
CREATE VIEW oracle_hot_opportunities AS
SELECT 
    company_name,
    funding_date,
    estimated_amount_millions,
    array_to_string(tech_stack, ', ') as tech_stack,
    hiring_probability,
    website,
    days_since_filing
FROM oracle_predictions
WHERE hiring_probability >= 70
ORDER BY hiring_probability DESC;
```

### 3. Configure GitHub Secrets (5 min)

Go to: `https://github.com/YOUR_USERNAME/PulseB2B/settings/secrets/actions`

Add these secrets:

| Name | Value | Where to Find |
|------|-------|---------------|
| `SUPABASE_URL` | `https://xxx.supabase.co` | Supabase → Settings → API → Project URL |
| `SUPABASE_SERVICE_KEY` | `eyJhbGci...` | Supabase → Settings → API → service_role key |
| `TELEGRAM_BOT_TOKEN` | `123456789:ABC...` | From @BotFather |
| `TELEGRAM_CHAT_ID` | `123456789` | From @userinfobot |

**Optional (for failure alerts):**
| Name | Value |
|------|-------|
| `EMAIL_USERNAME` | Your Gmail |
| `EMAIL_PASSWORD` | App-specific password |
| `ALERT_EMAIL` | Where to send alerts |

### 4. Enable GitHub Actions

1. Go to: `https://github.com/YOUR_USERNAME/PulseB2B/actions`
2. Enable workflows if disabled
3. Find "Oracle Ghost - Automated Lead Detection"
4. Click "Run workflow" to test manually

---

## 📋 Workflow Details

### Schedule

```yaml
schedule:
  - cron: '0 0,12 * * *'  # Every 12 hours (midnight and noon UTC)
```

**Conversion to your timezone:**
- `0 0 * * *` = 00:00 UTC = 7:00 PM EST (prev day) = 1:00 AM CET
- `0 12 * * *` = 12:00 UTC = 7:00 AM EST = 1:00 PM CET

**Why 12 hours?**
- SEC filings happen during business hours (9 AM - 5 PM EST)
- 2 runs/day = good coverage without spam
- GitHub Free: 2000 min/month ÷ 2 runs/day ÷ 5 min/run = 200 days (plenty!)

### Manual Trigger

Run on-demand with custom parameters:

```
Actions → Oracle Ghost → Run workflow
  Max companies: 20 (default) or custom
```

---

## 🔧 Components

### 1. Oracle Detector (`scripts/oracle_funding_detector.py`)

**Enhanced features:**
- ✅ **Google Cache bypass** - Uses `webcache.googleusercontent.com` prefix
- ✅ **Realistic User-Agent** - Chrome 120 headers
- ✅ **Retry logic** - Cache fails → direct scraping
- ✅ **Rate limiting** - 2-3s delays (respectful)

```python
# Google Cache URL format
cache_url = f"https://webcache.googleusercontent.com/search?q=cache:{url}"

# Fallback to direct if cache fails
if cache_fails:
    direct_url = url
```

### 2. Validator (`scripts/validate_oracle_output.py`)

**Checks performed:**
- ✅ **Structure**: All required columns present
- ✅ **Data quality**: No nulls, valid ranges (0-100%), correct formats
- ✅ **Business logic**: High prob with low signals = warning
- ✅ **Duplicates**: Same company + date flagged

**Exit codes:**
- `0` = Passed (continue pipeline)
- `1` = Failed (stop pipeline)

### 3. Uploader (`scripts/upload_to_supabase.py`)

**Features:**
- ✅ **Batch processing**: 50 records/batch (avoid timeouts)
- ✅ **Upsert**: Prevents duplicates on `(company_name, funding_date)`
- ✅ **Error handling**: Logs failed batches
- ✅ **Success threshold**: 80%+ required

### 4. Notifier (`scripts/telegram_notifier.py`)

**Behavior:**
- ✅ **Critical alerts**: Hiring probability ≥ 85%
- ✅ **Spam prevention**: Max 5 individual alerts per run
- ✅ **Daily summary**: Always sent (with stats)
- ✅ **Formatted messages**: HTML with links

**Alert format:**
```
🚨 CRITICAL LEAD ALERT 🚨

Anthropic Inc.

🎯 Hiring Probability: 92.3% (CRITICAL)
📅 Filed: 2025-12-18 (3 days ago)
💰 Funding: $450.0M

🔧 Tech Stack: Python, PyTorch, Kubernetes
📊 Hiring Signals: 20 detected

🌐 Website: https://anthropic.com

⚡ ACTION REQUIRED:
• Contact CTO/Head of Engineering TODAY
• Reference recent funding round
• Pitch offshore team scaling

📄 View SEC Filing
```

---

## 📊 Output Artifacts

### Generated Files (per run)

```
data/output/oracle/
├── oracle_predictions_20251221_143022.csv        # Main results
├── oracle_predictions_20251221_143022_summary.json  # Stats
├── validation_report.json                        # Quality checks
├── upload_summary.json                           # Supabase log
└── notification_log.json                         # Telegram log
```

### Artifact Retention

- **GitHub**: 30 days
- **Local**: Forever (manual cleanup)
- **Supabase**: Forever (manual cleanup)

---

## 🎯 Usage Examples

### Manual Run (Test Locally)

```bash
# Full pipeline (local)
python scripts/oracle_funding_detector.py
python scripts/validate_oracle_output.py
python scripts/upload_to_supabase.py
python scripts/telegram_notifier.py
```

### Query Supabase (SQL)

```sql
-- Find today's critical leads
SELECT * FROM oracle_predictions
WHERE hiring_probability >= 85
  AND funding_date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY hiring_probability DESC;

-- Tech stack analysis
SELECT 
    UNNEST(tech_stack) as technology,
    COUNT(*) as company_count,
    AVG(hiring_probability) as avg_probability
FROM oracle_predictions
GROUP BY technology
ORDER BY company_count DESC
LIMIT 20;

-- Funding trends
SELECT 
    DATE_TRUNC('month', funding_date) as month,
    COUNT(*) as filings,
    SUM(estimated_amount_millions) as total_funding,
    AVG(hiring_probability) as avg_probability
FROM oracle_predictions
WHERE funding_date >= CURRENT_DATE - INTERVAL '6 months'
GROUP BY month
ORDER BY month DESC;
```

### Dashboard Integration

```typescript
// Next.js Server Component
import { createServerComponentClient } from '@supabase/auth-helpers-nextjs'
import { cookies } from 'next/headers'

export default async function OracleDashboard() {
  const supabase = createServerComponentClient({ cookies })
  
  const { data: opportunities } = await supabase
    .from('oracle_hot_opportunities')
    .select('*')
    .order('hiring_probability', { ascending: false })
    .limit(20)
  
  return <BentoGridDashboard opportunities={opportunities} />
}
```

---

## 🐛 Troubleshooting

### Issue: Workflow doesn't run

**Check:**
1. GitHub Actions enabled? (Settings → Actions → Allow all)
2. Secrets configured? (Settings → Secrets → Actions)
3. Workflow file present? (`.github/workflows/oracle-ghost-automation.yml`)

**Fix:**
```bash
# Push workflow file if missing
git add .github/workflows/oracle-ghost-automation.yml
git commit -m "Add Oracle Ghost automation"
git push
```

### Issue: Validation fails

**Check logs:**
```
Actions → Oracle Ghost → Latest run → validate → View raw logs
```

**Common causes:**
- No CSV generated (Oracle scraping failed)
- Invalid data (check validation_report.json)
- Format issues (check CSV structure)

**Fix:**
- Reduce `max_companies` to 10 (faster)
- Check SEC EDGAR availability
- Review validation errors in logs

### Issue: Supabase upload fails

**Check:**
1. Table created? (`oracle_predictions`)
2. Secrets correct? (`SUPABASE_URL`, `SUPABASE_SERVICE_KEY`)
3. RLS policies? (Disable for service_role or add policy)

**Fix RLS:**
```sql
-- Allow service_role to insert/update
ALTER TABLE oracle_predictions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow service role full access"
ON oracle_predictions
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);
```

### Issue: Telegram not sending

**Check:**
1. Bot token valid? (Test with `setup_telegram_bot.bat`)
2. Chat ID correct? (Should be numeric)
3. Bot started? (Send `/start` to your bot in Telegram)

**Test manually:**
```bash
python scripts/telegram_notifier.py
```

### Issue: Rate limiting / Bot detection

**Cause:** Too many requests or bot detected

**Fix:**
1. Increase delays (3-5s instead of 2-3s)
2. Use Google Cache (already enabled)
3. Reduce `max_companies` to 10-15

```python
# In oracle_funding_detector.py
time.sleep(5)  # Increase from 3 to 5 seconds
```

---

## 📈 Performance Metrics

### GitHub Actions Usage

| Metric | Value | Monthly Limit |
|--------|-------|---------------|
| **Runs per day** | 2 | - |
| **Runtime per run** | ~5-8 minutes | - |
| **Total monthly** | ~240-360 minutes | 2000 minutes |
| **Usage** | ~12-18% | 82-88% remaining |

### Cost Breakdown

| Service | Plan | Cost |
|---------|------|------|
| GitHub Actions | Free tier | $0 |
| Supabase | Free tier | $0 |
| Telegram Bot | Free | $0 |
| **Total** | | **$0/month** 🎉 |

### Data Volume

| Metric | Per Run | Monthly |
|--------|---------|---------|
| Companies processed | 20 | 1,200 |
| Critical leads (avg) | 3-5 | 180-300 |
| CSV size | ~50 KB | ~3 MB |
| Database rows | 20 | 1,200 |

---

## 🔒 Security Best Practices

### Secrets Management

✅ **Do:**
- Use GitHub Secrets (encrypted at rest)
- Rotate tokens every 90 days
- Use service_role key for Supabase (not anon key)

❌ **Don't:**
- Commit `.env` file to git
- Share tokens in plain text
- Use personal API keys

### Rate Limiting

✅ **Implemented:**
- 2-3 second delays between requests
- Google Cache to reduce direct hits
- Respectful User-Agent header

### Data Privacy

✅ **Compliant:**
- Public SEC data only
- No personal information
- Business contact info (publicly available)

---

## 🎓 Advanced Configuration

### Custom Schedule

Edit `.github/workflows/oracle-ghost-automation.yml`:

```yaml
# Every 6 hours (4x daily)
- cron: '0 */6 * * *'

# Every day at 9 AM UTC
- cron: '0 9 * * *'

# Weekdays only at 9 AM and 5 PM UTC
- cron: '0 9,17 * * 1-5'
```

### Custom Threshold

Change critical threshold from 85% to 80%:

```python
# In scripts/telegram_notifier.py
CRITICAL_THRESHOLD = 80.0  # Was 85.0
```

### Email Alerts (Alternative to Telegram)

Add to workflow:

```yaml
- name: 📧 Send email alerts
  if: steps.validate.outputs.validation_success == 'true'
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    server_port: 587
    username: ${{ secrets.EMAIL_USERNAME }}
    password: ${{ secrets.EMAIL_PASSWORD }}
    subject: '🔮 Oracle: Critical Leads Detected'
    to: ${{ secrets.ALERT_EMAIL }}
    from: Oracle Ghost <noreply@github.com>
    body: file://data/output/oracle/oracle_predictions_*.csv
```

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [ORACLE_DETECTOR.md](./ORACLE_DETECTOR.md) | User guide |
| [ORACLE_ARCHITECTURE.md](./ORACLE_ARCHITECTURE.md) | Technical details |
| [ORACLE_INTEGRATION.md](./ORACLE_INTEGRATION.md) | Integration guide |
| [GHOST_AUTOMATION.md](./GHOST_AUTOMATION.md) | This file |

---

## ✅ Deployment Checklist

- [ ] Telegram bot created (`setup_telegram_bot.bat`)
- [ ] Test message received in Telegram
- [ ] Supabase table created (`oracle_predictions`)
- [ ] GitHub Secrets configured (4 required)
- [ ] Workflow file committed and pushed
- [ ] Manual test run successful
- [ ] CSV artifact generated
- [ ] Supabase upload verified
- [ ] Telegram alert received
- [ ] Schedule activated (automatic runs)

---

## 🎉 Success Metrics

**After 1 week, you should see:**
- ✅ 14 automated runs (2x daily × 7 days)
- ✅ ~280 companies detected
- ✅ ~40-70 high-probability leads (70%+)
- ✅ ~6-10 critical alerts sent (85%+)
- ✅ 0 errors in logs
- ✅ $0 spent 💰

**After 1 month:**
- ✅ 60 automated runs
- ✅ ~1,200 companies detected
- ✅ ~180-300 high-probability leads
- ✅ ~30-50 critical alerts sent
- ✅ Data-driven insights on tech trends
- ✅ Still $0 spent! 🎊

---

**Version**: 1.0.0  
**Last Updated**: December 21, 2025  
**Status**: ✅ Production Ready  
**Cost**: $0/month forever! 🚀
