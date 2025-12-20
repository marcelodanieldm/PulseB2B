import { createClient, SupabaseClient } from '@supabase/supabase-js';
import { z } from 'zod';

/**
 * Database Types
 */

// Lead Score Record (resultado del HPI calculator)
export const LeadScoreSchema = z.object({
  id: z.string().uuid().optional(),
  company_name: z.string(),
  country: z.enum(['MX', 'BR']),
  last_funding_date: z.string(),
  funding_stage: z.string().optional(),
  last_funding_amount: z.number().optional(),
  employee_count: z.number(),
  estimated_headcount_delta: z.number(),
  hpi_score: z.number().min(0).max(100),
  hpi_category: z.enum(['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']),
  urgency_level: z.string(),
  funding_recency_score: z.number(),
  growth_urgency_score: z.number(),
  created_at: z.string().optional(),
  updated_at: z.string().optional(),
});

export type LeadScore = z.infer<typeof LeadScoreSchema>;

// Scraping Cache (para evitar re-scrapear la misma empresa)
export interface ScrapingCache {
  id?: string;
  company_name: string;
  country: string;
  last_scraped_at: string;
  scrape_count: number;
  created_at?: string;
  updated_at?: string;
}

// Notification Log (registro de notificaciones enviadas)
export interface NotificationLog {
  id?: string;
  company_name: string;
  hpi_score: number;
  webhook_url: string;
  status: 'success' | 'failed' | 'retrying';
  retry_count: number;
  error_message?: string;
  created_at?: string;
}

/**
 * Supabase Client
 */
export class SupabaseService {
  private client: SupabaseClient;

  constructor() {
    const supabaseUrl = process.env.SUPABASE_URL;
    const supabaseKey = process.env.SUPABASE_ANON_KEY;

    if (!supabaseUrl || !supabaseKey) {
      throw new Error('SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment variables');
    }

    this.client = createClient(supabaseUrl, supabaseKey);
  }

  /**
   * Save lead scores to database
   */
  async saveLeadScores(leads: LeadScore[]): Promise<{ success: number; failed: number }> {
    let success = 0;
    let failed = 0;

    for (const lead of leads) {
      try {
        // Validate with Zod
        LeadScoreSchema.parse(lead);

        // Check if lead already exists (upsert based on company_name + country)
        const { data: existing } = await this.client
          .from('lead_scores')
          .select('id')
          .eq('company_name', lead.company_name)
          .eq('country', lead.country)
          .single();

        if (existing) {
          // Update existing
          const { error } = await this.client
            .from('lead_scores')
            .update({
              ...lead,
              updated_at: new Date().toISOString(),
            })
            .eq('id', existing.id);

          if (error) throw error;
        } else {
          // Insert new
          const { error } = await this.client
            .from('lead_scores')
            .insert({
              ...lead,
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
            });

          if (error) throw error;
        }

        success++;
      } catch (error) {
        console.error(`Failed to save lead ${lead.company_name}:`, error);
        failed++;
      }
    }

    return { success, failed };
  }

