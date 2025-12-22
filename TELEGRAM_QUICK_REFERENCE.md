# 🤖 Telegram Bot - Quick Reference

## Architecture Overview

```
┌─────────────────┐
│   @BotFather    │ (Create bot, get token)
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│                   TELEGRAM BOT                          │
│  - Handle /start, /latest, /help, /stats               │
│  - Register users in telegram_subscribers table         │
│  - Query high-scoring leads from signals table          │
│  - Format messages with company intelligence            │
└────────┬────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│         SUPABASE EDGE FUNCTION (Deno + Telegraf)        │
│  URL: https://<ref>.supabase.co/functions/v1/telegram- │
│       webhook                                           │
│  - Process Telegram updates (webhook)                   │
│  - Call database functions                              │
│  - Send responses via Telegram Bot API                  │
└────────┬────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│           SUPABASE DATABASE (PostgreSQL)                │
│  Tables:                                                │
│    - telegram_subscribers (users)                       │
│    - telegram_messages (delivery logs)                  │
│    - telegram_command_log (analytics)                   │
│  Functions:                                             │
│    - register_telegram_subscriber()                     │
│    - get_latest_telegram_lead()                         │
│    - log_telegram_command()                             │
└────────┬────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│      GITHUB ACTIONS (Daily Broadcast Cron)              │
│  Schedule: 8 AM UTC daily                               │
│  Script: scripts/telegram_broadcast.js                  │
│  - Query get_telegram_broadcast_list()                  │
│  - Get latest high-scoring lead                         │
│  - Send to all active subscribers                       │
│  - Rate limiting: 30 msgs/sec                           │
└─────────────────────────────────────────────────────────┘
```

---

## Database Schema

### telegram_subscribers
| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `chat_id` | BIGINT | Telegram chat ID (unique) |
| `username` | TEXT | Telegram username |
| `first_name` | TEXT | User's first name |
| `last_name` | TEXT | User's last name |
| `language_code` | TEXT | Language preference (default: 'en') |
| `is_active` | BOOLEAN | Active status (false if blocked bot) |
| `created_at` | TIMESTAMPTZ | Registration date |
| `last_interaction_at` | TIMESTAMPTZ | Last command/message |
| `total_commands_sent` | INTEGER | Engagement metric |
| `last_command` | TEXT | Most recent command |

### telegram_messages
| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `chat_id` | BIGINT | Recipient |
| `message_type` | TEXT | 'daily_signal', 'latest_command', 'welcome' |
| `lead_id` | UUID | Reference to signals table |
| `message_text` | TEXT | Message content (truncated) |
| `sent_at` | TIMESTAMPTZ | Delivery timestamp |
| `was_delivered` | BOOLEAN | Delivery success |
| `clicked_through` | BOOLEAN | User clicked link (from UTM) |

### telegram_command_log
| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `chat_id` | BIGINT | User who sent command |
| `command` | TEXT | '/start', '/latest', etc. |
| `command_args` | TEXT | Arguments passed |
| `received_at` | TIMESTAMPTZ | Command timestamp |
| `processing_time_ms` | INTEGER | Performance metric |
| `success` | BOOLEAN | Command success status |

---

## Bot Commands

| Command | Handler | Database Call | Response |
|---------|---------|---------------|----------|
| `/start` | `bot.command('start')` | `register_telegram_subscriber()` | Welcome message |
| `/latest` | `bot.command('latest')` | `get_latest_telegram_lead()` | Lead card with score |
| `/help` | `bot.command('help')` | None | Command reference |
| `/stats` | `bot.command('stats')` | Query `telegram_subscribers` | User engagement stats |

---

## Key Functions

### Database Functions (SQL)

**register_telegram_subscriber()**
```sql
-- Inserts or updates user in telegram_subscribers
-- Sets is_active = true (reactivates if previously blocked)
-- Returns subscriber UUID
```

