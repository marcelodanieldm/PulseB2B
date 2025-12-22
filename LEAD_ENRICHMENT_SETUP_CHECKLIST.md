# Lead Enrichment Setup Checklist

Step-by-step setup guide for the Lead Enrichment & Prioritization System.

---

## ✅ Pre-Deployment Checklist

### Phase 1: Environment Setup (10 minutes)

- [ ] **1.1 Install Node.js**
  ```bash
  # Check version (requires 16+)
  node --version
  
  # If not installed, download from:
  # https://nodejs.org/
  ```

- [ ] **1.2 Install NPM Dependencies**
  ```bash
  cd PulseB2B
  npm install @supabase/supabase-js axios dotenv express
  ```

- [ ] **1.3 Verify Supabase Credentials**
  ```bash
  # Get from: https://supabase.com/dashboard/project/_/settings/api
  # Check you have:
  # - Project URL
  # - Service Role Key (NOT anon key)
  ```

---

### Phase 2: API Configuration (20 minutes)

#### Option A: Clearbit (Recommended for Production)

- [ ] **2.1 Sign up for Clearbit**
  - Visit: https://clearbit.com/enrichment
  - Create account
  - Choose plan: $99/month (200 requests/day)
  - Get API key from dashboard

- [ ] **2.2 Test Clearbit API**
  ```bash
  curl -H "Authorization: Bearer YOUR_KEY" \
    "https://company.clearbit.com/v2/companies/find?domain=stripe.com"
  
  # Should return JSON with company data
  ```

#### Option B: Hunter.io (Free Tier for Testing)

- [ ] **2.3 Sign up for Hunter.io**
  - Visit: https://hunter.io/api
  - Create account (FREE - 50 requests/month)
  - Get API key from dashboard

- [ ] **2.4 Test Hunter.io API**
  ```bash
  curl "https://api.hunter.io/v2/domain-search?domain=stripe.com&api_key=YOUR_KEY"
  
  # Should return JSON with company data
  ```

---

### Phase 3: Telegram Bot Setup (15 minutes)

