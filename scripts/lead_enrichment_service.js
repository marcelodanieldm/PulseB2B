/**
 * Lead Enrichment Service
 * Enriches user signups with company data (size, industry, revenue)
 * Uses email domain to fetch company information
 */

const { createClient } = require('@supabase/supabase-js');
const axios = require('axios');

// Environment variables
const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_KEY;
const CLEARBIT_API_KEY = process.env.CLEARBIT_API_KEY; // https://clearbit.com/enrichment
const HUNTER_API_KEY = process.env.HUNTER_API_KEY; // https://hunter.io/api

const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);

/**
 * Extract domain from email
 */
function extractDomain(email) {
  if (!email) return null;
  const match = email.match(/@(.+)$/);
  return match ? match[1].toLowerCase() : null;
}

/**
 * Check if domain is a generic email provider
 */
function isGenericProvider(domain) {
  const genericProviders = [
    'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
    'aol.com', 'icloud.com', 'protonmail.com', 'mail.com',
    'zoho.com', 'yandex.com', 'gmx.com'
  ];
  return genericProviders.includes(domain);
}

/**
 * Enrich company data using Clearbit API
 */
async function enrichWithClearbit(domain) {
  if (!CLEARBIT_API_KEY) {
    console.log('⚠️  Clearbit API key not configured');
    return null;
  }

  try {
    const response = await axios.get(`https://company.clearbit.com/v2/companies/find`, {
      params: { domain },
      headers: { Authorization: `Bearer ${CLEARBIT_API_KEY}` },
      timeout: 5000
    });

    const company = response.data;
    
    return {
      name: company.name,
      domain: company.domain,
      employee_count: company.metrics?.employees || null,
      employee_range: company.metrics?.employeesRange || null,
      industry: company.category?.industry || null,
      sector: company.category?.sector || null,
      revenue: company.metrics?.estimatedAnnualRevenue || null,
      tech_stack: company.tech || [],
      description: company.description,
      founded_year: company.foundedYear,
      location: company.location,
      logo_url: company.logo,
      linkedin_url: company.linkedin?.handle ? `https://linkedin.com/company/${company.linkedin.handle}` : null,
      twitter_url: company.twitter?.handle ? `https://twitter.com/${company.twitter.handle}` : null,
      source: 'clearbit'
    };
  } catch (error) {
    if (error.response?.status === 404) {
      console.log(`Company not found in Clearbit: ${domain}`);
    } else {
      console.error(`Clearbit API error for ${domain}:`, error.message);
    }
    return null;
  }
}

/**
 * Enrich company data using Hunter.io API
 */
async function enrichWithHunter(domain) {
  if (!HUNTER_API_KEY) {
    console.log('⚠️  Hunter API key not configured');
    return null;
  }

  try {
    const response = await axios.get(`https://api.hunter.io/v2/domain-search`, {
      params: {
        domain,
        api_key: HUNTER_API_KEY,
        limit: 1
      },
      timeout: 5000
    });

    const data = response.data.data;
    
    return {
      name: data.organization,
      domain: data.domain,
      employee_count: data.company_size || null,
      employee_range: null,
      industry: data.industry || null,
      sector: null,
      revenue: null,
      tech_stack: [],
      description: data.description,
      founded_year: null,
      location: data.country,
      logo_url: null,
      linkedin_url: data.linkedin ? `https://linkedin.com/company/${data.linkedin}` : null,
      twitter_url: data.twitter ? `https://twitter.com/${data.twitter}` : null,
      source: 'hunter'
    };
  } catch (error) {
    console.error(`Hunter API error for ${domain}:`, error.message);
    return null;
  }
}

/**
 * Fallback: Basic enrichment using DNS and manual detection
 */
async function enrichBasic(domain) {
  // Check if domain exists and extract basic info
  try {
    const response = await axios.get(`https://${domain}`, {
      timeout: 3000,
      maxRedirects: 5
    });

    return {
      name: domain.split('.')[0].toUpperCase(),
      domain: domain,
      employee_count: null,
      employee_range: 'unknown',
      industry: null,
      sector: null,
      revenue: null,
      tech_stack: [],
      description: null,
      founded_year: null,
      location: null,
      logo_url: null,
      linkedin_url: null,
      twitter_url: null,
      source: 'basic'
    };
  } catch (error) {
    console.log(`Could not validate domain: ${domain}`);
    return null;
  }
}

/**
 * Main enrichment function - tries multiple sources
 */
async function enrichCompany(domain) {
  console.log(`🔍 Enriching company data for domain: ${domain}`);

  // Try Clearbit first (most comprehensive)
  let companyData = await enrichWithClearbit(domain);
  
  // Fallback to Hunter if Clearbit fails
  if (!companyData) {
    companyData = await enrichWithHunter(domain);
  }
  
  // Fallback to basic if all APIs fail
  if (!companyData) {
    companyData = await enrichBasic(domain);
  }

  if (companyData) {
    console.log(`✅ Company enriched: ${companyData.name} (${companyData.employee_count || 'unknown'} employees)`);
  } else {
    console.log(`❌ Could not enrich company data for: ${domain}`);
  }

  return companyData;
}

