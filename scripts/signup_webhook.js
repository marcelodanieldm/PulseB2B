#!/usr/bin/env node

/**
 * SIGNUP WEBHOOK ENDPOINT
 * Real-time lead enrichment and alerting on user signup
 * 
 * Triggers the complete enrichment pipeline:
 * 1. Enrich company data from email domain
 * 2. Calculate lead priority score
 * 3. Send high-value alert to Telegram if criteria met
 * 4. Update enrichment_completed flag
 * 
 * Usage:
 *   node signup_webhook.js
 *   
 * Endpoint:
 *   POST /api/webhooks/user-signup
 *   Body: { userId: string, email: string }
 * 
 * Environment Variables:
 *   - WEBHOOK_PORT (default: 3001)
 *   - WEBHOOK_SECRET (optional, for request validation)
 */

const express = require('express');
const { createClient } = require('@supabase/supabase-js');
require('dotenv').config();

// Import enrichment services
const { enrichUser } = require('./lead_enrichment_service');
const { scoreUser } = require('./lead_scoring_engine');
const { sendHighValueAlert } = require('./telegram_alert_service');

// ============================================================================
// CONFIGURATION
// ============================================================================

const PORT = process.env.WEBHOOK_PORT || 3001;
const WEBHOOK_SECRET = process.env.WEBHOOK_SECRET;

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_KEY;

if (!SUPABASE_URL || !SUPABASE_SERVICE_KEY) {
  console.error('❌ Missing Supabase credentials');
  process.exit(1);
}

const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);

// ============================================================================
// EXPRESS APP
// ============================================================================

const app = express();
app.use(express.json());

