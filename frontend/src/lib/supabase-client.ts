import { createClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

if (!supabaseUrl || !supabaseAnonKey) {
  console.warn("Missing Supabase environment variables. Using mock data.");
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    persistSession: false,
  },
});

// Helper function to fetch high priority leads
export async function getHighPriorityLeads(limit: number = 20) {
  const { data, error } = await supabase
    .from("high_priority_leads")
    .select("*")
    .gte("score", 60)
    .order("score", { ascending: false })
    .limit(limit);

  if (error) {
    console.error("Error fetching leads:", error);
    return [];
  }

  return data || [];
}

// Helper function to fetch recent activity
export async function getRecentActivity(days: number = 7) {
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - days);

  const { data, error } = await supabase
    .from("recent_activity")
    .select("*")
    .gte("activity_date", startDate.toISOString())
    .order("activity_date", { ascending: false })
    .limit(50);

  if (error) {
    console.error("Error fetching activity:", error);
    return [];
  }

  return data || [];
}

// Helper function to fetch company details
export async function getCompanyDetails(companyName: string) {
  const { data, error } = await supabase
    .from("companies")
    .select(
      `
      *,
      funding_rounds (*),
      job_postings (*),
      news_articles (*),
      lead_scores (*)
    `
    )
    .eq("company_name", companyName)
    .single();

  if (error) {
    console.error("Error fetching company:", error);
    return null;
  }

  return data;
}

// Helper function to get dashboard stats
export async function getDashboardStats() {
  // Count opportunities
  const { count: opportunitiesCount } = await supabase
    .from("lead_scores")
    .select("*", { count: "exact", head: true })
    .gte("score", 60);

  // Sum recent funding
  const { data: recentFunding } = await supabase
    .from("funding_rounds")
    .select("amount_usd")
    .gte("announced_date", new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString());

  const totalFunding = recentFunding?.reduce((sum, item) => sum + (item.amount_usd || 0), 0) || 0;

  // Count active jobs
  const { count: jobsCount } = await supabase
    .from("job_postings")
    .select("*", { count: "exact", head: true })
    .gte("posted_date", new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString());

  return {
    opportunities: opportunitiesCount || 0,
    fundingAmount: totalFunding,
    activeJobs: jobsCount || 0,
  };
}
