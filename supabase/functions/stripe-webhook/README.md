# Stripe Webhook Handler - Supabase Edge Function

## Overview
Serverless webhook endpoint to handle Stripe payment events and activate premium subscriptions.

**Cost:** $0 (2M requests/month free on Supabase Edge Functions)

## Architecture

```
Stripe Checkout → Webhook Event → Edge Function → Supabase Database
                                        ↓
                                 Signature Verify
                                        ↓
                              Update is_premium = true
```

## Supported Events

| Event Type | Action | Description |
|------------|--------|-------------|
| `checkout.session.completed` | Activate Premium | User completes payment, set `is_premium=true` |
| `customer.subscription.updated` | Update Status | Subscription status changes (active/trialing/canceled) |
| `customer.subscription.deleted` | Revoke Premium | Subscription canceled, set `is_premium=false` |
| `invoice.payment_failed` | Log for Retargeting | Payment failed, log for email retargeting |

## Security Features

### 1. Stripe Signature Verification
```typescript
const signature = req.headers.get('stripe-signature')
event = await stripe.webhooks.constructEventAsync(
  body,
  signature,
  webhookSecret
)
```
- Prevents webhook spoofing
- Verifies request is from Stripe
- Rejects unauthorized requests

### 2. Idempotency
- Events logged with unique `event_id`
- Duplicate events automatically ignored
- Safe to retry failed webhooks

### 3. Service Role Access
- Uses `SUPABASE_SERVICE_ROLE_KEY`
- Bypasses Row Level Security (RLS)
- Direct database access for webhook processing

## User Identification

Stripe must receive `client_reference_id` during checkout:

```typescript
// Frontend: Create Stripe Checkout Session
const checkoutUrl = `${process.env.NEXT_PUBLIC_STRIPE_PAYMENT_LINK}?client_reference_id=${user.id}`
window.location.href = checkoutUrl
```

The webhook extracts this ID to identify which user to activate:

```typescript
const userId = session.client_reference_id
await supabase.rpc('activate_premium_subscription', {
  p_user_id: userId,
  p_stripe_customer_id: customerId,
  p_subscription_id: subscriptionId,
  p_duration_days: 30,
})
```

## Deployment

### Step 1: Install Supabase CLI
```bash
npm install -g supabase
```

### Step 2: Link to your project
```bash
supabase link --project-ref <your-project-ref>
```

### Step 3: Deploy function
```bash
cd supabase/functions
supabase functions deploy stripe-webhook --no-verify-jwt
```

### Step 4: Set environment variables
```bash
supabase secrets set STRIPE_SECRET_KEY=sk_live_xxxxx
supabase secrets set STRIPE_WEBHOOK_SECRET=whsec_xxxxx
supabase secrets set SUPABASE_URL=https://xxxxx.supabase.co
supabase secrets set SUPABASE_SERVICE_ROLE_KEY=eyJxxx...
```

