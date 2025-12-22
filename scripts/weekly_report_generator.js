/**
 * Weekly Report Generator
 * Queries Supabase for top 5 companies with highest hiring probability across all regions
 * Generates data for Sunday email teaser reports
 */

const { createClient } = require('@supabase/supabase-js');
const crypto = require('crypto');

// Initialize Supabase client
const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

// Base URL for tracking links (production domain)
const BASE_URL = process.env.BASE_URL || 'https://pulseb2b.com';

/**
 * Generate unique tracking token for user + company combination
 */
function generateTrackingToken(userId, companyId) {
  const data = `${userId}-${companyId}-${Date.now()}`;
  return crypto.createHash('sha256').update(data).digest('hex').substring(0, 16);
}

/**
 * Query top 5 companies with highest hiring probability across all regions
 */
async function getTopCompanies() {
  console.log('📊 Querying top companies from Supabase...');
  
  try {
    const { data, error } = await supabase
      .from('leads_global')
      .select(`
        id,
        company_name,
        country_code,
        pulse_score,
        hiring_probability,
        desperation_level,
        urgency,
        tech_stack,
        funding_amount,
        funding_date,
        last_seen,
        expansion_density,
        recommendation
      `)
      .order('hiring_probability', { ascending: false })
      .limit(5);

    if (error) {
      throw new Error(`Supabase query error: ${error.message}`);
    }

    if (!data || data.length === 0) {
      throw new Error('No companies found in database');
    }

    console.log(`✅ Found ${data.length} top companies`);
    return data;
  } catch (err) {
    console.error('❌ Error querying companies:', err);
    throw err;
  }
}

/**
 * Get all active users who should receive the report
 */
async function getRecipients() {
  console.log('👥 Fetching recipient list...');
  
  try {
    const { data, error } = await supabase
      .from('users')
      .select('id, email, first_name, last_name, is_premium, email_notifications_enabled')
      .eq('email_notifications_enabled', true)
      .eq('is_active', true);

    if (error) {
      throw new Error(`Recipients query error: ${error.message}`);
    }

    console.log(`✅ Found ${data?.length || 0} recipients`);
    return data || [];
  } catch (err) {
    console.error('❌ Error fetching recipients:', err);
    throw err;
  }
}

/**
 * Generate tracking URL for a user-company pair
 */
function generateTrackingUrl(userId, company, token) {
  const params = new URLSearchParams({
    t: token,
    c: company.id,
    u: userId
  });
  return `${BASE_URL}/track/click?${params.toString()}`;
}

/**
 * Store tracking tokens in database for later verification
 */
async function storeTrackingTokens(tokens) {
  console.log(`💾 Storing ${tokens.length} tracking tokens...`);
  
  try {
    const { error } = await supabase
      .from('email_tracking_tokens')
      .insert(tokens);

    if (error) {
      throw new Error(`Token storage error: ${error.message}`);
    }

    console.log('✅ Tracking tokens stored successfully');
  } catch (err) {
    console.error('❌ Error storing tokens:', err);
    throw err;
  }
}

/**
 * Format currency for display
 */
function formatCurrency(amount) {
  if (!amount) return 'Undisclosed';
  
  if (amount >= 1000000) {
    return `$${(amount / 1000000).toFixed(1)}M`;
  } else if (amount >= 1000) {
    return `$${(amount / 1000).toFixed(0)}K`;
  }
  return `$${amount}`;
}

/**
 * Get country flag emoji
 */
function getCountryFlag(countryCode) {
  const flags = {
    'US': '🇺🇸', 'CA': '🇨🇦', 'MX': '🇲🇽', 'BR': '🇧🇷', 'AR': '🇦🇷',
    'CO': '🇨🇴', 'CL': '🇨🇱', 'PE': '🇵🇪', 'UY': '🇺🇾', 'CR': '🇨🇷',
    'PA': '🇵🇦', 'GT': '🇬🇹', 'EC': '🇪🇨', 'VE': '🇻🇪', 'BO': '🇧🇴',
    'PY': '🇵🇾'
  };
  return flags[countryCode] || '🌎';
}

/**
 * Get urgency color for email styling
 */
function getUrgencyColor(desperationLevel) {
  const colors = {
    'CRITICAL': '#EF4444',
    'HIGH': '#F59E0B',
    'MODERATE': '#3B82F6',
    'LOW': '#6B7280'
  };
  return colors[desperationLevel] || colors.LOW;
}

