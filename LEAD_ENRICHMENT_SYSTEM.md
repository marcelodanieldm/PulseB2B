# Lead Enrichment & Prioritization System

## 📋 Overview

The **Lead Enrichment & Prioritization System** automatically enriches user signups with company data, calculates multi-factor priority scores, and triggers real-time Telegram alerts for high-value prospects.

### Key Features

✅ **Automatic Company Enrichment** - Extract company data from email domains using Clearbit/Hunter APIs  
✅ **Multi-Factor Lead Scoring** - 5-component algorithm with weighted scoring (250+ points = CRITICAL)  
✅ **Software Factory Detection** - Identify tech companies by keywords across multiple fields  
✅ **High-Value Alerts** - Real-time Telegram notifications for 500+ employee Software Factories  
✅ **Priority Tiers** - 5 tiers from CRITICAL to MINIMAL for pipeline management  
✅ **Weekly Digest** - Top leads summary sent every Monday  
✅ **Admin Dashboard** - Visual interface to view top leads and scores  
✅ **Batch Processing** - Enrich existing users retroactively  

---

## 🏗️ Architecture

```
┌─────────────────┐
│  User Signup    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  1. ENRICHMENT SERVICE                  │
│  --------------------------------       │
│  • Extract domain from email            │
│  • Skip generic providers (gmail)       │
│  • Try Clearbit → Hunter → Basic        │
│  • Store company data                   │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  2. SCORING ENGINE                      │
│  --------------------------------       │
│  • Calculate employee score (0-100)     │
│  • Calculate industry score (0-50)      │
│  • Calculate role score (0-50)          │
│  • Apply revenue multiplier (1.0-1.5x)  │
│  • Add Software Factory bonus (+25)     │
│  • Add tech stack bonus (+25)           │
│  • Determine priority tier              │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  3. ALERT SERVICE                       │
│  --------------------------------       │
│  • Check if high-value prospect         │
│  • If YES: Send Telegram alert          │
│  • Log alert to database                │
│  • Update enrichment_completed flag     │
└─────────────────────────────────────────┘
```

---

## 🎯 Scoring Algorithm

### Formula

```
Total Score = (Employee Score + Industry Score + Role Score) 
              × Revenue Multiplier 
              + Software Factory Bonus 
              + Tech Stack Bonus
```

### Components

#### 1. Employee Score (0-100 points)

| Employee Count | Score |
|----------------|-------|
| 1000+          | 100   |
| 500-999        | 90    |
| 250-499        | 75    |
| 100-249        | 60    |
| 50-99          | 40    |
| 25-49          | 25    |
| 10-24          | 15    |
| 1-9            | 5     |

#### 2. Industry Score (0-50 points)

| Industry           | Score |
|--------------------|-------|
| Software           | 50    |
| SaaS               | 50    |
| Technology         | 50    |
| AI/ML              | 50    |
| Internet           | 45    |
| Marketing          | 35    |
| Finance            | 25    |
| Healthcare         | 20    |
| Other              | 10    |

#### 3. Job Role Score (0-50 points)

| Role             | Score |
|------------------|-------|
| CEO              | 50    |
| CTO              | 50    |
| Founder          | 50    |
| VP               | 45    |
| Director         | 40    |
| Manager          | 30    |
| Senior Engineer  | 20    |
| Engineer         | 15    |
| Other            | 5     |

#### 4. Revenue Multiplier (1.0-1.5x)

| Annual Revenue   | Multiplier |
|------------------|------------|
| $100M+           | 1.5x       |
| $50M-$100M       | 1.4x       |
| $10M-$50M        | 1.3x       |
| $1M-$10M         | 1.2x       |
| <$1M             | 1.0x       |

#### 5. Software Factory Bonus (+25 points)

Triggered if **any** of these keywords appear in company data:
- software, saas, technology, it services, development
- consulting, digital agency, cloud, platform, api
- web services, mobile app, enterprise software, etc.

#### 6. Tech Stack Bonus (+5 per tech, max +25)

Example tech stack: React, Node.js, Python, AWS, Docker = +25 points

---

## 🏆 Priority Tiers