**get_latest_telegram_lead()**
```sql
-- Queries signals table for highest desperation_score
-- Filters: created_at >= NOW() - INTERVAL '24 hours'
-- Filters: desperation_score >= 70
-- Returns: company_name, desperation_score, company_insight, tech_stack, etc.
```

**log_telegram_command()**
```sql
-- Logs command to telegram_command_log
-- Updates total_commands_sent in telegram_subscribers
-- Returns log UUID
```

**get_telegram_broadcast_list()**
```sql
-- Returns all active subscribers (is_active = true)
-- Ordered by created_at ASC (respect subscription order)
```

### Edge Function Handlers (TypeScript)

**formatLeadMessage()**
```typescript
// Formats lead data as Telegram message
// Includes: company_name, desperation_score, company_insight
// Includes: tech_stack, funding_range, hiring_velocity
// Includes: UTM-tracked link to frontend
```

**getCountryFlag()**
```typescript
// Maps country code to flag emoji
// Example: "US" → "🇺🇸"
```

---

## Message Flow

### User Sends /start

1. **Telegram** → Webhook → **Edge Function** (`telegram-webhook`)
2. Edge Function calls `register_telegram_subscriber(chat_id, username, ...)`
3. Database inserts/updates subscriber
4. Edge Function sends welcome message via Telegram API
5. Edge Function logs command via `log_telegram_command()`

### User Sends /latest

1. **Telegram** → Webhook → **Edge Function**
2. Edge Function checks if user is registered & active
3. Edge Function calls `get_latest_telegram_lead()`
4. Database queries signals table (last 24h, score >= 70)
5. Edge Function formats lead as message
6. Edge Function sends message via Telegram API
7. Edge Function logs command & message delivery

### Daily Broadcast (Automated)

1. **GitHub Actions** triggers at 8 AM UTC
2. Script calls `get_latest_telegram_lead()` → Get top lead
3. Script calls `get_telegram_broadcast_list()` → Get all active subscribers
4. Script loops through subscribers in batches (100 per batch)
5. Script sends message to each subscriber (rate-limited: 30/sec)
6. Script logs delivery via `log_telegram_message()`
7. If delivery fails with "blocked", script calls `deactivate_telegram_subscriber()`

---

## Environment Variables

### Supabase Edge Function Secrets

```bash
supabase secrets set TELEGRAM_BOT_TOKEN=<from @BotFather>
supabase secrets set FRONTEND_URL=https://pulseb2b.com
```

**Auto-injected by Supabase:**
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

### GitHub Actions Secrets

**Repository Settings > Secrets and variables > Actions:**

| Secret | Value | Purpose |
|--------|-------|---------|
| `TELEGRAM_BOT_TOKEN` | From @BotFather | Send messages via Bot API |
| `SUPABASE_URL` | Project URL | Database queries |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role key | Bypass RLS |
| `FRONTEND_URL` | Production URL | UTM links |

---

## Deployment Commands

### Database Migration
```bash
supabase db push
```

### Deploy Edge Function
```bash
supabase functions deploy telegram-webhook --no-verify-jwt
```

### Set Secrets
```bash
supabase secrets set TELEGRAM_BOT_TOKEN=<token>
supabase secrets set FRONTEND_URL=<url>
```

### Configure Webhook
```bash
curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://<project-ref>.supabase.co/functions/v1/telegram-webhook"}'
```

### Verify Webhook
```bash
curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"
```

---

## Analytics Queries

### Active Subscribers
```sql
SELECT * FROM telegram_active_summary;
-- Returns: active_subscribers, inactive_subscribers, active_rate_pct
```

### Daily Growth
```sql
SELECT * FROM telegram_growth_stats 
ORDER BY signup_date DESC LIMIT 7;
-- Returns: signup_date, new_subscribers, total_subscribers
```

### Command Performance
```sql
SELECT * FROM telegram_command_stats;
-- Returns: command, usage_count, avg_processing_ms, success_rate_pct
```

