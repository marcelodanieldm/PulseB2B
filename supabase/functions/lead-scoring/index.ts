// Supabase Edge Function: Lead Scoring Trigger
// Calculates lead scores when new companies or funding rounds are added

import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

interface LeadScoringPayload {
  company_name: string
  trigger_type: 'funding' | 'news' | 'jobs' | 'manual'
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    )

    const payload: LeadScoringPayload = await req.json()
    console.log('Lead scoring triggered for:', payload.company_name)

    // Fetch company data
    const { data: company, error: companyError } = await supabaseClient
      .from('companies')
      .select('*')
      .eq('company_name', payload.company_name)
      .single()

    if (companyError || !company) {
      throw new Error(`Company not found: ${payload.company_name}`)
    }

    // Fetch funding data
    const { data: fundingRounds } = await supabaseClient
      .from('funding_rounds')
      .select('*')
      .eq('company_name', payload.company_name)
      .order('announced_date', { ascending: false })

    // Fetch job postings
    const { data: jobPostings } = await supabaseClient
      .from('job_postings')
      .select('*')
      .eq('company_name', payload.company_name)

    // Fetch recent news
    const { data: newsArticles } = await supabaseClient
      .from('news_articles')
      .select('*')
      .eq('company_name', payload.company_name)
      .order('published_date', { ascending: false })
      .limit(10)

    // Calculate lead score
    let score = 0
    const factors: string[] = []

    // Funding signals
    if (fundingRounds && fundingRounds.length > 0) {
      const latestRound = fundingRounds[0]
      const daysSinceFunding = latestRound.announced_date 
        ? Math.floor((Date.now() - new Date(latestRound.announced_date).getTime()) / (1000 * 60 * 60 * 24))
        : 999

      if (daysSinceFunding < 90) {
        score += 50
        factors.push('Recent funding (< 90 days)')
      } else if (daysSinceFunding < 180) {
        score += 30
        factors.push('Funding in last 6 months')
      }

      // Large funding amounts indicate growth
      if (latestRound.amount_usd && latestRound.amount_usd > 10000000) {
        score += 30
        factors.push('Large funding round (>$10M)')
      }
    }

    // Job posting signals
    if (jobPostings && jobPostings.length > 0) {
      score += Math.min(jobPostings.length * 5, 40)
      factors.push(`${jobPostings.length} active job postings`)
    }

    // News sentiment signals
    if (newsArticles && newsArticles.length > 0) {
      const positiveEvents = ['Series A', 'Series B', 'Series C', 'Expansion', 'Acquisition']
      const negativeEvents = ['Layoffs', 'Bankruptcy', 'Shutdown']

      for (const article of newsArticles) {
        if (article.event_type) {
          if (positiveEvents.includes(article.event_type)) {
            score += 15
            factors.push(`Positive news: ${article.event_type}`)
          } else if (negativeEvents.includes(article.event_type)) {
            score -= 30
            factors.push(`Negative news: ${article.event_type}`)
          }
        }
      }
    }

    // Company size signals
    if (company.employee_count) {
      if (company.employee_count > 50 && company.employee_count < 500) {
        score += 20
        factors.push('Optimal company size (50-500 employees)')
      }
    }

    // Determine priority
    let priority = 'low'
    if (score >= 80) priority = 'critical'
    else if (score >= 60) priority = 'high'
    else if (score >= 40) priority = 'medium'

    // Insert or update lead score
    const { data: leadScore, error: scoreError } = await supabaseClient
      .from('lead_scores')
      .upsert({
        company_name: payload.company_name,
        score: Math.max(0, Math.min(100, score)),
        priority: priority,
        factors: factors,
        trigger_type: payload.trigger_type,
        calculated_at: new Date().toISOString()
      }, {
        onConflict: 'company_name'
      })
      .select()
      .single()

    if (scoreError) {
      throw scoreError
    }

    console.log('Lead score calculated:', leadScore)

    // Send notification if high-priority
    if (priority === 'critical' || priority === 'high') {
      console.log(`High-priority lead detected: ${payload.company_name} (Score: ${score})`)
      
      // You can integrate with notification services here
      // e.g., Slack webhook, Discord, email, etc.
    }

    return new Response(
      JSON.stringify({ 
        message: 'Lead score calculated successfully',
        score: score,
        priority: priority,
        factors: factors
      }),
      { 
        status: 200,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      }
    )

  } catch (error) {
    console.error('Error calculating lead score:', error)
    return new Response(
      JSON.stringify({ error: error.message }),
      { 
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      }
    )
  }
})
