/**
 * SendGrid Email Mailer
 * Sends weekly teaser reports via SendGrid API (Free Tier: 100 emails/day)
 * Handles batch sending, template rendering, and error tracking
 */

const sgMail = require('@sendgrid/mail');
const fs = require('fs').promises;
const path = require('path');
const Handlebars = require('handlebars');
const { generateEmailData } = require('./weekly_report_generator');

// Initialize SendGrid
const SENDGRID_API_KEY = process.env.SENDGRID_API_KEY;
const FROM_EMAIL = process.env.FROM_EMAIL || 'reports@pulseb2b.com';
const FROM_NAME = process.env.FROM_NAME || 'PulseB2B Intelligence';
const BASE_URL = process.env.BASE_URL || 'https://pulseb2b.com';

if (SENDGRID_API_KEY) {
  sgMail.setApiKey(SENDGRID_API_KEY);
}

// Register Handlebars helpers
Handlebars.registerHelper('eq', function(a, b) {
  return a === b;
});

Handlebars.registerHelper('unless', function(conditional, options) {
  if (!conditional) {
    return options.fn(this);
  }
  return options.inverse(this);
});

/**
 * Load and compile email template
 */
async function loadTemplate() {
  try {
    const templatePath = path.join(__dirname, '..', 'templates', 'email_template_teaser.html');
    const templateContent = await fs.readFile(templatePath, 'utf-8');
    return Handlebars.compile(templateContent);
  } catch (err) {
    console.error('❌ Error loading template:', err);
    throw new Error('Failed to load email template');
  }
}

/**
 * Render email HTML for a specific recipient
 */
function renderEmail(template, emailData) {
  try {
    // Add BASE_URL to context
    const context = {
      ...emailData,
      BASE_URL,
      unsubscribeToken: generateUnsubscribeToken(emailData.to)
    };
    
    return template(context);
  } catch (err) {
    console.error('❌ Error rendering email:', err);
    throw err;
  }
}

/**
 * Generate unsubscribe token (simple hash for demo)
 */
function generateUnsubscribeToken(email) {
  const crypto = require('crypto');
  return crypto.createHash('sha256').update(email + 'UNSUBSCRIBE_SALT').digest('hex').substring(0, 16);
}

/**
 * Send single email via SendGrid
 */
async function sendEmail(to, subject, html) {
  const msg = {
    to,
    from: {
      email: FROM_EMAIL,
      name: FROM_NAME
    },
    subject,
    html,
    trackingSettings: {
      clickTracking: {
        enable: false // We use our own click tracking
      },
      openTracking: {
        enable: true
      }
    },
    categories: ['weekly_report', 'teaser']
  };

  try {
    await sgMail.send(msg);
    return { success: true, to };
  } catch (error) {
    console.error(`❌ Failed to send to ${to}:`, error.response?.body || error.message);
    return { success: false, to, error: error.message };
  }
}

/**
 * Send emails in batches to respect rate limits
 */
async function sendBatch(emails, template, batchSize = 10, delayMs = 1000) {
  console.log(`📤 Sending ${emails.length} emails in batches of ${batchSize}...`);
  
  const results = {
    sent: [],
    failed: [],
    total: emails.length
  };

  const subject = `🎯 Your Weekly Hiring Intelligence - Top 5 Opportunities`;

  for (let i = 0; i < emails.length; i += batchSize) {
    const batch = emails.slice(i, i + batchSize);
    const batchNumber = Math.floor(i / batchSize) + 1;
    const totalBatches = Math.ceil(emails.length / batchSize);

    console.log(`\n📨 Processing batch ${batchNumber}/${totalBatches} (${batch.length} emails)...`);

    // Send batch concurrently
    const batchPromises = batch.map(async (emailData) => {
      try {
        const html = renderEmail(template, emailData);
        const result = await sendEmail(emailData.to, subject, html);
        
        if (result.success) {
          console.log(`  ✅ ${emailData.to}`);
          results.sent.push(result.to);
        } else {
          console.log(`  ❌ ${emailData.to}`);
          results.failed.push({ to: result.to, error: result.error });
        }
        
        return result;
      } catch (err) {
        console.log(`  ❌ ${emailData.to} - ${err.message}`);
        results.failed.push({ to: emailData.to, error: err.message });
        return { success: false, to: emailData.to };
      }
    });

    await Promise.all(batchPromises);

    // Delay between batches (except for last batch)
    if (i + batchSize < emails.length) {
      console.log(`⏳ Waiting ${delayMs}ms before next batch...`);
      await new Promise(resolve => setTimeout(resolve, delayMs));
    }
  }

  return results;
}

