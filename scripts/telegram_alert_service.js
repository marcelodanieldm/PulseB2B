/**
 * Telegram Alert Service
 * Sends high-value prospect alerts to Telegram channel
 */

const { createClient } = require('@supabase/supabase-js');
const axios = require('axios');

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_KEY;
const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const TELEGRAM_ALERT_CHAT_ID = process.env.TELEGRAM_ALERT_CHAT_ID; // Different from general notifications

const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);

/**
 * Format currency
 */
function formatCurrency(amount) {
  if (!amount) return 'Unknown';
  
  if (amount >= 1000000000) {
    return `$${(amount / 1000000000).toFixed(1)}B`;
  } else if (amount >= 1000000) {
    return `$${(amount / 1000000).toFixed(1)}M`;
  } else if (amount >= 1000) {
    return `$${(amount / 1000).toFixed(0)}K`;
  } else {
    return `$${amount.toFixed(0)}`;
  }
}

/**
 * Send Telegram message
 */
async function sendTelegramMessage(message, parseMode = 'HTML') {
  if (!TELEGRAM_BOT_TOKEN || !TELEGRAM_ALERT_CHAT_ID) {
    console.log('⚠️  Telegram credentials not configured');
    console.log('📱 Alert would have been sent:', message);
    return null;
  }

  try {
    const response = await axios.post(
      `https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`,
      {
        chat_id: TELEGRAM_ALERT_CHAT_ID,
        text: message,
        parse_mode: parseMode,
        disable_web_page_preview: false
      }
    );

    console.log('✅ Telegram alert sent successfully');
    return response.data;
  } catch (error) {
    console.error('❌ Error sending Telegram alert:', error.message);
    throw error;
  }
}

/**
 * Create high-value prospect alert message
 */
function createHighValueAlert(userData, companyData, scoreData) {
  const {
    email,
    first_name,
    last_name,
    job_title,
    created_at
  } = userData;

  const {
    company_name,
    employee_count,
    industry,
    estimated_revenue,
    location,
    linkedin_url
  } = companyData;

  const emoji = '🚨';
  const starEmoji = '⭐';
  
  let message = `${emoji} <b>HIGH VALUE PROSPECT ALERT!</b> ${emoji}\n\n`;
  
  message += `<b>🎯 Lead Score: ${scoreData.total_score}</b> (${scoreData.priority_tier})\n\n`;
  
  message += `<b>👤 Contact Information:</b>\n`;
  message += `• Name: ${first_name} ${last_name}\n`;
  message += `• Email: <code>${email}</code>\n`;
  message += `• Title: ${job_title || 'Not specified'}\n`;
  message += `• Signed up: ${new Date(created_at).toLocaleString()}\n\n`;
  
  message += `<b>🏢 Company Profile:</b>\n`;
  message += `• Name: ${company_name}\n`;
  message += `• Industry: ${industry || 'Unknown'}\n`;
  message += `• Size: <b>${employee_count} employees</b> ${starEmoji}\n`;
  message += `• Revenue: ${formatCurrency(estimated_revenue)}\n`;
  message += `• Location: ${location || 'Unknown'}\n\n`;
  
  message += `<b>💡 Why High Value?</b>\n`;
  message += `• ${scoreData.is_software_factory ? '✅' : '❌'} Software Factory\n`;
  message += `• ${employee_count >= 500 ? '✅' : '❌'} 500+ Employees\n`;
  message += `• Score Breakdown:\n`;
  message += `  - Employee: ${scoreData.breakdown.employee_score} pts\n`;
  message += `  - Industry: ${scoreData.breakdown.industry_score} pts\n`;
  message += `  - Role: ${scoreData.breakdown.role_score} pts\n`;
  message += `  - Revenue Multiplier: ${scoreData.breakdown.revenue_multiplier}x\n\n`;
  
  message += `<b>🎬 Next Actions:</b>\n`;
  message += `• Schedule demo call within 24 hours\n`;
  message += `• Send personalized onboarding email\n`;
  message += `• Add to high-touch sales sequence\n\n`;
  
  if (linkedin_url) {
    message += `<a href="${linkedin_url}">View Company on LinkedIn</a>\n\n`;
  }
  
  message += `<i>Sent by PulseB2B Lead Intelligence System</i>`;
  
  return message;
}

