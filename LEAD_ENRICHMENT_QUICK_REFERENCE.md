# Lead Enrichment Quick Reference

⚡ **Quick Commands** for the Lead Enrichment & Prioritization System

---

## 🚀 Getting Started (5 minutes)

```bash
# 1. Install dependencies
npm install @supabase/supabase-js axios dotenv

# 2. Configure .env file
cp .env.example .env  # Add your API keys

# 3. Apply database migration
supabase db push

# 4. Test all components
./test_lead_enrichment.sh   # Linux/Mac
test_lead_enrichment.bat    # Windows
```

---

## 📋 Common Commands

### Enrich Single User

```bash
# Syntax
node scripts/lead_enrichment_service.js enrich <userId> <email>

# Example
node scripts/lead_enrichment_service.js enrich "123e4567-e89b-12d3-a456-426614174000" "cto@acme.com"

# Output: Company data stored in company_enrichment table
```

### Score Single User

```bash
# Syntax
node scripts/lead_scoring_engine.js score <userId>

# Example
node scripts/lead_scoring_engine.js score "123e4567-e89b-12d3-a456-426614174000"

# Output: Total score, priority tier (CRITICAL/HIGH/etc.), breakdown
```

### Send High-Value Alert

```bash
# Syntax (automatic check if high-value)
node scripts/telegram_alert_service.js alert <userId>

# Example
node scripts/telegram_alert_service.js alert "123e4567-e89b-12d3-a456-426614174000"

# Output: Telegram message if 500+ employees + Software Factory
```

### Complete Pipeline (All 3 Steps)

```bash
# 1. Enrich
node scripts/lead_enrichment_service.js enrich "user-id" "email@company.com"

# 2. Score
node scripts/lead_scoring_engine.js score "user-id"

# 3. Alert (if high-value)
node scripts/telegram_alert_service.js alert "user-id"
```

---

## 📊 Batch Operations

### Enrich Existing Users

```bash
# Enrich first 100 users
node scripts/lead_enrichment_service.js batch 100

# Enrich all users (no limit)
node scripts/lead_enrichment_service.js batch

# Rate limiting: 1 request/second (configurable)
```

### Get Top Leads

```bash
# Show top 20 leads by score
node scripts/lead_scoring_engine.js top 20

# Show top 50 leads
node scripts/lead_scoring_engine.js top 50

# Output: Rank, name, company, score, tier, employees
```

### Send Weekly Digest

```bash
# Send top 10 leads from last week
node scripts/telegram_alert_service.js digest 10

# Send top 20 leads
node scripts/telegram_alert_service.js digest 20

# Output: Summary stats + top leads list to Telegram
```

---

## 🧪 Testing Commands

### Test Enrichment (Mock Domain)

```bash
# Test with public company domain
node scripts/lead_enrichment_service.js domain stripe.com
node scripts/lead_enrichment_service.js domain shopify.com
node scripts/lead_enrichment_service.js domain hubspot.com

# Output: Company data from Clearbit/Hunter API
```

### Test Scoring (Mock User)

```bash
# Test with mock user data
node scripts/lead_scoring_engine.js test

# Output: Score breakdown with mock company (Acme Software, 850 employees)
```

### Test Alert (Mock Message)

```bash
# Test Telegram alert without real user
node scripts/telegram_alert_service.js test

# Output: Mock high-value alert sent to Telegram
```

### Run All Tests

```bash
# Linux/Mac
chmod +x test_lead_enrichment.sh
./test_lead_enrichment.sh

# Windows
test_lead_enrichment.bat

# Output: Tests enrichment → scoring → alert with mock data
```

---

## 🌐 Webhook Server

### Start Server

```bash
# Start webhook on port 3001
node scripts/signup_webhook.js

# Custom port
WEBHOOK_PORT=8080 node scripts/signup_webhook.js

# With webhook secret validation
WEBHOOK_SECRET=your-secret node scripts/signup_webhook.js
```

### Trigger Webhook

```bash
# Enrich single user (POST request)
curl -X POST http://localhost:3001/api/webhooks/user-signup \
  -H "Content-Type: application/json" \
  -d '{"userId": "user-id", "email": "cto@acme.com"}'

# Batch enrich (POST request)
curl -X POST http://localhost:3001/api/webhooks/batch-enrich \
  -H "Content-Type: application/json" \
  -d '{"userIds": ["user-id-1", "user-id-2"]}'

# Check status (GET request)
curl http://localhost:3001/api/webhooks/status/user-id

# Health check
curl http://localhost:3001/health
```

---

## 🗄️ Database Queries

### Get All High-Value Prospects

```sql
SELECT * FROM high_value_prospects
ORDER BY total_score DESC;
```

### Get Lead Pipeline Summary

```sql
SELECT * FROM lead_pipeline_summary;
-- Shows count by tier: CRITICAL, HIGH, MEDIUM, LOW, MINIMAL
```

### Get Recent Signups (Last 7 Days)

```sql
SELECT * FROM recent_signups_enriched
ORDER BY signup_date DESC;
```

### Get Top 20 Leads (SQL)

```sql
SELECT * FROM get_top_leads(20);
```

### Check if User Needs Enrichment

