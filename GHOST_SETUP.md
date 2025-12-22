# Ghost Crawler Setup - Quick Guide 🚀

## Prerequisites Checklist

- [ ] GitHub repository with Actions enabled
- [ ] Google account for Custom Search API
- [ ] Supabase project created
- [ ] Telegram bot created (@BotFather)
- [ ] Node.js 18+ installed locally (for testing)

## Step-by-Step Setup (15 minutes)

### 1️⃣ Google Custom Search API (5 minutes)

**Create Search Engine**:
1. Visit: https://programmablesearchengine.google.com/
2. Click **"Add"** → **"Create a new search engine"**
3. **Sites to search**: `linkedin.com/jobs/*`
4. **Name**: `LinkedIn Jobs Scraper`
5. Click **"Create"**
6. Copy your **Search Engine ID** (looks like: `a1b2c3d4e5f6g7h`)

**Get API Key**:
1. Visit: https://console.cloud.google.com/apis/library
2. Enable **"Custom Search API"**
3. Go to: https://console.cloud.google.com/apis/credentials
4. Click **"Create Credentials"** → **"API Key"**
5. Click **"Restrict Key"**:
   - API restrictions: **Custom Search API only**
   - Save
6. Copy your **API Key** (looks like: `AIzaSyXXXXXXXXXXX`)

**Test Your Setup**:
```bash
# Replace YOUR_KEY and YOUR_CX
curl "https://www.googleapis.com/customsearch/v1?key=YOUR_KEY&cx=YOUR_CX&q=site:linkedin.com/jobs+hiring"
```

Expected: JSON response with search results

---

### 2️⃣ Supabase Schema (3 minutes)

**Update Database**:
1. Go to: https://app.supabase.com/project/YOUR_PROJECT/editor
2. Open SQL Editor
3. Run this SQL:

```sql
-- Add Pulse Intelligence columns
ALTER TABLE oracle_predictions ADD COLUMN IF NOT EXISTS pulse_score DECIMAL(5,2);
ALTER TABLE oracle_predictions ADD COLUMN IF NOT EXISTS desperation_level VARCHAR(20);
ALTER TABLE oracle_predictions ADD COLUMN IF NOT EXISTS urgency VARCHAR(20);
ALTER TABLE oracle_predictions ADD COLUMN IF NOT EXISTS expansion_density DECIMAL(5,2);
ALTER TABLE oracle_predictions ADD COLUMN IF NOT EXISTS tech_diversity_score INTEGER;
ALTER TABLE oracle_predictions ADD COLUMN IF NOT EXISTS has_red_flags BOOLEAN DEFAULT FALSE;
ALTER TABLE oracle_predictions ADD COLUMN IF NOT EXISTS recommendation TEXT;
ALTER TABLE oracle_predictions ADD COLUMN IF NOT EXISTS pulse_full_analysis JSONB;
ALTER TABLE oracle_predictions ADD COLUMN IF NOT EXISTS last_seen TIMESTAMP DEFAULT NOW();
ALTER TABLE oracle_predictions ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT NOW();

-- Unique constraint for upsert logic
CREATE UNIQUE INDEX IF NOT EXISTS idx_company_name_unique 
ON oracle_predictions(company_name);
```

4. Click **"Run"**
5. ✅ Verify: "Success. No rows returned"

---

### 3️⃣ GitHub Secrets (5 minutes)

**Navigate to Secrets**:
1. Go to: `https://github.com/YOUR_USERNAME/PulseB2B/settings/secrets/actions`
2. Click **"New repository secret"**

**Add 6 Secrets**:

| Name | Value | Where to get |
|------|-------|--------------|
| `GOOGLE_CSE_API_KEY` | `AIzaSyXXX...` | Step 1: Google Cloud Console |
| `GOOGLE_CSE_ID` | `a1b2c3d4e5f6g7h` | Step 1: Programmable Search Engine |
| `SUPABASE_URL` | `https://xxx.supabase.co` | Supabase Project Settings → API |
| `SUPABASE_SERVICE_KEY` | `eyJhbGciOi...` | Supabase → API → service_role key |
| `TELEGRAM_BOT_TOKEN` | `123456:ABC...` | Already created (from previous setup) |
| `TELEGRAM_CHAT_ID` | `123456789` | Already created (from previous setup) |

**Verify**:
```bash
# CLI method (optional)
gh secret list
```

Expected:
```
GOOGLE_CSE_API_KEY  Updated 2025-12-21
GOOGLE_CSE_ID       Updated 2025-12-21
SUPABASE_URL        Updated 2025-12-21
(etc.)
```

---

### 4️⃣ Test Workflow (2 minutes)

**Manual Trigger**:
1. Go to: `https://github.com/YOUR_USERNAME/PulseB2B/actions`
2. Click **"Ghost Crawler - Daily Scrape"** (left sidebar)
3. Click **"Run workflow"** dropdown (right side)
4. Click **"Run workflow"** button
5. Wait ~5-10 minutes

**Monitor Execution**:
- ✅ Green checkmarks = success
- ❌ Red X = failure (check logs)

**Check Results**:
1. Click on workflow run
2. Scroll to bottom → **"Artifacts"**
3. Download `ghost-crawler-results-XXX.zip`
4. Unzip and review CSVs

---

## Verification Checklist