### Message Delivery Stats
```sql
SELECT * FROM telegram_delivery_stats;
-- Returns: message_type, total_sent, delivered_count, click_through_rate_pct
```

### Recent Commands
```sql
SELECT 
  chat_id,
  command,
  processing_time_ms,
  success,
  received_at
FROM telegram_command_log
ORDER BY received_at DESC
LIMIT 20;
```

---

## Testing Checklist

- [ ] `/start` → Welcome message received
- [ ] User appears in `telegram_subscribers` table
- [ ] `/latest` → Lead card with score >= 70
- [ ] Lead appears in `telegram_messages` table
- [ ] `/help` → Command list displayed
- [ ] `/stats` → Personal stats shown
- [ ] Manual GitHub Actions run → Broadcast successful
- [ ] Check logs: "✅ BROADCAST COMPLETED SUCCESSFULLY"
- [ ] Webhook info shows correct URL
- [ ] Click "View Details" link → Frontend opens with UTM params

---

## Troubleshooting

### Bot Not Responding
```bash
# Check webhook status
curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"

# Check Edge Function logs
supabase functions logs telegram-webhook

# Test webhook directly
curl -X POST "https://<ref>.supabase.co/functions/v1/telegram-webhook" \
  -H "Content-Type: application/json" \
  -d '{"update_id": 1, "message": {"text": "/start"}}'
```

### No Leads Found
```sql
-- Check if any leads exist
SELECT COUNT(*) FROM signals 
WHERE desperation_score >= 70 
  AND created_at >= NOW() - INTERVAL '24 hours';

-- Lower threshold temporarily
UPDATE signals SET desperation_score = 75 WHERE id = '<some_id>';
```

### Broadcast Failing
```bash
# Check GitHub Actions logs (Actions tab)
# Common issues:
# - Missing secrets → Add in repo settings
# - No leads → Insert test data
# - Rate limiting → Already handled by script
```

---

## File Structure

```
PulseB2B/
├── supabase/
│   ├── migrations/
│   │   └── 20251222_telegram_integration.sql  (Database schema)
│   └── functions/
│       └── telegram-webhook/
│           └── index.ts  (Edge Function handler)
├── scripts/
│   └── telegram_broadcast.js  (Daily broadcast script)
├── .github/
│   └── workflows/
│       └── telegram_daily_broadcast.yml  (GitHub Actions cron)
└── TELEGRAM_BOT_SETUP.md  (Complete setup guide)
```

---

## Cost Breakdown

| Service | Usage | Free Tier | Cost |
|---------|-------|-----------|------|
| **GitHub Actions** | ~90 min/month | 2,000 min/month | $0 |
| **Supabase Queries** | ~3,000/month | 500,000/month | $0 |
| **Supabase Edge Functions** | ~1,500 invocations/month | 500,000/month | $0 |
| **Telegram Bot API** | Unlimited | Unlimited | $0 |
| **Total** | | | **$0/month** |

---

## UTM Tracking

All "View Details" links include:
```
?utm_source=telegram
&utm_medium=bot
&utm_campaign=daily_signal
&lead_id=<uuid>
```

Track conversions:
```sql
SELECT 
  DATE(clicked_at) as date,
  COUNT(*) as clicks,
  COUNT(DISTINCT chat_id) as unique_users
FROM telegram_messages
WHERE clicked_through = true
  AND message_type = 'daily_signal'
GROUP BY DATE(clicked_at)
ORDER BY date DESC;
```

---

## Production Checklist

- [x] Database migration applied
- [x] Edge Function deployed
- [x] Webhook configured
- [x] GitHub Actions secrets set
- [x] Test /start command
- [x] Test /latest command
- [x] Test daily broadcast
- [x] Verify analytics queries work
- [ ] Monitor first 7 days of broadcasts
- [ ] Adjust cron schedule if needed

---

**🚀 Your $0/month Telegram bot is production-ready!**
