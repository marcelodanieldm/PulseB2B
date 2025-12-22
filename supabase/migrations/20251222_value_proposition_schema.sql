-- =====================================================
-- VALUE PROPOSITION: COMPANY INSIGHTS AUTO-GENERATION
-- =====================================================
-- 
-- Purpose: Create compelling "teaser" data that's always visible
-- Strategy: Show HIGH-VALUE intelligence for free, gate CONTACT INFO
-- 
-- Free Data (Hooks):
--   ✅ company_insight: Auto-generated intelligence paragraph
--   ✅ tech_stack: Technologies they use
--   ✅ hiring_probability_score: Hiring intent score
--   ✅ pulse_score: Desperation score
--   ✅ regional_arbitrage_score: Cost savings potential
--   ✅ funding_fuzzy_range: Approximate funding (e.g., "$1M-$5M")
-- 
-- Gated Data (Premium Only):
--   🔒 lead_email: Actual contact email
--   🔒 direct_phone: Direct phone number
--   🔒 funding_exact_amount: Exact funding amount
-- 
-- Marketing Psychology:
--   "We show you WHO is hiring and WHY they're desperate...
--    but you need Premium to REACH them directly."
-- 
-- Date: December 22, 2025
-- =====================================================

-- =====================================================
-- STEP 1: Add company_insight field to signals table
-- =====================================================

-- Add company_insight column for auto-generated intelligence
ALTER TABLE public.signals 
ADD COLUMN IF NOT EXISTS company_insight TEXT;

-- Create index for search/filtering
CREATE INDEX IF NOT EXISTS idx_signals_company_insight 
ON public.signals USING gin(to_tsvector('english', company_insight));

COMMENT ON COLUMN public.signals.company_insight IS 'Auto-generated intelligence paragraph showing funding, tech stack, location, hiring signals - always visible to drive conversions';

-- =====================================================
-- STEP 2: Create function to generate company insights
-- =====================================================

-- Function to generate compelling company insight paragraph
CREATE OR REPLACE FUNCTION generate_company_insight(signal_row public.signals)
RETURNS TEXT
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
  insight TEXT := '';
  funding_info TEXT := '';
  tech_info TEXT := '';
  location_info TEXT := '';
  hiring_info TEXT := '';
  desperation_info TEXT := '';
  arbitrage_info TEXT := '';
BEGIN
  -- Start with company name
  insight := signal_row.company_name;
  
  -- Add funding information
  IF signal_row.funding_fuzzy_range IS NOT NULL THEN
    funding_info := ' raised ' || signal_row.funding_fuzzy_range;
    
    -- Add funding source if available from metadata
    IF signal_row.enrichment_metadata IS NOT NULL 
       AND signal_row.enrichment_metadata->>'funding_source' IS NOT NULL THEN
      funding_info := funding_info || ' (backed by ' || 
                     (signal_row.enrichment_metadata->>'funding_source') || ')';
    END IF;
    
    insight := insight || funding_info;
  END IF;
  
  -- Add location information
  IF signal_row.location IS NOT NULL THEN
    location_info := ' in ' || signal_row.location;
    insight := insight || location_info;
  END IF;
  
  -- Add tech stack information
  IF signal_row.tech_stack IS NOT NULL AND array_length(signal_row.tech_stack, 1) > 0 THEN
    tech_info := ' using ' || array_to_string(signal_row.tech_stack[1:3], ', ');
    IF array_length(signal_row.tech_stack, 1) > 3 THEN
      tech_info := tech_info || ' +' || (array_length(signal_row.tech_stack, 1) - 3)::TEXT || ' more';
    END IF;
    insight := insight || tech_info;
  END IF;
  
  -- Add hiring probability
  IF signal_row.hiring_probability_score IS NOT NULL THEN
    CASE 
      WHEN signal_row.hiring_probability_score >= 80 THEN
        hiring_info := '. 🔥 Actively hiring';
      WHEN signal_row.hiring_probability_score >= 60 THEN
        hiring_info := '. 📈 High hiring probability';
      WHEN signal_row.hiring_probability_score >= 40 THEN
        hiring_info := '. 👀 Exploring candidates';
      ELSE
        hiring_info := '';
    END CASE;
    insight := insight || hiring_info;
  END IF;
  
  -- Add pulse score (desperation level)
  IF signal_row.pulse_score IS NOT NULL THEN
    CASE 
      WHEN signal_row.pulse_score >= 8 THEN
        desperation_info := ' - URGENT need detected';
      WHEN signal_row.pulse_score >= 6 THEN
        desperation_info := ' - High urgency signals';
      WHEN signal_row.pulse_score >= 4 THEN
        desperation_info := ' - Moderate urgency';
      ELSE
        desperation_info := '';
    END CASE;
    insight := insight || desperation_info;
  END IF;
  
  -- Add regional arbitrage opportunity
  IF signal_row.regional_arbitrage_score IS NOT NULL 
     AND signal_row.regional_arbitrage_score >= 7 THEN
    arbitrage_info := '. 💰 High arbitrage opportunity (' || 
                     ROUND(signal_row.regional_arbitrage_score, 1)::TEXT || '/10 savings potential)';
    insight := insight || arbitrage_info;
  END IF;
  
  -- Add signal type context
  IF signal_row.signal_type IS NOT NULL THEN
    CASE signal_row.signal_type
      WHEN 'job_posting' THEN
        insight := insight || '. Signal: Active job posting';
      WHEN 'github_activity' THEN
        insight := insight || '. Signal: Increased GitHub activity';
      WHEN 'funding_announcement' THEN
        insight := insight || '. Signal: Recent funding round';
      WHEN 'tech_stack_change' THEN
        insight := insight || '. Signal: Tech stack migration';
      ELSE
        NULL;
    END CASE;
  END IF;
  
  -- Add employee count if available
  IF signal_row.employee_count IS NOT NULL THEN
    insight := insight || '. Team size: ~' || signal_row.employee_count::TEXT;
  END IF;
  
  -- Add period at end if not present
  IF insight !~ '\.$' THEN
    insight := insight || '.';
  END IF;
  
  RETURN insight;
