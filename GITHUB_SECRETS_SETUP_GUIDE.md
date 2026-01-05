# 🔐 GitHub Secrets Configuration Guide

**Last Updated:** January 5, 2026  
**Repository:** PulseB2B

---

## ⚠️ Critical Issue Resolved

**Problem:** Workflows failing with error: "supabaseUrl is required"

**Root Cause:** Missing environment variables in workflow steps that use `telegram_alert_service.js`

**Workflows Fixed:**
- ✅ `weekly-digest.yml` - Added SUPABASE_URL and SUPABASE_SERVICE_KEY
- ✅ `high-value-lead-alert.yml` - Added SUPABASE_URL and SUPABASE_SERVICE_KEY
- ✅ `weekly_lead_digest.yml` - Already configured correctly

---

## 📋 Required Secrets Inventory

Your repository requires **19 unique secrets** across all workflows:

### 🔵 Supabase (Database) - CRITICAL
| Secret Name | Description | Used By | Status |
|-------------|-------------|---------|--------|
| `SUPABASE_URL` | Supabase project URL | 14 workflows | ⚠️ **REQUIRED** |
| `SUPABASE_SERVICE_KEY` | Admin access key | 9 workflows | ⚠️ **REQUIRED** |
| `SUPABASE_SERVICE_ROLE_KEY` | Full permissions | 2 workflows | ⚠️ **REQUIRED** |
| `SUPABASE_KEY` | General access | 3 workflows | ⚠️ **REQUIRED** |
| `SUPABASE_ANON_KEY` | Public access | 1 workflow | Optional |

### 📱 Telegram (Notifications) - CRITICAL
| Secret Name | Description | Used By | Status |
|-------------|-------------|---------|--------|
| `TELEGRAM_BOT_TOKEN` | Bot authentication | 12 workflows | ⚠️ **REQUIRED** |
| `TELEGRAM_CHAT_ID` | Default chat ID | 10 workflows | ⚠️ **REQUIRED** |
| `TELEGRAM_ALERT_CHAT_ID` | Alerts chat ID | 2 workflows | ⚠️ **REQUIRED** |

### 🔍 Google (Search & APIs)
| Secret Name | Description | Used By | Status |
|-------------|-------------|---------|--------|
| `GOOGLE_CSE_API_KEY` | Custom Search API | 2 workflows | Optional |
| `GOOGLE_CSE_ID` | Search engine ID | 2 workflows | Optional |
| `GOOGLE_SEARCH_API_KEY` | Search API key | 1 workflow | Optional |

### 📧 Email & Communication
| Secret Name | Description | Used By | Status |
|-------------|-------------|---------|--------|
| `SENDGRID_API_KEY` | Email service | 1 workflow | Optional |
| `FROM_EMAIL` | Sender email | 1 workflow | Optional |
| `WEBHOOK_URL` | Generic webhook | 1 workflow | Optional |
| `SLACK_WEBHOOK_URL` | Slack integration | 1 workflow | Optional |
| `DISCORD_WEBHOOK_URL` | Discord integration | 1 workflow | Optional |

### 🔑 Other Services
| Secret Name | Description | Used By | Status |
|-------------|-------------|---------|--------|
| `CLEARBIT_API_KEY` | Lead enrichment | 1 workflow | Optional |
| `BASE_URL` | Application URL | 1 workflow | Optional |
| `FRONTEND_URL` | Frontend URL | 1 workflow | Optional |

---

## 🚀 How to Add Secrets to GitHub

### Step 1: Navigate to Repository Settings

1. Go to your GitHub repository: `https://github.com/YOUR_USERNAME/PulseB2B`
2. Click on **Settings** tab
3. In the left sidebar, click **Secrets and variables** → **Actions**

### Step 2: Add New Secret

1. Click the **New repository secret** button
2. Enter the **Name** (exactly as shown in the table above)
3. Enter the **Value** (your actual secret value)
4. Click **Add secret**

### Step 3: Verify Secrets

After adding all required secrets, you should see them listed (values will be hidden):

```
✅ SUPABASE_URL                 Updated X minutes ago
✅ SUPABASE_SERVICE_KEY         Updated X minutes ago
✅ TELEGRAM_BOT_TOKEN           Updated X minutes ago
✅ TELEGRAM_CHAT_ID             Updated X minutes ago
... and 15 more
```

---

## 📝 How to Get Secret Values

### Supabase Credentials

1. **SUPABASE_URL**
   - Go to your Supabase project dashboard
   - Navigate to **Settings** → **API**
   - Copy the **Project URL** (e.g., `https://xxxxx.supabase.co`)

2. **SUPABASE_SERVICE_KEY**
   - In the same **API** section
   - Find **service_role secret** (⚠️ Keep this secret!)
   - Copy the key

3. **SUPABASE_KEY** / **SUPABASE_ANON_KEY**
   - Also in **API** section
   - Copy the **anon public** key

### Telegram Bot Credentials