/**
 * Store enriched company data in Supabase
 */
async function storeCompanyEnrichment(userId, email, companyData) {
  const domain = extractDomain(email);
  
  try {
    const { data, error } = await supabase
      .from('company_enrichment')
      .upsert({
        user_id: userId,
        email_domain: domain,
        company_name: companyData.name,
        employee_count: companyData.employee_count,
        employee_range: companyData.employee_range,
        industry: companyData.industry,
        sector: companyData.sector,
        estimated_revenue: companyData.revenue,
        tech_stack: companyData.tech_stack,
        description: companyData.description,
        founded_year: companyData.founded_year,
        location: companyData.location,
        logo_url: companyData.logo_url,
        linkedin_url: companyData.linkedin_url,
        twitter_url: companyData.twitter_url,
        enrichment_source: companyData.source,
        enriched_at: new Date().toISOString(),
        is_generic_provider: isGenericProvider(domain)
      }, {
        onConflict: 'user_id'
      });

    if (error) throw error;
    
    console.log(`💾 Company enrichment stored for user: ${userId}`);
    return data;
  } catch (error) {
    console.error('Error storing company enrichment:', error);
    throw error;
  }
}

/**
 * Enrich user on signup
 */
async function enrichUser(userId, email) {
  console.log(`\n🚀 Starting enrichment for user: ${userId} (${email})`);

  const domain = extractDomain(email);
  
  if (!domain) {
    console.log('❌ Invalid email format');
    return null;
  }

  // Skip generic providers
  if (isGenericProvider(domain)) {
    console.log(`⏭️  Skipping generic email provider: ${domain}`);
    
    // Store with flag
    await supabase
      .from('company_enrichment')
      .upsert({
        user_id: userId,
        email_domain: domain,
        is_generic_provider: true,
        enriched_at: new Date().toISOString()
      }, {
        onConflict: 'user_id'
      });
    
    return null;
  }

  // Enrich company
  const companyData = await enrichCompany(domain);
  
  if (!companyData) {
    console.log('❌ Enrichment failed');
    return null;
  }

  // Store enrichment data
  await storeCompanyEnrichment(userId, email, companyData);

  return companyData;
}

/**
 * Batch enrichment for existing users
 */
async function batchEnrichUsers(limit = 50) {
  console.log(`\n📊 Starting batch enrichment (limit: ${limit})`);

  try {
    // Get users without enrichment data
    const { data: users, error } = await supabase
      .from('users')
      .select('id, email')
      .is('enrichment_completed', null)
      .limit(limit);

    if (error) throw error;

    console.log(`Found ${users.length} users to enrich`);

    let enriched = 0;
    let failed = 0;

    for (const user of users) {
      try {
        await enrichUser(user.id, user.email);
        enriched++;
        
        // Mark as enriched
        await supabase
          .from('users')
          .update({ enrichment_completed: true })
          .eq('id', user.id);
        
        // Rate limit: 1 request per second
        await new Promise(resolve => setTimeout(resolve, 1000));
      } catch (error) {
        console.error(`Failed to enrich user ${user.id}:`, error.message);
        failed++;
      }
    }

    console.log(`\n✅ Batch enrichment complete:`);
    console.log(`   Enriched: ${enriched}`);
    console.log(`   Failed: ${failed}`);

    return { enriched, failed, total: users.length };
  } catch (error) {
    console.error('Batch enrichment error:', error);
    throw error;
  }
}

/**
 * CLI Interface
 */
async function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  if (command === 'enrich') {
    const userId = args[1];
    const email = args[2];

    if (!userId || !email) {
      console.error('Usage: node lead_enrichment_service.js enrich <userId> <email>');
      process.exit(1);
    }

    await enrichUser(userId, email);
  } else if (command === 'batch') {
    const limit = parseInt(args[1]) || 50;
    await batchEnrichUsers(limit);
  } else if (command === 'domain') {
    const domain = args[1];
    
    if (!domain) {
      console.error('Usage: node lead_enrichment_service.js domain <domain>');
      process.exit(1);
    }

    const companyData = await enrichCompany(domain);
    console.log('\n📋 Company Data:');
    console.log(JSON.stringify(companyData, null, 2));
  } else {
    console.log('Lead Enrichment Service');
    console.log('=======================');
    console.log('');
    console.log('Commands:');
    console.log('  enrich <userId> <email>  - Enrich single user');
    console.log('  batch [limit]            - Batch enrich users (default: 50)');
    console.log('  domain <domain>          - Test domain enrichment');
    console.log('');
    console.log('Examples:');
    console.log('  node lead_enrichment_service.js enrich user-123 john@acme.com');
    console.log('  node lead_enrichment_service.js batch 100');
    console.log('  node lead_enrichment_service.js domain stripe.com');
  }
}

// Export functions
module.exports = {
  enrichUser,
  enrichCompany,
  storeCompanyEnrichment,
  batchEnrichUsers,
  extractDomain,
  isGenericProvider
};

// Run CLI if called directly
if (require.main === module) {
  main().catch(error => {
    console.error('Error:', error);
    process.exit(1);
  });
}
