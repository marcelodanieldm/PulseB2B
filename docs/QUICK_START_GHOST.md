# 🚀 Quick Start - Ghost Infrastructure

Get the Serverless Ghost pipeline running in 15 minutes.

---

## Prerequisites

- GitHub account
- Supabase account (free tier works)
- Python 3.9+
- Basic terminal knowledge

---

## Step 1: Clone & Install (2 minutes)

```bash
# Clone the repo
git clone <your-repo-url>
cd PulseB2B

# Install Python dependencies
pip install -r requirements.txt

# Download NLTK data (for sentiment analysis)
python -c "import nltk; nltk.download('vader_lexicon'); nltk.download('punkt')"
```

---

## Step 2: Supabase Setup (5 minutes)

### A. Create Project
1. Go to [supabase.com](https://supabase.com)
2. Click "New Project"
3. Name: `pulseb2b-ghost`
4. Database password: Generate strong password
5. Region: Choose closest to you
6. Click "Create new project"

### B. Run Database Schema
1. Wait for project to finish initializing (~2 minutes)
2. Go to **SQL Editor** in left sidebar
3. Copy entire contents of `supabase/schema.sql`
4. Paste into SQL Editor
5. Click **RUN** button
6. ✅ You should see "Success. No rows returned"

### C. Get API Credentials
1. Go to **Settings** → **API**
2. Copy **Project URL** (looks like `https://xxxxx.supabase.co`)
3. Copy **service_role** key (NOT the anon key)
4. Save these for Step 3

---

## Step 3: GitHub Secrets (3 minutes)

### A. Go to Repository Settings
1. Navigate to your GitHub repository
2. Click **Settings** tab (top right)
3. Click **Secrets and variables** → **Actions** (left sidebar)
4. Click **New repository secret**

### B. Add Required Secrets

**Secret 1: SUPABASE_URL**
- Name: `SUPABASE_URL`
- Value: Your Supabase project URL from Step 2C
- Click **Add secret**

**Secret 2: SUPABASE_KEY**
- Name: `SUPABASE_KEY`
- Value: Your Supabase service_role key from Step 2C
- Click **Add secret**

**Secret 3: SLACK_WEBHOOK_URL** (Optional)
- Name: `SLACK_WEBHOOK_URL`
- Value: Your Slack webhook URL (skip if you don't have one)
- Click **Add secret**

---

## Step 4: Deploy Edge Functions (3 minutes)

```bash
# Install Supabase CLI
npm install -g supabase

# Login to Supabase
supabase login

# Link your project (use project ref from Settings → General)
supabase link --project-ref YOUR_PROJECT_REF

# Deploy Edge Functions
supabase functions deploy news-webhook
supabase functions deploy lead-scoring

# ✅ Should see "Deployed function news-webhook" and "Deployed function lead-scoring"
```

---

## Step 5: Test the Pipeline (2 minutes)

### A. Manual Workflow Trigger
1. Go to **Actions** tab in GitHub
2. Click **Ghost Pipeline - Market Intelligence** workflow
3. Click **Run workflow** dropdown (right side)
4. Select `main` branch
5. Click green **Run workflow** button

### B. Monitor Execution
Watch the workflow run:
- ⏱️ Takes ~15 minutes to complete
- ✅ All 6 jobs should turn green
- ❌ If any fail, check the logs

### C. Verify Data in Supabase
1. Go to your Supabase project
2. Click **Table Editor** (left sidebar)
3. Check these tables for data:
   - `funding_rounds` - Should have SEC Form D filings
   - `job_postings` - Should have LinkedIn jobs from LATAM
   - `news_articles` - Should have Google News results
   - `lead_scores` - Should have calculated scores

---

## Step 6: View Results

### Check High Priority Leads
```sql
SELECT * FROM high_priority_leads
WHERE priority = 'critical'
ORDER BY score DESC
LIMIT 10;
```

### Check Recent Activity (Last 7 Days)
```sql
SELECT * FROM recent_activity
WHERE activity_date > NOW() - INTERVAL '7 days'
ORDER BY activity_date DESC;
```

### Check Pipeline Status
```sql
SELECT *
FROM pipeline_runs
ORDER BY started_at DESC
LIMIT 5;
```

---

## ✅ You're Done!

The pipeline now runs automatically every 6 hours:
- **00:00 UTC** - Midnight
- **06:00 UTC** - 6 AM
- **12:00 UTC** - Noon
- **18:00 UTC** - 6 PM

---

## 🎯 Next Steps

### Customize Target Companies
Edit `.github/workflows/serverless-ghost-pipeline.yml`:
```yaml
env:
  TARGET_COMPANIES: "OpenAI,Anthropic,Stripe,Figma,Notion"
```

### Add More Locations
Edit `src/ghost_linkedin_google_scraper.py`:
```python
locations = [
    "São Paulo, Brazil",
    "Rio de Janeiro, Brazil",
    "Mexico City, Mexico",
    "Buenos Aires, Argentina",  # NEW
    "Bogotá, Colombia"  # NEW
]
```

### Adjust Schedule
Edit `.github/workflows/serverless-ghost-pipeline.yml`:
```yaml
schedule:
  - cron: '0 */12 * * *'  # Every 12 hours instead of 6
```

---

## 🐛 Troubleshooting

### "Supabase connection failed"
- ✅ Verify `SUPABASE_URL` and `SUPABASE_KEY` in GitHub Secrets
- ✅ Make sure you used **service_role** key (not anon key)
- ✅ Check Supabase project is not paused (free tier pauses after 7 days inactivity)

### "No data in tables after workflow run"
- ✅ Check GitHub Actions logs for errors
- ✅ Verify all 6 jobs completed successfully (green checkmarks)
- ✅ Run SQL query: `SELECT COUNT(*) FROM pipeline_runs;` (should be > 0)

### "Google Search blocked"
- ✅ This is expected occasionally
- ✅ Wait 1 hour and run again
- ✅ Pipeline will retry next scheduled run

### "Edge Functions not found"
- ✅ Run `supabase functions list` to verify deployment
- ✅ Check function logs: `supabase functions logs news-webhook`
- ✅ Redeploy: `supabase functions deploy news-webhook --no-verify-jwt`

---

## 📖 Full Documentation

- [Serverless Ghost Infrastructure](./SERVERLESS_GHOST_INFRASTRUCTURE.md) - Complete technical guide
- [OSINT Lead Scoring](./OSINT_LEAD_SCORING.md) - Scoring algorithm details
- [Ghost Architecture](./GHOST_ARCHITECTURE.md) - System design

---

## 💬 Need Help?

Check the logs:
```bash
# GitHub Actions logs
# Go to Actions → Select failed job → View logs

# Supabase Edge Function logs
supabase functions logs news-webhook --tail

# Local testing
python src/ghost_sec_rss_scraper.py
python src/ghost_linkedin_google_scraper.py
```

---

**Total Setup Time:** ~15 minutes  
**Recurring Cost:** $0 (free tier Supabase + GitHub Actions)  
**Data Refresh:** Every 6 hours automatically
