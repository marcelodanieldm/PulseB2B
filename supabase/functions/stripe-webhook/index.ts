import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
import Stripe from 'https://esm.sh/stripe@14.10.0?target=deno'

/**
 * STRIPE WEBHOOK HANDLER - Supabase Edge Function
 * 
 * Purpose: Handle Stripe webhook events to activate premium subscriptions
 * Security: Stripe signature verification prevents spoofing
 * Cost: $0 - runs on Supabase Edge Functions (2M requests/month free)
 * 
 * Supported Events:
 *   - checkout.session.completed: Activate premium on successful payment
 *   - customer.subscription.updated: Handle plan changes
 *   - customer.subscription.deleted: Revoke premium on cancellation
 *   - invoice.payment_failed: Track failed payments for retargeting
 * 
 * User Identification:
 *   Stripe checkout must include client_reference_id = user.id from Supabase
 *   This links the Stripe customer to the Supabase user
 * 
 * Deployment:
 *   supabase functions deploy stripe-webhook --no-verify-jwt
 * 
 * Configuration:
 *   Stripe Dashboard → Webhooks → Add endpoint
 *   URL: https://<project-ref>.supabase.co/functions/v1/stripe-webhook
 *   Events: checkout.session.completed, customer.subscription.*
 * 
 * Environment Variables:
 *   STRIPE_WEBHOOK_SECRET: Webhook signing secret from Stripe Dashboard
 *   STRIPE_SECRET_KEY: Stripe API secret key (sk_live_xxx or sk_test_xxx)
 *   SUPABASE_URL: Your Supabase project URL
 *   SUPABASE_SERVICE_ROLE_KEY: Service role key (bypasses RLS)
 */

// CORS headers for preflight requests
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type, stripe-signature',
}

interface WebhookResult {
  success: boolean;
  message: string;
  event_id?: string;
  user_id?: string;
  error?: string;
}

