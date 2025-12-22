/**
 * Lead Scoring Algorithm
 * Calculates priority score for user signups based on company profile
 */

const { createClient } = require('@supabase/supabase-js');

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_KEY;

const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);

/**
 * Scoring weights (adjust based on your priorities)
 */
const SCORING_CONFIG = {
  // Company size weights
  employeeCount: {
    '1000+': 100,
    '500-999': 90,
    '250-499': 75,
    '100-249': 60,
    '50-99': 40,
    '25-49': 25,
    '11-24': 15,
    '1-10': 5,
    'unknown': 0
  },
  
  // Industry weights (tech/software = higher priority)
  industry: {
    'Software': 50,
    'Technology': 50,
    'SaaS': 50,
    'Internet': 45,
    'Computer Software': 50,
    'Information Technology': 45,
    'Cloud Computing': 50,
    'Artificial Intelligence': 55,
    'Data Analytics': 50,
    'Cybersecurity': 50,
    'FinTech': 45,
    'E-commerce': 40,
    'Marketing': 35,
    'Consulting': 30,
    'Finance': 25,
    'Healthcare': 20,
    'Education': 15,
    'default': 10
  },
  
  // Job role/title weights
  role: {
    'CEO': 50,
    'CTO': 50,
    'VP': 45,
    'Director': 40,
    'Head': 40,
    'Manager': 30,
    'Lead': 25,
    'Senior': 20,
    'Engineer': 15,
    'Analyst': 15,
    'Consultant': 15,
    'Coordinator': 10,
    'default': 5
  },
  
  // Revenue multiplier
  revenue: {
    '100M+': 1.5,
    '50M-100M': 1.4,
    '10M-50M': 1.3,
    '5M-10M': 1.2,
    '1M-5M': 1.1,
    '<1M': 1.0,
    'unknown': 1.0
  }
};

/**
 * Calculate employee score based on count
 */
function calculateEmployeeScore(employeeCount) {
  if (!employeeCount) return SCORING_CONFIG.employeeCount['unknown'];
  
  if (employeeCount >= 1000) return SCORING_CONFIG.employeeCount['1000+'];
  if (employeeCount >= 500) return SCORING_CONFIG.employeeCount['500-999'];
  if (employeeCount >= 250) return SCORING_CONFIG.employeeCount['250-499'];
  if (employeeCount >= 100) return SCORING_CONFIG.employeeCount['100-249'];
  if (employeeCount >= 50) return SCORING_CONFIG.employeeCount['50-99'];
  if (employeeCount >= 25) return SCORING_CONFIG.employeeCount['25-49'];
  if (employeeCount >= 11) return SCORING_CONFIG.employeeCount['11-24'];
  if (employeeCount >= 1) return SCORING_CONFIG.employeeCount['1-10'];
  
  return SCORING_CONFIG.employeeCount['unknown'];
}

/**
 * Calculate industry score
 */
function calculateIndustryScore(industry) {
  if (!industry) return SCORING_CONFIG.industry['default'];
  
  // Check for exact match
  if (SCORING_CONFIG.industry[industry]) {
    return SCORING_CONFIG.industry[industry];
  }
  
  // Check for partial matches
  const industryLower = industry.toLowerCase();
  for (const [key, score] of Object.entries(SCORING_CONFIG.industry)) {
    if (key !== 'default' && industryLower.includes(key.toLowerCase())) {
      return score;
    }
  }
  
  return SCORING_CONFIG.industry['default'];
}

/**
 * Calculate role score from job title
 */
function calculateRoleScore(jobTitle) {
  if (!jobTitle) return SCORING_CONFIG.role['default'];
  
  const titleUpper = jobTitle.toUpperCase();
  
  // Check for exact matches
  for (const [role, score] of Object.entries(SCORING_CONFIG.role)) {
    if (role !== 'default' && titleUpper.includes(role)) {
      return score;
    }
  }
  
  return SCORING_CONFIG.role['default'];
}

/**
 * Calculate revenue multiplier
 */
function calculateRevenueMultiplier(revenue) {
  if (!revenue) return SCORING_CONFIG.revenue['unknown'];
  
  if (revenue >= 100000000) return SCORING_CONFIG.revenue['100M+'];
  if (revenue >= 50000000) return SCORING_CONFIG.revenue['50M-100M'];
  if (revenue >= 10000000) return SCORING_CONFIG.revenue['10M-50M'];
  if (revenue >= 5000000) return SCORING_CONFIG.revenue['5M-10M'];
  if (revenue >= 1000000) return SCORING_CONFIG.revenue['1M-5M'];
  if (revenue > 0) return SCORING_CONFIG.revenue['<1M'];
  
  return SCORING_CONFIG.revenue['unknown'];
}

/**
 * Detect if company is a Software Factory
 */
