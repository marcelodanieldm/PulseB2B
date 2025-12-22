/**
 * Click Tracker API Endpoint
 * Records when users click on company links in email reports
 * Validates tracking tokens and redirects to company profile
 */

const { createClient } = require('@supabase/supabase-js');

// Initialize Supabase client
const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

// Base URL for redirects
const DASHBOARD_URL = process.env.DASHBOARD_URL || 'https://pulseb2b.com/dashboard';

/**
 * Validate tracking token
 */
async function validateToken(token, userId, companyId) {
  try {
    const { data, error } = await supabase
      .from('email_tracking_tokens')
      .select('*')
      .eq('token', token)
      .eq('user_id', userId)
      .eq('company_id', companyId)
      .single();

    if (error || !data) {
      console.error('Invalid token:', error);
      return { valid: false, reason: 'Token not found' };
    }

    // Check if token has expired
    const expiresAt = new Date(data.expires_at);
    if (expiresAt < new Date()) {
      return { valid: false, reason: 'Token expired' };
    }

    return { valid: true, token: data };
  } catch (err) {
    console.error('Token validation error:', err);
    return { valid: false, reason: err.message };
  }
}

/**
 * Record click event in database
 */
async function recordClick(userId, companyId, token, metadata = {}) {
  try {
    const clickData = {
      user_id: userId,
      company_id: companyId,
      tracking_token: token,
      clicked_at: new Date().toISOString(),
      ip_address: metadata.ipAddress || null,
      user_agent: metadata.userAgent || null,
      referrer: metadata.referrer || null
    };

    const { error } = await supabase
      .from('email_clicks')
      .insert([clickData]);

    if (error) {
      console.error('Error recording click:', error);
      return { success: false, error: error.message };
    }

    console.log(`✅ Click recorded: User ${userId} → Company ${companyId}`);
    return { success: true };
  } catch (err) {
    console.error('Click recording error:', err);
    return { success: false, error: err.message };
  }
}

/**
 * Get click analytics for a company
 */
async function getCompanyClickAnalytics(companyId, days = 30) {
  try {
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - days);

    const { data, error } = await supabase
      .from('email_clicks')
      .select('*')
      .eq('company_id', companyId)
      .gte('clicked_at', startDate.toISOString());

    if (error) {
      throw new Error(error.message);
    }

    return {
      totalClicks: data.length,
      uniqueUsers: [...new Set(data.map(c => c.user_id))].length,
      clicks: data
    };
  } catch (err) {
    console.error('Analytics error:', err);
    return null;
  }
}

/**
 * Get click analytics for a user
 */
async function getUserClickHistory(userId, limit = 50) {
  try {
    const { data, error } = await supabase
      .from('email_clicks')
      .select(`
        *,
        company:leads_global(company_name, country_code, pulse_score)
      `)
      .eq('user_id', userId)
      .order('clicked_at', { ascending: false })
      .limit(limit);

    if (error) {
      throw new Error(error.message);
    }

    return data;
  } catch (err) {
    console.error('User history error:', err);
    return [];
  }
}

/**
 * Handle tracking redirect (for web endpoint)
 */