### Step 5: Configure Stripe webhook
1. Go to [Stripe Dashboard → Webhooks](https://dashboard.stripe.com/webhooks)
2. Click **Add endpoint**
3. Set URL: `https://<project-ref>.supabase.co/functions/v1/stripe-webhook`
4. Select events:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_failed`
5. Copy **Signing secret** (`whsec_xxx`) and add to Supabase secrets

## Testing

### Test with Stripe CLI
```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Login
stripe login

# Forward webhooks to local Edge Function
stripe listen --forward-to http://localhost:54321/functions/v1/stripe-webhook

# Trigger test event
stripe trigger checkout.session.completed
```

### Local Development
```bash
# Run Edge Function locally
supabase functions serve stripe-webhook --env-file .env.local

# In another terminal, forward Stripe events
stripe listen --forward-to http://localhost:54321/functions/v1/stripe-webhook
```

### Test Event Payload
```json
{
  "id": "evt_test_webhook",
  "object": "event",
  "type": "checkout.session.completed",
  "data": {
    "object": {
      "id": "cs_test_xxx",
      "client_reference_id": "550e8400-e29b-41d4-a716-446655440000",
      "customer": "cus_xxx",
      "subscription": "sub_xxx",
      "amount_total": 4900,
      "currency": "usd",
      "payment_status": "paid"
    }
  }
}
```

## Database Functions Used

### `activate_premium_subscription()`
```sql
SELECT activate_premium_subscription(
  p_user_id := '550e8400-e29b-41d4-a716-446655440000',
  p_stripe_customer_id := 'cus_xxx',
  p_subscription_id := 'sub_xxx',
  p_duration_days := 30
);
```

**Updates:**
- `auth.users.is_premium = true`
- `auth.users.premium_until = NOW() + 30 days`
- `auth.users.stripe_customer_id = 'cus_xxx'`
- `auth.users.subscription_status = 'active'`

### `revoke_premium_subscription()`
```sql
SELECT revoke_premium_subscription(
  p_user_id := '550e8400-e29b-41d4-a716-446655440000',
  p_reason := 'subscription_canceled'
);
```

**Updates:**
- `auth.users.is_premium = false`
- `auth.users.subscription_status = 'subscription_canceled'`

## Payment Events Log

All webhook events are logged to `payment_events` table for:
- **Debugging:** Full webhook payload in `metadata` JSONB
- **Analytics:** Revenue tracking, conversion rates
- **Retargeting:** Failed payments for email campaigns

### Query Failed Payments
```sql
SELECT 
  pe.user_id,
  u.email,
  pe.amount_total / 100.0 AS amount_dollars,
  pe.created_at,
  pe.error_message
FROM payment_events pe
JOIN auth.users u ON u.id = pe.user_id
WHERE 
  pe.event_type = 'invoice.payment_failed'
  AND pe.created_at > NOW() - INTERVAL '7 days'
ORDER BY pe.created_at DESC;
```

### Query Revenue Analytics
```sql
SELECT 
  DATE_TRUNC('day', created_at) AS date,
  COUNT(*) AS total_payments,
  SUM(amount_total) / 100.0 AS revenue_dollars,
  COUNT(DISTINCT user_id) AS unique_customers
FROM payment_events
WHERE 
  event_type = 'checkout.session.completed'
  AND payment_status = 'paid'
GROUP BY DATE_TRUNC('day', created_at)
ORDER BY date DESC;
```

## Error Handling

### Webhook Signature Failed
```
Response: 400 Bad Request
{
  "success": false,
  "error": "Invalid signature"
}
```

**Fix:** Verify `STRIPE_WEBHOOK_SECRET` matches Stripe Dashboard

### Missing client_reference_id
```
Response: 400 Bad Request
{
  "success": false,
  "error": "client_reference_id not found"
}
```

**Fix:** Ensure checkout URL includes `?client_reference_id=${user.id}`

### User Not Found
```
Response: 400 Bad Request
{
  "success": false,
  "error": "No user matches stripe_customer_id"
}
```

**Fix:** Verify user exists in `auth.users` table

## Monitoring

### View Function Logs
```bash
supabase functions logs stripe-webhook
```

### Check Recent Webhook Events
```sql
SELECT 
  event_id,
  event_type,
  processed,
  error_message,
  created_at
FROM payment_events
ORDER BY created_at DESC
LIMIT 10;
```

### Alert on Failed Webhooks
```sql
-- Find unprocessed webhooks older than 5 minutes
SELECT COUNT(*) AS failed_webhooks
FROM payment_events
WHERE 
  processed = false
  AND created_at < NOW() - INTERVAL '5 minutes';
```

## Retargeting Workflow

### Failed Payment Email Campaign
1. Query failed payments from last 7 days
2. Send "Update Payment Method" email via SendGrid
3. Include link to Stripe Customer Portal
4. Track email opens/clicks for conversion

### Abandoned Checkout Campaign
1. Track `checkout.session.created` but not `completed`
2. Send "Complete Your Purchase" email after 24 hours
3. Include discount code for urgency
4. Track conversion rate

### Implementation (Future)
```typescript
// In handlePaymentFailed()
await sendgrid.send({
  to: userEmail,
  from: 'billing@pulseb2b.com',
  templateId: 'd-failed-payment',
  dynamicTemplateData: {
    user_name: userName,
    amount_due: amountDue / 100,
    update_payment_url: `https://billing.stripe.com/p/login/xxx`,
  },
});
```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `STRIPE_SECRET_KEY` | Stripe API key | `sk_live_xxx` or `sk_test_xxx` |
| `STRIPE_WEBHOOK_SECRET` | Webhook signing secret | `whsec_xxx` |
| `SUPABASE_URL` | Supabase project URL | `https://xxxxx.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role key (bypasses RLS) | `eyJxxx...` |

## Security Checklist

- [x] Stripe signature verification implemented
- [x] Service role key used (not anon key)
- [x] Webhook events logged for audit trail
- [x] Idempotency via `event_id` unique constraint
- [x] CORS headers configured for Stripe origin
- [x] Error handling prevents data leaks
- [x] Database functions use SECURITY DEFINER
- [x] RLS policies protect sensitive data

## Cost Analysis

| Component | Monthly Cost |
|-----------|--------------|
| Supabase Edge Functions | **$0** (2M requests free) |
| Database Storage | **$0** (500 MB free) |
| Stripe Fees | 2.9% + $0.30 per transaction |

**Example:** 100 monthly signups × $49/month = $4,900 revenue
- Stripe fees: ~$160 (3.3%)
- Infrastructure: **$0**
- **Net revenue: $4,740** ✅

## Next Steps

1. ✅ Deploy Edge Function
2. ✅ Configure Stripe webhook endpoint
3. ✅ Test with Stripe CLI
4. ⏳ Update frontend checkout to include `client_reference_id`
5. ⏳ Set up monitoring and alerts
6. ⏳ Implement retargeting email campaigns
7. ⏳ Add cron job for expired subscriptions
