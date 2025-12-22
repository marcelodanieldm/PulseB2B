# Oracle + Ghost Infrastructure Integration Guide

## 🎯 Overview

This guide shows how to integrate **Oracle Funding Detector** with the existing **Ghost Infrastructure** to create a fully automated, zero-cost lead generation pipeline.

## 🏗️ Unified Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    GITHUB ACTIONS                            │
│              (Serverless Orchestrator)                       │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   Oracle     │   │    Ghost     │   │ Lead Scoring │
│   Detector   │   │   Scraper    │   │   Engine     │
└──────────────┘   └──────────────┘   └──────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            ▼
                   ┌──────────────────┐
                   │ Supabase Storage │
                   │  (PostgreSQL)    │
                   └──────────────────┘
                            │
                            ▼
                   ┌──────────────────┐
                   │ Dashboard/Alerts │
                   └──────────────────┘
```

## 🔗 Integration Steps

### Step 1: Connect Oracle to Supabase

Create a new table for Oracle predictions:

```sql
-- supabase/migrations/003_oracle_predictions.sql

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
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for fast queries
CREATE INDEX idx_oracle_hiring_prob ON oracle_predictions(hiring_probability DESC);
CREATE INDEX idx_oracle_funding_date ON oracle_predictions(funding_date DESC);
CREATE INDEX idx_oracle_company_name ON oracle_predictions(company_name);

-- View for high-probability targets
CREATE VIEW oracle_hot_opportunities AS
SELECT 
    company_name,
    funding_date,
    estimated_amount_millions,
    array_to_string(tech_stack, ', ') as tech_stack,
    hiring_probability,
    website
FROM oracle_predictions
WHERE hiring_probability >= 70
ORDER BY hiring_probability DESC;
```

### Step 2: Update Oracle Script to Upload to Supabase

Modify `scripts/oracle_funding_detector.py`:

```python
# Add at the top
from supabase import create_client, Client
import os

# In OracleFundingDetector.__init__()
def __init__(self, output_dir: str = '../data/output/oracle'):
    # ... existing code ...
    
    # Initialize Supabase client
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
    
    if supabase_url and supabase_key:
        self.supabase: Client = create_client(supabase_url, supabase_key)
        logger.info("✅ Supabase client initialized")
    else:
        self.supabase = None
        logger.warning("⚠️  Supabase credentials not found (CSV export only)")

# Add new method
def upload_to_supabase(self, df: pd.DataFrame) -> bool:
    """
    Upload Oracle predictions to Supabase.
    
    Args:
        df: Results DataFrame
        
    Returns:
        True if successful, False otherwise
    """
    if not self.supabase:
        logger.warning("⚠️  Supabase not configured, skipping upload")
        return False
    
    try:
        logger.info("📤 Uploading to Supabase...")
        
        # Convert DataFrame to records
        records = []
        for _, row in df.iterrows():
            record = {
                'company_name': row['Company Name'],
                'funding_date': row['Funding Date'],
                'days_since_filing': row['Days Since Filing'],
                'estimated_amount_millions': float(row['Estimated Amount (M)'].replace('$', '').replace('M', '')) if row['Estimated Amount (M)'] != 'Not disclosed' else None,
                'funding_source': row['Funding Source'],
                'tech_stack': row['Tech Stack'].split(', ') if row['Tech Stack'] != 'Not detected' else [],
                'tech_count': row['Tech Count'],
                'hiring_signals': row['Hiring Signals'],
                'hiring_probability': float(row['Hiring Probability (%)']),
                'website': row['Website'],
                'description': row['Description'],
                'cik': row['CIK'],
                'filing_url': row['Filing URL']
            }
            records.append(record)
        
        # Upsert to Supabase (prevents duplicates)
        response = self.supabase.table('oracle_predictions').upsert(
            records,
            on_conflict='company_name,funding_date'
        ).execute()
        
        logger.info(f"✅ Uploaded {len(records)} predictions to Supabase")
        return True
        
    except Exception as e:
        logger.error(f"❌ Supabase upload failed: {e}")
        return False

# Update main() function
def main():
    # ... existing code ...
    
    # Export to CSV
    output_file = oracle.export_results(results_df)
    
    # Upload to Supabase
    oracle.upload_to_supabase(results_df)
    
    # ... rest of code ...
```

### Step 3: Create GitHub Actions Workflow

Create `.github/workflows/oracle-daily.yml`:

```yaml
name: Oracle Funding Detector - Daily Run

on:
  schedule:
    # Run every day at 9 AM EST (2 PM UTC)
    - cron: '0 14 * * *'
  
  workflow_dispatch:  # Allow manual trigger