| Tier     | Score Range | % of Leads | Action                               |
|----------|-------------|------------|--------------------------------------|
| CRITICAL | 250+        | Top 1%     | Immediate demo call (24h)            |
| HIGH     | 200-249     | Top 5%     | Personalized outreach (48h)          |
| MEDIUM   | 150-199     | Top 15%    | Add to high-touch sequence           |
| LOW      | 100-149     | Top 30%    | Standard follow-up                   |
| MINIMAL  | <100        | Bottom 70% | Automated nurture campaign           |

---

## 🚨 High-Value Prospect Criteria

**Trigger Telegram Alert if:**
1. Employee Count ≥ 500
2. Is Software Factory (keyword match)

**Example High-Value Companies:**
- BigTech Software Solutions (850 employees, Software Development)
- CloudScale Platform (600 employees, SaaS)
- DataForge AI Systems (550 employees, AI/ML)

---

## 🔧 Setup Guide

### 1. Install Dependencies

```bash
cd PulseB2B
npm install @supabase/supabase-js axios dotenv
```

### 2. Configure Environment Variables

Create `.env` file:

```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key

# Company Enrichment APIs (choose one or both)
CLEARBIT_API_KEY=sk_your_clearbit_api_key  # Paid: $99/month (recommended)
HUNTER_API_KEY=your_hunter_api_key          # Free: 50 requests/month

# Telegram Bot
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_ALERT_CHAT_ID=-1001234567890  # Dedicated high-value alerts channel
```

### 3. Run Database Migration

```bash
# Apply schema
supabase db push

# Or manually run SQL file
psql -h your-db-host -U postgres -d your-database -f supabase/migrations/20251222_lead_enrichment_schema.sql
```

### 4. Create Telegram Bot (One-Time Setup)

```
1. Open Telegram, search for @BotFather
2. Send /newbot
3. Name your bot: "PulseB2B Lead Alerts"
4. Username: pulse_lead_alerts_bot
5. Copy the bot token → Add to .env as TELEGRAM_BOT_TOKEN

6. Create dedicated channel for alerts:
   - Create new channel: "PulseB2B High-Value Prospects"
   - Add your bot as administrator
   - Get chat ID using @getidsbot
   - Copy chat ID → Add to .env as TELEGRAM_ALERT_CHAT_ID
```

### 5. Sign Up for Enrichment API

**Option A: Clearbit (Recommended - More comprehensive)**
- Visit: https://clearbit.com/enrichment
- Pricing: $99/month (200 requests/day)
- Data: 95+ fields (employees, revenue, tech stack, funding, etc.)

**Option B: Hunter.io (Free Tier)**
- Visit: https://hunter.io/api
- Pricing: Free (50 requests/month), $49/month (1000 requests)
- Data: Basic company info (size, industry, social links)

---

## 🚀 Usage

### Enrich Single User

```bash
node scripts/lead_enrichment_service.js enrich <userId> <email>

# Example
node scripts/lead_enrichment_service.js enrich "123e4567-e89b-12d3-a456-426614174000" "cto@acme.com"
```

**Output:**
```
✅ Enrichment Complete!
📧 Email: cto@acme.com
🏢 Company: Acme Software Solutions
👥 Employees: 850
🏭 Industry: Software Development
💰 Revenue: $75,000,000
📍 Location: San Francisco, CA
🔧 Tech Stack: React, Node.js, Python, AWS, Docker
📊 Source: clearbit
```

### Score Single User

```bash
node scripts/lead_scoring_engine.js score <userId>

# Example
node scripts/lead_scoring_engine.js score "123e4567-e89b-12d3-a456-426614174000"
```

**Output:**
```
📊 Lead Score Calculated

👤 User: Sarah Johnson (cto@acme.com)
🏢 Company: Acme Software Solutions
👥 Employees: 850

📊 Score Breakdown:
   Employee Score: 90
   Industry Score: 50
   Role Score: 50
   Revenue Multiplier: 1.4x
   Software Factory: YES (+25)
   Tech Stack: +20 (React, Node.js, Python, AWS)
   ─────────────────────────
   TOTAL SCORE: 285.5
   Priority Tier: CRITICAL ⭐

✅ High-Value Prospect Detected!
   → 500+ employees: YES
   → Software Factory: YES
   → Telegram alert will be sent!
```

### Send High-Value Alert

```bash
node scripts/telegram_alert_service.js alert <userId>

# Example
node scripts/telegram_alert_service.js alert "123e4567-e89b-12d3-a456-426614174000"
```