END;
$$;

COMMENT ON FUNCTION generate_company_insight IS 'Generates compelling intelligence paragraph from signal data - designed to showcase value without revealing contact info';

-- =====================================================
-- STEP 3: Create trigger to auto-generate insights
-- =====================================================

-- Trigger function to auto-generate company_insight
CREATE OR REPLACE FUNCTION trigger_generate_company_insight()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
  -- Generate insight on insert or update
  NEW.company_insight := generate_company_insight(NEW);
  RETURN NEW;
END;
$$;

-- Create trigger for automatic insight generation
DROP TRIGGER IF EXISTS trig_generate_company_insight ON public.signals;
CREATE TRIGGER trig_generate_company_insight
  BEFORE INSERT OR UPDATE ON public.signals
  FOR EACH ROW
  EXECUTE FUNCTION trigger_generate_company_insight();

COMMENT ON TRIGGER trig_generate_company_insight ON public.signals 
IS 'Automatically generates company_insight paragraph before insert/update - this is the "hook" that drives premium conversions';

-- =====================================================
-- STEP 4: Update signals_secure view with insight
-- =====================================================

-- Drop existing view
DROP VIEW IF EXISTS public.signals_secure;

-- Recreate view with company_insight always visible
CREATE OR REPLACE VIEW public.signals_secure AS
SELECT 
  id,
  company_name,
  website,
  signal_type,
  
  -- ==========================================
  -- ALWAYS VISIBLE (Free Tier - The Hooks)
  -- ==========================================
  
  company_insight,  -- ✅ Intelligence paragraph (ALWAYS FREE)
  tech_stack,  -- ✅ Technologies used (ALWAYS FREE)
  hiring_probability_score,  -- ✅ Hiring intent (ALWAYS FREE)
  pulse_score,  -- ✅ Desperation level (ALWAYS FREE)
  regional_arbitrage_score,  -- ✅ Cost savings (ALWAYS FREE)
  funding_fuzzy_range,  -- ✅ Approximate funding (ALWAYS FREE)
  employee_count,  -- ✅ Team size (ALWAYS FREE)
  location,  -- ✅ Location (ALWAYS FREE)
  desperation_level,  -- ✅ Urgency level (ALWAYS FREE)
  
  -- ==========================================
  -- GATED (Premium Only - The Revenue)
  -- ==========================================
  
  CASE 
    WHEN is_user_premium() THEN lead_email
    ELSE NULL  -- 🔒 Hidden for free users
  END AS lead_email,
  
  CASE 
    WHEN is_user_premium() THEN direct_phone
    ELSE NULL  -- 🔒 Hidden for free users
  END AS direct_phone,
  
  CASE 
    WHEN is_user_premium() THEN funding_exact_amount
    ELSE NULL  -- 🔒 Hidden for free users
  END AS funding_exact_amount,
  
  -- ==========================================
  -- METADATA (Non-sensitive)
  -- ==========================================
  
  detected_at,
  enrichment_status,
  enrichment_metadata,
  last_enriched_at,
  created_at,
  updated_at
  