// Middleware: Request logging
app.use((req, res, next) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.path}`);
  next();
});

// Middleware: Webhook secret validation (optional)
function validateWebhookSecret(req, res, next) {
  if (!WEBHOOK_SECRET) {
    return next(); // Skip validation if no secret configured
  }
  
  const providedSecret = req.headers['x-webhook-secret'];
  if (providedSecret !== WEBHOOK_SECRET) {
    return res.status(401).json({ error: 'Invalid webhook secret' });
  }
  
  next();
}

// ============================================================================
// WEBHOOK ENDPOINTS
// ============================================================================

/**
 * POST /api/webhooks/user-signup
 * Trigger lead enrichment pipeline on user signup
 */
app.post('/api/webhooks/user-signup', validateWebhookSecret, async (req, res) => {
  const { userId, email } = req.body;
  
  // Validate input
  if (!userId || !email) {
    return res.status(400).json({ 
      error: 'Missing required fields: userId, email' 
    });
  }
  
  console.log(`\n🔔 New signup webhook received:`);
  console.log(`   User ID: ${userId}`);
  console.log(`   Email: ${email}`);
  
  // Return 200 immediately, process async
  res.status(200).json({ 
    message: 'Enrichment queued',
    userId,
    status: 'processing'
  });
  
  // Process enrichment pipeline asynchronously
  processEnrichmentPipeline(userId, email).catch(error => {
    console.error('❌ Pipeline error:', error);
  });
});

/**
 * POST /api/webhooks/batch-enrich
 * Trigger batch enrichment for multiple users
 */
app.post('/api/webhooks/batch-enrich', validateWebhookSecret, async (req, res) => {
  const { userIds } = req.body;
  
  if (!userIds || !Array.isArray(userIds)) {
    return res.status(400).json({ 
      error: 'Missing or invalid userIds array' 
    });
  }
  
  console.log(`\n📦 Batch enrichment webhook received:`);
  console.log(`   Users: ${userIds.length}`);
  
  res.status(200).json({ 
    message: 'Batch enrichment queued',
    count: userIds.length,
    status: 'processing'
  });
  
  // Process batch asynchronously
  processBatchEnrichment(userIds).catch(error => {
    console.error('❌ Batch error:', error);
  });
});

/**
 * GET /api/webhooks/status/:userId
 * Check enrichment status for a user
 */
app.get('/api/webhooks/status/:userId', async (req, res) => {
  const { userId } = req.params;
  
  try {
    const { data: user } = await supabase
      .from('users')
      .select('enrichment_completed, last_enriched_at')
      .eq('id', userId)
      .single();
    
    const { data: enrichment } = await supabase
      .from('company_enrichment')
      .select('company_name, employee_count, industry')
      .eq('user_id', userId)
      .single();
    
    const { data: score } = await supabase
      .from('lead_scores')
      .select('total_score, priority_tier, is_high_value_prospect')
      .eq('user_id', userId)
      .single();
    
    res.json({
      userId,
      enrichment_completed: user?.enrichment_completed || false,
      last_enriched_at: user?.last_enriched_at,
      company: enrichment ? {
        name: enrichment.company_name,
        employees: enrichment.employee_count,
        industry: enrichment.industry
      } : null,
      score: score ? {
        total: score.total_score,
        tier: score.priority_tier,
        is_high_value: score.is_high_value_prospect
      } : null
    });
    
  } catch (error) {
    console.error('Status check error:', error);
    res.status(500).json({ error: 'Failed to check status' });
  }
});

/**
 * GET /health
 * Health check endpoint
 */
app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok',
    service: 'lead-enrichment-webhook',
    timestamp: new Date().toISOString()
  });
});

// ============================================================================
// ENRICHMENT PIPELINE
// ============================================================================

/**
 * Process complete enrichment pipeline for a single user
 */
async function processEnrichmentPipeline(userId, email) {
  const startTime = Date.now();
  
  try {
    console.log(`\n🔄 Starting enrichment pipeline for ${email}...`);
    
    // Step 1: Enrich company data
    console.log('   [1/4] Enriching company data...');
    const enrichmentResult = await enrichUser(userId, email);
    
    if (!enrichmentResult || enrichmentResult.is_generic_provider) {
      console.log('   ⏭️  Skipped (generic email provider)');
      await markEnrichmentComplete(userId, false);
      return;
    }
    
    console.log(`   ✅ Company enriched: ${enrichmentResult.company_name}`);
    
    // Step 2: Calculate lead score
    console.log('   [2/4] Calculating lead score...');
    const scoreResult = await scoreUser(userId);
    
    if (!scoreResult) {
      console.log('   ❌ Scoring failed');
      await markEnrichmentComplete(userId, false);
      return;
    }
    
    console.log(`   ✅ Score calculated: ${scoreResult.total_score} (${scoreResult.priority_tier})`);
    
    // Step 3: Check if high-value prospect
    console.log('   [3/4] Checking high-value criteria...');
    const { data: score } = await supabase
      .from('lead_scores')
      .select('is_high_value_prospect, total_score, priority_tier')
      .eq('user_id', userId)
      .single();
    
    // Step 4: Send alert if high-value
    if (score?.is_high_value_prospect) {
      console.log('   [4/4] 🚨 High-value prospect detected! Sending alert...');
      await sendHighValueAlert(userId);
      console.log('   ✅ Telegram alert sent');
    } else {
      console.log('   [4/4] Standard prospect (no alert needed)');
    }
    
    // Mark enrichment complete
    await markEnrichmentComplete(userId, true);
    
    const duration = ((Date.now() - startTime) / 1000).toFixed(2);
    console.log(`\n✅ Pipeline complete for ${email} (${duration}s)`);
    
    // Log summary
    await logPipelineExecution(userId, {
      success: true,
      duration_ms: Date.now() - startTime,
      company_name: enrichmentResult?.company_name,
      lead_score: score?.total_score,
      priority_tier: score?.priority_tier,
      high_value: score?.is_high_value_prospect
    });
    
  } catch (error) {
    console.error(`\n❌ Pipeline failed for ${email}:`, error.message);
    
    // Log failure
    await logPipelineExecution(userId, {
      success: false,
      duration_ms: Date.now() - startTime,
      error: error.message
    });
    
    // Mark enrichment as incomplete
    await markEnrichmentComplete(userId, false);
  }
}

/**
 * Process batch enrichment for multiple users
 */
async function processBatchEnrichment(userIds) {
  console.log(`\n🔄 Starting batch enrichment for ${userIds.length} users...`);
  
  let processed = 0;
  let enriched = 0;
  let failed = 0;
  let skipped = 0;
  
  for (const userId of userIds) {
    try {
      // Fetch user email
      const { data: user } = await supabase
        .from('users')
        .select('email')
        .eq('id', userId)
        .single();
      
      if (!user?.email) {
        console.log(`   ⏭️  [${++processed}/${userIds.length}] Skipped (no email)`);
        skipped++;
        continue;
      }
      
      // Process enrichment
      await processEnrichmentPipeline(userId, user.email);
      enriched++;
      
      console.log(`   ✅ [${++processed}/${userIds.length}] Processed ${user.email}`);
      
      // Rate limiting: 1 request per second
      await new Promise(resolve => setTimeout(resolve, 1000));
      
    } catch (error) {
      console.error(`   ❌ [${++processed}/${userIds.length}] Failed:`, error.message);
      failed++;
    }
  }
  
  console.log(`\n✅ Batch enrichment complete:`);
  console.log(`   Enriched: ${enriched}`);
  console.log(`   Skipped: ${skipped}`);
  console.log(`   Failed: ${failed}`);
}

/**
 * Mark enrichment as complete in users table
 */
async function markEnrichmentComplete(userId, success) {
  try {
    await supabase
      .from('users')
      .update({ 
        enrichment_completed: success,
        last_enriched_at: new Date().toISOString()
      })
      .eq('id', userId);
  } catch (error) {
    console.error('Failed to update enrichment status:', error);
  }
}

/**
 * Log pipeline execution to database (optional analytics table)
 */
async function logPipelineExecution(userId, details) {
  try {
    // Optional: Create a pipeline_logs table for analytics
    // For now, just log to console
    console.log(`\n📊 Pipeline Summary:`, JSON.stringify(details, null, 2));
  } catch (error) {
    console.error('Failed to log pipeline execution:', error);
  }
}

// ============================================================================
// SERVER START
// ============================================================================

app.listen(PORT, () => {
  console.log('\n' + '='.repeat(60));
  console.log('🚀 Lead Enrichment Webhook Server Started');
  console.log('='.repeat(60));
  console.log(`\n📡 Listening on: http://localhost:${PORT}`);
  console.log('\n📋 Available Endpoints:');
  console.log(`   POST   /api/webhooks/user-signup`);
  console.log(`   POST   /api/webhooks/batch-enrich`);
  console.log(`   GET    /api/webhooks/status/:userId`);
  console.log(`   GET    /health`);
  console.log('\n🔐 Webhook Secret:', WEBHOOK_SECRET ? 'Configured ✅' : 'Not configured ⚠️');
  console.log('\n📚 Documentation: LEAD_ENRICHMENT_SYSTEM.md');
  console.log('\n' + '='.repeat(60) + '\n');
});

// ============================================================================
// GRACEFUL SHUTDOWN
// ============================================================================

process.on('SIGTERM', () => {
  console.log('\n⚠️  SIGTERM received, shutting down gracefully...');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('\n⚠️  SIGINT received, shutting down gracefully...');
  process.exit(0);
});

// ============================================================================
// ERROR HANDLING
// ============================================================================

process.on('unhandledRejection', (reason, promise) => {
  console.error('❌ Unhandled Rejection at:', promise, 'reason:', reason);
});

process.on('uncaughtException', (error) => {
  console.error('❌ Uncaught Exception:', error);
  process.exit(1);
});