/**
 * Generate email data for all recipients
 */
async function generateEmailData() {
  console.log('🎯 Generating email data...\n');
  
  try {
    // Get top companies and recipients
    const [companies, recipients] = await Promise.all([
      getTopCompanies(),
      getRecipients()
    ]);

    if (recipients.length === 0) {
      console.warn('⚠️  No recipients found. Skipping email generation.');
      return { emails: [], tokens: [] };
    }

    const emails = [];
    const tokens = [];
    const reportDate = new Date().toLocaleDateString('en-US', { 
      weekday: 'long', 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });

    // Generate personalized email data for each recipient
    for (const recipient of recipients) {
      const companiesWithTracking = companies.map(company => {
        const token = generateTrackingToken(recipient.id, company.id);
        const trackingUrl = generateTrackingUrl(recipient.id, company, token);
        
        // Store token for verification
        tokens.push({
          token,
          user_id: recipient.id,
          company_id: company.id,
          created_at: new Date().toISOString(),
          expires_at: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString() // 30 days
        });

        return {
          ...company,
          trackingUrl,
          flag: getCountryFlag(company.country_code),
          urgencyColor: getUrgencyColor(company.desperation_level),
          fundingFormatted: formatCurrency(company.funding_amount),
          isPremiumContent: company.pulse_score >= 70 && !recipient.is_premium
        };
      });

      emails.push({
        to: recipient.email,
        firstName: recipient.first_name || 'Valued User',
        isPremium: recipient.is_premium,
        reportDate,
        companies: companiesWithTracking
      });
    }

    // Store all tracking tokens
    await storeTrackingTokens(tokens);

    console.log(`\n✅ Generated ${emails.length} personalized emails`);
    console.log(`📊 Report date: ${reportDate}`);
    console.log(`🔗 Generated ${tokens.length} tracking links\n`);

    return { emails, tokens };
  } catch (err) {
    console.error('❌ Error generating email data:', err);
    throw err;
  }
}

/**
 * Get analytics summary for logging
 */
async function getAnalyticsSummary() {
  try {
    const { data, error } = await supabase
      .from('leads_global')
      .select('country_code, desperation_level')
      .order('hiring_probability', { ascending: false })
      .limit(5);

    if (error || !data) return 'N/A';

    const countries = [...new Set(data.map(c => c.country_code))];
    const criticalCount = data.filter(c => c.desperation_level === 'CRITICAL').length;

    return `${countries.length} countries, ${criticalCount} critical`;
  } catch {
    return 'N/A';
  }
}

/**
 * Main execution function
 */
async function main() {
  console.log('═══════════════════════════════════════════════');
  console.log('📧 PulseB2B Weekly Report Generator');
  console.log('═══════════════════════════════════════════════\n');

  try {
    // Validate environment variables
    if (!supabaseUrl || !supabaseKey) {
      throw new Error('Missing Supabase credentials. Set SUPABASE_URL and SUPABASE_SERVICE_KEY');
    }

    // Generate email data
    const { emails, tokens } = await generateEmailData();

    if (emails.length === 0) {
      console.log('⏭️  No emails to send. Exiting.\n');
      return { success: true, emailCount: 0 };
    }

    // Get analytics
    const analytics = await getAnalyticsSummary();

    console.log('📈 Report Summary:');
    console.log(`   Recipients: ${emails.length}`);
    console.log(`   Tracking Links: ${tokens.length}`);
    console.log(`   Top Companies: ${analytics}`);
    console.log('\n✅ Email data generation complete!');
    console.log('📤 Ready to send via SendGrid/Mailersend\n');

    return {
      success: true,
      emailCount: emails.length,
      tokenCount: tokens.length,
      emails
    };
  } catch (err) {
    console.error('\n❌ Report generation failed:', err.message);
    throw err;
  }
}

// Export for use in other scripts
module.exports = {
  generateEmailData,
  generateTrackingToken,
  generateTrackingUrl,
  getTopCompanies,
  getRecipients,
  formatCurrency,
  getCountryFlag
};

// Run if executed directly
if (require.main === module) {
  main()
    .then(result => {
      console.log('═══════════════════════════════════════════════\n');
      process.exit(0);
    })
    .catch(err => {
      console.error('\n💥 Fatal error:', err);
      process.exit(1);
    });
}