FROM public.signals;

COMMENT ON VIEW public.signals_secure IS 'Secure view with FREE high-value intelligence (company_insight, tech_stack, hiring_score) and GATED contact info (email, phone, exact funding)';

-- Grant access to authenticated users
GRANT SELECT ON public.signals_secure TO authenticated;
GRANT SELECT ON public.signals_secure TO anon;  -- Allow preview for non-authenticated users

-- =====================================================
-- STEP 5: Backfill existing signals with insights
-- =====================================================

-- Regenerate insights for all existing signals
UPDATE public.signals
SET company_insight = generate_company_insight(signals.*)
WHERE company_insight IS NULL;

-- Log backfill completion
DO $$
DECLARE
  updated_count INTEGER;
BEGIN
  SELECT COUNT(*) INTO updated_count FROM public.signals WHERE company_insight IS NOT NULL;
  RAISE NOTICE 'Generated company insights for % signals', updated_count;
END $$;

-- =====================================================
-- STEP 6: Add helper function for insight quality check
-- =====================================================

-- Function to assess insight quality (for A/B testing)
CREATE OR REPLACE FUNCTION assess_insight_quality(signal_row public.signals)
RETURNS INTEGER
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
  quality_score INTEGER := 0;
BEGIN
  -- Points for each data point included
  IF signal_row.funding_fuzzy_range IS NOT NULL THEN quality_score := quality_score + 2; END IF;
  IF signal_row.tech_stack IS NOT NULL AND array_length(signal_row.tech_stack, 1) > 0 THEN quality_score := quality_score + 2; END IF;
  IF signal_row.location IS NOT NULL THEN quality_score := quality_score + 1; END IF;
  IF signal_row.hiring_probability_score IS NOT NULL THEN quality_score := quality_score + 2; END IF;
  IF signal_row.pulse_score IS NOT NULL THEN quality_score := quality_score + 1; END IF;
  IF signal_row.regional_arbitrage_score IS NOT NULL THEN quality_score := quality_score + 1; END IF;
  IF signal_row.employee_count IS NOT NULL THEN quality_score := quality_score + 1; END IF;
  
  RETURN quality_score;
END;
$$;

COMMENT ON FUNCTION assess_insight_quality IS 'Returns quality score (0-10) based on data completeness - use for conversion rate optimization';

-- =====================================================
-- STEP 7: Create view for conversion optimization
-- =====================================================

-- View showing insight quality distribution
CREATE OR REPLACE VIEW public.insight_quality_analytics AS
SELECT 
  assess_insight_quality(signals.*) AS quality_score,
  COUNT(*) AS signal_count,
  ROUND(AVG(hiring_probability_score), 1) AS avg_hiring_score,
  ROUND(AVG(pulse_score), 1) AS avg_pulse_score,
  COUNT(DISTINCT company_name) AS unique_companies
FROM public.signals
GROUP BY assess_insight_quality(signals.*)
ORDER BY quality_score DESC;

COMMENT ON VIEW public.insight_quality_analytics IS 'Analytics view showing distribution of insight quality scores - higher scores = better conversion potential';

-- =====================================================
-- STEP 8: Create sample insights for testing
-- =====================================================

-- Example insights that should be generated:
-- 
-- "Acme Corp raised $1M-$5M (backed by Y Combinator) in San Francisco using React, Node.js, PostgreSQL +2 more. 🔥 Actively hiring - URGENT need detected. 💰 High arbitrage opportunity (8.5/10 savings potential). Signal: Active job posting. Team size: ~25."
-- 
-- "TechStart in Buenos Aires using Ruby on Rails, React, Redis. 📈 High hiring probability - High urgency signals. 💰 High arbitrage opportunity (9.2/10 savings potential). Signal: Recent funding round. Team size: ~15."
-- 
-- "GlobalSoft raised $10M-$50M in Remote using Python, Django, AWS +5 more. 🔥 Actively hiring. Signal: Increased GitHub activity. Team size: ~50."

-- =====================================================
-- STEP 9: Add insight templates for specific patterns
-- =====================================================

