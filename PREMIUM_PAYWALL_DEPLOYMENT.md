# 🚀 PREMIUM PAYWALL DEPLOYMENT GUIDE

Complete step-by-step guide to deploy the enterprise-grade premium paywall system for PulseB2B.

**Estimated Time:** 60-90 minutes  
**Required Access:** Supabase Dashboard, Stripe Dashboard, Google Cloud Console

---

## 📋 Pre-Deployment Checklist

### Required Accounts
- [ ] Supabase project (free tier works)
- [ ] Stripe account (test mode for development)
- [ ] Google Cloud Console account
- [ ] Git repository access

### Local Setup
```bash
# Install Supabase CLI
npm install -g supabase

# Install dependencies
cd frontend
npm install

# Verify installations
supabase --version
node --version
```

---

## 🗄️ STEP 1: Database Setup (15 minutes)

### 1.1 Connect to Supabase

```bash
# Navigate to project root
cd c:\Users\danie\OneDrive\Escritorio\proyectos programacion\PulseB2B

# Link to your Supabase project
supabase link --project-ref <your-project-ref>
```

**Find your project ref:**
- Go to [Supabase Dashboard](https://app.supabase.com)
- Select your project
- Settings → General → Reference ID

### 1.2 Apply Database Migrations

```bash
# Apply RLS security migration
supabase db push --include-all

# This will apply:
# - 20251222_rls_premium_security.sql (400+ lines)
# - 20251222_value_proposition_schema.sql (550+ lines)
```

**Expected output:**
```
✓ Migrations applied successfully
✓ Created tables: payment_events, insight_conversions
✓ Created views: signals_secure, payment_analytics
✓ Created functions: is_user_premium(), activate_premium_subscription(), etc.
```

### 1.3 Verify Migration Success

```sql
-- Run in Supabase SQL Editor
-- Check if views exist
SELECT table_name 
FROM information_schema.views 
WHERE table_name IN ('signals_secure', 'payment_analytics');

-- Check if functions exist
SELECT routine_name 
FROM information_schema.routines 
WHERE routine_name LIKE '%premium%';

-- Test premium function
SELECT is_user_premium();  -- Should return false for non-premium users
```

### 1.4 Setup Cron Job for Subscription Expiry

```sql
-- Run in Supabase SQL Editor
-- Enable pg_cron extension
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- Schedule daily expiration check at midnight UTC
SELECT cron.schedule(
  'expire-premium-subscriptions',
  '0 0 * * *',  -- Daily at 00:00 UTC
  $$ SELECT expire_premium_subscriptions(); $$
);

-- Verify cron job created
SELECT * FROM cron.job;
```

**Expected result:**
```
jobid | schedule    | command
------|-------------|----------------------------------
1     | 0 0 * * *   | SELECT expire_premium_subscriptions();
```

---

## 🔐 STEP 2: Stripe Configuration (20 minutes)

### 2.1 Create Product in Stripe Dashboard

1. Go to [Stripe Dashboard → Products](https://dashboard.stripe.com/products)
2. Click **Add product**
3. Configure:
   - **Name:** `PulseB2B Premium`
   - **Description:** `Access to direct contact information (emails, phones, exact funding data)`
   - **Pricing model:** `Standard pricing`
   - **Price:** `$49.00 USD`
   - **Billing period:** `Monthly`
   - **Payment type:** `Recurring`
4. Click **Add product**

### 2.2 Create Payment Link

1. In the product page, click **Create payment link**
2. Configure settings:

**Collect customer information:**
- [x] Email addresses
- [ ] Shipping addresses (not needed)
- [x] Tax ID (optional)

**After payment:**
- **Type:** `Hosted success page`
- **Custom message:** `Thank you! Your premium access is being activated...`
- **Redirect URL:** `https://yourdomain.com/success`

**Advanced options:**
- [x] Allow promotion codes
- [ ] Collect consent to promotional emails
- **Prefill email:** Leave empty

**Custom fields (CRITICAL):**
Click **Add custom field**:
- **Label:** `User ID`
- **Type:** `Text`
- **Key:** `client_reference_id`
- **Required:** Yes
- **Default value:** `{{CUSTOMER_ID}}`

3. Click **Create link**
4. Copy the payment link URL (e.g., `https://buy.stripe.com/test_xxx...`)

### 2.3 Get Stripe API Keys

1. Go to [Stripe Dashboard → Developers → API keys](https://dashboard.stripe.com/test/apikeys)
2. Copy the following keys:
   - **Publishable key:** `pk_test_...` or `pk_live_...`
   - **Secret key:** `sk_test_...` or `sk_live_...`

### 2.4 Configure Webhook (We'll complete this after deploying Edge Function)

**For now, note these values:**
- Webhook endpoint URL: `https://<project-ref>.supabase.co/functions/v1/stripe-webhook`
- Events to listen for:
  - `checkout.session.completed`
  - `customer.subscription.updated`
  - `customer.subscription.deleted`
  - `invoice.payment_failed`

---

## ☁️ STEP 3: Deploy Supabase Edge Function (15 minutes)

### 3.1 Set Supabase Secrets

```bash
# Set Stripe keys
supabase secrets set STRIPE_SECRET_KEY=sk_test_xxx...
supabase secrets set STRIPE_WEBHOOK_SECRET=whsec_xxx  # Get this after webhook setup

# Set Supabase credentials
supabase secrets set SUPABASE_URL=https://your-project.supabase.co
supabase secrets set SUPABASE_SERVICE_ROLE_KEY=eyJxxx...
```

**Get SUPABASE_SERVICE_ROLE_KEY:**
- Supabase Dashboard → Settings → API → service_role key (secret)
- ⚠️ **Never commit this to git!**

### 3.2 Deploy Edge Function

```bash
# Deploy stripe-webhook function
cd supabase/functions
supabase functions deploy stripe-webhook --no-verify-jwt

# Expected output:
# ✓ Function stripe-webhook deployed successfully
# URL: https://<project-ref>.supabase.co/functions/v1/stripe-webhook
```

### 3.3 Test Edge Function Locally (Optional)

```bash
# Start local Edge Functions server
supabase functions serve stripe-webhook --env-file .env.local

# In another terminal, test with curl
curl -X POST http://localhost:54321/functions/v1/stripe-webhook \
  -H "Content-Type: application/json" \
  -H "stripe-signature: test" \
  -d '{"type":"test","id":"evt_test"}'
```

### 3.4 Complete Stripe Webhook Setup

1. Go back to [Stripe Dashboard → Webhooks](https://dashboard.stripe.com/webhooks)
2. Click **Add endpoint**
3. Configure:
   - **Endpoint URL:** `https://<project-ref>.supabase.co/functions/v1/stripe-webhook`
   - **Description:** `PulseB2B Premium Subscription Webhook`
   - **Version:** `Latest API version`
   - **Events to send:**
     - [x] `checkout.session.completed`
     - [x] `customer.subscription.updated`
     - [x] `customer.subscription.deleted`
     - [x] `invoice.payment_failed`
4. Click **Add endpoint**
5. **Copy the signing secret** (`whsec_xxx...`)

### 3.5 Update Webhook Secret

```bash
# Update the webhook secret
supabase secrets set STRIPE_WEBHOOK_SECRET=whsec_xxx...

# Redeploy function to pick up new secret
supabase functions deploy stripe-webhook --no-verify-jwt
```

### 3.6 Test Webhook with Stripe CLI

```bash
# Install Stripe CLI (Windows)
# Download from https://stripe.com/docs/stripe-cli

# Login
stripe login

# Forward events to your Edge Function
stripe listen --forward-to https://<project-ref>.supabase.co/functions/v1/stripe-webhook

# In another terminal, trigger test event
stripe trigger checkout.session.completed
```

**Expected output:**
```
✓ Webhook received: checkout.session.completed
✓ User premium status activated
✓ Payment event logged to database
```

---

## 🔑 STEP 4: Google OAuth Setup (20 minutes)

### 4.1 Create Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Navigate to **APIs & Services → Credentials**
4. Click **Create Credentials → OAuth client ID**
5. Configure OAuth consent screen (if first time):
   - **User Type:** External
   - **App name:** `PulseB2B`
   - **User support email:** Your email
   - **Developer contact:** Your email
   - Click **Save and Continue**
   - **Scopes:** Add `email` and `profile`
   - Click **Save and Continue**

### 4.2 Create OAuth Client ID

1. **Application type:** `Web application`
2. **Name:** `PulseB2B - Supabase Auth`
3. **Authorized JavaScript origins:**
   - `https://<project-ref>.supabase.co`
   - `http://localhost:3000` (for local dev)
4. **Authorized redirect URIs:**
   - `https://<project-ref>.supabase.co/auth/v1/callback`
   - `http://localhost:54321/auth/v1/callback` (for local dev)
5. Click **Create**
6. **Copy the credentials:**
   - Client ID: `xxx.apps.googleusercontent.com`
   - Client Secret: `GOCSPX-xxx...`

### 4.3 Enable Google OAuth in Supabase

1. Go to [Supabase Dashboard → Authentication → Providers](https://app.supabase.com/project/_/auth/providers)
2. Find **Google** provider
3. Click **Enable**
4. Paste credentials:
   - **Client ID:** `xxx.apps.googleusercontent.com`
   - **Client Secret:** `GOCSPX-xxx...`
5. Click **Save**

### 4.4 Test Google OAuth Flow

1. Start your Next.js app locally
2. Go to `http://localhost:3000/login`
3. Click **Continue with Google**
4. You should be redirected to Google login
5. After login, should redirect back to `/auth/callback`
6. Then redirect to `/continental`

**Troubleshooting:**
- If redirect fails, check authorized redirect URIs in Google Console
- If user not created, check Supabase logs: Authentication → Logs
- Verify callback route exists: `frontend/src/app/auth/callback/route.ts`

---

## 🌐 STEP 5: Frontend Configuration (10 minutes)

### 5.1 Create Environment Variables File

```bash
# Create .env.local in frontend directory
cd frontend
```

**Create `frontend/.env.local`:**
```env
# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJxxx...

# Stripe
NEXT_PUBLIC_STRIPE_PAYMENT_LINK=https://buy.stripe.com/test_xxx...
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_xxx...

# App URL (for OAuth callbacks)
NEXT_PUBLIC_APP_URL=http://localhost:3000

# Feature Flags (optional)
NEXT_PUBLIC_ENABLE_PREMIUM_PAYWALL=true
NEXT_PUBLIC_ENABLE_GOOGLE_OAUTH=true
```

**Get NEXT_PUBLIC_SUPABASE_ANON_KEY:**
- Supabase Dashboard → Settings → API → anon public key

### 5.2 Update .gitignore

```bash
# Add to .gitignore if not present
echo ".env.local" >> .gitignore
echo ".env*.local" >> .gitignore
echo "*.env" >> .gitignore
```

### 5.3 Create Environment Variables Template

**Create `frontend/.env.example`:**
```env
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key_here

# Stripe Configuration
NEXT_PUBLIC_STRIPE_PAYMENT_LINK=https://buy.stripe.com/your_payment_link
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_or_pk_live_xxx

# App Configuration
NEXT_PUBLIC_APP_URL=http://localhost:3000

# Feature Flags
NEXT_PUBLIC_ENABLE_PREMIUM_PAYWALL=true
NEXT_PUBLIC_ENABLE_GOOGLE_OAUTH=true
```

### 5.4 Update Package.json Scripts

**Add to `frontend/package.json`:**
```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "type-check": "tsc --noEmit",
    "test:env": "node -e \"console.log('Supabase URL:', process.env.NEXT_PUBLIC_SUPABASE_URL)\"",
    "clean": "rm -rf .next out"
  }
}
```

---

## 🧪 STEP 6: Testing & Verification (20 minutes)

### 6.1 Test Database Security (RLS)

```sql
-- In Supabase SQL Editor

-- Test as anonymous user (should see NULL for gated fields)
SELECT 
  company_name,
  company_insight,      -- Should be visible
  tech_stack,           -- Should be visible
  hiring_probability_score, -- Should be visible
  lead_email,          -- Should be NULL
  direct_phone,        -- Should be NULL
  funding_exact_amount -- Should be NULL
FROM signals_secure
LIMIT 1;

-- Create test premium user
INSERT INTO auth.users (
  email,
  encrypted_password,
  email_confirmed_at,
  is_premium,
  premium_until
) VALUES (
  'premium@test.com',
  crypt('test123', gen_salt('bf')),
  NOW(),
  true,
  NOW() + INTERVAL '30 days'
);

-- Test as premium user (should see all fields)
-- First, authenticate as this user in your app
-- Then run the same query - should see actual data
```

### 6.2 Test Company Insight Generation

```sql
-- Insert test signal to trigger insight generation
INSERT INTO signals (
  company_name,
  website,
  location,
  funding_fuzzy_range,
  tech_stack,
  hiring_probability_score,
  pulse_score,
  regional_arbitrage_score,
  signal_type,
  employee_count
) VALUES (
  'TestCorp AI',
  'https://testcorp.ai',
  'San Francisco, CA',
  '$10M-$50M',
  ARRAY['Python', 'TensorFlow', 'AWS'],
  85,
  8.5,
  7.2,
  'funding_announcement',
  120
);

-- Check if company_insight was auto-generated
SELECT company_name, company_insight
FROM signals
WHERE company_name = 'TestCorp AI';

-- Expected output:
-- "TestCorp AI raised $10M-$50M in San Francisco, CA using Python, TensorFlow, AWS. 
--  🔥 Actively hiring - High urgency signals. 
--  💰 High arbitrage opportunity (7.2/10 savings potential). 
--  Signal: Recent funding round. Team size: ~120."
```

### 6.3 Test Stripe Webhook Flow

**Using Stripe CLI:**
```bash
# Trigger test payment
stripe trigger checkout.session.completed \
  --override checkout_session:client_reference_id=<user-uuid>

# Check payment_events table
```

```sql
-- Verify webhook was logged
SELECT 
  event_id,
  event_type,
  user_id,
  processed,
  created_at
FROM payment_events
ORDER BY created_at DESC
LIMIT 5;
```

### 6.4 Test Frontend Authentication

**Test Checklist:**
- [ ] Visit `/login` - should show login page
- [ ] Visit `/signup` - should show signup page with Free vs Premium comparison
- [ ] Click "Continue with Google" - should redirect to Google OAuth
- [ ] After Google login - should redirect to `/continental`
- [ ] Visit `/continental` without auth - should show AuthGuard fallback
- [ ] Login with email/password - should work
- [ ] Visit `/continental` after login - should see dashboard

### 6.5 Test Premium Gating

**As Free User:**
- [ ] See company_insight column (not blurred)
- [ ] See tech_stack (not blurred)
- [ ] See hiring_probability_score (not blurred)
- [ ] See funding_fuzzy_range (not blurred)
- [ ] Email column shows blur-md placeholder with unlock button
- [ ] Phone column shows blur-md placeholder with unlock button
- [ ] Funding shows fuzzy range with "Unlock exact amount" link
- [ ] Click unlock button - redirects to Stripe Payment Link

**As Premium User:**
```sql
-- Manually set test user to premium
UPDATE auth.users
SET 
  is_premium = true,
  premium_until = NOW() + INTERVAL '30 days',
  subscription_status = 'active'
WHERE email = 'your-test-email@example.com';
```

- [ ] Email column shows actual email (clickable mailto link)
- [ ] Phone column shows actual phone (clickable tel link)
- [ ] Funding shows exact amount in blue ($15.23M)
- [ ] No blur effects on any columns
- [ ] Premium badge shows in header

### 6.6 Test Payment Success Flow

1. Complete Stripe payment with test card: `4242 4242 4242 4242`
2. Should redirect to `/success`
3. Should see confetti animation
4. Should see "Processing your payment..." message
5. After webhook processes (~2-5 seconds):
   - `is_premium` should update to `true`
   - Success page should detect change
   - Should auto-redirect to `/continental?premium=activated`
6. Dashboard should now show unlocked data

---

## 🚀 STEP 7: Production Deployment

### 7.1 Update Environment Variables for Production

```env
# Production .env.local
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_prod_anon_key

# Use LIVE Stripe keys
NEXT_PUBLIC_STRIPE_PAYMENT_LINK=https://buy.stripe.com/live_xxx...
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_xxx...

NEXT_PUBLIC_APP_URL=https://yourdomain.com
```

### 7.2 Switch Stripe to Live Mode

1. Go to [Stripe Dashboard](https://dashboard.stripe.com/)
2. Toggle from **Test mode** to **Live mode** (top right)
3. Recreate product and payment link in live mode
4. Get live API keys (not test keys)
5. Update webhook endpoint with live keys

### 7.3 Deploy Frontend to Vercel/Netlify

**For Vercel:**
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel --prod

# Set environment variables in Vercel dashboard
# Project Settings → Environment Variables
```

**For Netlify:**
```bash
# Install Netlify CLI
npm i -g netlify-cli

# Deploy
cd frontend
netlify deploy --prod

# Set environment variables in Netlify dashboard
# Site Settings → Environment variables
```

### 7.4 Update OAuth Redirect URIs

**Update in Google Cloud Console:**
- Add production URL: `https://yourdomain.com`
- Add production callback: `https://<project-ref>.supabase.co/auth/v1/callback`

**Update in Supabase:**
- Dashboard → Authentication → URL Configuration
- Add `https://yourdomain.com` to allowed redirect URLs

### 7.5 Production Security Checklist

- [ ] All API keys are in environment variables (not hardcoded)
- [ ] `.env.local` is in `.gitignore`
- [ ] Service role key never exposed to frontend
- [ ] CORS configured correctly in Supabase
- [ ] RLS policies enabled on all tables
- [ ] Webhook signature verification enabled
- [ ] SSL/HTTPS enabled on all endpoints
- [ ] Rate limiting configured (optional)

---

## 📊 STEP 8: Monitoring & Analytics

### 8.1 Setup Payment Analytics Dashboard

```sql
-- Create dashboard view
CREATE OR REPLACE VIEW payment_dashboard AS
SELECT 
  DATE_TRUNC('day', created_at) AS date,
  COUNT(*) AS total_events,
  SUM(CASE WHEN event_type = 'checkout.session.completed' THEN 1 ELSE 0 END) AS successful_payments,
  SUM(CASE WHEN event_type = 'invoice.payment_failed' THEN 1 ELSE 0 END) AS failed_payments,
  SUM(amount_total) / 100.0 AS total_revenue_usd,
  COUNT(DISTINCT user_id) AS unique_customers
FROM payment_events
WHERE created_at > NOW() - INTERVAL '30 days'
GROUP BY DATE_TRUNC('day', created_at)
ORDER BY date DESC;

-- Query dashboard
SELECT * FROM payment_dashboard;
```

### 8.2 Setup Error Monitoring

**Monitor failed webhooks:**
```sql
-- Find unprocessed webhooks
SELECT 
  event_id,
  event_type,
  error_message,
  created_at,
  AGE(NOW(), created_at) as time_since_failure
FROM payment_events
WHERE processed = false
ORDER BY created_at DESC;

-- Set up alert (run daily)
SELECT COUNT(*) AS failed_webhooks
FROM payment_events
WHERE 
  processed = false
  AND created_at > NOW() - INTERVAL '24 hours';
```

### 8.3 Setup Conversion Tracking

```sql
-- Track free to premium conversions
SELECT 
  DATE_TRUNC('day', pe.created_at) AS date,
  COUNT(DISTINCT pe.user_id) AS new_premium_users,
  AVG(EXTRACT(EPOCH FROM (pe.created_at - u.created_at)) / 86400) AS avg_days_to_convert
FROM payment_events pe
JOIN auth.users u ON u.id = pe.user_id
WHERE pe.event_type = 'checkout.session.completed'
GROUP BY DATE_TRUNC('day', pe.created_at)
ORDER BY date DESC;
```

---

## 🆘 Troubleshooting Guide

### Issue: Webhook not receiving events

**Check:**
1. Verify webhook URL in Stripe Dashboard
2. Check Edge Function logs: `supabase functions logs stripe-webhook`
3. Verify webhook secret is correct
4. Test with Stripe CLI: `stripe listen --forward-to ...`

**Solution:**
```bash
# Redeploy function
supabase functions deploy stripe-webhook --no-verify-jwt

# Update webhook endpoint in Stripe Dashboard
```

### Issue: RLS blocking premium users

**Check:**
```sql
-- Verify user has premium status
SELECT id, email, is_premium, premium_until, subscription_status
FROM auth.users
WHERE email = 'user@example.com';

-- Test premium function
SELECT is_user_premium();
```

**Solution:**
```sql
-- Manually fix premium status
UPDATE auth.users
SET 
  is_premium = true,
  premium_until = NOW() + INTERVAL '30 days',
  subscription_status = 'active'
WHERE email = 'user@example.com';
```

### Issue: Google OAuth redirect loop

**Check:**
1. Verify redirect URIs match in Google Console
2. Check callback route exists: `/auth/callback/route.ts`
3. Verify Supabase provider is enabled

**Solution:**
```bash
# Check authorized redirect URIs
# Should include: https://<project-ref>.supabase.co/auth/v1/callback
```

### Issue: Company insights not generating

**Check:**
```sql
-- Verify trigger exists
SELECT tgname, tgtype, tgisinternal
FROM pg_trigger
WHERE tgrelid = 'signals'::regclass;

-- Manually trigger insight generation
UPDATE signals
SET company_insight = generate_company_insight(signals.*)
WHERE company_insight IS NULL;
```

---

## 📚 Additional Resources

### Documentation Links
- [Supabase Edge Functions](https://supabase.com/docs/guides/functions)
- [Stripe Webhooks](https://stripe.com/docs/webhooks)
- [Google OAuth Setup](https://developers.google.com/identity/protocols/oauth2)
- [Next.js Environment Variables](https://nextjs.org/docs/basic-features/environment-variables)

### Support Channels
- Supabase Discord: https://discord.supabase.com
- Stripe Support: https://support.stripe.com
- Stack Overflow: Tag `supabase` or `stripe`

---

## ✅ Final Checklist

### Before Launch
- [ ] All database migrations applied successfully
- [ ] Cron job scheduled for subscription expiry
- [ ] Stripe webhook endpoint configured and tested
- [ ] Google OAuth working in production
- [ ] Environment variables set in production
- [ ] RLS policies verified (free vs premium access)
- [ ] Company insights auto-generating
- [ ] Payment flow tested end-to-end
- [ ] Success page redirecting correctly
- [ ] Dashboard showing gated data properly

### Security Verification
- [ ] No API keys in git repository
- [ ] Service role key never exposed to frontend
- [ ] Webhook signature verification enabled
- [ ] RLS enabled on all sensitive tables
- [ ] CORS configured correctly

### Monitoring Setup
- [ ] Payment analytics dashboard created
- [ ] Error monitoring for failed webhooks
- [ ] Conversion tracking queries ready
- [ ] Supabase logs accessible

---

## 🎉 Congratulations!

Your premium paywall system is now live! Here's what you've built:

### Backend Security
- ✅ Row Level Security at database level
- ✅ Stripe webhook handler with signature verification
- ✅ Payment event logging for analytics
- ✅ Automated subscription expiry

### Frontend Features
- ✅ Authentication with Google OAuth + Email/Password
- ✅ Premium status checking
- ✅ Gated UI with blur effects
- ✅ Company intelligence display
- ✅ Success page with confetti

### Business Logic
- ✅ Free tier: See WHO is hiring (company insights)
- ✅ Premium tier: Get HOW to reach them (contact info)
- ✅ FOMO design driving conversions
- ✅ $0 infrastructure cost

### Revenue Protection
- ✅ No contact data in Network tab for free users
- ✅ Database-level security (can't bypass with curl)
- ✅ Stripe Payment Links (no backend API needed)
- ✅ Webhook-based premium activation

**Monthly Recurring Revenue Goal:** $49 × N subscribers  
**Cost:** $0 (Supabase + Stripe free tiers)  
**Profit Margin:** ~97% (minus Stripe fees)

---

## 🔄 Next Steps

1. **Marketing:** Create landing page highlighting free tier + premium features
2. **Analytics:** Set up Mixpanel/PostHog for conversion funnel tracking
3. **Retargeting:** Build SendGrid email campaigns for failed payments
4. **A/B Testing:** Test different company_insight formats for conversion
5. **API:** Build REST API for premium users (future feature)

**Need help?** Check troubleshooting section or reach out to support channels above.
