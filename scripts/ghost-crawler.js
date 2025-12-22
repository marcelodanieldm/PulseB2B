/**
 * Ghost Crawler - Intelligent LinkedIn Job Scraper
 * ================================================
 * Uses Google Custom Search API to find LinkedIn job postings
 * without directly scraping LinkedIn (avoids IP bans).
 * 
 * Free Tier: 100 searches/day (Google CSE)
 * Rate Limiting: 1 request per 2 seconds (smart delays)
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

// Configuration
const CONFIG = {
  GOOGLE_CSE_API_KEY: process.env.GOOGLE_CSE_API_KEY,
  GOOGLE_CSE_ID: process.env.GOOGLE_CSE_ID,
  OUTPUT_DIR: path.join(__dirname, '..', 'data', 'output'),
  OUTPUT_FILE: 'scraped_companies.csv',
  MAX_SEARCHES: 50,  // Stay under 100/day limit
  DELAY_MS: 2000,    // 2 seconds between requests
  SEARCH_KEYWORDS: [
    'hiring software engineers',
    'hiring data scientists',
    'hiring ML engineers',
    'hiring backend developers',
    'hiring frontend developers',
    'scaling engineering team',
    'software engineering jobs',
    'tech jobs United States'
  ]
};

// Target companies (expand from Oracle predictions)
const TARGET_COMPANIES = [
  'Google', 'Meta', 'Amazon', 'Apple', 'Microsoft',
  'Tesla', 'Netflix', 'Uber', 'Airbnb', 'Stripe',
  'OpenAI', 'Anthropic', 'Scale AI', 'Databricks',
  'Snowflake', 'MongoDB', 'Redis', 'Vercel', 'Supabase'
  // Will load from Oracle predictions if available
];

class GhostCrawler {
  constructor() {
    this.results = [];
    this.searchCount = 0;
    this.errors = [];
  }

  /**
   * Main execution flow
   */
  async run() {
    console.log('🕵️  Ghost Crawler - Starting intelligent scrape...\n');

    // Load target companies from Oracle predictions if available
    const companies = await this.loadTargetCompanies();
    console.log(`📋 Loaded ${companies.length} target companies\n`);

    // Perform searches
    for (const company of companies.slice(0, CONFIG.MAX_SEARCHES)) {
      if (this.searchCount >= CONFIG.MAX_SEARCHES) {
        console.log(`⚠️  Reached daily limit (${CONFIG.MAX_SEARCHES} searches)`);
        break;
      }

      await this.searchCompanyJobs(company);
      await this.delay(CONFIG.DELAY_MS);  // Rate limiting
    }

    // Save results
    await this.saveResults();

    // Print summary
    this.printSummary();
  }

  /**
   * Load target companies from Oracle predictions or use defaults
   */
  async loadTargetCompanies() {
    const oraclePath = path.join(CONFIG.OUTPUT_DIR, 'oracle_predictions.csv');
    
    if (fs.existsSync(oraclePath)) {
      console.log('📂 Loading companies from Oracle predictions...');
      try {
        const content = fs.readFileSync(oraclePath, 'utf-8');
        const lines = content.split('\n').slice(1);  // Skip header
        const companies = lines
          .filter(line => line.trim())
          .map(line => {
            const parts = line.split(',');
            return parts[0]?.replace(/"/g, '').trim();
          })
          .filter(Boolean);
        
        if (companies.length > 0) {
          return companies;
        }
      } catch (error) {
        console.log(`⚠️  Could not load Oracle predictions: ${error.message}`);
      }
    }

    console.log('📋 Using default company list...');
    return TARGET_COMPANIES;
  }

  /**
   * Search for jobs at a specific company using Google Custom Search
   */
  async searchCompanyJobs(companyName) {
    this.searchCount++;
    
    console.log(`[${this.searchCount}/${CONFIG.MAX_SEARCHES}] Searching: ${companyName}`);

    // Build search query
    const keyword = CONFIG.SEARCH_KEYWORDS[
      Math.floor(Math.random() * CONFIG.SEARCH_KEYWORDS.length)
    ];
    const query = `site:linkedin.com/jobs "${keyword}" "${companyName}" "United States"`;

    try {
      const results = await this.googleCustomSearch(query);
      
      if (results && results.items && results.items.length > 0) {
        console.log(`  ✅ Found ${results.items.length} job postings`);
        
        this.results.push({
          company_name: companyName,
          job_count: results.items.length,
          job_titles: results.items
            .map(item => this.extractJobTitle(item.title))
            .filter(Boolean)
            .slice(0, 5)
            .join('; '),
          search_query: keyword,
          linkedin_urls: results.items
            .map(item => item.link)
            .slice(0, 3)
            .join('; '),
          scraped_at: new Date().toISOString()
        });
      } else {
        console.log(`  ℹ️  No jobs found`);
      }
    } catch (error) {
      console.log(`  ❌ Error: ${error.message}`);
      this.errors.push({ company: companyName, error: error.message });
    }
  }

  /**
   * Google Custom Search API request
   */
  async googleCustomSearch(query) {
    if (!CONFIG.GOOGLE_CSE_API_KEY || !CONFIG.GOOGLE_CSE_ID) {
      throw new Error('Google CSE credentials not configured');
    }

    const url = `https://www.googleapis.com/customsearch/v1?` +
      `key=${CONFIG.GOOGLE_CSE_API_KEY}` +
      `&cx=${CONFIG.GOOGLE_CSE_ID}` +
      `&q=${encodeURIComponent(query)}` +
      `&num=10`;  // Max 10 results per request

    return new Promise((resolve, reject) => {
      https.get(url, (res) => {
        let data = '';

        res.on('data', (chunk) => {
          data += chunk;
        });

        res.on('end', () => {
          try {
            if (res.statusCode === 200) {
              resolve(JSON.parse(data));
            } else if (res.statusCode === 429) {
              reject(new Error('API rate limit exceeded'));
            } else {
              reject(new Error(`API returned status ${res.statusCode}`));
            }
          } catch (error) {
            reject(error);
          }
        });
      }).on('error', (error) => {
        reject(error);
      });
    });
  }

  /**
   * Extract clean job title from search result
   */
  extractJobTitle(title) {
    // Remove common suffixes
    return title
      .replace(/\s*-\s*LinkedIn.*$/i, '')
      .replace(/\s*\|\s*LinkedIn.*$/i, '')
      .replace(/\s*hiring.*$/i, '')
      .trim();
  }

  /**
   * Save results to CSV
   */
  async saveResults() {
    // Ensure output directory exists
    if (!fs.existsSync(CONFIG.OUTPUT_DIR)) {
      fs.mkdirSync(CONFIG.OUTPUT_DIR, { recursive: true });
    }

    const outputPath = path.join(CONFIG.OUTPUT_DIR, CONFIG.OUTPUT_FILE);

    // Build CSV
    const header = 'company_name,job_count,job_titles,search_query,linkedin_urls,scraped_at\n';
    const rows = this.results.map(row => 
      `"${row.company_name}",${row.job_count},"${row.job_titles}","${row.search_query}","${row.linkedin_urls}","${row.scraped_at}"`
    ).join('\n');

    const csv = header + rows;

    // Write to file
    fs.writeFileSync(outputPath, csv, 'utf-8');
    console.log(`\n💾 Results saved: ${outputPath}`);
  }

  /**
   * Print execution summary
   */
  printSummary() {
    console.log('\n' + '='.repeat(60));
    console.log('📊 GHOST CRAWLER SUMMARY');
    console.log('='.repeat(60));
    console.log(`Total Searches: ${this.searchCount}`);
    console.log(`Companies with Jobs: ${this.results.length}`);
    console.log(`Total Jobs Found: ${this.results.reduce((sum, r) => sum + r.job_count, 0)}`);
    console.log(`Errors: ${this.errors.length}`);
    
    if (this.results.length > 0) {
      console.log('\n🔥 Top Hiring Companies:');
      this.results
        .sort((a, b) => b.job_count - a.job_count)
        .slice(0, 5)
        .forEach((r, i) => {
          console.log(`  ${i + 1}. ${r.company_name} - ${r.job_count} jobs`);
        });
    }

    if (this.errors.length > 0) {
      console.log('\n⚠️  Errors:');
      this.errors.slice(0, 3).forEach(e => {
        console.log(`  - ${e.company}: ${e.error}`);
      });
    }

    console.log('='.repeat(60));
  }

  /**
   * Smart delay with jitter to avoid patterns
   */
  async delay(ms) {
    const jitter = Math.floor(Math.random() * 500);  // 0-500ms jitter
    return new Promise(resolve => setTimeout(resolve, ms + jitter));
  }
}

// ============================================
// MAIN EXECUTION
// ============================================
if (require.main === module) {
  const crawler = new GhostCrawler();
  
  crawler.run()
    .then(() => {
      console.log('\n✅ Ghost Crawler completed successfully');
      process.exit(0);
    })
    .catch((error) => {
      console.error('\n❌ Ghost Crawler failed:', error);
      process.exit(1);
    });
}

module.exports = GhostCrawler;