function isSoftwareFactory(companyData) {
  if (!companyData) return false;
  
  const { industry, sector, description, company_name } = companyData;
  
  // Industry/sector keywords
  const softwareKeywords = [
    'software', 'saas', 'technology', 'it services',
    'computer software', 'internet', 'cloud', 'development',
    'consulting', 'digital agency', 'web development',
    'mobile app', 'software development', 'tech consulting'
  ];
  
  // Check industry
  if (industry) {
    const industryLower = industry.toLowerCase();
    if (softwareKeywords.some(keyword => industryLower.includes(keyword))) {
      return true;
    }
  }
  
  // Check sector
  if (sector) {
    const sectorLower = sector.toLowerCase();
    if (softwareKeywords.some(keyword => sectorLower.includes(keyword))) {
      return true;
    }
  }
  
  // Check description
  if (description) {
    const descLower = description.toLowerCase();
    if (softwareKeywords.some(keyword => descLower.includes(keyword))) {
      return true;
    }
  }
  
  // Check company name
  if (company_name) {
    const nameLower = company_name.toLowerCase();
    const factoryKeywords = ['software', 'tech', 'digital', 'systems', 'solutions', 'consulting'];
    if (factoryKeywords.some(keyword => nameLower.includes(keyword))) {
      return true;
    }
  }
  
  return false;
}

/**
 * Calculate total lead score
 */
function calculateLeadScore(userData, companyData) {
  let score = 0;
  const breakdown = {};
  
  // 1. Employee count score (0-100 points)
  const employeeScore = calculateEmployeeScore(companyData?.employee_count);
  score += employeeScore;
  breakdown.employee_score = employeeScore;
  
  // 2. Industry score (0-50 points)
  const industryScore = calculateIndustryScore(companyData?.industry);
  score += industryScore;
  breakdown.industry_score = industryScore;
  
  // 3. Role score (0-50 points)
  const roleScore = calculateRoleScore(userData?.job_title);
  score += roleScore;
  breakdown.role_score = roleScore;
  
  // 4. Revenue multiplier (1.0-1.5x)
  const revenueMultiplier = calculateRevenueMultiplier(companyData?.estimated_revenue);
  score *= revenueMultiplier;
  breakdown.revenue_multiplier = revenueMultiplier;
  
  // 5. Software Factory bonus (+25 points)
  const isSoftwareCo = isSoftwareFactory(companyData);
  if (isSoftwareCo) {
    score += 25;
    breakdown.software_factory_bonus = 25;
  }
  
  // 6. Tech stack bonus (5 points per relevant tech)
  const techStackScore = (companyData?.tech_stack?.length || 0) * 5;
  score += Math.min(techStackScore, 25); // Max 25 points
  breakdown.tech_stack_score = Math.min(techStackScore, 25);
  
  // Round to 2 decimals
  score = Math.round(score * 100) / 100;
  
  return {
    total_score: score,
    breakdown,
    is_software_factory: isSoftwareCo,
    priority_tier: getPriorityTier(score)
  };
}

/**
 * Determine priority tier based on score
 */
function getPriorityTier(score) {
  if (score >= 250) return 'CRITICAL'; // Top 1%
  if (score >= 200) return 'HIGH';     // Top 5%
  if (score >= 150) return 'MEDIUM';   // Top 15%
  if (score >= 100) return 'LOW';      // Top 30%
  return 'MINIMAL';                     // Bottom 70%
}

/**
 * Check if lead is high-value prospect (trigger alert)
 */
function isHighValueProspect(companyData) {
  if (!companyData) return false;
  
  const { employee_count } = companyData;
  const isSoftwareCo = isSoftwareFactory(companyData);
  
  // High-value criteria:
  // - 500+ employees AND Software Factory
  return employee_count >= 500 && isSoftwareCo;
}

/**
 * Store lead score in database
 */
async function storeLeadScore(userId, scoreData, companyData) {
  try {
    const { data, error } = await supabase
      .from('lead_scores')
      .upsert({
        user_id: userId,
        total_score: scoreData.total_score,
        priority_tier: scoreData.priority_tier,
        employee_score: scoreData.breakdown.employee_score,
        industry_score: scoreData.breakdown.industry_score,
        role_score: scoreData.breakdown.role_score,
        revenue_multiplier: scoreData.breakdown.revenue_multiplier,
        software_factory_bonus: scoreData.breakdown.software_factory_bonus || 0,
        tech_stack_score: scoreData.breakdown.tech_stack_score || 0,
        is_software_factory: scoreData.is_software_factory,
        is_high_value_prospect: isHighValueProspect(companyData),
        scored_at: new Date().toISOString()
      }, {
        onConflict: 'user_id'
      });

    if (error) throw error;
    
    console.log(`💯 Lead score stored: ${scoreData.total_score} (${scoreData.priority_tier})`);
    return data;
  } catch (error) {
    console.error('Error storing lead score:', error);
    throw error;
  }
}

/**
 * Score a lead (user + company data)
 */
