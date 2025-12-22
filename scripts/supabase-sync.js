/**
 * Supabase Sync - Intelligent Upsert Logic
 * ==========================================
 * Syncs Pulse-scored companies to Supabase with smart upsert:
 * - If company exists: Update hiring_probability, pulse_score, last_seen
 * - If new company: Insert full record
 * 
 * Prevents duplicates and maintains historical tracking.
 */

const fs = require('fs');
const path = require('path');
const { createClient } = require('@supabase/supabase-js');

// Configuration
const CONFIG = {
  SUPABASE_URL: process.env.SUPABASE_URL,
  SUPABASE_SERVICE_KEY: process.env.SUPABASE_SERVICE_KEY,
  INPUT_FILE: path.join(__dirname, '..', 'data', 'output', 'pulse_scored.csv'),
  TABLE_NAME: 'oracle_predictions',
  BATCH_SIZE: 50,
  MIN_SCORE_THRESHOLD: 40  // Only sync companies with 40+ score
};

class SupabaseSync {
  constructor() {
    if (!CONFIG.SUPABASE_URL || !CONFIG.SUPABASE_SERVICE_KEY) {
      throw new Error('Supabase credentials not configured');
    }

    this.supabase = createClient(
      CONFIG.SUPABASE_URL,
      CONFIG.SUPABASE_SERVICE_KEY
    );
    
    this.stats = {
      total: 0,
      inserted: 0,
      updated: 0,
      skipped: 0,
      errors: 0
    };
  }

  /**
   * Main execution flow
   */
  async run() {
    console.log('💾 Supabase Sync - Starting intelligent upsert...\n');

    // Load scored companies
    const companies = await this.loadScoredCompanies();
    console.log(`📊 Loaded ${companies.length} scored companies\n`);

    // Filter by minimum score
    const filtered = companies.filter(c => c.pulse_score >= CONFIG.MIN_SCORE_THRESHOLD);
    console.log(`✅ ${filtered.length} companies meet threshold (${CONFIG.MIN_SCORE_THRESHOLD}+ score)`);
    
    if (filtered.length === 0) {
      console.log('ℹ️  No companies to sync');
      return;
    }

    // Process in batches
    const batches = this.createBatches(filtered, CONFIG.BATCH_SIZE);
    console.log(`📦 Processing ${batches.length} batches...\n`);

    for (let i = 0; i < batches.length; i++) {
      console.log(`Batch ${i + 1}/${batches.length}...`);
      await this.processBatch(batches[i]);
      await this.delay(1000);  // 1 second between batches
    }

    // Print summary
    this.printSummary();
  }

