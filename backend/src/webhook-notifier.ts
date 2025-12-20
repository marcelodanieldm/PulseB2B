import axios, { AxiosInstance } from 'axios';
import axiosRetry from 'axios-retry';
import { LeadScore, SupabaseService } from './supabase-client';

/**
 * Webhook Payload for Slack
 */
interface SlackWebhookPayload {
  text?: string;
  blocks?: Array<{
    type: string;
    text?: {
      type: string;
      text: string;
    };
    fields?: Array<{
      type: string;
      text: string;
    }>;
  }>;
}

/**
 * Webhook Payload for Discord
 */
interface DiscordWebhookPayload {
  content?: string;
  embeds?: Array<{
    title: string;
    description?: string;
    color: number;
    fields: Array<{
      name: string;
      value: string;
      inline?: boolean;
    }>;
    footer?: {
      text: string;
    };
    timestamp?: string;
  }>;
}

/**
 * Webhook Notifier with axios-retry
 */
export class WebhookNotifier {
  private axiosInstance: AxiosInstance;
  private supabaseService: SupabaseService;

  constructor(supabaseService: SupabaseService) {
    this.supabaseService = supabaseService;

    // Create axios instance with retry logic
    this.axiosInstance = axios.create({
      timeout: 10000, // 10 seconds
    });

    // Configure axios-retry for resilience
    axiosRetry(this.axiosInstance, {
      retries: 3,
      retryDelay: axiosRetry.exponentialDelay, // 1s, 2s, 4s
      retryCondition: (error) => {
        // Retry on network errors or 5xx server errors
        return (
          axiosRetry.isNetworkOrIdempotentRequestError(error) ||
          (error.response?.status !== undefined && error.response.status >= 500)
        );
      },
      onRetry: (retryCount, error, requestConfig) => {
        console.log(`Retrying webhook request (${retryCount}/3): ${error.message}`);
      },
    });
  }

  /**
   * Send notification to Slack webhook
   */
  private async sendSlackNotification(webhookUrl: string, lead: LeadScore): Promise<void> {
    const payload: SlackWebhookPayload = {
      blocks: [
        {
          type: 'header',
          text: {
            type: 'plain_text',
            text: '🔥 CRITICAL LEAD DETECTED!',
          },
        },
        {
          type: 'section',
          fields: [
            {
              type: 'mrkdwn',
              text: `*Company:*\n${lead.company_name}`,
            },
            {
              type: 'mrkdwn',
              text: `*Country:*\n${lead.country === 'MX' ? '🇲🇽 Mexico' : '🇧🇷 Brazil'}`,
            },
            {
              type: 'mrkdwn',
              text: `*HPI Score:*\n${lead.hpi_score.toFixed(2)} (${lead.hpi_category})`,
            },
            {
              type: 'mrkdwn',
              text: `*Urgency:*\n${lead.urgency_level}`,
            },
            {
              type: 'mrkdwn',
              text: `*Employees:*\n${lead.employee_count.toLocaleString()}`,
            },
            {
              type: 'mrkdwn',
              text: `*Hiring Delta:*\n+${lead.estimated_headcount_delta} (next 6m)`,
            },
            {
              type: 'mrkdwn',
              text: `*Last Funding:*\n${lead.last_funding_date}`,
            },
            {
              type: 'mrkdwn',
              text: `*Funding Stage:*\n${lead.funding_stage || 'N/A'}`,
            },
          ],
        },
        {
          type: 'section',
          text: {
            type: 'mrkdwn',
            text: `💡 *Why Critical?*\n• Funding Recency Score: ${lead.funding_recency_score.toFixed(2)}\n• Growth Urgency Score: ${lead.growth_urgency_score}\n\n_This lead should be contacted immediately for maximum conversion potential._`,
          },
        },
      ],
    };

    await this.axiosInstance.post(webhookUrl, payload);
  }