async function scoreUser(userId) {
  console.log(`\n🎯 Scoring user: ${userId}`);

  try {
    // Get user data
    const { data: userData, error: userError } = await supabase
      .from('users')
      .select('id, email, job_title, company')
      .eq('id', userId)
      .single();

    if (userError) throw userError;

    // Get company enrichment data
    const { data: companyData, error: companyError } = await supabase
      .from('company_enrichment')
      .select('*')
      .eq('user_id', userId)
      .single();

    if (companyError && companyError.code !== 'PGRST116') {
      throw companyError;
    }

    // Calculate score
    const scoreData = calculateLeadScore(userData, companyData);
    
    console.log(`\n📊 Score Breakdown:`);
    console.log(`   Employee Score: ${scoreData.breakdown.employee_score}`);
    console.log(`   Industry Score: ${scoreData.breakdown.industry_score}`);
    console.log(`   Role Score: ${scoreData.breakdown.role_score}`);
    console.log(`   Revenue Multiplier: ${scoreData.breakdown.revenue_multiplier}x`);
    console.log(`   Software Factory: ${scoreData.is_software_factory ? 'YES (+25)' : 'NO'}`);
    console.log(`   Tech Stack: +${scoreData.breakdown.tech_stack_score || 0}`);
    console.log(`   ─────────────────────────`);
    console.log(`   TOTAL SCORE: ${scoreData.total_score}`);
    console.log(`   Priority Tier: ${scoreData.priority_tier}`);

    // Store score
    await storeLeadScore(userId, scoreData, companyData);

    // Check if high-value prospect
    const isHighValue = isHighValueProspect(companyData);
    
    return {
      userId,
      email: userData.email,
      score: scoreData.total_score,
      tier: scoreData.priority_tier,
      isHighValue,
      companyName: companyData?.company_name,
      employeeCount: companyData?.employee_count
    };
  } catch (error) {
    console.error('Error scoring user:', error);
    throw error;
  }
}

/**
 * Get top leads by score
 */
async function getTopLeads(limit = 20) {
  try {
    const { data, error } = await supabase
      .from('lead_scores')
      .select(`
        *,
        users!inner(email, first_name, last_name, created_at),
        company_enrichment(company_name, employee_count, industry)
      `)
      .order('total_score', { ascending: false })
      .limit(limit);

    if (error) throw error;

    console.log(`\n🏆 Top ${limit} Leads:`);
    console.log('════════════════════════════════════════════════════════');
    
    data.forEach((lead, idx) => {
      const user = lead.users;
      const company = lead.company_enrichment;
      
      console.log(`${idx + 1}. ${user.first_name} ${user.last_name} (${user.email})`);
      console.log(`   Company: ${company?.company_name || 'Unknown'} (${company?.employee_count || '?'} employees)`);
      console.log(`   Score: ${lead.total_score} | Tier: ${lead.priority_tier}`);
      console.log(`   High Value: ${lead.is_high_value_prospect ? '⭐ YES' : 'No'}`);
      console.log('');
    });

    return data;
  } catch (error) {
    console.error('Error fetching top leads:', error);
    throw error;
  }
}

/**
 * CLI Interface
 */
async function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  if (command === 'score') {
    const userId = args[1];

    if (!userId) {
      console.error('Usage: node lead_scoring_engine.js score <userId>');
      process.exit(1);
    }

    await scoreUser(userId);
  } else if (command === 'top') {
    const limit = parseInt(args[1]) || 20;
    await getTopLeads(limit);
  } else if (command === 'test') {
    // Test scoring algorithm with mock data
    const mockUser = {
      job_title: 'VP of Engineering'
    };
    
    const mockCompany = {
      company_name: 'TechCorp Software',
      employee_count: 750,
      industry: 'Software',
      estimated_revenue: 50000000,
      tech_stack: ['React', 'Node.js', 'Python', 'AWS']
    };
    
    const scoreData = calculateLeadScore(mockUser, mockCompany);
    
    console.log('\n🧪 Test Score:');
    console.log(JSON.stringify(scoreData, null, 2));
    console.log(`\nHigh Value Prospect: ${isHighValueProspect(mockCompany)}`);
  } else {
    console.log('Lead Scoring Engine');
    console.log('===================');
    console.log('');
    console.log('Commands:');
    console.log('  score <userId>   - Score a user');
    console.log('  top [limit]      - Show top leads (default: 20)');
    console.log('  test             - Test scoring with mock data');
    console.log('');
    console.log('Examples:');
    console.log('  node lead_scoring_engine.js score user-123');
    console.log('  node lead_scoring_engine.js top 50');
    console.log('  node lead_scoring_engine.js test');
  }
}

// Export functions
module.exports = {
  calculateLeadScore,
  scoreUser,
  isHighValueProspect,
  isSoftwareFactory,
  getTopLeads,
  storeLeadScore
};

// Run CLI if called directly
if (require.main === module) {
  main().catch(error => {
    console.error('Error:', error);
    process.exit(1);
  });
}
