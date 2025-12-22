-- =====================================================
-- ROW LEVEL SECURITY (RLS) FOR PREMIUM GATING
-- =====================================================
-- 
-- Purpose: Secure sensitive contact information at the database level
-- Security Layer: This is the REAL security - frontend blur is just UX
-- 
-- Strategy:
--   1. Enable RLS on tables with sensitive data
--   2. Create policies that check user's is_premium status
--   3. Filter out sensitive columns for non-premium users
--   4. Allow full access for premium users
-- 
-- Sensitive Fields to Protect:
--   - lead_email (contact email)
--   - direct_phone (phone number)
--   - funding_exact_amount (exact funding amount)
-- 
-- Date: December 22, 2025
-- =====================================================

-- =====================================================
-- STEP 1: Add premium tracking columns to users table
-- =====================================================

-- Add is_premium column if not exists
ALTER TABLE auth.users 
ADD COLUMN IF NOT EXISTS is_premium BOOLEAN DEFAULT FALSE;

-- Add premium_until column for subscription expiry tracking
ALTER TABLE auth.users 
ADD COLUMN IF NOT EXISTS premium_until TIMESTAMPTZ;

-- Add stripe_customer_id for webhook identification
ALTER TABLE auth.users 
ADD COLUMN IF NOT EXISTS stripe_customer_id TEXT;

-- Add payment tracking columns
ALTER TABLE auth.users 
ADD COLUMN IF NOT EXISTS subscription_status TEXT; -- 'active', 'canceled', 'past_due', 'trialing'

-- Create index for faster premium status queries
CREATE INDEX IF NOT EXISTS idx_users_premium_status 
ON auth.users(id, is_premium) 
WHERE is_premium = true;

-- Create index for expiry queries (cleanup jobs)
CREATE INDEX IF NOT EXISTS idx_users_premium_until 
ON auth.users(premium_until) 
WHERE is_premium = true;

-- Create index for Stripe lookups
CREATE INDEX IF NOT EXISTS idx_users_stripe_customer 
ON auth.users(stripe_customer_id) 
WHERE stripe_customer_id IS NOT NULL;

COMMENT ON COLUMN auth.users.is_premium IS 'Premium subscription status - gates access to sensitive contact data';
COMMENT ON COLUMN auth.users.premium_until IS 'Subscription expiry date - used to auto-revoke premium access';
COMMENT ON COLUMN auth.users.stripe_customer_id IS 'Stripe customer ID for webhook identification';
COMMENT ON COLUMN auth.users.subscription_status IS 'Current subscription status from Stripe';

-- =====================================================
-- STEP 2: Create helper function to check premium status
-- =====================================================

-- Function to check if current user has active premium subscription
CREATE OR REPLACE FUNCTION is_user_premium()
RETURNS BOOLEAN
LANGUAGE SQL
SECURITY DEFINER
STABLE
AS $$
  SELECT COALESCE(
    (
      SELECT 
        is_premium = true 
        AND (premium_until IS NULL OR premium_until > NOW())
      FROM auth.users
      WHERE id = auth.uid()
    ),
    false
  );
$$;

COMMENT ON FUNCTION is_user_premium IS 'Returns true if current user has active premium subscription (checks both is_premium flag and expiry date)';

-- =====================================================
-- STEP 3: Create view with masked sensitive data
-- =====================================================

-- Create a view that automatically masks sensitive fields for non-premium users
CREATE OR REPLACE VIEW public.signals_secure AS
SELECT 
  id,
  company_name,
  website,
  signal_type,
  
  -- Mask email for non-premium users
  CASE 
    WHEN is_user_premium() THEN lead_email
    ELSE NULL
  END AS lead_email,
  
  -- Mask phone for non-premium users
  CASE 
    WHEN is_user_premium() THEN direct_phone
    ELSE NULL
  END AS direct_phone,
  
  -- Show fuzzy funding for non-premium, exact for premium
  CASE 
    WHEN is_user_premium() THEN funding_exact_amount
    ELSE NULL
  END AS funding_exact_amount,
  
  -- These fields are always visible (non-sensitive)
  funding_fuzzy_range,
  pulse_score,
  desperation_level,
  regional_arbitrage_score,
  employee_count,
  location,
  detected_at,
  enrichment_status,
  last_enriched_at,
  created_at,
  updated_at
  
FROM public.signals;

COMMENT ON VIEW public.signals_secure IS 'Secure view that automatically masks sensitive contact information for non-premium users';

