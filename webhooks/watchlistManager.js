/**
 * Watchlist Manager
 * Gestiona la lista de empresas a monitorear
 */

const { createClient } = require('@supabase/supabase-js');

class WatchlistManager {
  constructor() {
    if (!process.env.SUPABASE_URL || !process.env.SUPABASE_KEY) {
      throw new Error('Supabase credentials not configured');
    }

    this.supabase = createClient(
      process.env.SUPABASE_URL,
      process.env.SUPABASE_KEY
    );
  }

  /**
   * Obtiene todas las empresas activas en la watchlist
   */
  async getActiveCompanies() {
    const { data, error } = await this.supabase
      .from('watchlist')
      .select('*')
      .eq('active', true)
      .order('priority', { ascending: false });

    if (error) {
      throw new Error(`Error fetching watchlist: ${error.message}`);
    }

    return data;
  }

  /**
   * Obtiene empresas por región
   */
  async getCompaniesByRegion(region) {
    const { data, error } = await this.supabase
      .from('watchlist')
      .select('*')
      .eq('active', true)
      .eq('region', region)
      .order('priority', { ascending: false });

    if (error) {
      throw new Error(`Error fetching companies by region: ${error.message}`);
    }

    return data;
  }

  /**
   * Agrega una empresa a la watchlist
   */
  async addCompany(company) {
    const { data, error } = await this.supabase
      .from('watchlist')
      .insert([{
        name: company.name,
        careers_url: company.careers_url,
        scraper_type: company.scraper_type || 'generic',
        job_selector: company.job_selector || null,
        region: company.region || 'us',
        priority: company.priority || 5,
        webhook_url: company.webhook_url || null,
        notification_channels: company.notification_channels || ['webhook'],
        active: true,
        metadata: company.metadata || {},
        created_at: new Date().toISOString()
      }])
      .select();

    if (error) {
      throw new Error(`Error adding company: ${error.message}`);
    }

    console.log(`✓ Added ${company.name} to watchlist`);
    return data[0];
  }

  /**
   * Actualiza una empresa en la watchlist
   */
  async updateCompany(companyId, updates) {
    const { data, error } = await this.supabase
      .from('watchlist')
      .update({
        ...updates,
        updated_at: new Date().toISOString()
      })
      .eq('id', companyId)
      .select();

    if (error) {
      throw new Error(`Error updating company: ${error.message}`);
    }

    return data[0];
  }

  /**
   * Elimina (desactiva) una empresa de la watchlist
   */
  async removeCompany(companyId) {
    const { data, error } = await this.supabase
      .from('watchlist')
      .update({ active: false })
      .eq('id', companyId)
      .select();

    if (error) {
      throw new Error(`Error removing company: ${error.message}`);
    }

    return data[0];
  }

  /**
   * Actualiza el último scrape de una empresa
   */
  async updateLastScrape(companyId, jobCount, success = true) {
    const { data, error } = await this.supabase
      .from('watchlist')
      .update({
        last_scraped_at: new Date().toISOString(),
        last_job_count: jobCount,
        scrape_status: success ? 'success' : 'failed',
        scrape_attempts: this.supabase.rpc('increment', { row_id: companyId })
      })
      .eq('id', companyId)
      .select();

    if (error) {
      console.error(`Error updating last scrape: ${error.message}`);
    }

    return data?.[0];
  }

  /**
   * Obtiene estadísticas de la watchlist
   */
  async getStats() {
    const { data: companies } = await this.supabase
      .from('watchlist')
      .select('active, region, scrape_status');

    const stats = {
      total: companies?.length || 0,
      active: companies?.filter(c => c.active).length || 0,
      inactive: companies?.filter(c => !c.active).length || 0,
      by_region: {},
      by_status: {}
    };

    // Agrupar por región
    companies?.forEach(c => {
      stats.by_region[c.region] = (stats.by_region[c.region] || 0) + 1;
    });

    // Agrupar por status
    companies?.forEach(c => {
      const status = c.scrape_status || 'never';
      stats.by_status[status] = (stats.by_status[status] || 0) + 1;
    });

    return stats;
  }

  /**
   * Obtiene empresas que necesitan re-scraping
   */
  async getCompaniesNeedingScrape(hoursThreshold = 24) {
    const threshold = new Date();
    threshold.setHours(threshold.getHours() - hoursThreshold);

    const { data, error } = await this.supabase
      .from('watchlist')
      .select('*')
      .eq('active', true)
      .or(`last_scraped_at.is.null,last_scraped_at.lt.${threshold.toISOString()}`)
      .order('priority', { ascending: false });

    if (error) {
      throw new Error(`Error fetching companies needing scrape: ${error.message}`);
    }

    return data;
  }
}

module.exports = WatchlistManager;