  /**
   * Send notification to Discord webhook
   */
  private async sendDiscordNotification(webhookUrl: string, lead: LeadScore): Promise<void> {
    // Color based on HPI score (red for critical)
    const color = lead.hpi_score >= 90 ? 0xff0000 : lead.hpi_score >= 80 ? 0xff6600 : 0xffaa00;

    const payload: DiscordWebhookPayload = {
      embeds: [
        {
          title: '🔥 CRITICAL LEAD DETECTED!',
          description: `**${lead.company_name}** from ${lead.country === 'MX' ? '🇲🇽 Mexico' : '🇧🇷 Brazil'} has a high hiring potential.`,
          color,
          fields: [
            {
              name: '📊 HPI Score',
              value: `**${lead.hpi_score.toFixed(2)}** (${lead.hpi_category})`,
              inline: true,
            },
            {
              name: '⚡ Urgency',
              value: lead.urgency_level,
              inline: true,
            },
            {
              name: '👥 Current Employees',
              value: lead.employee_count.toLocaleString(),
              inline: true,
            },
            {
              name: '📈 Hiring Delta (6m)',
              value: `+${lead.estimated_headcount_delta}`,
              inline: true,
            },
            {
              name: '💰 Last Funding',
              value: lead.last_funding_date,
              inline: true,
            },
            {
              name: '🎯 Funding Stage',
              value: lead.funding_stage || 'N/A',
              inline: true,
            },
            {
              name: '💡 Why Critical?',
              value: `• Funding Recency: **${lead.funding_recency_score.toFixed(2)}**\n• Growth Urgency: **${lead.growth_urgency_score}**\n\n_Contact immediately for maximum conversion!_`,
              inline: false,
            },
          ],
          footer: {
            text: 'PulseB2B Ghost System',
          },
          timestamp: new Date().toISOString(),
        },
      ],
    };

    await this.axiosInstance.post(webhookUrl, payload);
  }

  /**
   * Detect webhook type from URL
   */
  private detectWebhookType(url: string): 'slack' | 'discord' | 'unknown' {
    if (url.includes('hooks.slack.com')) {
      return 'slack';
    } else if (url.includes('discord.com/api/webhooks')) {
      return 'discord';
    }
    return 'unknown';
  }

  /**
   * Send notification to webhook (auto-detects Slack or Discord)
   */
  async notify(webhookUrl: string, lead: LeadScore): Promise<boolean> {
    let retryCount = 0;

    try {
      // Check if already notified recently (avoid spam)
      const wasNotified = await this.supabaseService.wasNotifiedRecently(lead.company_name, 24);
      if (wasNotified) {
        console.log(`Skipping notification for ${lead.company_name} (already notified in last 24h)`);
        return true;
      }

      // Detect webhook type and send
      const webhookType = this.detectWebhookType(webhookUrl);

      console.log(`Sending ${webhookType} notification for ${lead.company_name} (HPI: ${lead.hpi_score})`);

      if (webhookType === 'slack') {
        await this.sendSlackNotification(webhookUrl, lead);
      } else if (webhookType === 'discord') {
        await this.sendDiscordNotification(webhookUrl, lead);
      } else {
        throw new Error(`Unknown webhook type: ${webhookUrl}`);
      }

      // Log success
      await this.supabaseService.logNotification({
        company_name: lead.company_name,
        hpi_score: lead.hpi_score,
        webhook_url: webhookUrl,
        status: 'success',
        retry_count: retryCount,
      });

      console.log(`✓ Notification sent successfully for ${lead.company_name}`);
      return true;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || error.message || 'Unknown error';

      // Log failure
      await this.supabaseService.logNotification({
        company_name: lead.company_name,
        hpi_score: lead.hpi_score,
        webhook_url: webhookUrl,
        status: 'failed',
        retry_count: retryCount,
        error_message: errorMessage,
      });

      console.error(`✗ Failed to send notification for ${lead.company_name}:`, errorMessage);
      return false;
    }
  }

  /**
   * Notify all critical leads (HPI >= threshold)
   */
  async notifyCriticalLeads(webhookUrl: string, threshold: number = 80): Promise<{ sent: number; failed: number }> {
    try {
      const criticalLeads = await this.supabaseService.getTopLeads(threshold);

      if (criticalLeads.length === 0) {
        console.log(`No critical leads found (threshold: ${threshold})`);
        return { sent: 0, failed: 0 };
      }

      console.log(`Found ${criticalLeads.length} critical leads to notify`);

      let sent = 0;
      let failed = 0;

      for (const lead of criticalLeads) {
        const success = await this.notify(webhookUrl, lead);
        if (success) {
          sent++;
        } else {
          failed++;
        }

        // Small delay between notifications to avoid rate limits
        await new Promise((resolve) => setTimeout(resolve, 1000));
      }

      return { sent, failed };
    } catch (error) {
      console.error('Error notifying critical leads:', error);
      return { sent: 0, failed: 0 };
    }
  }
}
