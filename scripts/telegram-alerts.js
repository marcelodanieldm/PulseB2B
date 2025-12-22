/**
 * Telegram Alerts - High Priority Notifications
 * ==============================================
 * Sends alerts for companies with 90+ Pulse score.
 * Simple webhook approach using axios.
 * 
 * Alert Frequency: Once per company per 24 hours (prevents spam)
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

// Configuration
const CONFIG = {
  TELEGRAM_BOT_TOKEN: process.env.TELEGRAM_BOT_TOKEN,
  TELEGRAM_CHAT_ID: process.env.TELEGRAM_CHAT_ID,
  SCORE_THRESHOLD: 90,
  MAX_ALERTS: 10,  // Max 10 alerts per run
  ALERT_LOG: path.join(__dirname, '..', 'data', 'output', 'alert_log.json'),
  REPORTS_DIR: path.join(__dirname, '..', 'data', 'output', 'pulse_reports')
};

class TelegramAlerts {
  constructor() {
    if (!CONFIG.TELEGRAM_BOT_TOKEN || !CONFIG.TELEGRAM_CHAT_ID) {
      throw new Error('Telegram credentials not configured');
    }

    this.alertLog = this.loadAlertLog();
    this.sentCount = 0;
  }

  /**
   * Main execution flow
   */
  async run() {
    console.log('📢 Telegram Alerts - Checking for high-priority leads...\n');

    // Load critical opportunities
    const opportunities = await this.loadCriticalOpportunities();
    
    if (opportunities.length === 0) {
      console.log('ℹ️  No companies with 90+ score');
      return;
    }

    console.log(`🔥 Found ${opportunities.length} critical opportunities\n`);

    // Filter out already alerted companies
    const newOpportunities = opportunities.filter(opp => 
      !this.wasRecentlyAlerted(opp.company_name)
    );

    console.log(`📊 ${newOpportunities.length} new opportunities (not alerted in 24h)`);

    if (newOpportunities.length === 0) {
      console.log('✅ All high-priority leads already alerted');
      return;
    }

    // Send alerts (max 10)
    const toAlert = newOpportunities.slice(0, CONFIG.MAX_ALERTS);
    
    for (const opportunity of toAlert) {
      await this.sendAlert(opportunity);
      await this.delay(1000);  // 1 second between alerts
    }

    // Save alert log
    this.saveAlertLog();

    // Print summary
    this.printSummary();
  }

  /**
   * Load critical opportunities from Pulse reports
   */
  async loadCriticalOpportunities() {
    const files = fs.readdirSync(CONFIG.REPORTS_DIR)
      .filter(f => f.startsWith('critical_opportunities_') && f.endsWith('.csv'))
      .sort()
      .reverse();  // Most recent first

    if (files.length === 0) {
      return [];
    }

    const latestFile = path.join(CONFIG.REPORTS_DIR, files[0]);
    const content = fs.readFileSync(latestFile, 'utf-8');
    const lines = content.split('\n');
    const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''));

    const opportunities = [];

    for (let i = 1; i < lines.length; i++) {
      const line = lines[i].trim();
      if (!line) continue;

      const values = this.parseCSVLine(line);
      const record = {};
      
      headers.forEach((header, index) => {
        record[header] = values[index];
      });

      // Only include 90+ score
      const score = parseFloat(record.pulse_score) || 0;
      if (score >= CONFIG.SCORE_THRESHOLD) {
        opportunities.push(record);
      }
    }

    return opportunities.sort((a, b) => b.pulse_score - a.pulse_score);
  }

  /**
   * Send Telegram alert
   */
  async sendAlert(opportunity) {
    const message = this.formatAlertMessage(opportunity);

    try {
      await this.sendTelegramMessage(message);
      this.sentCount++;
      this.logAlert(opportunity.company_name);
      console.log(`  ✅ Alert sent: ${opportunity.company_name} (${opportunity.pulse_score} pts)`);
    } catch (error) {
      console.log(`  ❌ Failed to send alert: ${error.message}`);
    }
  }

  /**
   * Format alert message with HTML
   */
  formatAlertMessage(opp) {
    const emoji = opp.pulse_score >= 95 ? '🔥🔥🔥' : '🔥🔥';
    
    return `${emoji} <b>CRITICAL OPPORTUNITY</b> ${emoji}

<b>${opp.company_name}</b>
Pulse Score: <b>${opp.pulse_score}/100</b>
Desperation: <b>${opp.desperation_level}</b>

📊 Signals:
• Expansion Density: ${opp.expansion_density || 'N/A'}%
• Tech Stack: ${opp.tech_diversity_score || 0} technologies
• Hiring Probability: ${opp.hiring_probability || 0}%

💡 <b>${opp.recommendation || 'Contact immediately'}</b>

🔗 ${opp.website_url || 'N/A'}

⏰ <i>Detected: ${new Date().toLocaleString('en-US', { timeZone: 'America/New_York' })} ET</i>`;
  }

  /**
   * Send message via Telegram API
   */
  async sendTelegramMessage(text) {
    const url = `https://api.telegram.org/bot${CONFIG.TELEGRAM_BOT_TOKEN}/sendMessage`;
    
    const payload = JSON.stringify({
      chat_id: CONFIG.TELEGRAM_CHAT_ID,
      text: text,
      parse_mode: 'HTML',
      disable_web_page_preview: false
    });

    return new Promise((resolve, reject) => {
      const options = {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Content-Length': Buffer.byteLength(payload)
        }
      };

      const req = https.request(url, options, (res) => {
        let data = '';

        res.on('data', (chunk) => {
          data += chunk;
        });

        res.on('end', () => {
          if (res.statusCode === 200) {
            resolve(JSON.parse(data));
          } else {
            reject(new Error(`Telegram API returned ${res.statusCode}`));
          }
        });
      });

      req.on('error', (error) => {
        reject(error);
      });

      req.write(payload);
      req.end();
    });
  }

  /**
   * Check if company was alerted in last 24 hours
   */
  wasRecentlyAlerted(companyName) {
    const key = companyName.toLowerCase().trim();
    if (!this.alertLog[key]) return false;

    const lastAlert = new Date(this.alertLog[key]);
    const hoursSince = (Date.now() - lastAlert.getTime()) / (1000 * 60 * 60);
    
    return hoursSince < 24;
  }

  /**
   * Log alert for deduplication
   */
  logAlert(companyName) {
    const key = companyName.toLowerCase().trim();
    this.alertLog[key] = new Date().toISOString();
  }

  /**
   * Load alert log from disk
   */
  loadAlertLog() {
    if (!fs.existsSync(CONFIG.ALERT_LOG)) {
      return {};
    }

    try {
      const content = fs.readFileSync(CONFIG.ALERT_LOG, 'utf-8');
      return JSON.parse(content);
    } catch (error) {
      console.log('⚠️  Could not load alert log, starting fresh');
      return {};
    }
  }

  /**
   * Save alert log to disk
   */
  saveAlertLog() {
    const dir = path.dirname(CONFIG.ALERT_LOG);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    fs.writeFileSync(
      CONFIG.ALERT_LOG,
      JSON.stringify(this.alertLog, null, 2),
      'utf-8'
    );
  }

  /**
   * Parse CSV line
   */
  parseCSVLine(line) {
    const values = [];
    let current = '';
    let inQuotes = false;

    for (let i = 0; i < line.length; i++) {
      const char = line[i];

      if (char === '"') {
        inQuotes = !inQuotes;
      } else if (char === ',' && !inQuotes) {
        values.push(current.trim());
        current = '';
      } else {
        current += char;
      }
    }

    values.push(current.trim());
    return values;
  }

  /**
   * Print summary
   */
  printSummary() {
    console.log('\n' + '='.repeat(60));
    console.log('📊 TELEGRAM ALERTS SUMMARY');
    console.log('='.repeat(60));
    console.log(`Alerts Sent: ${this.sentCount}`);
    console.log(`Total Logged: ${Object.keys(this.alertLog).length} companies`);
    console.log('='.repeat(60));
  }

  /**
   * Delay helper
   */
  async delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// ============================================
// MAIN EXECUTION
// ============================================
if (require.main === module) {
  const alerts = new TelegramAlerts();
  
  alerts.run()
    .then(() => {
      console.log('\n✅ Telegram alerts completed');
      process.exit(0);
    })
    .catch((error) => {
      console.error('\n❌ Telegram alerts failed:', error);
      process.exit(1);
    });
}

module.exports = TelegramAlerts;
