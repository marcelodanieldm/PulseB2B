/**
 * Supabase Client
 * Cliente configurado para interactuar con Supabase
 */

const { createClient } = require('@supabase/supabase-js');

class SupabaseClient {
  constructor() {
    if (!process.env.SUPABASE_URL) {
      throw new Error('SUPABASE_URL environment variable is required');
    }
    
    if (!process.env.SUPABASE_KEY) {
      throw new Error('SUPABASE_KEY environment variable is required');
    }

    this.client = createClient(
      process.env.SUPABASE_URL,
      process.env.SUPABASE_KEY,
      {
        auth: {
          autoRefreshToken: true,
          persistSession: false
        }
      }
    );
  }

  /**
   * Obtiene el cliente de Supabase
   */
  getClient() {
    return this.client;
  }

  /**
   * Health check de la conexión
   */
  async healthCheck() {
    try {
      const { data, error } = await this.client
        .from('watchlist')
        .select('count')
        .limit(1);

      if (error) throw error;

      return { status: 'healthy', timestamp: new Date().toISOString() };
    } catch (error) {
      return { 
        status: 'unhealthy', 
        error: error.message,
        timestamp: new Date().toISOString()
      };
    }
  }

  /**
   * Obtiene estadísticas generales
   */
  async getGeneralStats() {
    const [watchlistCount, jobsCount, notificationsCount] = await Promise.all([
      this.client.from('watchlist').select('count').single(),
      this.client.from('jobs').select('count').single(),
      this.client.from('notifications').select('count').single()
    ]);

    return {
      watchlist_companies: watchlistCount.data?.count || 0,
      total_jobs: jobsCount.data?.count || 0,
      total_notifications: notificationsCount.data?.count || 0
    };
  }

  /**
   * Búsqueda full-text de jobs
   */
  async searchJobs(query, limit = 50) {
    const { data, error } = await this.client
      .rpc('search_jobs', { search_query: query })
      .limit(limit);

    if (error) {
      throw new Error(`Error searching jobs: ${error.message}`);
    }

    return data;
  }

  /**
   * Obtiene jobs recientes
   */
  async getRecentJobs(days = 7, limit = 100) {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - days);

    const { data, error } = await this.client
      .from('jobs')
      .select('*')
      .gte('scraped_at', cutoffDate.toISOString())
      .order('scraped_at', { ascending: false })
      .limit(limit);

    if (error) {
      throw new Error(`Error fetching recent jobs: ${error.message}`);
    }

    return data;
  }

  /**
   * Registra un log de scraping
   */
  async logScrape(companyId, region, result) {
    const { data, error } = await this.client
      .from('scrape_logs')
      .insert([{
        company_id: companyId,
        region: region,
        proxy_used: result.proxy || null,
        jobs_found: result.jobs_found || 0,
        new_jobs: result.new_jobs || 0,
        success: result.success,
        error_message: result.error || null,
        duration_ms: result.duration || null,
        metadata: result.metadata || {},
        scraped_at: new Date().toISOString()
      }])
      .select();

    if (error) {
      console.error('Error logging scrape:', error.message);
    }

    return data?.[0];
  }

  /**
   * Obtiene logs de scraping recientes
   */
  async getScrapeLogs(companyId = null, limit = 100) {
    let query = this.client
      .from('scrape_logs')
      .select('*')
      .order('scraped_at', { ascending: false })
      .limit(limit);

    if (companyId) {
      query = query.eq('company_id', companyId);
    }

    const { data, error } = await query;

    if (error) {
      throw new Error(`Error fetching scrape logs: ${error.message}`);
    }

    return data;
  }

  /**
   * Obtiene estadísticas por empresa
   */
  async getCompanyStats(companyId = null) {
    let query = this.client.from('company_stats').select('*');

    if (companyId) {
      query = query.eq('id', companyId);
    }

    const { data, error } = await query;

    if (error) {
      throw new Error(`Error fetching company stats: ${error.message}`);
    }

    return companyId ? data?.[0] : data;
  }

  /**
   * Limpia jobs antiguos
   */
  async cleanOldJobs(daysToKeep = 90) {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - daysToKeep);

    const { data, error } = await this.client
      .from('jobs')
      .delete()
      .lt('scraped_at', cutoffDate.toISOString());

    if (error) {
      throw new Error(`Error cleaning old jobs: ${error.message}`);
    }

    console.log(`✓ Cleaned jobs older than ${daysToKeep} days`);
    return data;
  }

  /**
   * Limpia logs antiguos
   */
  async cleanOldLogs(daysToKeep = 30) {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - daysToKeep);

    const { data, error } = await this.client
      .from('scrape_logs')
      .delete()
      .lt('scraped_at', cutoffDate.toISOString());

    if (error) {
      throw new Error(`Error cleaning old logs: ${error.message}`);
    }

    console.log(`✓ Cleaned logs older than ${daysToKeep} days`);
    return data;
  }
}

// Singleton instance
let instance = null;

module.exports = {
  getSupabaseClient: () => {
    if (!instance) {
      instance = new SupabaseClient();
    }
    return instance;
  },
  SupabaseClient
};