  /**
   * Load companies from CSV
   */
  async loadScoredCompanies() {
    if (!fs.existsSync(CONFIG.INPUT_FILE)) {
      throw new Error(`Input file not found: ${CONFIG.INPUT_FILE}`);
    }

    const content = fs.readFileSync(CONFIG.INPUT_FILE, 'utf-8');
    const lines = content.split('\n');
    const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''));

    const companies = [];

    for (let i = 1; i < lines.length; i++) {
      const line = lines[i].trim();
      if (!line) continue;

      try {
        const values = this.parseCSVLine(line);
        const record = {};
        
        headers.forEach((header, index) => {
          record[header] = values[index];
        });

        // Parse numeric fields
        record.pulse_score = parseFloat(record.pulse_score) || 0;
        record.hiring_probability = parseFloat(record.hiring_probability) || 0;
        record.expansion_density = parseFloat(record.expansion_density) || 0;
        record.tech_diversity_score = parseInt(record.tech_diversity_score) || 0;
        record.funding_amount = parseFloat(record.funding_amount) || 0;

        companies.push(record);
      } catch (error) {
        console.log(`⚠️  Skipped line ${i}: ${error.message}`);
      }
    }

    return companies;
  }

  /**
   * Process a batch of companies with upsert logic
   */
  async processBatch(batch) {
    this.stats.total += batch.length;

    for (const company of batch) {
      try {
        // Check if company exists
        const existing = await this.findExistingCompany(company.company_name);

        if (existing) {
          // UPDATE: Only critical fields
          await this.updateCompany(existing.id, company);
          this.stats.updated++;
          console.log(`  ✅ Updated: ${company.company_name} (${company.pulse_score} pts)`);
        } else {
          // INSERT: Full record
          await this.insertCompany(company);
          this.stats.inserted++;
          console.log(`  ➕ Inserted: ${company.company_name} (${company.pulse_score} pts)`);
        }
      } catch (error) {
        this.stats.errors++;
        console.log(`  ❌ Error: ${company.company_name} - ${error.message}`);
      }
    }
  }

  /**
   * Find existing company by name
   */
  async findExistingCompany(companyName) {
    const { data, error } = await this.supabase
      .from(CONFIG.TABLE_NAME)
      .select('id, hiring_probability, pulse_score')
      .eq('company_name', companyName)
      .single();

    if (error && error.code !== 'PGRST116') {  // PGRST116 = not found
      throw error;
    }

    return data;
  }

  /**
   * Update existing company (upsert logic)
   */
  async updateCompany(id, company) {
    const updateData = {
      hiring_probability: company.hiring_probability,
      pulse_score: company.pulse_score,
      desperation_level: company.desperation_level,
      urgency: company.urgency,
      expansion_density: company.expansion_density,
      tech_diversity_score: company.tech_diversity_score,
      has_red_flags: company.has_red_flags === 'True' || company.has_red_flags === true,
      recommendation: company.recommendation,
      last_seen: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };

    const { error } = await this.supabase
      .from(CONFIG.TABLE_NAME)
      .update(updateData)
      .eq('id', id);

    if (error) throw error;
  }

  /**
   * Insert new company (full record)
   */
  async insertCompany(company) {
    const insertData = {
      company_name: company.company_name,
      industry: company.industry || 'Technology',
      funding_amount: company.funding_amount,
      funding_date: company.funding_date,
      tech_stack: company.tech_stack,
      hiring_probability: company.hiring_probability,
      pulse_score: company.pulse_score,
      desperation_level: company.desperation_level,
      urgency: company.urgency,
      expansion_density: company.expansion_density,
      tech_diversity_score: company.tech_diversity_score,
      has_red_flags: company.has_red_flags === 'True' || company.has_red_flags === true,
      recommendation: company.recommendation,
      pulse_full_analysis: company.pulse_full_analysis || null,
      website_url: company.website_url,
      last_seen: new Date().toISOString(),
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };

    const { error } = await this.supabase
      .from(CONFIG.TABLE_NAME)
      .insert(insertData);

    if (error) throw error;
  }

  /**
   * Parse CSV line handling quoted fields
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
   * Create batches from array
   */
  createBatches(array, size) {
    const batches = [];
    for (let i = 0; i < array.length; i += size) {
      batches.push(array.slice(i, i + size));
    }
    return batches;
  }

  /**
   * Print execution summary
   */
  printSummary() {
    console.log('\n' + '='.repeat(60));
    console.log('📊 SUPABASE SYNC SUMMARY');
    console.log('='.repeat(60));
    console.log(`Total Processed: ${this.stats.total}`);
    console.log(`✅ Inserted: ${this.stats.inserted}`);
    console.log(`🔄 Updated: ${this.stats.updated}`);
    console.log(`❌ Errors: ${this.stats.errors}`);
    
    const successRate = ((this.stats.inserted + this.stats.updated) / this.stats.total * 100).toFixed(1);
    console.log(`\n📈 Success Rate: ${successRate}%`);
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
  const sync = new SupabaseSync();
  
  sync.run()
    .then(() => {
      console.log('\n✅ Supabase sync completed successfully');
      process.exit(0);
    })
    .catch((error) => {
      console.error('\n❌ Supabase sync failed:', error);
      process.exit(1);
    });
}

module.exports = SupabaseSync;