/**
 * Send test email to verify setup
 */
async function sendTestEmail(testRecipient) {
  console.log(`🧪 Sending test email to ${testRecipient}...\n`);

  try {
    // Load template
    const template = await loadTemplate();

    // Mock data for test
    const testData = {
      to: testRecipient,
      firstName: 'Test User',
      isPremium: false,
      reportDate: new Date().toLocaleDateString('en-US', { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      }),
      companies: [
        {
          company_name: 'TechCorp Demo',
          country_code: 'US',
          flag: '🇺🇸',
          pulse_score: 92,
          hiring_probability: 87,
          desperation_level: 'CRITICAL',
          urgency: 'Immediate',
          urgencyColor: '#EF4444',
          expansion_density: 85,
          fundingFormatted: '$50M',
          tech_stack: ['React', 'Node.js', 'AWS'],
          trackingUrl: `${BASE_URL}/track/click?t=test123&c=demo1&u=test`,
          isPremiumContent: false
        },
        {
          company_name: 'DataFlow Brasil',
          country_code: 'BR',
          flag: '🇧🇷',
          pulse_score: 88,
          hiring_probability: 82,
          desperation_level: 'HIGH',
          urgency: 'High',
          urgencyColor: '#F59E0B',
          expansion_density: 78,
          fundingFormatted: '$30M',
          tech_stack: ['Python', 'Django', 'PostgreSQL'],
          trackingUrl: `${BASE_URL}/track/click?t=test456&c=demo2&u=test`,
          isPremiumContent: true
        }
      ]
    };

    const html = renderEmail(template, testData);
    const subject = `🧪 TEST - Your Weekly Hiring Intelligence`;

    const result = await sendEmail(testRecipient, subject, html);

    if (result.success) {
      console.log('✅ Test email sent successfully!');
      console.log('📬 Check your inbox at:', testRecipient);
    } else {
      console.log('❌ Test email failed:', result.error);
    }

    return result;
  } catch (err) {
    console.error('❌ Test email error:', err);
    throw err;
  }
}

/**
 * Main execution function
 */
async function main() {
  console.log('═══════════════════════════════════════════════');
  console.log('📧 PulseB2B SendGrid Email Sender');
  console.log('═══════════════════════════════════════════════\n');

  try {
    // Validate SendGrid API key
    if (!SENDGRID_API_KEY) {
      throw new Error('Missing SENDGRID_API_KEY environment variable');
    }

    // Check if this is a test run
    const isTest = process.argv.includes('--test');
    const testEmail = process.argv.find(arg => arg.startsWith('--email='))?.split('=')[1];

    if (isTest && testEmail) {
      await sendTestEmail(testEmail);
      return;
    }

    // Generate email data
    console.log('📊 Generating email data...');
    const { emails } = await generateEmailData();

    if (emails.length === 0) {
      console.log('⏭️  No recipients found. Exiting.\n');
      return { success: true, sent: 0 };
    }

    // Load template
    console.log('📄 Loading email template...');
    const template = await loadTemplate();
    console.log('✅ Template loaded\n');

    // Send emails
    const results = await sendBatch(emails, template, 10, 1000);

    // Print summary
    console.log('\n═══════════════════════════════════════════════');
    console.log('📊 Email Campaign Summary:');
    console.log(`   Total: ${results.total}`);
    console.log(`   ✅ Sent: ${results.sent.length}`);
    console.log(`   ❌ Failed: ${results.failed.length}`);
    console.log(`   Success Rate: ${((results.sent.length / results.total) * 100).toFixed(1)}%`);

    if (results.failed.length > 0) {
      console.log('\n❌ Failed Recipients:');
      results.failed.forEach(f => {
        console.log(`   - ${f.to}: ${f.error}`);
      });
    }

    console.log('═══════════════════════════════════════════════\n');

    // Exit with error if too many failures
    if (results.failed.length > results.total * 0.2) {
      throw new Error('More than 20% of emails failed. Check SendGrid configuration.');
    }

    return results;
  } catch (err) {
    console.error('\n❌ Email sending failed:', err.message);
    throw err;
  }
}

// Export for use in other scripts
module.exports = {
  sendEmail,
  sendBatch,
  sendTestEmail,
  loadTemplate,
  renderEmail
};

// Run if executed directly
if (require.main === module) {
  main()
    .then(() => {
      console.log('✅ Email campaign completed successfully');
      process.exit(0);
    })
    .catch(err => {
      console.error('💥 Fatal error:', err);
      process.exit(1);
    });
}