/**
 * Create medium priority alert
 */
function createMediumPriorityAlert(userData, companyData, scoreData) {
  const { email, first_name, last_name } = userData;
  const { company_name, employee_count } = companyData;
  
  let message = `🟡 <b>Medium Priority Lead</b>\n\n`;
  message += `<b>${first_name} ${last_name}</b> from <b>${company_name}</b>\n`;
  message += `Score: ${scoreData.total_score} | ${employee_count || '?'} employees\n`;
  message += `Email: <code>${email}</code>\n\n`;
  message += `<i>Review in sales queue</i>`;
  
  return message;
}

/**
 * Send high-value prospect alert
 */
async function sendHighValueAlert(userId) {
  console.log(`\n📢 Preparing high-value prospect alert for user: ${userId}`);

  try {
    // Get user data
    const { data: userData, error: userError } = await supabase
      .from('users')
      .select('*')
      .eq('id', userId)
      .single();

    if (userError) throw userError;

    // Get company enrichment
    const { data: companyData, error: companyError } = await supabase
      .from('company_enrichment')
      .select('*')
      .eq('user_id', userId)
      .single();

    if (companyError) throw companyError;

    // Get lead score
    const { data: scoreData, error: scoreError } = await supabase
      .from('lead_scores')
      .select('*')
      .eq('user_id', userId)
      .single();

    if (scoreError) throw scoreError;

    // Create alert message
    const message = createHighValueAlert(userData, companyData, scoreData);

    // Send to Telegram
    await sendTelegramMessage(message);

    // Log alert
    await supabase
      .from('lead_alerts')
      .insert({
        user_id: userId,
        alert_type: 'high_value_prospect',
        alert_tier: scoreData.priority_tier,
        lead_score: scoreData.total_score,
        message_sent: message,
        sent_at: new Date().toISOString()
      });

    console.log(`✅ High-value alert sent for: ${userData.email}`);
    
    return { success: true, message };
  } catch (error) {
    console.error('Error sending high-value alert:', error);
    throw error;
  }
}

/**
 * Send batch alerts for top leads (weekly digest)
 */
async function sendWeeklyDigest(limit = 10) {
  console.log(`\n📊 Preparing weekly lead digest (top ${limit})`);

  try {
    // Get top leads from last week
    const weekAgo = new Date();
    weekAgo.setDate(weekAgo.getDate() - 7);

    const { data: leads, error } = await supabase
      .from('lead_scores')
      .select(`
        *,
        users!inner(email, first_name, last_name, created_at),
        company_enrichment(company_name, employee_count, industry)
      `)
      .gte('users.created_at', weekAgo.toISOString())
      .order('total_score', { ascending: false })
      .limit(limit);

    if (error) throw error;

    if (leads.length === 0) {
      console.log('No new leads this week');
      return { success: true, count: 0 };
    }

    // Build digest message
    let message = `📈 <b>Weekly Lead Digest</b>\n`;
    message += `${new Date().toLocaleDateString()} - Top ${leads.length} Signups\n\n`;

    const highValue = leads.filter(l => l.is_high_value_prospect).length;
    const critical = leads.filter(l => l.priority_tier === 'CRITICAL').length;
    const high = leads.filter(l => l.priority_tier === 'HIGH').length;

    message += `<b>📊 Summary:</b>\n`;
    message += `• Total New Leads: ${leads.length}\n`;
    message += `• High Value Prospects: ${highValue}\n`;
    message += `• Critical Tier: ${critical}\n`;
    message += `• High Tier: ${high}\n\n`;

    message += `<b>🏆 Top Leads:</b>\n`;
    
    leads.slice(0, 5).forEach((lead, idx) => {
      const user = lead.users;
      const company = lead.company_enrichment;
      
      message += `\n${idx + 1}. <b>${user.first_name} ${user.last_name}</b>\n`;
      message += `   ${company?.company_name || 'Unknown'} (${company?.employee_count || '?'} emp)\n`;
      message += `   Score: ${lead.total_score} | ${lead.priority_tier}\n`;
      message += `   ${lead.is_high_value_prospect ? '⭐ High Value' : ''}\n`;
    });

    message += `\n\n<i>PulseB2B Weekly Lead Intelligence Report</i>`;

    // Send to Telegram
    await sendTelegramMessage(message);

    console.log(`✅ Weekly digest sent (${leads.length} leads)`);
    
    return { success: true, count: leads.length };
  } catch (error) {
    console.error('Error sending weekly digest:', error);
    throw error;
  }
}

