// Supabase Edge Function: News Webhook Handler
// Handles incoming webhooks from news sources and processes them

import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

interface NewsWebhookPayload {
  source: string
  article_url: string
  title: string
  description?: string
  published_date?: string
  company_name?: string
  event_type?: string
  funding_amount?: number
}

serve(async (req) => {
  // Handle CORS preflight requests
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    // Initialize Supabase client
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    )

    // Parse incoming webhook
    const payload: NewsWebhookPayload = await req.json()
    
    console.log('Received news webhook:', payload)

    // Validate payload
    if (!payload.article_url || !payload.title) {
      return new Response(
        JSON.stringify({ error: 'Missing required fields: article_url, title' }),
        { 
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        }
      )
    }

    // Check for duplicate articles
    const { data: existingArticle } = await supabaseClient
      .from('news_articles')
      .select('id')
      .eq('article_url', payload.article_url)
      .single()

    if (existingArticle) {
      console.log('Article already exists, skipping')
      return new Response(
        JSON.stringify({ message: 'Article already processed', id: existingArticle.id }),
        { 
          status: 200,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        }
      )
    }

    // Insert news article
    const { data: article, error: articleError } = await supabaseClient
      .from('news_articles')
      .insert({
        source: payload.source,
        article_url: payload.article_url,
        title: payload.title,
        description: payload.description,
        published_date: payload.published_date,
        company_name: payload.company_name,
        event_type: payload.event_type,
        created_at: new Date().toISOString()
      })
      .select()
      .single()

    if (articleError) {
      throw articleError
    }

    console.log('Article inserted:', article)

    // If funding information is provided, also create funding record
    if (payload.company_name && payload.funding_amount) {
      const { data: funding, error: fundingError } = await supabaseClient
        .from('funding_rounds')
        .insert({
          company_name: payload.company_name,
          amount_usd: payload.funding_amount,
          funding_type: payload.event_type || 'Unknown',
          source_url: payload.article_url,
          announced_date: payload.published_date,
          created_at: new Date().toISOString()
        })
        .select()
        .single()

      if (fundingError) {
        console.error('Error inserting funding:', fundingError)
      } else {
        console.log('Funding record created:', funding)
      }
    }

    // Trigger lead scoring if high-priority event
    const highPriorityEvents = ['Series A', 'Series B', 'Series C', 'IPO', 'Acquisition']
    if (payload.event_type && highPriorityEvents.includes(payload.event_type)) {
      console.log('High-priority event detected, triggering lead scoring')
      
      // You can call another edge function or webhook here
      // For now, we'll just log it
    }

    return new Response(
      JSON.stringify({ 
        message: 'Webhook processed successfully',
        article_id: article.id 
      }),
      { 
        status: 200,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      }
    )

  } catch (error) {
    console.error('Error processing webhook:', error)
    return new Response(
      JSON.stringify({ error: error.message }),
      { 
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      }
    )
  }
})