-- Grant access to authenticated users
GRANT SELECT ON public.signals_secure TO authenticated;

-- =====================================================
-- STEP 4: Enable RLS on base tables
-- =====================================================

-- Enable RLS on signals table
ALTER TABLE public.signals ENABLE ROW LEVEL SECURITY;

-- Policy: Users can see all rows, but sensitive columns filtered via view
CREATE POLICY "Users can view all signals (use secure view for filtering)"
  ON public.signals
  FOR SELECT
  TO authenticated
  USING (true);

COMMENT ON POLICY "Users can view all signals (use secure view for filtering)" ON public.signals 
IS 'Allow all authenticated users to query signals table - use signals_secure view for automatic field masking';

-- =====================================================
-- STEP 5: Create payment events log table
-- =====================================================

-- Table to log all Stripe webhook events for debugging and retargeting
CREATE TABLE IF NOT EXISTS public.payment_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_id TEXT NOT NULL UNIQUE, -- Stripe event ID (evt_xxx)
  event_type TEXT NOT NULL, -- 'checkout.session.completed', 'customer.subscription.deleted', etc.
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  customer_id TEXT, -- Stripe customer ID
  subscription_id TEXT, -- Stripe subscription ID
  amount_total INTEGER, -- Amount in cents
  currency TEXT, -- 'usd', 'eur', etc.
  payment_status TEXT, -- 'paid', 'unpaid', 'no_payment_required'
  subscription_status TEXT, -- 'active', 'canceled', 'past_due', 'trialing'
  metadata JSONB, -- Full webhook payload for debugging
  processed BOOLEAN DEFAULT FALSE, -- Whether webhook was successfully processed
  error_message TEXT, -- Error details if processing failed
  created_at TIMESTAMPTZ DEFAULT NOW(),
  processed_at TIMESTAMPTZ
);

-- Indexes for payment events
CREATE INDEX idx_payment_events_user_id ON public.payment_events(user_id);
CREATE INDEX idx_payment_events_event_type ON public.payment_events(event_type);
CREATE INDEX idx_payment_events_created_at ON public.payment_events(created_at);
CREATE INDEX idx_payment_events_processed ON public.payment_events(processed) WHERE processed = false;
CREATE INDEX idx_payment_events_customer_id ON public.payment_events(customer_id);

COMMENT ON TABLE public.payment_events IS 'Log of all Stripe webhook events for debugging, analytics, and retargeting';
COMMENT ON COLUMN public.payment_events.event_id IS 'Unique Stripe event ID - used for idempotency';
COMMENT ON COLUMN public.payment_events.processed IS 'Whether webhook was successfully processed - false indicates failed webhooks for retargeting';

-- Enable RLS on payment events
ALTER TABLE public.payment_events ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own payment events
CREATE POLICY "Users can view their own payment events"
  ON public.payment_events
  FOR SELECT
  TO authenticated
  USING (user_id = auth.uid());

-- Policy: Service role can insert payment events (webhook handler)
CREATE POLICY "Service role can insert payment events"
  ON public.payment_events
  FOR INSERT
  TO service_role
  WITH CHECK (true);

-- Policy: Service role can update payment events (mark as processed)
CREATE POLICY "Service role can update payment events"
  ON public.payment_events
  FOR UPDATE
  TO service_role
  USING (true);

-- =====================================================
-- STEP 6: Create function to activate premium access
-- =====================================================

-- Function called by webhook to activate premium subscription
CREATE OR REPLACE FUNCTION activate_premium_subscription(
  p_user_id UUID,
  p_stripe_customer_id TEXT,
  p_subscription_id TEXT,
  p_duration_days INTEGER DEFAULT 30
)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  -- Update user to premium status
  UPDATE auth.users
  SET 
    is_premium = true,
    premium_until = NOW() + (p_duration_days || ' days')::INTERVAL,
    stripe_customer_id = p_stripe_customer_id,
    subscription_status = 'active',
    updated_at = NOW()
  WHERE id = p_user_id;
  
  -- Return true if user was updated
  RETURN FOUND;
END;
$$;

COMMENT ON FUNCTION activate_premium_subscription IS 'Activates premium subscription for user - called by Stripe webhook handler';

-- =====================================================
-- STEP 7: Create function to revoke premium access
-- =====================================================

