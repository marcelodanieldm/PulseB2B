/**
 * Global Supabase Sync
 * ====================
 * Syncs multi-region scraped data to Supabase using smart upsert logic.
 * 
 * Features:
 * - Uses upsert_global_lead() function for intelligent updates
 * - Handles country_code, timezone_match, currency_type
 * - Merges job_urls arrays without duplicates
 * - Increments scrape_count on updates
 * - Batch processing with rate limiting
 * 
 * Author: PulseB2B Senior Backend Engineer
 */

const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');
const csv = require('csv-parser');

// ============================================
// Configuration
// ============================================

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_KEY;
const INPUT_CSV = 'data/output/regional_enhanced_global.csv';
const BATCH_SIZE = 50;
const DELAY_MS = 1000;  // 1 second between batches

// ============================================
// Initialize Supabase Client
// ============================================

if (!SUPABASE_URL || !SUPABASE_SERVICE_KEY) {
    console.error('❌ Missing environment variables: SUPABASE_URL or SUPABASE_SERVICE_KEY');
    process.exit(1);
}

const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);

// ============================================
// Helper Functions
// ============================================

async function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function loadCSV(filePath) {
    return new Promise((resolve, reject) => {
        const results = [];
        
        if (!fs.existsSync(filePath)) {
            console.error(`❌ File not found: ${filePath}`);
            reject(new Error('File not found'));
            return;
        }
        
        fs.createReadStream(filePath)
            .pipe(csv())
            .on('data', (row) => results.push(row))
            .on('end', () => resolve(results))
            .on('error', (error) => reject(error));
    });
}

async function upsertGlobalLead(lead) {
    /**
     * Upsert a single lead using the stored function.
     */
    const { data, error } = await supabase.rpc('upsert_global_lead', {
        p_company_name: lead.company_name,
        p_country_code: lead.country_code,
        p_job_count: parseInt(lead.job_count || 0),
        p_job_urls: lead.job_urls ? lead.job_urls.split('|').filter(url => url.trim()) : [],
        p_timezone_match: parseInt(lead.timezone_match || 0),
        p_currency_type: lead.currency_type || 'USD',
        p_region: lead.region || 'unknown'
    });
    
    if (error) {
        console.error(`❌ Error upserting ${lead.company_name} (${lead.country_code}):`, error.message);
        return false;
    }
    
    return true;
}

async function syncBatch(batch, batchNumber, totalBatches) {
    /**
     * Sync a batch of leads to Supabase.
     */
    console.log(`\n📦 Processing Batch ${batchNumber}/${totalBatches} (${batch.length} leads)`);
    
    let successCount = 0;
    let errorCount = 0;
    
    for (const lead of batch) {
        const success = await upsertGlobalLead(lead);
        
        if (success) {
            successCount++;
            process.stdout.write('.');
        } else {
            errorCount++;
            process.stdout.write('x');
        }
    }
    
    console.log(`\n   ✅ Success: ${successCount}/${batch.length}`);
    if (errorCount > 0) {
        console.log(`   ❌ Errors: ${errorCount}/${batch.length}`);
    }
    
    return { successCount, errorCount };
}

async function verifySync() {
    /**
     * Verify sync by querying recent leads.
     */
    const { data, error } = await supabase
        .from('leads_global')
        .select('country_code, count')
        .gte('last_seen', new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString());
    
    if (error) {
        console.error('❌ Verification failed:', error.message);
        return;
    }
    
    console.log('\n📊 Recent Leads by Country:');
    const countryCounts = {};
    data.forEach(row => {
        countryCounts[row.country_code] = (countryCounts[row.country_code] || 0) + 1;
    });
    
    Object.entries(countryCounts)
        .sort((a, b) => b[1] - a[1])
        .forEach(([country, count]) => {
            console.log(`   ${country}: ${count} leads`);
        });
}

// ============================================
// Main Sync Function
// ============================================

async function syncGlobalLeads() {
    console.log('🌎 Multi-Region Global Sync to Supabase');
    console.log('='repeat(80));
    
    // Load CSV
    console.log(`\n📥 Loading ${INPUT_CSV}...`);
    let leads;
    
    try {
        leads = await loadCSV(INPUT_CSV);
        console.log(`✅ Loaded ${leads.length} leads`);
    } catch (error) {
        console.error('❌ Failed to load CSV:', error.message);
        process.exit(1);
    }
    
    // Filter leads with minimum quality threshold
    const filteredLeads = leads.filter(lead => {
        const pulseScore = parseFloat(lead.pulse_score || 0);
        return pulseScore >= 40;  // Only sync leads with pulse_score >= 40
    });
    
    console.log(`\n🔍 Filtered to ${filteredLeads.length} leads (pulse_score >= 40)`);
    
    if (filteredLeads.length === 0) {
        console.log('⚠️ No leads to sync');
        process.exit(0);
    }
    
    // Split into batches
    const batches = [];
    for (let i = 0; i < filteredLeads.length; i += BATCH_SIZE) {
        batches.push(filteredLeads.slice(i, i + BATCH_SIZE));
    }
    
    console.log(`\n📦 Processing ${batches.length} batches of ${BATCH_SIZE} leads each`);
    
    // Process batches
    let totalSuccess = 0;
    let totalErrors = 0;
    
    for (let i = 0; i < batches.length; i++) {
        const { successCount, errorCount } = await syncBatch(batches[i], i + 1, batches.length);
        
        totalSuccess += successCount;
        totalErrors += errorCount;
        
        // Delay between batches (except last batch)
        if (i < batches.length - 1) {
            console.log(`   ⏳ Waiting ${DELAY_MS}ms before next batch...`);
            await sleep(DELAY_MS);
        }
    }
    
    // Summary
    console.log('\n' + '='.repeat(80));
    console.log('📊 SYNC SUMMARY');
    console.log('='.repeat(80));
    console.log(`   Total Leads:    ${filteredLeads.length}`);
    console.log(`   Synced:         ${totalSuccess}`);
    console.log(`   Errors:         ${totalErrors}`);
    console.log(`   Success Rate:   ${((totalSuccess / filteredLeads.length) * 100).toFixed(1)}%`);
    
    // Verify sync
    await verifySync();
    
    // Success threshold
    const successRate = (totalSuccess / filteredLeads.length);
    if (successRate < 0.8) {
        console.error('\n❌ Sync failed: Success rate below 80%');
        process.exit(1);
    }
    
    console.log('\n✅ Global sync complete!');
}

// ============================================
// Run
// ============================================

syncGlobalLeads().catch(error => {
    console.error('❌ Fatal error:', error);
    process.exit(1);
});