**Telegram Message:**
```
🚨 HIGH VALUE PROSPECT ALERT! 🚨

🎯 Lead Score: 285.5 (CRITICAL)

👤 Contact Information:
• Name: Sarah Johnson
• Email: cto@acme.com
• Title: CTO
• Signed up: 12/22/2025, 3:45 PM

🏢 Company Profile:
• Name: Acme Software Solutions
• Industry: Software Development
• Size: 850 employees ⭐
• Revenue: $75.0M
• Location: San Francisco, CA

💡 Why High Value?
• ✅ Software Factory
• ✅ 500+ Employees
• Score Breakdown:
  - Employee: 90 pts
  - Industry: 50 pts
  - Role: 50 pts
  - Revenue Multiplier: 1.4x

🎬 Next Actions:
• Schedule demo call within 24 hours
• Send personalized onboarding email
• Add to high-touch sales sequence

🔗 View Company on LinkedIn

━━━━━━━━━━━━━━━━━━━━━━━━
Sent by PulseB2B Lead Intelligence System
```

### Batch Enrich Existing Users

```bash
node scripts/lead_enrichment_service.js batch [limit]

# Example: Enrich first 100 users
node scripts/lead_enrichment_service.js batch 100

# Enrich all users (no limit)
node scripts/lead_enrichment_service.js batch
```

**Output:**
```
🔄 Batch Enrichment Started
📊 Processing 100 users...

[1/100] ✅ john@startup.com → Startup Inc (25 employees)
[2/100] ⏭️  jane@gmail.com → Skipped (generic provider)
[3/100] ✅ cto@bigcorp.com → BigCorp (1200 employees)
...
[100/100] ✅ Complete!

📈 Results:
   Enriched: 87
   Skipped (generic): 8
   Failed: 5
   Duration: 2m 15s
```

### Get Top Leads

```bash
node scripts/lead_scoring_engine.js top [limit]

# Example: Show top 20 leads
node scripts/lead_scoring_engine.js top 20
```

**Output:**
```
🏆 Top 20 Leads by Priority Score

Rank | Name              | Company             | Score | Tier     | Employees
-----|-------------------|---------------------|-------|----------|----------
1    | Sarah Johnson     | Acme Software       | 285.5 | CRITICAL | 850
2    | Michael Chen      | CloudScale Platform | 270.0 | CRITICAL | 600
3    | Emily Rodriguez   | DataForge AI        | 255.0 | CRITICAL | 550
4    | David Kim         | TechVentures Inc    | 235.0 | HIGH     | 450
...
```

### Send Weekly Digest

```bash
node scripts/telegram_alert_service.js digest [limit]

# Example: Top 10 leads from last week
node scripts/telegram_alert_service.js digest 10
```

**Telegram Message:**
```
📊 WEEKLY LEAD DIGEST
Week of Dec 16-22, 2025

📈 Summary:
• Total New Leads: 47
• High-Value Prospects: 3
• Average Score: 142.5

🏆 Top 5 Leads:
1. Sarah Johnson (Acme Software) - 285.5 (CRITICAL)
2. Michael Chen (CloudScale Platform) - 270.0 (CRITICAL)
3. Emily Rodriguez (DataForge AI) - 255.0 (CRITICAL)
4. David Kim (TechVentures Inc) - 235.0 (HIGH)
5. Lisa Wang (InnovateCo) - 220.0 (HIGH)

📊 Tier Breakdown:
• CRITICAL: 3 (6%)
• HIGH: 7 (15%)
• MEDIUM: 12 (26%)
• LOW: 15 (32%)
• MINIMAL: 10 (21%)
```

### Test Mode (No Real Data Required)

```bash
# Test enrichment with sample domain
node scripts/lead_enrichment_service.js domain stripe.com

# Test scoring with mock data
node scripts/lead_scoring_engine.js test

# Test Telegram alert (mock data)
node scripts/telegram_alert_service.js test
```

---

## 🔗 Webhook Integration

### Real-Time Enrichment on Signup

Create `scripts/signup_webhook.js`:

