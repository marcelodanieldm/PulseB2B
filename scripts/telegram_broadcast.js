// =====================================================
// TELEGRAM DAILY BROADCAST SCRIPT
// =====================================================
// Purpose: Send daily signal to all active subscribers
// Trigger: GitHub Actions cron (8 AM UTC daily)
// Cost: $0 (runs on GitHub Actions free tier)
// Author: Senior Backend Developer
// Date: December 22, 2025
// =====================================================

const https = require('https');

// =====================================================
// CONFIGURATION
// =====================================================

const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;
const FRONTEND_URL = process.env.FRONTEND_URL || 'https://pulseb2b.com';

// Rate limiting config
const MESSAGES_PER_SECOND = 30; // Telegram limit is 30 msgs/sec
const BATCH_SIZE = 100; // Process subscribers in batches
const DELAY_BETWEEN_BATCHES = 3000; // 3 seconds

// =====================================================
// HELPER FUNCTIONS
// =====================================================

/**
 * Make HTTP request (Promise wrapper)
 */
function makeRequest(url, options = {}, body = null) {
  return new Promise((resolve, reject) => {
    const req = https.request(url, options, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        try {
          const parsed = JSON.parse(data);
          resolve(parsed);
        } catch (e) {
          resolve(data);
        }
      });
    });

    req.on('error', reject);

    if (body) {
      req.write(JSON.stringify(body));
    }

    req.end();
  });
}

/**
 * Query Supabase
 */
async function querySupabase(endpoint, method = 'GET', body = null) {
  const url = new URL(endpoint, SUPABASE_URL);
  
  const options = {
    method,
    headers: {
      'Content-Type': 'application/json',
      'apikey': SUPABASE_SERVICE_ROLE_KEY,
      'Authorization': `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`,
    },
  };

  return makeRequest(url, options, body);
}

/**
 * Send Telegram message
 */