1. **TELEGRAM_BOT_TOKEN**
   - Message [@BotFather](https://t.me/botfather) on Telegram
   - Create a new bot with `/newbot`
   - Copy the API token (format: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

2. **TELEGRAM_CHAT_ID**
   - Add your bot to a channel/group
   - Message [@userinfobot](https://t.me/userinfobot) or [@getidsbot](https://t.me/getidsbot)
   - Get your chat ID (format: `-1001234567890` for groups)

3. **TELEGRAM_ALERT_CHAT_ID**
   - Same process as CHAT_ID
   - Use a different channel for critical alerts (recommended)

### Google API Keys

1. **GOOGLE_CSE_API_KEY** & **GOOGLE_CSE_ID**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Enable **Custom Search API**
   - Create credentials → API Key
   - Create a Custom Search Engine at [CSE Panel](https://cse.google.com/)

### Email (SendGrid)

1. **SENDGRID_API_KEY**
   - Go to [SendGrid Dashboard](https://app.sendgrid.com/)
   - Navigate to **Settings** → **API Keys**
   - Create API Key with full access

2. **FROM_EMAIL**
   - Use your verified sender email

### Webhooks

1. **SLACK_WEBHOOK_URL**
   - Go to your Slack workspace
   - Navigate to **Apps** → **Incoming Webhooks**
   - Create a webhook for your channel

2. **DISCORD_WEBHOOK_URL**
   - In your Discord server
   - Go to **Server Settings** → **Integrations** → **Webhooks**
   - Create a webhook for your channel

---

## ✅ Validation Checklist

Before running workflows, verify:

- [ ] All CRITICAL secrets are added (marked ⚠️ **REQUIRED**)
- [ ] Secret names match exactly (case-sensitive)
- [ ] No extra spaces in secret values
- [ ] Supabase URL format: `https://xxxxx.supabase.co`
- [ ] Telegram bot token format: `1234567890:ABCdef...`
- [ ] Telegram chat ID format: `-1001234567890` (groups) or `1234567890` (private)

---

## 🧪 Test Your Secrets

Run this workflow manually to test all credentials:

```bash
# Go to Actions tab → test-and-report-telegram.yml → Run workflow
```

This will validate:
- ✅ Telegram Bot connectivity
- ✅ Telegram message sending
- ✅ Basic workflow functionality

---

## 🔧 Troubleshooting

### Error: "supabaseUrl is required"

**Cause:** Missing `SUPABASE_URL` secret

**Solution:**
1. Verify secret is added in GitHub Settings
2. Check secret name is exactly `SUPABASE_URL` (case-sensitive)
3. Ensure value is the full URL: `https://xxxxx.supabase.co`

### Error: "Telegram Bot token invalid"

**Cause:** Wrong `TELEGRAM_BOT_TOKEN` format or revoked token

**Solution:**
1. Verify token format: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`
2. Test token with: `curl https://api.telegram.org/bot<TOKEN>/getMe`
3. If invalid, create a new bot with @BotFather

### Error: "Chat not found"

**Cause:** Bot not added to channel or wrong chat ID

**Solution:**
1. Add bot to your Telegram channel/group
2. Make bot an admin (for groups)
3. Verify chat ID format (negative for groups)

### Workflow runs but no output

**Cause:** Secrets might be empty or whitespace

**Solution:**
1. Re-add secrets, ensuring no trailing spaces
2. Test locally with `.env` file first
3. Check workflow logs for detailed errors

---

## 🔒 Security Best Practices

### ✅ DO

- ✅ Rotate secrets every 90 days
- ✅ Use different secrets for production/staging
- ✅ Use `SUPABASE_SERVICE_KEY` only in backend workflows
- ✅ Use `SUPABASE_ANON_KEY` for public-facing operations
- ✅ Store secrets in GitHub Secrets, never in code
- ✅ Use environment-specific secrets when possible

### ❌ DON'T

- ❌ Commit secrets to repository (even in `.env`)
- ❌ Share service keys publicly
- ❌ Use production secrets in development
- ❌ Log secret values in workflow outputs
- ❌ Copy secrets to multiple repositories unnecessarily

---

## 📊 Secrets Usage Matrix

| Workflow | SUPABASE | TELEGRAM | GOOGLE | EMAIL | OTHER |
|----------|----------|----------|--------|-------|-------|
| critical-funding-alert | ✅ | ✅ | ❌ | ❌ | ❌ |
| daily-scrape | ✅ | ✅ | ✅ | ❌ | ❌ |
| high-value-lead-alert | ✅ | ✅ | ❌ | ❌ | ✅ Clearbit |
| weekly-digest | ✅ | ✅ | ❌ | ❌ | ❌ |
| weekly_email_reports | ✅ | ✅ | ❌ | ✅ | ❌ |
| serverless-ghost-pipeline | ✅ | ❌ | ✅ | ❌ | ✅ Webhooks |

---

## 🆘 Quick Reference Commands

### Test Supabase Connection
```bash
curl -H "apikey: YOUR_SUPABASE_KEY" \
     -H "Authorization: Bearer YOUR_SUPABASE_KEY" \
     "YOUR_SUPABASE_URL/rest/v1/"
```

### Test Telegram Bot
```bash
curl "https://api.telegram.org/bot<TOKEN>/getMe"
```

### Test Telegram Send Message
```bash
curl -X POST "https://api.telegram.org/bot<TOKEN>/sendMessage" \
     -d "chat_id=<CHAT_ID>" \
     -d "text=Test from GitHub Actions"
```

---

## 📞 Support

If you continue to experience issues:

1. Check the workflow logs in Actions tab
2. Verify secret values are correct
3. Test credentials manually using commands above
4. Review [WORKFLOW_TESTING_REPORT.md](./WORKFLOW_TESTING_REPORT.md)

---

**Document Version:** 1.0  
**Last Validated:** January 5, 2026  
**Status:** ✅ All workflows updated with correct environment variables