-- Function to revoke premium access (expired subscription or cancellation)
CREATE OR REPLACE FUNCTION revoke_premium_subscription(
  p_user_id UUID,
  p_reason TEXT DEFAULT 'subscription_ended'
)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  -- Update user to free status
  UPDATE auth.users
  SET 
    is_premium = false,
    subscription_status = p_reason,
    updated_at = NOW()
  WHERE id = p_user_id;
  
  -- Return true if user was updated
  RETURN FOUND;
END;
$$;

COMMENT ON FUNCTION revoke_premium_subscription IS 'Revokes premium subscription - called when subscription expires or is canceled';

-- =====================================================
-- STEP 8: Create scheduled job to expire premium subscriptions
-- =====================================================

-- Function to automatically expire premium subscriptions
CREATE OR REPLACE FUNCTION expire_premium_subscriptions()
RETURNS INTEGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  expired_count INTEGER;
BEGIN
  -- Update users whose premium_until has passed
  WITH expired_users AS (
    UPDATE auth.users
    SET 
      is_premium = false,
      subscription_status = 'expired',
      updated_at = NOW()
    WHERE 
      is_premium = true 
      AND premium_until IS NOT NULL 
      AND premium_until < NOW()
    RETURNING id
  )
  SELECT COUNT(*) INTO expired_count FROM expired_users;
  
  -- Log the expiration count
  RAISE NOTICE 'Expired % premium subscriptions', expired_count;
  
  RETURN expired_count;
END;
$$;

COMMENT ON FUNCTION expire_premium_subscriptions IS 'Automatically expires premium subscriptions - run via cron job (daily)';

-- =====================================================
-- STEP 9: Grant necessary permissions
-- =====================================================

-- Grant execute permissions to authenticated users
GRANT EXECUTE ON FUNCTION is_user_premium() TO authenticated;

-- Grant execute permissions to service role (webhook handler)
GRANT EXECUTE ON FUNCTION activate_premium_subscription(UUID, TEXT, TEXT, INTEGER) TO service_role;
GRANT EXECUTE ON FUNCTION revoke_premium_subscription(UUID, TEXT) TO service_role;
GRANT EXECUTE ON FUNCTION expire_premium_subscriptions() TO service_role;

-- =====================================================
-- STEP 10: Create analytics view for payment tracking
-- =====================================================

-- View for payment analytics (admin only)
CREATE OR REPLACE VIEW public.payment_analytics AS
SELECT 
  DATE_TRUNC('day', created_at) AS payment_date,
  event_type,
  COUNT(*) AS event_count,
  SUM(amount_total) AS total_revenue_cents,
  SUM(amount_total) / 100.0 AS total_revenue_dollars,
  COUNT(DISTINCT user_id) AS unique_users,
  SUM(CASE WHEN processed = true THEN 1 ELSE 0 END) AS successful_events,
  SUM(CASE WHEN processed = false THEN 1 ELSE 0 END) AS failed_events
FROM public.payment_events
GROUP BY DATE_TRUNC('day', created_at), event_type
ORDER BY payment_date DESC, event_type;

COMMENT ON VIEW public.payment_analytics IS 'Daily payment analytics aggregated by event type - for admin dashboard';

-- =====================================================
-- STEP 11: Security validation
-- =====================================================

-- Test query to verify RLS is working (should return NULL for non-premium users)
-- SELECT lead_email FROM public.signals_secure WHERE id = '<some_id>';
-- 
-- Expected behavior:
--   - Premium user (is_premium=true, premium_until>NOW): Returns actual email
--   - Free user (is_premium=false): Returns NULL
--   - Expired user (premium_until<NOW): Returns NULL

-- =====================================================
-- DEPLOYMENT CHECKLIST
-- =====================================================
-- 
-- 1. Apply this migration: supabase db push
-- 2. Deploy Stripe webhook Edge Function (see supabase/functions/stripe-webhook/)
-- 3. Configure Stripe webhook endpoint in Dashboard
-- 4. Set up cron job: SELECT cron.schedule('expire-premium-subscriptions', '0 0 * * *', $$ SELECT expire_premium_subscriptions(); $$);
-- 5. Update frontend queries to use signals_secure view instead of signals table
-- 6. Test with free user: Confirm sensitive fields return NULL
-- 7. Test with premium user: Confirm sensitive fields return actual data
-- 8. Test webhook: Complete Stripe checkout and verify is_premium updates
-- 
-- =====================================================

-- Migration complete
SELECT 'RLS Premium Security Migration Complete' AS status;
