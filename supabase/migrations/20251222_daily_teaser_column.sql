-- =====================================================
-- ADD DAILY_TEASER COLUMN TO SIGNALS TABLE
-- =====================================================
-- Purpose: Store NLP-generated Telegram teasers
-- Author: Senior Data Scientist
-- Date: December 22, 2025
-- =====================================================

-- Add daily_teaser column to signals table
ALTER TABLE signals 
ADD COLUMN IF NOT EXISTS daily_teaser TEXT;

-- Add index for fast lookups of recent teasers
CREATE INDEX IF NOT EXISTS idx_signals_daily_teaser 
ON signals(created_at DESC) 
WHERE daily_teaser IS NOT NULL;

COMMENT ON COLUMN signals.daily_teaser IS 'NLP-generated 3-line Telegram teaser optimized for mobile viewing';

-- =====================================================
-- HELPER FUNCTION: Get Latest Daily Teaser
-- =====================================================

CREATE OR REPLACE FUNCTION get_latest_daily_teaser()
RETURNS TABLE (
    signal_id UUID,
    company_name TEXT,
    daily_teaser TEXT,
    desperation_score INTEGER,
    created_at TIMESTAMPTZ
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.id as signal_id,
        s.company_name,
        s.daily_teaser,
        s.desperation_score,
        s.created_at
    FROM signals s
    WHERE s.daily_teaser IS NOT NULL
      AND s.created_at >= NOW() - INTERVAL '48 hours'
    ORDER BY s.created_at DESC
    LIMIT 1;
END;
$$;

COMMENT ON FUNCTION get_latest_daily_teaser IS 'Returns the most recent signal with a daily teaser (last 48 hours)';

-- Grant permissions
GRANT EXECUTE ON FUNCTION get_latest_daily_teaser TO service_role;
GRANT EXECUTE ON FUNCTION get_latest_daily_teaser TO authenticated;

-- =====================================================
-- ANALYTICS VIEW: Teaser Performance
-- =====================================================

CREATE OR REPLACE VIEW telegram_teaser_stats AS
SELECT 
    DATE(created_at) as teaser_date,
    COUNT(*) as teasers_generated,
    AVG(desperation_score) as avg_desperation_score,
    MAX(desperation_score) as max_desperation_score,
    AVG(LENGTH(daily_teaser)) as avg_teaser_length
FROM signals
WHERE daily_teaser IS NOT NULL
  AND created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY teaser_date DESC;

COMMENT ON VIEW telegram_teaser_stats IS 'Daily statistics for generated Telegram teasers';

-- Grant permissions
GRANT SELECT ON telegram_teaser_stats TO authenticated;
GRANT SELECT ON telegram_teaser_stats TO service_role;

-- =====================================================
-- SAMPLE TEASER (for testing)
-- =====================================================
-- Uncomment to test:
-- UPDATE signals 
-- SET daily_teaser = E'🏢 TechCorp AI 🇺🇸\n💎 Series B ($25M+) • React, Python, AWS\n🔥🔥 92% likely • fresh funding + rapid expansion'
-- WHERE id = (SELECT id FROM signals ORDER BY created_at DESC LIMIT 1);

-- =====================================================
-- DEPLOYMENT NOTES
-- =====================================================
-- 1. Apply migration: supabase db push
-- 2. Run Python script daily: python src/telegram_teaser_generator.py
-- 3. Schedule with cron or GitHub Actions
-- 4. Integrate with Telegram broadcast script
-- =====================================================