jobs:
  oracle-detector:
    runs-on: ubuntu-latest
    
    steps:
      - name: 📥 Checkout code
        uses: actions/checkout@v3
      
      - name: 🐍 Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          cache: 'pip'
      
      - name: 📦 Install dependencies
        run: |
          pip install -r requirements-oracle.txt
          python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
      
      - name: 🔮 Run Oracle Detector
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_SERVICE_KEY: ${{ secrets.SUPABASE_SERVICE_KEY }}
        run: |
          python scripts/oracle_funding_detector.py
      
      - name: 📊 Upload Results Artifact
        uses: actions/upload-artifact@v3
        with:
          name: oracle-results
          path: data/output/oracle/
          retention-days: 30
      
      - name: 📧 Send Notification (on failure)
        if: failure()
        uses: dawidd6/action-send-mail@v3
        with:
          server_address: smtp.gmail.com
          server_port: 587
          username: ${{ secrets.EMAIL_USERNAME }}
          password: ${{ secrets.EMAIL_PASSWORD }}
          subject: '❌ Oracle Daily Run Failed'
          to: daniel@pulseb2b.com
          from: GitHub Actions <noreply@github.com>
          body: |
            The Oracle Funding Detector failed to run.
            Check: https://github.com/${{ github.repository }}/actions/runs/${{ github.run_id }}
```

### Step 4: Combine with Existing Ghost Scraper

Create unified workflow `.github/workflows/ghost-oracle-pipeline.yml`:

```yaml
name: Ghost + Oracle Unified Pipeline

on:
  schedule:
    # Run every 6 hours
    - cron: '0 */6 * * *'
  
  workflow_dispatch:

jobs:
  # Job 1: Run Oracle (US funding detection)
  oracle-detector:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: 🔮 Run Oracle
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_SERVICE_KEY: ${{ secrets.SUPABASE_SERVICE_KEY }}
        run: |
          pip install -r requirements-oracle.txt
          python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
          python scripts/oracle_funding_detector.py
      
      - name: 📤 Upload Oracle Results
        uses: actions/upload-artifact@v3
        with:
          name: oracle-results
          path: data/output/oracle/

  # Job 2: Run Ghost Scraper (SEC + LinkedIn + News)
  ghost-scraper:
    runs-on: ubuntu-latest
    needs: oracle-detector
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: 👻 Run Ghost Scraper
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_SERVICE_KEY: ${{ secrets.SUPABASE_SERVICE_KEY }}
        run: |
          pip install -r requirements.txt
          python scripts/ghost_orchestrator.py

  # Job 3: Run Lead Scoring
  lead-scoring:
    runs-on: ubuntu-latest
    needs: [oracle-detector, ghost-scraper]
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: 🎯 Calculate Lead Scores
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_SERVICE_KEY: ${{ secrets.SUPABASE_SERVICE_KEY }}
        run: |
          pip install -r requirements.txt
          python scripts/lead_scoring.py

  # Job 4: Generate Dashboard
  update-dashboard:
    runs-on: ubuntu-latest
    needs: [oracle-detector, ghost-scraper, lead-scoring]
    steps:
      - uses: actions/checkout@v3
      
      - name: 📊 Trigger Dashboard Rebuild
        run: |
          curl -X POST https://api.vercel.com/v1/integrations/deploy/... \
            -H "Authorization: Bearer ${{ secrets.VERCEL_TOKEN }}"
```

### Step 5: Query Combined Data

Create unified view in Supabase:

```sql
-- Combine Oracle + Ghost + Lead Scoring
CREATE VIEW unified_lead_intelligence AS
SELECT 
    o.company_name,
    o.funding_date,
    o.estimated_amount_millions as oracle_funding,
    o.hiring_probability as oracle_score,
    o.tech_stack,
    g.linkedin_jobs,
    g.news_sentiment,
    l.lead_score,
    l.priority,
    GREATEST(o.hiring_probability, l.lead_score) as combined_score,
    CASE
        WHEN GREATEST(o.hiring_probability, l.lead_score) >= 80 THEN 'critical'
        WHEN GREATEST(o.hiring_probability, l.lead_score) >= 60 THEN 'high'
        WHEN GREATEST(o.hiring_probability, l.lead_score) >= 40 THEN 'medium'
        ELSE 'low'
    END as combined_priority,
    o.website,
    o.description
FROM oracle_predictions o
LEFT JOIN ghost_companies g ON LOWER(o.company_name) = LOWER(g.company_name)
LEFT JOIN lead_scores l ON LOWER(o.company_name) = LOWER(l.company_name)
WHERE o.hiring_probability >= 40 OR l.lead_score >= 40
ORDER BY combined_score DESC;
```

## 🎯 Dashboard Integration

Update `frontend/src/app/dashboard/page.tsx` to show Oracle data:

```typescript
// Add Oracle data fetching
async function getOracleOpportunities() {
  const supabase = createServerComponentClient({ cookies })
  
  const { data, error } = await supabase
    .from('oracle_hot_opportunities')
    .select('*')
    .order('hiring_probability', { ascending: false })
    .limit(10)
  
  return data || []
}