serve(async (req: Request): Promise<Response> => {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    // ============================================
    // STEP 1: Initialize Stripe and Supabase
    // ============================================
    
    const stripeSecretKey = Deno.env.get('STRIPE_SECRET_KEY')
    const webhookSecret = Deno.env.get('STRIPE_WEBHOOK_SECRET')
    const supabaseUrl = Deno.env.get('SUPABASE_URL')
    const supabaseServiceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')

    if (!stripeSecretKey || !webhookSecret || !supabaseUrl || !supabaseServiceKey) {
      console.error('Missing required environment variables')
      return new Response(
        JSON.stringify({ 
          success: false, 
          error: 'Server configuration error' 
        }),
        { 
          status: 500, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    const stripe = new Stripe(stripeSecretKey, {
      apiVersion: '2023-10-16',
      httpClient: Stripe.createFetchHttpClient(),
    })

    const supabase = createClient(supabaseUrl, supabaseServiceKey)

    // ============================================
    // STEP 2: Verify Stripe signature
    // ============================================
    
    const signature = req.headers.get('stripe-signature')
    if (!signature) {
      console.error('Missing stripe-signature header')
      return new Response(
        JSON.stringify({ 
          success: false, 
          error: 'Missing signature' 
        }),
        { 
          status: 400, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    const body = await req.text()
    let event: Stripe.Event

    try {
      event = await stripe.webhooks.constructEventAsync(
        body,
        signature,
        webhookSecret,
        undefined,
        Stripe.createSubtleCryptoProvider()
      )
    } catch (err) {
      console.error('Webhook signature verification failed:', err.message)
      return new Response(
        JSON.stringify({ 
          success: false, 
          error: 'Invalid signature' 
        }),
        { 
          status: 400, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    console.log(`Processing webhook event: ${event.type} (${event.id})`)

    // ============================================
    // STEP 3: Log webhook event for debugging
    // ============================================
    
    const { error: logError } = await supabase
      .from('payment_events')
      .insert({
        event_id: event.id,
        event_type: event.type,
        metadata: event.data.object,
        processed: false,
        created_at: new Date(event.created * 1000).toISOString(),
      })

    if (logError) {
      console.warn('Failed to log webhook event:', logError)
      // Continue processing even if logging fails
    }

    // ============================================
    // STEP 4: Handle specific event types
    // ============================================
    
    let result: WebhookResult

    switch (event.type) {
      case 'checkout.session.completed':
        result = await handleCheckoutCompleted(event, supabase)
        break
        
      case 'customer.subscription.updated':
        result = await handleSubscriptionUpdated(event, supabase)
        break
        
      case 'customer.subscription.deleted':
        result = await handleSubscriptionDeleted(event, supabase)
        break
        
      case 'invoice.payment_failed':
        result = await handlePaymentFailed(event, supabase)
        break
        
      default:
        console.log(`Unhandled event type: ${event.type}`)
        result = {
          success: true,
          message: `Event ${event.type} received but not processed`,
          event_id: event.id,
        }
    }

    // ============================================
    // STEP 5: Update event log with result
    // ============================================
    
    await supabase
      .from('payment_events')
      .update({
        processed: result.success,
        error_message: result.error || null,
        processed_at: new Date().toISOString(),
        user_id: result.user_id || null,
      })
      .eq('event_id', event.id)

    // ============================================
    // STEP 6: Return response to Stripe
    // ============================================
    
    return new Response(
      JSON.stringify(result),
      { 
        status: result.success ? 200 : 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      }
    )

  } catch (error) {
    console.error('Webhook handler error:', error)
    return new Response(
      JSON.stringify({ 
        success: false, 
        error: error.message 
      }),
      { 
        status: 500, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )
  }
})

/**
 * Handle checkout.session.completed event
 * Activates premium subscription for user
 */
async function handleCheckoutCompleted(
  event: Stripe.Event,
  supabase: any
): Promise<WebhookResult> {
  const session = event.data.object as Stripe.Checkout.Session

  // Extract user_id from client_reference_id (set during checkout)
  const userId = session.client_reference_id
  if (!userId) {
    console.error('Missing client_reference_id in checkout session')
    return {
      success: false,
      message: 'Missing user identification',
      event_id: event.id,
      error: 'client_reference_id not found',
    }
  }

  // Extract payment details
  const customerId = session.customer as string
  const subscriptionId = session.subscription as string
  const amountTotal = session.amount_total
  const currency = session.currency

  console.log(`Activating premium for user ${userId}`)

  // Call database function to activate premium
  const { data, error } = await supabase.rpc('activate_premium_subscription', {
    p_user_id: userId,
    p_stripe_customer_id: customerId,
    p_subscription_id: subscriptionId,
    p_duration_days: 30, // Monthly subscription
  })

  if (error) {
    console.error('Failed to activate premium:', error)
    return {
      success: false,
      message: 'Failed to activate premium subscription',
      event_id: event.id,
      user_id: userId,
      error: error.message,
    }
  }

  console.log(`✅ Premium activated for user ${userId}`)

  // Update payment_events with payment details
  await supabase
    .from('payment_events')
    .update({
      user_id: userId,
      customer_id: customerId,
      subscription_id: subscriptionId,
      amount_total: amountTotal,
      currency: currency,
      payment_status: session.payment_status,
      subscription_status: 'active',
    })
    .eq('event_id', event.id)

  return {
    success: true,
    message: 'Premium subscription activated',
    event_id: event.id,
    user_id: userId,
  }
}

/**
 * Handle customer.subscription.updated event
 * Updates subscription status (e.g., trialing → active)
 */
async function handleSubscriptionUpdated(
  event: Stripe.Event,
  supabase: any
): Promise<WebhookResult> {
  const subscription = event.data.object as Stripe.Subscription

  // Find user by stripe_customer_id
  const { data: users, error: queryError } = await supabase
    .from('users')
    .select('id')
    .eq('stripe_customer_id', subscription.customer)
    .single()

  if (queryError || !users) {
    console.error('User not found for customer:', subscription.customer)
    return {
      success: false,
      message: 'User not found',
      event_id: event.id,
      error: 'No user matches stripe_customer_id',
    }
  }

  const userId = users.id
  const status = subscription.status

  console.log(`Updating subscription status for user ${userId}: ${status}`)

  // Update subscription status in users table
  const { error: updateError } = await supabase
    .from('users')
    .update({
      subscription_status: status,
      // Keep is_premium true only for active/trialing subscriptions
      is_premium: ['active', 'trialing'].includes(status),
      updated_at: new Date().toISOString(),
    })
    .eq('id', userId)

  if (updateError) {
    console.error('Failed to update subscription:', updateError)
    return {
      success: false,
      message: 'Failed to update subscription status',
      event_id: event.id,
      user_id: userId,
      error: updateError.message,
    }
  }

  console.log(`✅ Subscription status updated for user ${userId}`)

  return {
    success: true,
    message: `Subscription status updated to ${status}`,
    event_id: event.id,
    user_id: userId,
  }
}

/**
 * Handle customer.subscription.deleted event
 * Revokes premium access when subscription is canceled
 */
async function handleSubscriptionDeleted(
  event: Stripe.Event,
  supabase: any
): Promise<WebhookResult> {
  const subscription = event.data.object as Stripe.Subscription

  // Find user by stripe_customer_id
  const { data: users, error: queryError } = await supabase
    .from('users')
    .select('id')
    .eq('stripe_customer_id', subscription.customer)
    .single()

  if (queryError || !users) {
    console.error('User not found for customer:', subscription.customer)
    return {
      success: false,
      message: 'User not found',
      event_id: event.id,
      error: 'No user matches stripe_customer_id',
    }
  }

  const userId = users.id

  console.log(`Revoking premium for user ${userId} (subscription canceled)`)

  // Call database function to revoke premium
  const { error } = await supabase.rpc('revoke_premium_subscription', {
    p_user_id: userId,
    p_reason: 'subscription_canceled',
  })

  if (error) {
    console.error('Failed to revoke premium:', error)
    return {
      success: false,
      message: 'Failed to revoke premium subscription',
      event_id: event.id,
      user_id: userId,
      error: error.message,
    }
  }

  console.log(`✅ Premium revoked for user ${userId}`)

  return {
    success: true,
    message: 'Premium subscription revoked',
    event_id: event.id,
    user_id: userId,
  }
}

/**
 * Handle invoice.payment_failed event
 * Logs failed payments for retargeting campaigns
 */
async function handlePaymentFailed(
  event: Stripe.Event,
  supabase: any
): Promise<WebhookResult> {
  const invoice = event.data.object as Stripe.Invoice

  // Find user by stripe_customer_id
  const { data: users, error: queryError } = await supabase
    .from('users')
    .select('id, email')
    .eq('stripe_customer_id', invoice.customer)
    .single()

  if (queryError || !users) {
    console.error('User not found for customer:', invoice.customer)
    return {
      success: false,
      message: 'User not found',
      event_id: event.id,
      error: 'No user matches stripe_customer_id',
    }
  }

  const userId = users.id
  const userEmail = users.email

  console.log(`⚠️ Payment failed for user ${userId} (${userEmail})`)

  // Update payment_events with failure details
  await supabase
    .from('payment_events')
    .update({
      user_id: userId,
      customer_id: invoice.customer as string,
      amount_total: invoice.amount_due,
      currency: invoice.currency,
      payment_status: 'failed',
      subscription_status: 'past_due',
    })
    .eq('event_id', event.id)

  // TODO: Trigger retargeting email via SendGrid
  // Send "Payment Failed - Update Payment Method" email
  // This can be a separate Edge Function or queued job

  console.log(`Failed payment logged for retargeting: ${userEmail}`)

  return {
    success: true,
    message: 'Failed payment logged for retargeting',
    event_id: event.id,
    user_id: userId,
  }
}

/* Edge Function serves on port 8000 */