async function handleTrackingRedirect(req, res) {
  try {
    // Extract query parameters
    const { t: token, c: companyId, u: userId } = req.query;

    if (!token || !companyId || !userId) {
      return res.status(400).json({ 
        error: 'Missing required parameters (t, c, u)' 
      });
    }

    // Validate token
    const validation = await validateToken(token, userId, companyId);
    
    if (!validation.valid) {
      console.warn(`Invalid tracking attempt: ${validation.reason}`);
      // Still redirect but don't record click
      return res.redirect(`${DASHBOARD_URL}/companies/${companyId}?error=invalid_link`);
    }

    // Extract metadata
    const metadata = {
      ipAddress: req.ip || req.headers['x-forwarded-for'] || req.connection.remoteAddress,
      userAgent: req.headers['user-agent'],
      referrer: req.headers['referer'] || req.headers['referrer']
    };

    // Record click (async, don't wait)
    recordClick(userId, companyId, token, metadata).catch(err => {
      console.error('Failed to record click:', err);
    });

    // Redirect to company profile
    res.redirect(`${DASHBOARD_URL}/companies/${companyId}?utm_source=email&utm_campaign=weekly_report`);
  } catch (err) {
    console.error('Tracking redirect error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
}

/**
 * Generate click analytics report
 */
async function generateClickReport(startDate, endDate) {
  try {
    const { data, error } = await supabase
      .from('email_clicks')
      .select(`
        *,
        user:users(email, first_name, last_name),
        company:leads_global(company_name, country_code)
      `)
      .gte('clicked_at', startDate.toISOString())
      .lte('clicked_at', endDate.toISOString())
      .order('clicked_at', { ascending: false });

    if (error) {
      throw new Error(error.message);
    }

    // Calculate metrics
    const totalClicks = data.length;
    const uniqueUsers = [...new Set(data.map(c => c.user_id))].length;
    const uniqueCompanies = [...new Set(data.map(c => c.company_id))].length;
    
    // Top clicked companies
    const companyClicks = {};
    data.forEach(click => {
      const cid = click.company_id;
      companyClicks[cid] = (companyClicks[cid] || 0) + 1;
    });
    
    const topCompanies = Object.entries(companyClicks)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([companyId, clicks]) => {
        const company = data.find(c => c.company_id === companyId)?.company;
        return { companyId, companyName: company?.company_name || 'Unknown', clicks };
      });

    // Click rate by day
    const clicksByDay = {};
    data.forEach(click => {
      const day = click.clicked_at.split('T')[0];
      clicksByDay[day] = (clicksByDay[day] || 0) + 1;
    });

    return {
      totalClicks,
      uniqueUsers,
      uniqueCompanies,
      clickThroughRate: totalClicks > 0 ? (uniqueUsers / totalClicks * 100).toFixed(2) : 0,
      topCompanies,
      clicksByDay,
      rawData: data
    };
  } catch (err) {
    console.error('Report generation error:', err);
    return null;
  }
}

/**
 * Clean up expired tokens
 */
async function cleanupExpiredTokens() {
  try {
    const { data, error } = await supabase
      .from('email_tracking_tokens')
      .delete()
      .lt('expires_at', new Date().toISOString());

    if (error) {
      throw new Error(error.message);
    }

    console.log(`✅ Cleaned up expired tokens`);
    return { success: true };
  } catch (err) {
    console.error('Cleanup error:', err);
    return { success: false, error: err.message };
  }
}

// Export functions
module.exports = {
  validateToken,
  recordClick,
  getCompanyClickAnalytics,
  getUserClickHistory,
  handleTrackingRedirect,
  generateClickReport,
  cleanupExpiredTokens
};

// CLI usage for testing
if (require.main === module) {
  const command = process.argv[2];

  if (command === 'cleanup') {
    console.log('🧹 Cleaning up expired tokens...');
    cleanupExpiredTokens()
      .then(() => process.exit(0))
      .catch(err => {
        console.error('Failed:', err);
        process.exit(1);
      });
  } else if (command === 'report') {
    const days = parseInt(process.argv[3]) || 7;
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - days);

    console.log(`📊 Generating click report (last ${days} days)...`);
    generateClickReport(startDate, endDate)
      .then(report => {
        if (report) {
          console.log('\n📈 Report Summary:');
          console.log(`   Total Clicks: ${report.totalClicks}`);
          console.log(`   Unique Users: ${report.uniqueUsers}`);
          console.log(`   Unique Companies: ${report.uniqueCompanies}`);
          console.log(`   CTR: ${report.clickThroughRate}%`);
          console.log('\n🏆 Top Companies:');
          report.topCompanies.forEach((c, i) => {
            console.log(`   ${i + 1}. ${c.companyName} (${c.clicks} clicks)`);
          });
        }
        process.exit(0);
      })
      .catch(err => {
        console.error('Failed:', err);
        process.exit(1);
      });
  } else {
    console.log('Usage:');
    console.log('  node click_tracker.js cleanup          - Remove expired tokens');
    console.log('  node click_tracker.js report [days]    - Generate analytics report');
    process.exit(0);
  }
}
