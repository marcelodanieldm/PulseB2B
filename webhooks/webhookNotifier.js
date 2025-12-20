/**
 * Webhook Notifier
 * Envía notificaciones en tiempo real cuando se detectan nuevos jobs
 */

const axios = require('axios');
const { createClient } = require('@supabase/supabase-js');

class WebhookNotifier {
  constructor() {
    this.supabase = createClient(
      process.env.SUPABASE_URL,
      process.env.SUPABASE_KEY
    );
  }

  /**
   * Notifica sobre nuevos jobs detectados
   */
  async notifyNewJobs(company, newJobs) {
    if (newJobs.length === 0) {
      return;
    }

    console.log(`📢 Notifying ${newJobs.length} new jobs for ${company.name}`);

    // Obtener canales de notificación configurados
    const channels = company.notification_channels || ['webhook'];

    const promises = [];

    // Webhook personalizado
    if (channels.includes('webhook') && company.webhook_url) {
      promises.push(this.sendWebhook(company, newJobs));
    }

    // Slack
    if (channels.includes('slack') && process.env.SLACK_WEBHOOK_URL) {
      promises.push(this.sendSlackNotification(company, newJobs));
    }

    // Discord
    if (channels.includes('discord') && process.env.DISCORD_WEBHOOK_URL) {
      promises.push(this.sendDiscordNotification(company, newJobs));
    }

    // Email (via Supabase Edge Functions o SendGrid)
    if (channels.includes('email')) {
      promises.push(this.sendEmailNotification(company, newJobs));
    }

    // Telegram
    if (channels.includes('telegram') && process.env.TELEGRAM_BOT_TOKEN) {
      promises.push(this.sendTelegramNotification(company, newJobs));
    }

    // Ejecutar todas las notificaciones en paralelo
    await Promise.allSettled(promises);

    // Registrar notificación en la base de datos
    await this.logNotification(company.id, newJobs.length);
  }

  /**
   * Envía webhook personalizado
   */
  async sendWebhook(company, newJobs) {
    try {
      const payload = {
        event: 'new_jobs_detected',
        timestamp: new Date().toISOString(),
        company: {
          id: company.id,
          name: company.name,
          careers_url: company.careers_url
        },
        jobs: newJobs.map(job => ({
          title: job.title,
          link: job.link,
          location: job.location,
          department: job.department,
          scraped_at: job.scraped_at
        })),
        summary: {
          total_new_jobs: newJobs.length,
          locations: [...new Set(newJobs.map(j => j.location).filter(Boolean))],
          departments: [...new Set(newJobs.map(j => j.department).filter(Boolean))]
        }
      };

      const response = await axios.post(company.webhook_url, payload, {
        headers: {
          'Content-Type': 'application/json',
          'User-Agent': 'PulseB2B-Webhook/1.0'
        },
        timeout: 10000
      });

      console.log(`✓ Webhook sent to ${company.webhook_url}: ${response.status}`);
      return { success: true, channel: 'webhook' };

    } catch (error) {
      console.error(`❌ Webhook error for ${company.name}:`, error.message);
      return { success: false, channel: 'webhook', error: error.message };
    }
  }

  /**
   * Envía notificación a Slack
   */
  async sendSlackNotification(company, newJobs) {
    try {
      const jobsList = newJobs
        .slice(0, 5) // Primeros 5
        .map(job => `• <${job.link}|${job.title}> ${job.location ? `(${job.location})` : ''}`)
        .join('\n');

      const payload = {
        text: `🚀 *${newJobs.length} New Job${newJobs.length > 1 ? 's' : ''} at ${company.name}*`,
        blocks: [
          {
            type: 'header',
            text: {
              type: 'plain_text',
              text: `🚀 ${newJobs.length} New Job${newJobs.length > 1 ? 's' : ''} Detected`
            }
          },
          {
            type: 'section',
            text: {
              type: 'mrkdwn',
              text: `*Company:* <${company.careers_url}|${company.name}>`
            }
          },
          {
            type: 'section',
            text: {
              type: 'mrkdwn',
              text: `*Jobs:*\n${jobsList}`
            }
          },
          ...(newJobs.length > 5 ? [{
            type: 'context',
            elements: [{
              type: 'mrkdwn',
              text: `_...and ${newJobs.length - 5} more_`
            }]
          }] : []),
          {
            type: 'actions',
            elements: [
              {
                type: 'button',
                text: { type: 'plain_text', text: 'View All Jobs' },
                url: company.careers_url,
                style: 'primary'
              }
            ]
          }
        ]
      };

      const response = await axios.post(process.env.SLACK_WEBHOOK_URL, payload, {
        timeout: 10000
      });

      console.log(`✓ Slack notification sent: ${response.status}`);
      return { success: true, channel: 'slack' };

    } catch (error) {
      console.error(`❌ Slack error:`, error.message);
      return { success: false, channel: 'slack', error: error.message };
    }
  }