// In page component
export default async function DashboardPage() {
  const oracleOpps = await getOracleOpportunities()
  const ghostLeads = await getHighPriorityLeads()
  
  return (
    <div>
      <section>
        <h2>🔮 Oracle Hot Opportunities (US Funding)</h2>
        <BentoGridDashboard opportunities={oracleOpps} />
      </section>
      
      <section>
        <h2>👻 Ghost Intelligence (LATAM Expansion)</h2>
        <BentoGridDashboard opportunities={ghostLeads} />
      </section>
    </div>
  )
}
```

## 📊 Example Combined Output

```json
{
  "company_name": "Anthropic Inc.",
  "oracle_score": 92.3,
  "ghost_score": 85.0,
  "combined_score": 92.3,
  "priority": "critical",
  "signals": {
    "oracle": {
      "funding_date": "2025-12-18",
      "amount": "$450M",
      "tech_stack": ["Python", "PyTorch", "Kubernetes"],
      "hiring_probability": 92.3
    },
    "ghost": {
      "linkedin_jobs": 47,
      "news_sentiment": 0.89,
      "latam_expansion": true
    },
    "combined": {
      "recommendation": "IMMEDIATE CONTACT",
      "reasons": [
        "Recent $450M Series B (18 days ago)",
        "47 open positions globally",
        "High-demand tech stack (Python, PyTorch)",
        "Strong hiring signals detected"
      ]
    }
  }
}
```

## 🚀 Deployment Checklist

- [ ] Create Supabase table `oracle_predictions`
- [ ] Add secrets to GitHub:
  - `SUPABASE_URL`
  - `SUPABASE_SERVICE_KEY`
- [ ] Update `.env.local` with Supabase credentials
- [ ] Test Oracle locally: `python scripts/oracle_funding_detector.py`
- [ ] Deploy GitHub Actions workflow
- [ ] Verify data appears in Supabase
- [ ] Update dashboard to show Oracle data
- [ ] Set up Slack/email alerts for critical leads

## 📈 Performance Metrics

After integration, you'll have:

- **3x more leads**: Oracle (US) + Ghost (LATAM) + Manual
- **Higher accuracy**: Cross-validation between sources
- **Faster response**: Automated daily runs
- **Better targeting**: Combined scoring model

## 🎓 Advanced Use Cases

### Use Case 1: Immediate Follow-Up
```sql
-- Find companies that JUST filed (< 7 days)
SELECT * FROM unified_lead_intelligence
WHERE oracle_funding IS NOT NULL
  AND (CURRENT_DATE - funding_date) <= 7
  AND combined_score >= 70
ORDER BY combined_score DESC;
```

### Use Case 2: Tech Stack Matching
```sql
-- Find Python shops for developer recruitment
SELECT * FROM oracle_predictions
WHERE 'Python' = ANY(tech_stack)
  AND hiring_probability >= 60
ORDER BY hiring_probability DESC;
```

### Use Case 3: Funding + Jobs Correlation
```sql
-- High funding + low job postings = upcoming hiring surge
SELECT 
    o.company_name,
    o.estimated_amount_millions,
    g.linkedin_jobs,
    o.hiring_probability
FROM oracle_predictions o
JOIN ghost_companies g ON LOWER(o.company_name) = LOWER(g.company_name)
WHERE o.estimated_amount_millions >= 50
  AND g.linkedin_jobs < 10
  AND o.hiring_probability >= 70
ORDER BY o.estimated_amount_millions DESC;
```

## 🐛 Troubleshooting

### Issue: Duplicate companies in Supabase
**Solution**: Use `UPSERT` with conflict resolution:
```python
.upsert(records, on_conflict='company_name,funding_date')
```

### Issue: GitHub Actions timeout
**Solution**: Reduce `max_items` in Oracle:
```python
filings = oracle.fetch_sec_filings(max_items=10)  # Instead of 20
```

### Issue: Dashboard not showing Oracle data
**Solution**: Check Supabase RLS policies:
```sql
-- Allow anonymous read access
CREATE POLICY "Allow public read" ON oracle_predictions
FOR SELECT USING (true);
```

## 📚 Documentation Links

- [Oracle Detector Docs](./ORACLE_DETECTOR.md)
- [Ghost Infrastructure Docs](./GHOST_ARCHITECTURE.md)
- [Lead Scoring System](./LEAD_SCORING.md)
- [Dashboard Setup](../frontend/README_DASHBOARD.md)

---

**Ready to Deploy?** Run `./run_oracle.bat` to test locally first! 🚀