```javascript
const express = require('express');
const { enrichUser } = require('./lead_enrichment_service');
const { scoreUser } = require('./lead_scoring_engine');
const { sendHighValueAlert } = require('./telegram_alert_service');

const app = express();
app.use(express.json());

app.post('/api/webhooks/user-signup', async (req, res) => {
  const { userId, email } = req.body;
  
  // Return 200 immediately, process async
  res.status(200).json({ message: 'Enrichment queued' });
  
  try {
    // 1. Enrich company data
    await enrichUser(userId, email);
    
    // 2. Calculate lead score
    await scoreUser(userId);
    
    // 3. Check if high-value prospect
    const { data: score } = await supabase
      .from('lead_scores')
      .select('is_high_value_prospect')
      .eq('user_id', userId)
      .single();
    
    // 4. Send alert if high-value
    if (score?.is_high_value_prospect) {
      await sendHighValueAlert(userId);
    }
    
    // 5. Update enrichment flag
    await supabase
      .from('users')
      .update({ 
        enrichment_completed: true,
        last_enriched_at: new Date().toISOString()
      })
      .eq('id', userId);
      
  } catch (error) {
    console.error('Webhook error:', error);
  }
});

app.listen(3001, () => {
  console.log('Webhook server running on port 3001');
});
```

**Start webhook server:**
```bash
node scripts/signup_webhook.js
```

**Trigger from your auth flow:**
```javascript
// In your signup handler
await fetch('http://localhost:3001/api/webhooks/user-signup', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ userId, email })
});
```

---

## 📅 Automated Weekly Digest (GitHub Actions)

Create `.github/workflows/weekly_lead_digest.yml`:

```yaml
name: Weekly Lead Digest

on:
  schedule:
    # Every Monday at 10:00 AM UTC
    - cron: '0 10 * * 1'
  workflow_dispatch:  # Manual trigger

jobs:
  send-digest:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: npm install @supabase/supabase-js axios dotenv
      
      - name: Send weekly digest
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_SERVICE_KEY: ${{ secrets.SUPABASE_SERVICE_KEY }}
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_ALERT_CHAT_ID: ${{ secrets.TELEGRAM_ALERT_CHAT_ID }}
        run: node scripts/telegram_alert_service.js digest 20
```

---

## 📊 Database Queries

### Get All High-Value Prospects

```sql
SELECT * FROM high_value_prospects;
```

### Get Lead Pipeline Summary

```sql
SELECT * FROM lead_pipeline_summary;
```

### Get Recent Signups (Last 7 Days)

```sql
SELECT * FROM recent_signups_enriched;
```

### Get Top 20 Leads

```sql
SELECT * FROM get_top_leads(20);
```

### Check if User Needs Enrichment

```sql
SELECT needs_enrichment('user-uuid-here');
```

### Average Score by Industry

```sql
SELECT 
  ce.industry,
  COUNT(*) as lead_count,
  ROUND(AVG(ls.total_score), 2) as avg_score,
  MAX(ls.total_score) as max_score,
  COUNT(CASE WHEN ls.is_high_value_prospect THEN 1 END) as high_value_count
FROM company_enrichment ce
INNER JOIN lead_scores ls ON ce.user_id = ls.user_id
WHERE ce.industry IS NOT NULL
GROUP BY ce.industry
ORDER BY avg_score DESC
LIMIT 10;
```

### Software Factories by Size

```sql
SELECT 
  CASE 
    WHEN ce.employee_count >= 1000 THEN '1000+'
    WHEN ce.employee_count >= 500 THEN '500-999'
    WHEN ce.employee_count >= 250 THEN '250-499'
    ELSE '<250'
  END as company_size,
  COUNT(*) as lead_count,
  AVG(ls.total_score) as avg_score
FROM company_enrichment ce
INNER JOIN lead_scores ls ON ce.user_id = ls.user_id
WHERE ls.is_software_factory = TRUE
GROUP BY 1
ORDER BY avg_score DESC;
```

---

## 🐛 Troubleshooting

### Issue: Enrichment failing with "Invalid API key"

**Solution:**
- Check `.env` file has correct API keys
- Verify Clearbit/Hunter API key is active
- Check API usage limits (Hunter free tier: 50 requests/month)

```bash
# Test API key
curl -H "Authorization: Bearer YOUR_KEY" https://company.clearbit.com/v2/companies/find?domain=stripe.com
```

### Issue: Telegram alerts not sending

**Solution:**
- Verify bot token is correct
- Check bot is added as admin to channel
- Confirm chat ID is correct (should be negative for channels)
- Test with mock alert:

```bash
node scripts/telegram_alert_service.js test
```