  /**
   * Envía notificación a Discord
   */
  async sendDiscordNotification(company, newJobs) {
    try {
      const jobsList = newJobs
        .slice(0, 10)
        .map(job => `• [${job.title}](${job.link}) ${job.location ? `- ${job.location}` : ''}`)
        .join('\n');

      const payload = {
        username: 'PulseB2B Job Alert',
        avatar_url: 'https://cdn-icons-png.flaticon.com/512/2910/2910791.png',
        embeds: [
          {
            title: `🚀 ${newJobs.length} New Job${newJobs.length > 1 ? 's' : ''} at ${company.name}`,
            url: company.careers_url,
            description: jobsList + (newJobs.length > 10 ? `\n\n_...and ${newJobs.length - 10} more_` : ''),
            color: 0x00ff00,
            timestamp: new Date().toISOString(),
            footer: {
              text: 'PulseB2B Market Intelligence'
            }
          }
        ]
      };

      const response = await axios.post(process.env.DISCORD_WEBHOOK_URL, payload, {
        timeout: 10000
      });

      console.log(`✓ Discord notification sent: ${response.status}`);
      return { success: true, channel: 'discord' };

    } catch (error) {
      console.error(`❌ Discord error:`, error.message);
      return { success: false, channel: 'discord', error: error.message };
    }
  }

  /**
   * Envía notificación por Email
   */
  async sendEmailNotification(company, newJobs) {
    try {
      // Usando Supabase Edge Function o SendGrid
      const emailData = {
        to: process.env.NOTIFICATION_EMAIL,
        subject: `${newJobs.length} New Job${newJobs.length > 1 ? 's' : ''} at ${company.name}`,
        html: this.generateEmailHTML(company, newJobs)
      };

      // Opción 1: Supabase Edge Function
      const { data, error } = await this.supabase.functions.invoke('send-email', {
        body: emailData
      });

      if (error) throw error;

      console.log(`✓ Email notification sent`);
      return { success: true, channel: 'email' };

    } catch (error) {
      console.error(`❌ Email error:`, error.message);
      return { success: false, channel: 'email', error: error.message };
    }
  }

  /**
   * Envía notificación a Telegram
   */
  async sendTelegramNotification(company, newJobs) {
    try {
      const jobsList = newJobs
        .slice(0, 5)
        .map(job => `• <a href="${job.link}">${job.title}</a> ${job.location ? `(${job.location})` : ''}`)
        .join('\n');

      const message = `
🚀 <b>${newJobs.length} New Job${newJobs.length > 1 ? 's' : ''} at ${company.name}</b>

${jobsList}
${newJobs.length > 5 ? `\n<i>...and ${newJobs.length - 5} more</i>` : ''}

<a href="${company.careers_url}">View All Jobs →</a>
      `.trim();

      const response = await axios.post(
        `https://api.telegram.org/bot${process.env.TELEGRAM_BOT_TOKEN}/sendMessage`,
        {
          chat_id: process.env.TELEGRAM_CHAT_ID,
          text: message,
          parse_mode: 'HTML',
          disable_web_page_preview: false
        },
        { timeout: 10000 }
      );

      console.log(`✓ Telegram notification sent`);
      return { success: true, channel: 'telegram' };

    } catch (error) {
      console.error(`❌ Telegram error:`, error.message);
      return { success: false, channel: 'telegram', error: error.message };
    }
  }

  /**
   * Genera HTML para email
   */
  generateEmailHTML(company, newJobs) {
    const jobsHTML = newJobs
      .map(job => `
        <div style="margin: 15px 0; padding: 15px; border-left: 3px solid #4CAF50; background: #f9f9f9;">
          <h3 style="margin: 0 0 5px 0;"><a href="${job.link}" style="color: #2196F3; text-decoration: none;">${job.title}</a></h3>
          ${job.location ? `<p style="margin: 5px 0; color: #666;">📍 ${job.location}</p>` : ''}
          ${job.department ? `<p style="margin: 5px 0; color: #666;">🏢 ${job.department}</p>` : ''}
        </div>
      `)
      .join('');

    return `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="utf-8">
        <style>
          body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
          .container { max-width: 600px; margin: 0 auto; padding: 20px; }
          .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
          .content { background: white; padding: 30px; }
          .footer { background: #f5f5f5; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; }
          .button { display: inline-block; padding: 12px 30px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px; margin-top: 20px; }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="header">
            <h1>🚀 New Job Alert</h1>
            <p>${newJobs.length} new position${newJobs.length > 1 ? 's' : ''} at ${company.name}</p>
          </div>
          <div class="content">
            <h2>Recently Posted Jobs:</h2>
            ${jobsHTML}
            <a href="${company.careers_url}" class="button">View All Jobs →</a>
          </div>
          <div class="footer">
            <p>PulseB2B Market Intelligence | ${new Date().toLocaleDateString()}</p>
          </div>
        </div>
      </body>
      </html>
    `;
  }

  /**
   * Registra la notificación en la base de datos
   */
  async logNotification(companyId, jobCount) {
    try {
      await this.supabase
        .from('notifications')
        .insert([{
          company_id: companyId,
          job_count: jobCount,
          sent_at: new Date().toISOString(),
          status: 'sent'
        }]);
    } catch (error) {
      console.error('Error logging notification:', error.message);
    }
  }

  /**
   * Obtiene historial de notificaciones
   */
  async getNotificationHistory(companyId, limit = 10) {
    const { data, error } = await this.supabase
      .from('notifications')
      .select('*')
      .eq('company_id', companyId)
      .order('sent_at', { ascending: false })
      .limit(limit);

    if (error) {
      throw new Error(`Error fetching notification history: ${error.message}`);
    }

    return data;
  }
}

module.exports = WebhookNotifier;
