# 🤖 Telegram Bot Setup Guide

## Overview

**The Telegram Bridge** - A serverless Telegram bot that costs $0/month and delivers high-scoring B2B leads directly to subscribers.

**Architecture:**
- **Bot Handler**: Supabase Edge Function (Deno runtime, Telegraf.js)
- **Database**: PostgreSQL with subscriber tracking and analytics
- **Daily Broadcast**: GitHub Actions cron job (8 AM UTC)
- **Cost**: $0 (Supabase + GitHub free tiers)

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Step 1: Create Telegram Bot](#step-1-create-telegram-bot)
3. [Step 2: Apply Database Migration](#step-2-apply-database-migration)
4. [Step 3: Deploy Edge Function](#step-3-deploy-edge-function)
5. [Step 4: Configure Webhook](#step-4-configure-webhook)
6. [Step 5: Setup GitHub Actions](#step-5-setup-github-actions)
7. [Step 6: Testing](#step-6-testing)
8. [Commands Reference](#commands-reference)
9. [Analytics & Monitoring](#analytics--monitoring)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- [ ] Telegram account
- [ ] Supabase project (free tier)
- [ ] GitHub repository with Actions enabled
- [ ] Supabase CLI installed (`npm install -g supabase`)

---

## Step 1: Create Telegram Bot

### 1.1 Talk to BotFather

Open Telegram and search for **@BotFather** (official Telegram bot creator).

```
/start
/newbot
```

### 1.2 Configure Your Bot

**BotFather will ask:**

1. **Bot name**: `PulseB2B Intelligence Bot` (or your choice)
2. **Bot username**: `pulseb2b_bot` (must end with `_bot`)

**BotFather will respond with:**
```
Done! Congratulations on your new bot. You will find it at t.me/pulseb2b_bot.

Use this token to access the HTTP API:
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

⚠️ **Save this token securely!** This is your `TELEGRAM_BOT_TOKEN`.

### 1.3 Customize Bot Settings (Optional)

```
/setdescription
Select your bot: @pulseb2b_bot
Enter description:
```

**Suggested description:**
```
Get high-scoring B2B leads delivered daily. Real-time signals from 19 countries. Track funding, hiring, tech stacks, and desperation scores. Free intelligence + Premium contact data.
```

```
/setabouttext
Select your bot: @pulseb2b_bot
Enter about text:
```

**Suggested about text:**
```
PulseB2B - B2B Intelligence Bot
Daily signals | Real-time scoring | 19 countries
```

```
/setuserpic
Select your bot: @pulseb2b_bot
Upload bot avatar (512x512 PNG)
```

---

## Step 2: Apply Database Migration

### 2.1 Link Supabase Project

```bash
cd PulseB2B
supabase link --project-ref <your-project-ref>
```

### 2.2 Apply Migration

```bash
supabase db push
```

This creates:
- `telegram_subscribers` table
- `telegram_messages` table (message delivery logs)
- `telegram_command_log` table (command analytics)
- Helper functions (`register_telegram_subscriber`, `get_latest_telegram_lead`, etc.)
- Analytics views (`telegram_growth_stats`, `telegram_delivery_stats`, etc.)

### 2.3 Verify Migration

```bash
supabase db diff
```

Should show: `No schema changes detected.`

---

## Step 3: Deploy Edge Function

### 3.1 Deploy Webhook Handler

```bash
supabase functions deploy telegram-webhook --no-verify-jwt
```

**Expected output:**
```
Bundling telegram-webhook...
Deploying telegram-webhook (project ref: <ref>)
Deployed Function URL:
https://<project-ref>.supabase.co/functions/v1/telegram-webhook
```

### 3.2 Set Environment Secrets

```bash
# Required: Telegram Bot Token (from BotFather)
supabase secrets set TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# Required: Frontend URL (for UTM links)
supabase secrets set FRONTEND_URL=https://pulseb2b.com

# Optional: Custom frontend URL for staging
# supabase secrets set FRONTEND_URL=https://staging.pulseb2b.com
```

### 3.3 Verify Secrets

```bash
supabase secrets list
```

**Expected output:**
```
TELEGRAM_BOT_TOKEN (digest: abc...)
FRONTEND_URL (digest: def...)
SUPABASE_URL (automatic)
SUPABASE_SERVICE_ROLE_KEY (automatic)
```

---

## Step 4: Configure Webhook

### 4.1 Get Your Function URL

```bash
supabase status
```

Look for: `Functions URL: https://<project-ref>.supabase.co/functions/v1`

Your webhook URL: `https://<project-ref>.supabase.co/functions/v1/telegram-webhook`

### 4.2 Set Telegram Webhook

**Option A: Using curl (recommended)**

```bash
curl -X POST "https://api.telegram.org/bot<YOUR_TELEGRAM_BOT_TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://<project-ref>.supabase.co/functions/v1/telegram-webhook",
    "allowed_updates": ["message", "callback_query"],
    "drop_pending_updates": true
  }'
```

**Option B: Using browser**

Visit: `https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook?url=https://<project-ref>.supabase.co/functions/v1/telegram-webhook`

### 4.3 Verify Webhook

```bash
curl "https://api.telegram.org/bot<YOUR_TOKEN>/getWebhookInfo"
```

**Expected response:**
```json
{
  "ok": true,
  "result": {
    "url": "https://<project-ref>.supabase.co/functions/v1/telegram-webhook",
    "has_custom_certificate": false,
    "pending_update_count": 0,
    "last_error_date": 0,
    "max_connections": 40
  }
}
```

✅ **Webhook is live!** Your bot will now receive updates.

---

## Step 5: Setup GitHub Actions

### 5.1 Configure Repository Secrets

Go to: **GitHub Repository > Settings > Secrets and variables > Actions**

Click **"New repository secret"** and add:

| Secret Name | Value | Where to Get It |
|------------|-------|-----------------|
| `TELEGRAM_BOT_TOKEN` | `1234567890:ABC...` | From @BotFather |
| `SUPABASE_URL` | `https://<ref>.supabase.co` | Supabase Dashboard > Project Settings > API |
| `SUPABASE_SERVICE_ROLE_KEY` | `eyJhbGciOi...` | Supabase Dashboard > Project Settings > API > service_role (secret) |
| `FRONTEND_URL` | `https://pulseb2b.com` | Your production domain |

### 5.2 Verify Workflow File

The workflow file should already exist:
```
.github/workflows/telegram_daily_broadcast.yml
```

### 5.3 Enable GitHub Actions

1. Go to **Actions** tab in your repository
2. If disabled, click **"I understand my workflows, go ahead and enable them"**
3. You should see: **"Telegram Daily Broadcast"** workflow

### 5.4 Test Manual Run

1. Click on **"Telegram Daily Broadcast"** workflow
2. Click **"Run workflow"** dropdown
3. Select branch: `main`
4. Leave dry_run: `false`
5. Click **"Run workflow"**

**Check logs:**
- Should see: "Fetching latest lead..."
- Should see: "Found X active subscribers"
- Should see: "Broadcasting to subscribers..."
- Should see: "✅ BROADCAST COMPLETED SUCCESSFULLY"

---

## Step 6: Testing

### 6.1 Test Bot Registration

1. Open Telegram
2. Search for your bot: `@pulseb2b_bot` (or your username)
3. Click **"Start"**
4. You should receive welcome message

**Verify in database:**
```sql
SELECT * FROM telegram_subscribers ORDER BY created_at DESC LIMIT 5;
```

Should show your `chat_id`, `username`, `created_at`.

### 6.2 Test /latest Command

In Telegram, send:
```
/latest
```

**Expected response:**
```
🔥🔥 Daily Signal - Dec 22

TechCorp USA 🇺🇸
━━━━━━━━━━━━━━━━━━━━

📊 Desperation Score: 87/100

💡 Intelligence:
TechCorp USA raised $10M-$50M (backed by Y Combinator)...

💰 Funding: $10M-$50M
📈 Hiring: 🔥 URGENT
🛠 Tech: React, Node.js, AWS, PostgreSQL, Docker

━━━━━━━━━━━━━━━━━━━━
👉 View Full Details

Tip: Premium users see contact info + exact funding 💎
```

### 6.3 Test /help Command

```
/help
```

Should show command list.

### 6.4 Test /stats Command

```
/stats
```

Should show your engagement stats.

### 6.5 Verify Analytics

**Check command log:**
```sql
SELECT * FROM telegram_command_log 
WHERE chat_id = <your_chat_id> 
ORDER BY received_at DESC;
```

**Check message delivery:**
```sql
SELECT * FROM telegram_messages 
WHERE chat_id = <your_chat_id> 
ORDER BY sent_at DESC;
```

**View analytics:**
```sql
SELECT * FROM telegram_command_stats;
SELECT * FROM telegram_delivery_stats;
SELECT * FROM telegram_active_summary;
```

---

## Commands Reference

### User Commands

| Command | Description | Example Output |
|---------|-------------|----------------|
| `/start` | Register with bot | Welcome message + command list |
| `/latest` | Get highest-scoring lead (last 24h) | Lead card with desperation score |
| `/help` | Show available commands | Command reference |
| `/stats` | Show personal engagement stats | Commands sent, member since |

### Bot Responses

**If no leads found:**
```
🤷 No high-scoring leads found in the last 24 hours.
Check back later or lower your standards! 😉
```

**If not registered:**
```
Please use /start first to register!
```

**If unknown command:**
```
Unknown command. Use /help to see available commands.
```

---

## Analytics & Monitoring

### Real-Time Metrics

**Query active subscribers:**
```sql
SELECT * FROM telegram_active_summary;
```

**Output:**
| active_subscribers | inactive_subscribers | active_rate_pct | avg_commands_per_user |
|--------------------|----------------------|-----------------|----------------------|
| 247 | 12 | 95.37 | 4.2 |

**Query growth stats:**
```sql
SELECT * FROM telegram_growth_stats 
ORDER BY signup_date DESC 
LIMIT 7;
```

**Output (last 7 days):**
| signup_date | new_subscribers | total_subscribers |
|-------------|-----------------|-------------------|
| 2025-12-22 | 14 | 259 |
| 2025-12-21 | 18 | 245 |
| 2025-12-20 | 22 | 227 |

### Command Performance

```sql
SELECT * FROM telegram_command_stats;
```

**Output:**
| command | usage_count | avg_processing_ms | success_rate_pct |
|---------|-------------|-------------------|------------------|
| /start | 259 | 124 | 100.00 |
| /latest | 1847 | 89 | 99.73 |
| /help | 412 | 45 | 100.00 |

### Message Delivery

```sql
SELECT * FROM telegram_delivery_stats;
```

**Output:**
| message_type | total_sent | delivered_count | click_through_rate_pct |
|--------------|------------|-----------------|------------------------|
| daily_signal | 7410 | 7398 | 12.40 |
| latest_command | 1847 | 1842 | 8.20 |
| welcome | 259 | 259 | 0.00 |

### GitHub Actions Logs

**View workflow history:**
1. Go to **Actions** tab
2. Click **"Telegram Daily Broadcast"**
3. Click on latest run
4. Check logs for:
   - Number of subscribers
   - Success/failure count
   - Processing time

---

## Troubleshooting

### Issue: Bot Not Responding

**Symptoms:**
- Sending `/start` does nothing
- No welcome message received

**Solutions:**

1. **Check webhook status:**
   ```bash
   curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"
   ```
   
   Look for `last_error_message`. Common errors:
   - `Connection refused` → Edge Function not deployed
   - `Wrong response` → Function returning invalid response
   - `Certificate verify failed` → SSL issue (shouldn't happen with Supabase)

2. **Check Edge Function logs:**
   ```bash
   supabase functions logs telegram-webhook
   ```
   
   Look for errors in webhook processing.

3. **Verify secrets:**
   ```bash
   supabase secrets list
   ```
   
   Should show `TELEGRAM_BOT_TOKEN`.

4. **Test Edge Function directly:**
   ```bash
   curl -X POST "https://<project-ref>.supabase.co/functions/v1/telegram-webhook" \
     -H "Content-Type: application/json" \
     -d '{"update_id": 1, "message": {"text": "/start"}}'
   ```

---

### Issue: Daily Broadcast Not Sending

**Symptoms:**
- No messages received at 8 AM UTC
- GitHub Actions workflow failing

**Solutions:**

1. **Check workflow runs:**
   - Go to **Actions** tab
   - Look for failed runs (red X icon)
   - Click on failed run to see logs

2. **Common failure causes:**
   
   **Missing secrets:**
   ```
   Error: TELEGRAM_BOT_TOKEN is required
   ```
   → Add secret in GitHub repository settings
   
   **No leads found:**
   ```
   ❌ No leads found for broadcast. Exiting.
   ```
   → Verify signals table has recent high-scoring leads (desperation_score >= 70)
   
   **Supabase connection error:**
   ```
   Error: fetch failed
   ```
   → Verify `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` secrets

3. **Test broadcast manually:**
   ```bash
   # From local machine
   export TELEGRAM_BOT_TOKEN=<your_token>
   export SUPABASE_URL=<your_url>
   export SUPABASE_SERVICE_ROLE_KEY=<your_key>
   export FRONTEND_URL=https://pulseb2b.com
   
   node scripts/telegram_broadcast.js
   ```

---

### Issue: Users Not Seeing Leads

**Symptoms:**
- `/latest` returns "No high-scoring leads found"
- Even though signals table has data

**Solutions:**

1. **Check lead scoring:**
   ```sql
   SELECT COUNT(*) 
   FROM signals 
   WHERE desperation_score >= 70 
     AND created_at >= NOW() - INTERVAL '24 hours';
   ```
   
   If count is 0, no leads meet criteria.

2. **Lower threshold temporarily:**
   
   Edit `get_latest_telegram_lead()` function:
   ```sql
   WHERE s.desperation_score >= 60  -- Was 70
   ```

3. **Check date filter:**
   
   Make sure signals have recent `created_at` timestamps.

---

### Issue: Rate Limiting Errors

**Symptoms:**
- Broadcast fails with "Too Many Requests"
- Telegram returns HTTP 429

**Solutions:**

1. **Our script already implements:**
   - Rate limiting: 30 msgs/sec (Telegram's limit)
   - Batch processing: 100 subscribers per batch
   - Delays between batches: 3 seconds

2. **If still rate limited:**
   
   Edit `telegram_broadcast.js`:
   ```javascript
   const MESSAGES_PER_SECOND = 20; // Reduce from 30
   const DELAY_BETWEEN_BATCHES = 5000; // Increase from 3000
   ```

---

### Issue: Webhook Timeout

**Symptoms:**
- Function logs show timeout errors
- Bot responses delayed or missing

**Solutions:**

1. **Check processing time:**
   ```sql
   SELECT command, AVG(processing_time_ms), MAX(processing_time_ms)
   FROM telegram_command_log
   GROUP BY command;
   ```

2. **If `/latest` is slow:**
   - Add index: `CREATE INDEX idx_signals_desperation ON signals(desperation_score DESC, created_at DESC);`
   - Optimize `get_latest_telegram_lead()` function query

3. **If database queries are slow:**
   - Check Supabase Dashboard > Database > Slow Queries
   - Add appropriate indexes

---

## Advanced Configuration

### Custom Broadcast Times

Edit `.github/workflows/telegram_daily_broadcast.yml`:

```yaml
schedule:
  # Multiple times per day
  - cron: '0 8 * * *'   # 8 AM UTC
  - cron: '0 16 * * *'  # 4 PM UTC
  
  # Weekdays only
  - cron: '0 8 * * 1-5'  # Mon-Fri at 8 AM UTC
```

### Custom Message Formatting

Edit `supabase/functions/telegram-webhook/index.ts`:

```typescript
function formatLeadMessage(lead: any): string {
  // Customize message format here
  return `Custom format: ${lead.company_name}`;
}
```

### Add Custom Commands

Edit `supabase/functions/telegram-webhook/index.ts`:

```typescript
bot.command("mycommand", async (ctx) => {
  await ctx.reply("Custom response!");
});
```

### UTM Tracking

All links include UTM parameters:
```
?utm_source=telegram&utm_medium=bot&utm_campaign=daily_signal
```

Track clicks in frontend:
```typescript
// In Continental Dashboard
useEffect(() => {
  const params = new URLSearchParams(window.location.search);
  if (params.get('utm_source') === 'telegram') {
    // Log click-through from Telegram
    trackEvent('telegram_click_through', {
      lead_id: params.get('lead_id'),
      campaign: params.get('utm_campaign'),
    });
  }
}, []);
```

---

## Cost Analysis

### Monthly Usage (Estimated)

**GitHub Actions:**
- Daily broadcast: ~3 minutes/day
- Monthly total: ~90 minutes/month
- Free tier: 2,000 minutes/month
- **Cost: $0**

**Supabase:**
- Database queries: ~100/day (broadcast + commands)
- Monthly total: ~3,000 queries/month
- Free tier: 500,000 queries/month
- Edge Function invocations: ~50/day
- Monthly total: ~1,500 invocations/month
- Free tier: 500,000 invocations/month
- **Cost: $0**

**Telegram:**
- Bot API: Free (unlimited)
- Messages: Free (unlimited)
- **Cost: $0**

### **Total Cost: $0/month** 🎉

---

## Production Checklist

- [ ] Bot created via @BotFather
- [ ] Database migration applied (`supabase db push`)
- [ ] Edge Function deployed (`supabase functions deploy telegram-webhook`)
- [ ] Webhook configured and verified
- [ ] GitHub Actions secrets configured
- [ ] Test broadcast run successful
- [ ] Bot responds to `/start` command
- [ ] Bot responds to `/latest` command
- [ ] Analytics views created and populated
- [ ] Daily broadcast scheduled (8 AM UTC)
- [ ] Monitoring dashboard setup (optional)

---

## Support

**Issues?** Check:
1. Supabase Edge Function logs
2. GitHub Actions workflow logs
3. Telegram webhook info (`getWebhookInfo`)
4. Database tables (`telegram_command_log` for errors)

**Need help?** 
- GitHub Issues: Report bugs or request features
- Email: support@pulseb2b.com

---

**🚀 Your Telegram bot is now live and broadcasting daily intelligence to subscribers at $0/month!**