- [ ] **3.1 Create Telegram Bot**
  1. Open Telegram app (desktop or mobile)
  2. Search for `@BotFather`
  3. Send `/newbot`
  4. Name: `PulseB2B Lead Alerts`
  5. Username: `pulse_lead_alerts_bot` (must be unique)
  6. Copy bot token (format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

- [ ] **3.2 Test Bot Token**
  ```bash
  curl "https://api.telegram.org/botYOUR_TOKEN/getMe"
  
  # Should return bot info (username, id, etc.)
  ```

- [ ] **3.3 Create Dedicated Channel**
  1. Open Telegram → Create New Channel
  2. Name: `PulseB2B High-Value Prospects`
  3. Type: Private (only your team)
  4. Description: `Automated alerts for 500+ employee Software Factory signups`

- [ ] **3.4 Add Bot as Administrator**
  1. Open channel settings
  2. Administrators → Add Administrator
  3. Search for your bot username
  4. Grant permissions: Send Messages, Edit Messages

- [ ] **3.5 Get Chat ID**
  ```bash
  # Method 1: Use @getidsbot
  # 1. Add @getidsbot to your channel
  # 2. It will send the chat ID (starts with -)
  # 3. Remove @getidsbot from channel
  
  # Method 2: Manual (send message first)
  # 1. Post any message to channel
  # 2. Run:
  curl "https://api.telegram.org/botYOUR_TOKEN/getUpdates"
  # 3. Find "chat":{"id":-1001234567890}
  ```

- [ ] **3.6 Test Telegram Alert**
  ```bash
  curl -X POST "https://api.telegram.org/botYOUR_TOKEN/sendMessage" \
    -d "chat_id=YOUR_CHAT_ID" \
    -d "text=Test message from PulseB2B"
  
  # Should appear in your channel
  ```

---

### Phase 4: Environment Variables (5 minutes)

- [ ] **4.1 Create .env File**
  ```bash
  # In PulseB2B root directory
  touch .env
  ```

- [ ] **4.2 Add Required Variables**
  ```bash
  # Supabase (REQUIRED)
  SUPABASE_URL=https://your-project.supabase.co
  SUPABASE_SERVICE_KEY=your-service-role-key
  
  # Company Enrichment (CHOOSE ONE OR BOTH)
  CLEARBIT_API_KEY=sk_your_clearbit_key
  HUNTER_API_KEY=your_hunter_key
  
  # Telegram Bot (REQUIRED)
  TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
  TELEGRAM_ALERT_CHAT_ID=-1001234567890
  
  # Webhook (OPTIONAL)
  WEBHOOK_PORT=3001
  WEBHOOK_SECRET=your-random-secret-123
  ```

- [ ] **4.3 Verify .env File**
  ```bash
  # Check file exists
  cat .env
  
  # Check no syntax errors
  node -e "require('dotenv').config(); console.log('✅ .env loaded')"
  ```

---

### Phase 5: Database Migration (5 minutes)

- [ ] **5.1 Connect to Supabase**
  ```bash
  # Option A: Using Supabase CLI
  supabase db push
  
  # Option B: Manual SQL
  # 1. Open Supabase Dashboard
  # 2. SQL Editor
  # 3. Copy/paste supabase/migrations/20251222_lead_enrichment_schema.sql
  # 4. Run query
  ```

- [ ] **5.2 Verify Tables Created**
  ```sql
  -- Run in Supabase SQL Editor
  SELECT table_name 
  FROM information_schema.tables 
  WHERE table_schema = 'public' 
  AND table_name IN ('company_enrichment', 'lead_scores', 'lead_alerts')
  ORDER BY table_name;
  
  -- Should return 3 rows
  ```

- [ ] **5.3 Verify Views Created**
  ```sql
  SELECT table_name 
  FROM information_schema.views 
  WHERE table_schema = 'public'
  AND table_name LIKE '%lead%'
  OR table_name LIKE '%prospect%';
  
  -- Should show: high_value_prospects, lead_pipeline_summary, recent_signups_enriched
  ```

- [ ] **5.4 Verify Functions Created**
  ```sql
  SELECT routine_name 
  FROM information_schema.routines 
  WHERE routine_schema = 'public'
  AND routine_name LIKE '%lead%'
  OR routine_name LIKE '%enrichment%';
  
  -- Should show: get_lead_enrichment_status, get_top_leads, needs_enrichment
  ```

---

### Phase 6: Testing (15 minutes)

- [ ] **6.1 Test Company Enrichment**
  ```bash
  # Test with public company domain
  node scripts/lead_enrichment_service.js domain stripe.com
  
  # Expected output:
  # ✅ Company found
  # 🏢 Name: Stripe
  # 👥 Employees: 8000+
  # 🏭 Industry: Financial Services
  ```

- [ ] **6.2 Test Lead Scoring**
  ```bash
  # Test with mock user data
  node scripts/lead_scoring_engine.js test
  
  # Expected output:
  # 📊 Lead Score Calculated
  # Total Score: 285.5
  # Priority Tier: CRITICAL
  ```

- [ ] **6.3 Test Telegram Alert**
  ```bash
  # Test with mock high-value prospect
  node scripts/telegram_alert_service.js test
  
  # Expected output:
  # ✅ Telegram alert sent
  # Check your Telegram channel for message
  ```

- [ ] **6.4 Run Complete Test Suite**
  ```bash
  # Linux/Mac
  chmod +x test_lead_enrichment.sh
  ./test_lead_enrichment.sh
  
  # Windows
  test_lead_enrichment.bat
  
  # Should run all 3 tests sequentially
  ```

---

### Phase 7: Production Deployment (10 minutes)

- [ ] **7.1 Test Webhook Server**
  ```bash
  # Start webhook server
  node scripts/signup_webhook.js
  
  # In another terminal, test health endpoint
  curl http://localhost:3001/health
  
  # Expected: {"status":"ok","service":"lead-enrichment-webhook"}
  ```

- [ ] **7.2 Test Webhook Enrichment**
  ```bash
  # Trigger webhook (replace with real user ID/email)
  curl -X POST http://localhost:3001/api/webhooks/user-signup \
    -H "Content-Type: application/json" \
    -d '{"userId":"test-user-123","email":"test@example.com"}'
  
  # Expected: {"message":"Enrichment queued","status":"processing"}
  # Check logs for enrichment pipeline execution
  ```

- [ ] **7.3 Enable GitHub Actions (Optional)**
  1. Go to GitHub repo → Settings → Secrets and variables → Actions
  2. Add secrets:
     - `SUPABASE_URL`
     - `SUPABASE_SERVICE_KEY`
     - `TELEGRAM_BOT_TOKEN`
     - `TELEGRAM_ALERT_CHAT_ID`
  3. Enable workflow: `.github/workflows/weekly_lead_digest.yml`
  4. Test manual trigger: Actions → Weekly Lead Digest → Run workflow

---

### Phase 8: Integration (15 minutes)

- [ ] **8.1 Add Enrichment to Signup Flow**
  
  **Option A: Webhook (Recommended)**
  ```javascript
  // In your signup handler (e.g., pages/api/auth/signup.js)
  async function handleSignup(userId, email) {
    // ... existing signup logic ...
    
    // Trigger enrichment webhook
    await fetch('http://localhost:3001/api/webhooks/user-signup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ userId, email })
    });
  }
  ```
  
  **Option B: Direct Function Call**
  ```javascript
  const { enrichUser } = require('./scripts/lead_enrichment_service');
  const { scoreUser } = require('./scripts/lead_scoring_engine');
  const { sendHighValueAlert } = require('./scripts/telegram_alert_service');
  
  async function handleSignup(userId, email) {
    // ... existing signup logic ...
    
    // Run enrichment pipeline
    await enrichUser(userId, email);
    await scoreUser(userId);
    
    // Check if high-value
    const { data } = await supabase
      .from('lead_scores')
      .select('is_high_value_prospect')
      .eq('user_id', userId)
      .single();
    
    if (data?.is_high_value_prospect) {
      await sendHighValueAlert(userId);
    }
  }
  ```

- [ ] **8.2 Test with Real Signup**
  1. Create test user account
  2. Use company email (not gmail/yahoo)
  3. Check console logs for enrichment pipeline
  4. Verify data in Supabase tables:
     - `company_enrichment` table
     - `lead_scores` table
     - `lead_alerts` table (if high-value)
  5. Check Telegram channel for alert (if 500+ employees + Software Factory)

---

## 🎯 Success Criteria

### Enrichment Service

- ✅ Domain extraction works (email → domain)
- ✅ Generic provider detection (skips gmail.com, etc.)
- ✅ Clearbit/Hunter API returns company data
- ✅ Data stored in `company_enrichment` table
- ✅ Batch processing works with rate limiting

### Scoring Engine

- ✅ Employee score calculated correctly (0-100)
- ✅ Industry score applied (Software = 50)
- ✅ Role score extracted from job title
- ✅ Revenue multiplier applied (1.0-1.5x)
- ✅ Software Factory detected (keyword match)
- ✅ Tech stack bonus calculated (+5 per tech)
- ✅ Total score stored in `lead_scores` table
- ✅ Priority tier determined (CRITICAL/HIGH/etc.)

### Alert Service

- ✅ High-value criteria checked (500+ + Software Factory)
- ✅ Rich HTML message generated
- ✅ Telegram Bot API receives POST request
- ✅ Message appears in Telegram channel
- ✅ Alert logged to `lead_alerts` table
- ✅ Weekly digest works (top leads summary)

### Webhook Server

- ✅ Server starts on port 3001
- ✅ Health check responds (GET /health)
- ✅ Signup webhook processes requests (POST /api/webhooks/user-signup)
- ✅ Status check works (GET /api/webhooks/status/:userId)
- ✅ Error handling (doesn't crash on failures)

---

## 📊 Monitoring Checklist

### Daily Checks

- [ ] Check enrichment queue (users.enrichment_completed = FALSE)
  ```sql
  SELECT COUNT(*) FROM users WHERE enrichment_completed = FALSE;
  ```

- [ ] Check high-value prospects today
  ```sql
  SELECT * FROM high_value_prospects WHERE DATE(scored_at) = CURRENT_DATE;
  ```

- [ ] Check alert delivery status
  ```sql
  SELECT 
    alert_type, 
    COUNT(*) as count,
    COUNT(CASE WHEN delivery_status = 'sent' THEN 1 END) as sent,
    COUNT(CASE WHEN delivery_status = 'failed' THEN 1 END) as failed
  FROM lead_alerts 
  WHERE DATE(sent_at) = CURRENT_DATE
  GROUP BY alert_type;
  ```

### Weekly Checks

- [ ] Review lead pipeline summary
  ```sql
  SELECT * FROM lead_pipeline_summary;
  ```

- [ ] Check average score by industry
  ```sql
  SELECT 
    ce.industry,
    COUNT(*) as lead_count,
    ROUND(AVG(ls.total_score), 2) as avg_score
  FROM company_enrichment ce
  INNER JOIN lead_scores ls ON ce.user_id = ls.user_id
  GROUP BY ce.industry
  ORDER BY avg_score DESC
  LIMIT 10;
  ```

- [ ] Verify weekly digest sent (check Telegram channel on Monday)

### Monthly Checks

- [ ] Review API usage (Clearbit/Hunter limits)
- [ ] Check enrichment success rate
  ```sql
  SELECT 
    enrichment_source,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
  FROM company_enrichment
  WHERE enriched_at >= NOW() - INTERVAL '30 days'
  GROUP BY enrichment_source;
  ```

- [ ] Update Software Factory keywords if needed
- [ ] Adjust scoring weights based on performance

---

## 🐛 Common Issues & Solutions

### Issue 1: Enrichment returns null

**Symptoms:**
- `enrichUser()` returns null
- Company data not found

**Solutions:**
- [ ] Check if domain is generic (gmail.com, yahoo.com)
- [ ] Verify API key is valid (Clearbit/Hunter)
- [ ] Check API usage limits (Hunter: 50/month free)
- [ ] Try different domain for testing (stripe.com, shopify.com)

### Issue 2: Telegram alert not sending

**Symptoms:**
- `sendHighValueAlert()` runs but no message
- Error: "Forbidden: bot is not a member of the channel"

**Solutions:**
- [ ] Verify bot is added to channel as administrator
- [ ] Check chat ID is negative (e.g., -1001234567890)
- [ ] Test bot token: `curl https://api.telegram.org/botTOKEN/getMe`
- [ ] Send test message: `node telegram_alert_service.js test`

### Issue 3: Webhook server not responding

**Symptoms:**
- `curl http://localhost:3001/health` times out
- Connection refused error

**Solutions:**
- [ ] Check if server is running: `ps aux | grep signup_webhook`
- [ ] Verify port 3001 not in use: `lsof -i :3001` (Mac/Linux) or `netstat -ano | findstr :3001` (Windows)
- [ ] Check firewall settings
- [ ] Try different port: `WEBHOOK_PORT=8080 node scripts/signup_webhook.js`

### Issue 4: Database tables not created

**Symptoms:**
- Error: "relation 'company_enrichment' does not exist"

**Solutions:**
- [ ] Run migration: `supabase db push`
- [ ] Or manually execute SQL in Supabase Dashboard
- [ ] Verify Supabase credentials in .env
- [ ] Check table exists: `SELECT * FROM information_schema.tables WHERE table_name = 'company_enrichment';`

### Issue 5: Scoring seems incorrect

**Symptoms:**
- All scores are too low/high
- Software Factory not detected

**Solutions:**
- [ ] Test with mock data: `node lead_scoring_engine.js test`
- [ ] Adjust scoring weights in `lead_scoring_engine.js`
- [ ] Add custom keywords to `softwareKeywords` array
- [ ] Change high-value threshold (500 → 250 employees)

---

## 🎉 Deployment Complete!

Once all checkboxes are complete, your Lead Enrichment & Prioritization System is ready for production!

### Final Steps

1. ✅ All environment variables configured
2. ✅ Database migration applied
3. ✅ Telegram bot created and tested
4. ✅ Webhook server running
5. ✅ Integrated with signup flow
6. ✅ First test user enriched successfully
7. ✅ High-value alert received in Telegram

### Next Actions

- [ ] Monitor daily for first week
- [ ] Adjust scoring weights based on results
- [ ] Add custom Software Factory keywords
- [ ] Train sales team on alert handling
- [ ] Set up weekly review meeting (review digest)
- [ ] Build admin dashboard (optional - see frontend/src/app/leads/)

---

## 📚 Documentation References

- **Complete Guide:** [LEAD_ENRICHMENT_SYSTEM.md](LEAD_ENRICHMENT_SYSTEM.md)
- **Architecture:** [LEAD_ENRICHMENT_ARCHITECTURE.md](LEAD_ENRICHMENT_ARCHITECTURE.md)
- **Quick Reference:** [LEAD_ENRICHMENT_QUICK_REFERENCE.md](LEAD_ENRICHMENT_QUICK_REFERENCE.md)
- **Implementation Summary:** [LEAD_ENRICHMENT_SUMMARY.md](LEAD_ENRICHMENT_SUMMARY.md)

---

**Setup Time:** ~90 minutes  
**Status:** Ready for Production 🚀  
**Last Updated:** December 22, 2025