### Issue: Generic email providers being enriched

**Solution:**
- Check `isGenericProvider()` function in `lead_enrichment_service.js`
- Add more providers to `genericProviders` array:

```javascript
const genericProviders = [
  'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
  'icloud.com', 'aol.com', 'protonmail.com', 'zoho.com',
  'mail.com', 'yandex.com', 'gmx.com', 'custom-domain.com'
];
```

### Issue: Software Factory not detected

**Solution:**
- Check keywords in `isSoftwareFactory()` function
- Add more industry-specific keywords:

```javascript
const softwareKeywords = [
  'software', 'saas', 'technology', 'it services',
  'development', 'consulting', 'digital agency',
  'cloud', 'platform', 'api', 'web services',
  'mobile app', 'enterprise software', 'dev tools',
  'your-custom-keyword'
];
```

### Issue: Scores seem too low/high

**Solution:**
- Adjust scoring weights in `lead_scoring_engine.js`:

```javascript
const SCORING_CONFIG = {
  employeeCount: {
    '1000+': 100,  // Increase for larger companies
    '500-999': 90,
    // ...
  },
  industry: {
    'Software': 50,  // Increase for preferred industries
    // ...
  }
};
```

### Issue: Rate limiting from APIs

**Solution:**
- Increase delay in batch processing:

```javascript
// In lead_enrichment_service.js
await new Promise(resolve => setTimeout(resolve, 2000)); // 2 seconds instead of 1
```

---

## 📈 Performance & Costs

### API Costs

| Service           | Free Tier         | Paid Plan         | Recommendation    |
|-------------------|-------------------|-------------------|-------------------|
| **Clearbit**      | N/A               | $99/mo (200/day)  | Best for scale    |
| **Hunter.io**     | 50 req/month      | $49/mo (1000/mo)  | Good for testing  |
| **Telegram Bot**  | Unlimited FREE    | FREE              | Always use        |

### Processing Time

- **Single user enrichment**: 2-5 seconds
- **Batch 100 users**: ~2 minutes (with rate limiting)
- **Scoring calculation**: <1 second
- **Telegram alert send**: <2 seconds

### Database Size Estimates

| Users  | company_enrichment | lead_scores | lead_alerts | Total   |
|--------|-------------------|-------------|-------------|---------|
| 1,000  | ~1 MB             | ~500 KB     | ~200 KB     | ~2 MB   |
| 10,000 | ~10 MB            | ~5 MB       | ~2 MB       | ~17 MB  |
| 100,000| ~100 MB           | ~50 MB      | ~20 MB      | ~170 MB |

---

## 🎯 Next Steps

1. ✅ **Apply database migration** → `supabase db push`
2. ✅ **Configure API keys** → Add to `.env` file
3. ✅ **Create Telegram bot** → @BotFather setup
4. ✅ **Test enrichment** → `node lead_enrichment_service.js domain stripe.com`
5. ✅ **Test scoring** → `node lead_scoring_engine.js test`
6. ✅ **Test alerts** → `node telegram_alert_service.js test`
7. ✅ **Batch enrich existing users** → `node lead_enrichment_service.js batch 100`
8. ✅ **Set up webhook** → Create `signup_webhook.js` endpoint
9. ✅ **Enable GitHub Actions** → Weekly digest automation
10. ✅ **Build admin dashboard** → View top leads UI

---

## 📚 Related Documentation

- [Enrichment Service Code](../scripts/lead_enrichment_service.js)
- [Scoring Engine Code](../scripts/lead_scoring_engine.js)
- [Alert Service Code](../scripts/telegram_alert_service.js)
- [Database Schema](../supabase/migrations/20251222_lead_enrichment_schema.sql)
- [Clearbit API Docs](https://clearbit.com/docs)
- [Hunter.io API Docs](https://hunter.io/api-documentation)
- [Telegram Bot API Docs](https://core.telegram.org/bots/api)

---

## 🤝 Support

For questions or issues:
1. Check [Troubleshooting](#troubleshooting) section
2. Review [Database Queries](#database-queries) for analytics
3. Test with mock data using `test` commands
4. Adjust scoring weights in `lead_scoring_engine.js`
5. Add custom keywords for Software Factory detection

---

**Built by PulseB2B Engineering Team** 🚀  
**Last Updated:** December 22, 2025