/**
 * Test alert system
 */
async function testAlert() {
  const mockUser = {
    email: 'cto@bigtech.com',
    first_name: 'Sarah',
    last_name: 'Johnson',
    job_title: 'CTO',
    created_at: new Date().toISOString()
  };

  const mockCompany = {
    company_name: 'BigTech Software Solutions',
    employee_count: 850,
    industry: 'Software Development',
    estimated_revenue: 75000000,
    location: 'San Francisco, CA',
    linkedin_url: 'https://linkedin.com/company/bigtech'
  };

  const mockScore = {
    total_score: 285.5,
    priority_tier: 'CRITICAL',
    is_software_factory: true,
    breakdown: {
      employee_score: 90,
      industry_score: 50,
      role_score: 50,
      revenue_multiplier: 1.4,
      software_factory_bonus: 25,
      tech_stack_score: 20
    }
  };

  const message = createHighValueAlert(mockUser, mockCompany, mockScore);
  
  console.log('\n📱 Test Alert Preview:');
  console.log('═══════════════════════════════════════════════════════');
  console.log(message.replace(/<[^>]*>/g, '')); // Strip HTML for console
  console.log('═══════════════════════════════════════════════════════');
  
  if (TELEGRAM_BOT_TOKEN && TELEGRAM_ALERT_CHAT_ID) {
    console.log('\nSending test alert to Telegram...');
    await sendTelegramMessage(message);
  } else {
    console.log('\n⚠️  Set TELEGRAM_BOT_TOKEN and TELEGRAM_ALERT_CHAT_ID to send real alerts');
  }
}

/**
 * CLI Interface
 */
async function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  if (command === 'alert') {
    const userId = args[1];

    if (!userId) {
      console.error('Usage: node telegram_alert_service.js alert <userId>');
      process.exit(1);
    }

    await sendHighValueAlert(userId);
  } else if (command === 'digest') {
    const limit = parseInt(args[1]) || 10;
    await sendWeeklyDigest(limit);
  } else if (command === 'test') {
    await testAlert();
  } else {
    console.log('Telegram Alert Service');
    console.log('======================');
    console.log('');
    console.log('Commands:');
    console.log('  alert <userId>   - Send high-value prospect alert');
    console.log('  digest [limit]   - Send weekly top leads digest (default: 10)');
    console.log('  test             - Send test alert');
    console.log('');
    console.log('Environment Variables Required:');
    console.log('  TELEGRAM_BOT_TOKEN        - Your Telegram bot token');
    console.log('  TELEGRAM_ALERT_CHAT_ID    - Chat ID for high-value alerts');
    console.log('');
    console.log('Examples:');
    console.log('  node telegram_alert_service.js alert user-123');
    console.log('  node telegram_alert_service.js digest 20');
    console.log('  node telegram_alert_service.js test');
  }
}

// Export functions
module.exports = {
  sendHighValueAlert,
  sendWeeklyDigest,
  sendTelegramMessage,
  createHighValueAlert,
  testAlert
};

// Run CLI if called directly
if (require.main === module) {
  main().catch(error => {
    console.error('Error:', error);
    process.exit(1);
  });
}