```sql
SELECT needs_enrichment('user-uuid-here');
-- Returns TRUE if not enriched or >30 days old
```

### Average Score by Industry

```sql
SELECT 
  ce.industry,
  COUNT(*) as lead_count,
  ROUND(AVG(ls.total_score), 2) as avg_score,
  COUNT(CASE WHEN ls.is_high_value_prospect THEN 1 END) as high_value_count
FROM company_enrichment ce
INNER JOIN lead_scores ls ON ce.user_id = ls.user_id
WHERE ce.industry IS NOT NULL
GROUP BY ce.industry
ORDER BY avg_score DESC
LIMIT 10;
```

---

## ⚙️ Environment Variables

### Required

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key
```

### Company Enrichment (Choose One or Both)

```bash
# Option A: Clearbit (Paid, $99/month, comprehensive)
CLEARBIT_API_KEY=sk_your_clearbit_api_key

# Option B: Hunter.io (Free tier: 50/month, basic)
HUNTER_API_KEY=your_hunter_api_key
```

### Telegram Bot

```bash
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_ALERT_CHAT_ID=-1001234567890  # Negative for channels
```

### Optional

```bash
WEBHOOK_PORT=3001                # Default port for webhook server
WEBHOOK_SECRET=your-secret       # For webhook authentication
```

---

## 🎯 Scoring Tiers

| Tier     | Score Range | Action                          |
|----------|-------------|---------------------------------|
| CRITICAL | 250+        | Immediate demo call (24h)       |
| HIGH     | 200-249     | Personalized outreach (48h)     |
| MEDIUM   | 150-199     | Add to high-touch sequence      |
| LOW      | 100-149     | Standard follow-up              |
| MINIMAL  | <100        | Automated nurture campaign      |

---

## 🚨 High-Value Criteria

**Telegram alert triggers when:**
1. Employee Count ≥ 500
2. Software Factory = TRUE (keyword match in industry/sector/description)

**Example keywords:** software, saas, technology, it services, development, consulting, digital agency, cloud, platform, api, web services, etc.

---

## 🔧 Configuration Adjustments

### Increase Batch Rate Limit

```javascript
// In lead_enrichment_service.js, line ~440
await new Promise(resolve => setTimeout(resolve, 2000)); // 2 seconds instead of 1
```

### Adjust Employee Score Weights

```javascript
// In lead_scoring_engine.js, line ~30
const SCORING_CONFIG = {
  employeeCount: {
    '1000+': 100,  // Increase for larger companies
    '500-999': 90,
    // ...
  }
};
```

### Add Custom Industry Keywords

```javascript
// In lead_scoring_engine.js, line ~180
const softwareKeywords = [
  'software', 'saas', 'technology',
  'your-custom-keyword'  // Add here
];
```

### Change High-Value Threshold

```javascript
// In lead_scoring_engine.js, isHighValueProspect()
return employee_count >= 250  // Lower from 500
    && isSoftwareFactory(companyData);
```

---

## 📚 Documentation Files

- **[LEAD_ENRICHMENT_SYSTEM.md](LEAD_ENRICHMENT_SYSTEM.md)** - Complete guide (900+ lines)
- **[LEAD_ENRICHMENT_SUMMARY.md](LEAD_ENRICHMENT_SUMMARY.md)** - Implementation summary
- **[LEAD_ENRICHMENT_QUICK_REFERENCE.md](LEAD_ENRICHMENT_QUICK_REFERENCE.md)** - This file

---

## 🐛 Troubleshooting Quick Fixes

### API Key Issues

```bash
# Test Clearbit API
curl -H "Authorization: Bearer YOUR_KEY" \
  https://company.clearbit.com/v2/companies/find?domain=stripe.com

# Test Hunter API
curl "https://api.hunter.io/v2/domain-search?domain=stripe.com&api_key=YOUR_KEY"
```

### Telegram Not Sending

```bash
# Test bot token
curl https://api.telegram.org/botYOUR_TOKEN/getMe

# Test send message
curl -X POST "https://api.telegram.org/botYOUR_TOKEN/sendMessage" \
  -d "chat_id=YOUR_CHAT_ID&text=Test"
```

### Database Connection Issues

```bash
# Test Supabase connection
psql -h db.your-project.supabase.co -U postgres -d postgres

# Check if tables exist
psql -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
```

---

## 🎉 One-Liner Commands

```bash
# Complete enrichment pipeline for one user
node scripts/lead_enrichment_service.js enrich "user-id" "email@company.com" && \
node scripts/lead_scoring_engine.js score "user-id" && \
node scripts/telegram_alert_service.js alert "user-id"

# Test entire system
node scripts/lead_enrichment_service.js domain stripe.com && \
node scripts/lead_scoring_engine.js test && \
node scripts/telegram_alert_service.js test

# Start webhook + background
nohup node scripts/signup_webhook.js > webhook.log 2>&1 &

# Weekly digest (cron job)
0 10 * * 1 cd /path/to/PulseB2B && node scripts/telegram_alert_service.js digest 20
```

---

**Last Updated:** December 22, 2025  
**Version:** 1.0.0  
**Status:** ✅ Production Ready