async function sendTelegramMessage(chatId, text, parseMode = 'Markdown') {
  const url = `https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`;
  
  const body = {
    chat_id: chatId,
    text,
    parse_mode: parseMode,
    disable_web_page_preview: false,
  };

  try {
    const response = await makeRequest(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    }, body);

    return { success: response.ok, response };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

/**
 * Get country flag emoji
 */
function getCountryFlag(countryCode) {
  const flagMap = {
    "US": "🇺🇸", "GB": "🇬🇧", "DE": "🇩🇪", "FR": "🇫🇷",
    "CA": "🇨🇦", "AU": "🇦🇺", "NL": "🇳🇱", "SE": "🇸🇪",
    "SG": "🇸🇬", "IN": "🇮🇳", "BR": "🇧🇷", "MX": "🇲🇽",
    "ES": "🇪🇸", "IT": "🇮🇹", "JP": "🇯🇵", "KR": "🇰🇷",
    "CN": "🇨🇳", "IL": "🇮🇱", "CH": "🇨🇭",
  };
  return flagMap[countryCode] || "🌍";
}

/**
 * Format lead as Telegram message
 */
function formatLeadMessage(lead) {
  const scoreEmoji = lead.desperation_score >= 90 ? "🔥🔥🔥" : 
                     lead.desperation_score >= 80 ? "🔥🔥" : "🔥";
  
  const countryFlag = getCountryFlag(lead.country);

  const message = `
${scoreEmoji} *Daily Signal - ${new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}*

*${lead.company_name}* ${countryFlag}
━━━━━━━━━━━━━━━━━━━━

📊 *Desperation Score:* ${lead.desperation_score}/100

💡 *Intelligence:*
${lead.company_insight || "High-value B2B prospect detected"}

💰 *Funding:* ${lead.funding_range}
📈 *Hiring:* ${lead.hiring_velocity}
🛠 *Tech:* ${lead.tech_stack?.slice(0, 5).join(", ") || "N/A"}

━━━━━━━━━━━━━━━━━━━━
👉 [View Full Details](${FRONTEND_URL}/continental?lead_id=${lead.lead_id}&utm_source=telegram&utm_medium=bot&utm_campaign=daily_signal)

_Tip: Premium users see contact info + exact funding 💎_
  `.trim();

  return message;
}

/**
 * Sleep for specified milliseconds
 */
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// =====================================================
// MAIN BROADCAST LOGIC
// =====================================================

async function runDailyBroadcast() {
  console.log('=====================================================');
  console.log('TELEGRAM DAILY BROADCAST - Starting');
  console.log(`Time: ${new Date().toISOString()}`);
  console.log('=====================================================\n');

  const stats = {
    totalSubscribers: 0,
    successCount: 0,
    failureCount: 0,
    deactivatedCount: 0,
    startTime: Date.now(),
  };

  try {
    // =====================================================
    // STEP 1: Get Latest High-Scoring Lead
    // =====================================================
    console.log('[Step 1] Fetching latest lead...');
    
    const leadResponse = await querySupabase(
      '/rest/v1/rpc/get_latest_telegram_lead',
      'POST'
    );

    if (!leadResponse || leadResponse.length === 0) {
      console.error('❌ No leads found for broadcast. Exiting.');
      process.exit(1);
    }

    const lead = leadResponse[0];
    console.log(`✅ Found lead: ${lead.company_name} (Score: ${lead.desperation_score})`);
    console.log(`   Lead ID: ${lead.lead_id}\n`);

    // =====================================================
    // STEP 2: Get All Active Subscribers
    // =====================================================
    console.log('[Step 2] Fetching active subscribers...');
    
    const subscribersResponse = await querySupabase(
      '/rest/v1/rpc/get_telegram_broadcast_list',
      'POST'
    );

    if (!subscribersResponse || subscribersResponse.length === 0) {
      console.log('⚠️  No active subscribers found. Exiting.');
      process.exit(0);
    }

    const subscribers = subscribersResponse;
    stats.totalSubscribers = subscribers.length;
    console.log(`✅ Found ${subscribers.length} active subscribers\n`);

    // =====================================================
    // STEP 3: Format Message
    // =====================================================
    console.log('[Step 3] Formatting message...');
    const message = formatLeadMessage(lead);
    console.log('✅ Message formatted\n');

    // =====================================================
    // STEP 4: Send to All Subscribers (with rate limiting)
    // =====================================================
    console.log('[Step 4] Broadcasting to subscribers...');
    console.log(`   Rate limit: ${MESSAGES_PER_SECOND} msgs/sec`);
    console.log(`   Batch size: ${BATCH_SIZE} subscribers\n`);

    // Process in batches
    for (let i = 0; i < subscribers.length; i += BATCH_SIZE) {
      const batch = subscribers.slice(i, Math.min(i + BATCH_SIZE, subscribers.length));
      const batchNumber = Math.floor(i / BATCH_SIZE) + 1;
      const totalBatches = Math.ceil(subscribers.length / BATCH_SIZE);

      console.log(`[Batch ${batchNumber}/${totalBatches}] Processing ${batch.length} subscribers...`);

      // Send messages in parallel with rate limiting
      const promises = batch.map(async (subscriber, index) => {
        // Stagger sends to respect rate limit
        const delay = Math.floor(index * (1000 / MESSAGES_PER_SECOND));
        await sleep(delay);

        const { success, error } = await sendTelegramMessage(
          subscriber.chat_id,
          message
        );

        // Log delivery to database
        const logBody = {
          p_chat_id: subscriber.chat_id,
          p_message_type: 'daily_signal',
          p_lead_id: lead.lead_id,
          p_message_text: message.substring(0, 500), // Truncate for storage
          p_was_delivered: success,
          p_error_message: error || null,
        };

        await querySupabase('/rest/v1/rpc/log_telegram_message', 'POST', logBody);

        if (success) {
          stats.successCount++;
          console.log(`   ✓ Sent to ${subscriber.chat_id} (${subscriber.username || subscriber.first_name})`);
        } else {
          stats.failureCount++;
          console.error(`   ✗ Failed to send to ${subscriber.chat_id}: ${error}`);

          // If user blocked bot, deactivate subscriber
          if (error && (error.includes('blocked') || error.includes('user is deactivated'))) {
            await querySupabase(
              '/rest/v1/rpc/deactivate_telegram_subscriber',
              'POST',
              { p_chat_id: subscriber.chat_id }
            );
            stats.deactivatedCount++;
            console.log(`   ⚠️  Deactivated subscriber ${subscriber.chat_id}`);
          }
        }
      });

      await Promise.all(promises);

      // Delay between batches
      if (i + BATCH_SIZE < subscribers.length) {
        console.log(`   Waiting ${DELAY_BETWEEN_BATCHES}ms before next batch...\n`);
        await sleep(DELAY_BETWEEN_BATCHES);
      }
    }

    // =====================================================
    // STEP 5: Print Summary
    // =====================================================
    const duration = ((Date.now() - stats.startTime) / 1000).toFixed(2);
    
    console.log('\n=====================================================');
    console.log('BROADCAST COMPLETE');
    console.log('=====================================================');
    console.log(`📊 Total Subscribers:    ${stats.totalSubscribers}`);
    console.log(`✅ Successfully Sent:     ${stats.successCount}`);
    console.log(`❌ Failed:               ${stats.failureCount}`);
    console.log(`⚠️  Deactivated:         ${stats.deactivatedCount}`);
    console.log(`⏱️  Duration:             ${duration}s`);
    console.log(`🎯 Success Rate:         ${((stats.successCount / stats.totalSubscribers) * 100).toFixed(1)}%`);
    console.log('=====================================================\n');

    // Exit with success
    process.exit(0);

  } catch (error) {
    console.error('\n=====================================================');
    console.error('❌ BROADCAST FAILED');
    console.error('=====================================================');
    console.error('Error:', error.message);
    console.error('Stack:', error.stack);
    console.error('=====================================================\n');

    process.exit(1);
  }
}

// =====================================================
// ENTRY POINT
// =====================================================

// Validate environment variables
if (!TELEGRAM_BOT_TOKEN) {
  console.error('❌ TELEGRAM_BOT_TOKEN is required');
  process.exit(1);
}

if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) {
  console.error('❌ Supabase credentials are required');
  process.exit(1);
}

// Run broadcast
runDailyBroadcast();