-- Function to generate specialized insights for YC companies
CREATE OR REPLACE FUNCTION generate_yc_insight(signal_row public.signals)
RETURNS TEXT
LANGUAGE plpgsql
IMMUTABLE
AS $$
BEGIN
  IF signal_row.enrichment_metadata IS NOT NULL 
     AND (signal_row.enrichment_metadata->>'funding_source' ILIKE '%Y Combinator%' 
          OR signal_row.enrichment_metadata->>'funding_source' ILIKE '%YC%') THEN
    RETURN '🚀 Y Combinator backed startup ' || generate_company_insight(signal_row);
  END IF;
  
  RETURN generate_company_insight(signal_row);
END;
$$;

-- Function to generate specialized insights for high-arbitrage opportunities
CREATE OR REPLACE FUNCTION generate_arbitrage_insight(signal_row public.signals)
RETURNS TEXT
LANGUAGE plpgsql
IMMUTABLE
AS $$
BEGIN
  IF signal_row.regional_arbitrage_score >= 8 THEN
    RETURN '💎 PREMIUM ARBITRAGE: ' || generate_company_insight(signal_row);
  END IF;
  
  RETURN generate_company_insight(signal_row);
END;
$$;

-- =====================================================
-- STEP 10: Create A/B testing framework
-- =====================================================

-- Table to track which insights drove conversions
CREATE TABLE IF NOT EXISTS public.insight_conversions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  signal_id UUID REFERENCES public.signals(id) ON DELETE CASCADE,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  insight_version TEXT,  -- 'standard', 'yc_emphasis', 'arbitrage_emphasis'
  viewed_at TIMESTAMPTZ DEFAULT NOW(),
  converted_to_premium BOOLEAN DEFAULT FALSE,
  converted_at TIMESTAMPTZ,
  time_to_conversion_seconds INTEGER,
  CONSTRAINT unique_user_signal_view UNIQUE(signal_id, user_id, viewed_at)
);

CREATE INDEX idx_insight_conversions_signal ON public.insight_conversions(signal_id);
CREATE INDEX idx_insight_conversions_user ON public.insight_conversions(user_id);
CREATE INDEX idx_insight_conversions_converted ON public.insight_conversions(converted_to_premium) WHERE converted_to_premium = true;

COMMENT ON TABLE public.insight_conversions IS 'Tracks which company insights led to premium conversions - use for A/B testing and optimization';

-- Enable RLS
ALTER TABLE public.insight_conversions ENABLE ROW LEVEL SECURITY;

-- Policy: Service role can insert/update (analytics tracking)
CREATE POLICY "Service role can manage insight conversions"
  ON public.insight_conversions
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- =====================================================
-- STEP 11: Create conversion analytics view
-- =====================================================

CREATE OR REPLACE VIEW public.insight_conversion_analytics AS
SELECT 
  ic.insight_version,
  COUNT(*) AS total_views,
  SUM(CASE WHEN ic.converted_to_premium THEN 1 ELSE 0 END) AS conversions,
  ROUND(
    100.0 * SUM(CASE WHEN ic.converted_to_premium THEN 1 ELSE 0 END) / COUNT(*), 
    2
  ) AS conversion_rate_percent,
  ROUND(AVG(ic.time_to_conversion_seconds) / 60, 1) AS avg_time_to_conversion_minutes,
  ROUND(AVG(iq.quality_score), 1) AS avg_insight_quality
FROM public.insight_conversions ic
LEFT JOIN LATERAL (
  SELECT assess_insight_quality(s.*) AS quality_score
  FROM public.signals s
  WHERE s.id = ic.signal_id
) iq ON true
GROUP BY ic.insight_version
ORDER BY conversion_rate_percent DESC;

COMMENT ON VIEW public.insight_conversion_analytics IS 'A/B testing results showing which insight styles drive highest conversion rates';

-- =====================================================
-- DEPLOYMENT CHECKLIST
-- =====================================================
-- 
-- 1. Apply migration: supabase db push
-- 2. Verify insights generated: SELECT company_insight FROM signals LIMIT 5;
-- 3. Test free user experience: Query signals_secure as non-premium user
-- 4. Test premium user experience: Query signals_secure as premium user
-- 5. Update frontend to display company_insight prominently
-- 6. Add analytics tracking for insight views
-- 7. Monitor conversion rates by insight quality
-- 
-- =====================================================

-- Migration complete
SELECT 'Value Proposition Schema Complete - Company Insights Generated' AS status;