### ✅ Google CSE
- [ ] Created Custom Search Engine
- [ ] Sites restricted to `linkedin.com/jobs/*`
- [ ] API Key created and restricted
- [ ] Test query returns results

### ✅ Supabase
- [ ] Schema updated with new columns
- [ ] Unique index created on company_name
- [ ] Can connect with service_role key

### ✅ GitHub Secrets
- [ ] All 6 secrets added
- [ ] No typos in secret names
- [ ] Values copied correctly (no extra spaces)

### ✅ Workflow
- [ ] Manual trigger successful
- [ ] All steps completed (green checks)
- [ ] Artifacts generated
- [ ] Telegram alert received (if 90+ score)

---

## Expected Output

### Scraped Companies CSV
```csv
company_name,job_count,job_titles,search_query,linkedin_urls,scraped_at
Google,8,"Senior Software Engineer; ML Engineer; Backend Dev",hiring software engineers,https://linkedin.com/jobs/...,2025-12-21T10:30:00Z
Meta,5,"Frontend Engineer; Data Scientist",hiring data scientists,https://linkedin.com/jobs/...,2025-12-21T10:32:00Z
```

### Pulse Scored CSV
```csv
company_name,pulse_score,desperation_level,urgency,recommendation,...
Google,87.5,CRITICAL,immediate,"🔥 IMMEDIATE ACTION - Contact within 24h",...
Meta,72.3,HIGH,urgent,"⚡ High priority - engage within 48-72h",...
```

### Telegram Alert (if 90+ score)
```
🔥🔥 CRITICAL OPPORTUNITY 🔥🔥

Google
Pulse Score: 92/100
Desperation: CRITICAL

📊 Signals:
• Expansion Density: 75%
• Tech Stack: 18 technologies
• Hiring Probability: 89%

💡 Contact immediately - Company is desperately hiring

🔗 https://google.com

⏰ Detected: Dec 21, 2025 3:45 PM ET
```

---

## Troubleshooting

### ❌ "Google CSE API Error"
**Symptoms**: Workflow fails at Ghost Crawler step

**Solutions**:
1. Verify API key is correct (no extra spaces)
2. Check API key restrictions allow Custom Search API
3. Ensure you haven't exceeded 100 searches/day
4. Test API key with curl command from Step 1

### ❌ "Supabase Connection Failed"
**Symptoms**: Workflow fails at Supabase Sync step

**Solutions**:
1. Use `service_role` key (not `anon` key)
2. Check URL format: `https://xxx.supabase.co` (no trailing slash)
3. Verify table `oracle_predictions` exists
4. Run schema update SQL again

### ❌ "No Jobs Found"
**Symptoms**: scraped_companies.csv is empty or has 0 job_count

**Solutions**:
1. Check Google CSE site restrictions include `linkedin.com/jobs/*`
2. Try different target companies (update ghost-crawler.js)
3. Verify companies have active job postings on LinkedIn
4. Check you haven't hit rate limits

### ❌ "Telegram Alerts Not Sent"
**Symptoms**: No messages in Telegram

**Possible Reasons**:
1. No companies scored 90+ (check pulse_scored.csv)
2. Companies already alerted in last 24h (check alert_log.json)
3. Bot token incorrect
4. Chat ID incorrect

**Test Manually**:
```bash
curl -X POST "https://api.telegram.org/botYOUR_TOKEN/sendMessage" \
  -d "chat_id=YOUR_CHAT_ID" \
  -d "text=Test from Ghost Crawler"
```

---

## Next Steps After Setup

### Week 1: Monitoring
- [ ] Check workflow runs daily
- [ ] Review artifacts for data quality
- [ ] Verify Telegram alerts are actionable
- [ ] Monitor Supabase database size

### Week 2: Optimization
- [ ] Adjust target company list based on results
- [ ] Tune Pulse score threshold (default: 90)
- [ ] Add more search keywords
- [ ] Review false positives/negatives

### Week 3: Scale
- [ ] Consider increasing to every 12 hours
- [ ] Add more target companies (up to 100)
- [ ] Integrate with CRM/sales tools
- [ ] Build dashboard visualizations

---

## Quick Commands

### Test Locally (Before Pushing)
```bash
# Ghost Crawler
node scripts/ghost-crawler.js

# Supabase Sync
node scripts/supabase-sync.js

# Telegram Alerts
node scripts/telegram-alerts.js
```

### View Workflow Logs
```bash
gh run list --workflow=daily_scrape.yml
gh run view XXXXX  # Replace with run ID
```

### Download Latest Artifacts
```bash
gh run download --name ghost-crawler-results-XXX
```

---

## Success Criteria

After 24 hours, you should have:
- ✅ 1-2 workflow runs completed
- ✅ 20-50 companies scraped
- ✅ 10-30 companies scored with Pulse
- ✅ 5-15 companies synced to Supabase
- ✅ 1-5 Telegram alerts (if critical opportunities found)

---

**Need Help?**
- Check [Full Documentation](GHOST_CRAWLER.md)
- Review [Pulse Intelligence Docs](PULSE_INTELLIGENCE.md)
- Test components individually with local scripts

---

**Status**: ✅ Setup Complete  
**Estimated Time**: 15 minutes  
**Cost**: $0/month  
**Last Updated**: December 21, 2025