  /**
   * Check if company was scraped in the last 7 days (cache-first logic)
   */
  async shouldScrapeCompany(companyName: string, country: string): Promise<boolean> {
    try {
      const sevenDaysAgo = new Date();
      sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);

      const { data, error } = await this.client
        .from('scraping_cache')
        .select('last_scraped_at')
        .eq('company_name', companyName)
        .eq('country', country)
        .single();

      if (error && error.code !== 'PGRST116') {
        // PGRST116 = no rows found (not an error)
        throw error;
      }

      if (!data) {
        return true; // Never scraped, should scrape
      }

      const lastScraped = new Date(data.last_scraped_at);
      return lastScraped < sevenDaysAgo; // Scrape if older than 7 days
    } catch (error) {
      console.error(`Error checking cache for ${companyName}:`, error);
      return true; // On error, allow scraping
    }
  }

  /**
   * Update scraping cache after successful scrape
   */
  async updateScrapingCache(companyName: string, country: string): Promise<void> {
    try {
      const { data: existing } = await this.client
        .from('scraping_cache')
        .select('id, scrape_count')
        .eq('company_name', companyName)
        .eq('country', country)
        .single();

      if (existing) {
        // Update existing
        await this.client
          .from('scraping_cache')
          .update({
            last_scraped_at: new Date().toISOString(),
            scrape_count: existing.scrape_count + 1,
            updated_at: new Date().toISOString(),
          })
          .eq('id', existing.id);
      } else {
        // Insert new
        await this.client
          .from('scraping_cache')
          .insert({
            company_name: companyName,
            country,
            last_scraped_at: new Date().toISOString(),
            scrape_count: 1,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          });
      }
    } catch (error) {
      console.error(`Failed to update cache for ${companyName}:`, error);
    }
  }

  /**
   * Get companies that need scraping (not scraped in last 7 days)
   */
  async getCompaniesToScrape(allCompanies: Array<{ company_name: string; country: string }>): Promise<typeof allCompanies> {
    const toScrape: typeof allCompanies = [];

    for (const company of allCompanies) {
      const shouldScrape = await this.shouldScrapeCompany(company.company_name, company.country);
      if (shouldScrape) {
        toScrape.push(company);
      }
    }

    console.log(`Cache check: ${toScrape.length}/${allCompanies.length} companies need scraping`);
    return toScrape;
  }

  /**
   * Get top leads (HPI >= threshold)
   */
  async getTopLeads(threshold: number = 80): Promise<LeadScore[]> {
    const { data, error } = await this.client
      .from('lead_scores')
      .select('*')
      .gte('hpi_score', threshold)
      .order('hpi_score', { ascending: false });

    if (error) throw error;
    return data as LeadScore[];
  }

  /**
   * Log notification attempt
   */
  async logNotification(log: NotificationLog): Promise<void> {
    try {
      const { error } = await this.client
        .from('notification_logs')
        .insert({
          ...log,
          created_at: new Date().toISOString(),
        });

      if (error) throw error;
    } catch (error) {
      console.error('Failed to log notification:', error);
    }
  }

  /**
   * Check if notification was already sent for this lead recently (avoid spam)
   */
  async wasNotifiedRecently(companyName: string, hoursAgo: number = 24): Promise<boolean> {
    try {
      const cutoff = new Date();
      cutoff.setHours(cutoff.getHours() - hoursAgo);

      const { data, error } = await this.client
        .from('notification_logs')
        .select('id')
        .eq('company_name', companyName)
        .eq('status', 'success')
        .gte('created_at', cutoff.toISOString())
        .limit(1);

      if (error) throw error;
      return (data?.length ?? 0) > 0;
    } catch (error) {
      console.error(`Error checking notification history for ${companyName}:`, error);
      return false; // On error, allow notification
    }
  }
}

/**
 * SQL Schema for Supabase (for reference)
 * 
 * Run these commands in Supabase SQL Editor:
 * 
 * -- Lead Scores Table
 * CREATE TABLE lead_scores (
 *   id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
 *   company_name TEXT NOT NULL,
 *   country TEXT NOT NULL,
 *   last_funding_date TEXT NOT NULL,
 *   funding_stage TEXT,
 *   last_funding_amount NUMERIC,
 *   employee_count INTEGER NOT NULL,
 *   estimated_headcount_delta INTEGER NOT NULL,
 *   hpi_score NUMERIC NOT NULL CHECK (hpi_score >= 0 AND hpi_score <= 100),
 *   hpi_category TEXT NOT NULL CHECK (hpi_category IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')),
 *   urgency_level TEXT NOT NULL,
 *   funding_recency_score NUMERIC NOT NULL,
 *   growth_urgency_score NUMERIC NOT NULL,
 *   created_at TIMESTAMPTZ DEFAULT NOW(),
 *   updated_at TIMESTAMPTZ DEFAULT NOW(),
 *   UNIQUE(company_name, country)
 * );
 * 
 * CREATE INDEX idx_lead_scores_hpi ON lead_scores(hpi_score DESC);
 * CREATE INDEX idx_lead_scores_company ON lead_scores(company_name, country);
 * 
 * -- Scraping Cache Table
 * CREATE TABLE scraping_cache (
 *   id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
 *   company_name TEXT NOT NULL,
 *   country TEXT NOT NULL,
 *   last_scraped_at TIMESTAMPTZ NOT NULL,
 *   scrape_count INTEGER DEFAULT 1,
 *   created_at TIMESTAMPTZ DEFAULT NOW(),
 *   updated_at TIMESTAMPTZ DEFAULT NOW(),
 *   UNIQUE(company_name, country)
 * );
 * 
 * CREATE INDEX idx_scraping_cache_last_scraped ON scraping_cache(last_scraped_at);
 * 
 * -- Notification Logs Table
 * CREATE TABLE notification_logs (
 *   id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
 *   company_name TEXT NOT NULL,
 *   hpi_score NUMERIC NOT NULL,
 *   webhook_url TEXT NOT NULL,
 *   status TEXT NOT NULL CHECK (status IN ('success', 'failed', 'retrying')),
 *   retry_count INTEGER DEFAULT 0,
 *   error_message TEXT,
 *   created_at TIMESTAMPTZ DEFAULT NOW()
 * );
 * 
 * CREATE INDEX idx_notification_logs_company ON notification_logs(company_name, created_at DESC);
 * CREATE INDEX idx_notification_logs_status ON notification_logs(status, created_at DESC);
 */
