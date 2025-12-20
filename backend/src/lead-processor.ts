import { spawn } from 'child_process';
import { promises as fs } from 'fs';
import * as path from 'path';
import * as dotenv from 'dotenv';
import { SupabaseService, LeadScore } from './supabase-client';
import { WebhookNotifier } from './webhook-notifier';

// Load environment variables
dotenv.config();

/**
 * Lead Processor - Main orchestrator for Ghost system
 */
export class LeadProcessor {
  private supabaseService: SupabaseService;
  private webhookNotifier: WebhookNotifier;
  private pythonScriptPath: string;
  private outputDir: string;

  constructor() {
    this.supabaseService = new SupabaseService();
    this.webhookNotifier = new WebhookNotifier(this.supabaseService);

    // Paths (adjust based on your project structure)
    const projectRoot = path.join(__dirname, '..', '..');
    this.pythonScriptPath = path.join(projectRoot, 'scripts', 'lead_scoring.py');
    this.outputDir = path.join(projectRoot, 'data', 'output', 'lead_scoring');
  }

  /**
   * Run Python lead scoring script
   */
  private async runPythonScript(): Promise<string> {
    return new Promise((resolve, reject) => {
      console.log('🐍 Running Python lead scoring script...');

      const pythonProcess = spawn('python', [
        this.pythonScriptPath,
        '--no-scraper', // Use mock data by default (change to enable real scraping)
        '--output',
        this.outputDir,
      ]);

      let stdout = '';
      let stderr = '';

      pythonProcess.stdout.on('data', (data) => {
        const output = data.toString();
        stdout += output;
        console.log(output);
      });

      pythonProcess.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      pythonProcess.on('close', (code) => {
        if (code !== 0) {
          reject(new Error(`Python script failed with code ${code}: ${stderr}`));
        } else {
          resolve(stdout);
        }
      });

      pythonProcess.on('error', (error) => {
        reject(new Error(`Failed to start Python process: ${error.message}`));
      });
    });
  }

  /**
   * Parse CSV output from Python script
   */
  private async parseCsvResults(csvPath: string): Promise<LeadScore[]> {
    const content = await fs.readFile(csvPath, 'utf-8');
    const lines = content.split('\n').filter((line) => line.trim());

    if (lines.length < 2) {
      throw new Error('CSV file is empty or invalid');
    }

    const headers = lines[0].split(',');
    const leads: LeadScore[] = [];

    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(',');
      const lead: any = {};

      headers.forEach((header, index) => {
        const key = header.trim();
        const value = values[index]?.trim();

        // Type conversion
        if (key === 'employee_count' || key === 'estimated_headcount_delta') {
          lead[key] = parseInt(value) || 0;
        } else if (
          key === 'hpi_score' ||
          key === 'funding_recency_score' ||
          key === 'growth_urgency_score' ||
          key === 'last_funding_amount'
        ) {
          lead[key] = parseFloat(value) || 0;
        } else {
          lead[key] = value;
        }
      });

      leads.push(lead as LeadScore);
    }

    return leads;
  }

  /**
   * Get latest CSV report from output directory
   */
  private async getLatestReport(): Promise<string> {
    const files = await fs.readdir(this.outputDir);
    const csvFiles = files.filter((f) => f.startsWith('lead_scoring_report_') && f.endsWith('.csv'));

    if (csvFiles.length === 0) {
      throw new Error('No CSV reports found');
    }

    // Sort by filename (contains timestamp) and get latest
    csvFiles.sort().reverse();
    return path.join(this.outputDir, csvFiles[0]);
  }

  /**
   * Filter companies that need scraping based on cache
   */
  private async filterCompaniesToScrape(): Promise<void> {
    // Load companies from CSV
    const companiesCsvPath = path.join(__dirname, '..', '..', 'data', 'input', 'companies_latam.csv');

    try {
      const content = await fs.readFile(companiesCsvPath, 'utf-8');
      const lines = content.split('\n').filter((line) => line.trim());

      const companies: Array<{ company_name: string; country: string }> = [];

      // Skip header
      for (let i = 1; i < lines.length; i++) {
        const [company_name, , country] = lines[i].split(',');
        if (company_name && country) {
          companies.push({
            company_name: company_name.trim(),
            country: country.trim(),
          });
        }
      }

      // Check cache and filter
      const toScrape = await this.supabaseService.getCompaniesToScrape(companies);

      if (toScrape.length === 0) {
        console.log('✓ All companies are cached (no scraping needed)');
        return;
      }

      console.log(`Cache-first logic: ${toScrape.length}/${companies.length} companies need fresh data`);

      // Update cache for companies we're about to scrape
      for (const company of toScrape) {
        await this.supabaseService.updateScrapingCache(company.company_name, company.country);
      }
    } catch (error) {
      console.error('Error filtering companies:', error);
    }
  }

  /**
   * Main processing pipeline
   */
  async process(): Promise<void> {
    const startTime = Date.now();

    try {
      console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
      console.log('🚀 PulseB2B Ghost System - Lead Processor');
      console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
      console.log(`⏰ Started at: ${new Date().toISOString()}\n`);

      // Step 1: Check cache and filter companies
      console.log('📋 Step 1: Checking scraping cache...');
      await this.filterCompaniesToScrape();

      // Step 2: Run Python script
      console.log('\n📋 Step 2: Running lead scoring script...');
      await this.runPythonScript();

      // Step 3: Load and parse results
      console.log('\n📋 Step 3: Loading results...');
      const latestReport = await this.getLatestReport();
      console.log(`✓ Latest report: ${path.basename(latestReport)}`);

      const leads = await this.parseCsvResults(latestReport);
      console.log(`✓ Parsed ${leads.length} lead scores`);

      // Step 4: Save to Supabase
      console.log('\n📋 Step 4: Saving to Supabase...');
      const saveResult = await this.supabaseService.saveLeadScores(leads);
      console.log(`✓ Saved: ${saveResult.success} leads`);
      if (saveResult.failed > 0) {
        console.log(`✗ Failed: ${saveResult.failed} leads`);
      }

      // Step 5: Notify critical leads
      const webhookUrl = process.env.WEBHOOK_URL;
      if (webhookUrl) {
        console.log('\n📋 Step 5: Checking for critical leads...');
        const threshold = parseInt(process.env.CRITICAL_THRESHOLD || '80');

        const notifyResult = await this.webhookNotifier.notifyCriticalLeads(webhookUrl, threshold);
        console.log(`✓ Notifications sent: ${notifyResult.sent}`);
        if (notifyResult.failed > 0) {
          console.log(`✗ Notifications failed: ${notifyResult.failed}`);
        }
      } else {
        console.log('\n⚠️  WEBHOOK_URL not configured - skipping notifications');
      }

      // Summary
      const duration = ((Date.now() - startTime) / 1000).toFixed(2);
      console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
      console.log('✅ Processing completed successfully');
      console.log(`⏱️  Duration: ${duration}s`);
      console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
    } catch (error: any) {
      console.error('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
      console.error('❌ Processing failed');
      console.error(`Error: ${error.message}`);
      console.error('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
      throw error;
    }
  }
}

/**
 * Main entry point
 */
async function main() {
  try {
    const processor = new LeadProcessor();
    await processor.process();
    process.exit(0);
  } catch (error) {
    console.error('Fatal error:', error);
    process.exit(1);
  }
}

// Run if executed directly
if (require.main === module) {
  main();
}
