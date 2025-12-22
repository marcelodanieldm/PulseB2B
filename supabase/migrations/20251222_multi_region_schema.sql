-- Multi-Region Global Crawler Schema Update
-- ==========================================
-- Adds columns for multi-region lead tracking
-- 
-- New Columns:
-- - country_code: ISO 3166-1 alpha-2 (US, CA, MX, AR, etc.)
-- - timezone_match: Hours offset from EST (0 = EST, +2 = Argentina, -1 = Mexico)
-- - currency_type: ISO 4217 currency code (USD, CAD, MXN, ARS, etc.)
-- - job_urls: Array of job posting URLs from regional boards
-- - last_scraped_region: Which region last updated this record
-- - scrape_count: How many times this company has been scraped
--
-- Author: PulseB2B Senior Backend Engineer
-- Date: 2025-12-22

-- ============================================
-- 1. Add New Columns to leads_global table
-- ============================================

-- Country code (ISO 3166-1 alpha-2)
ALTER TABLE leads_global 
ADD COLUMN IF NOT EXISTS country_code VARCHAR(2) DEFAULT 'US';

-- Timezone offset from EST (positive = ahead, negative = behind)
ALTER TABLE leads_global 
ADD COLUMN IF NOT EXISTS timezone_match INTEGER DEFAULT 0;

-- Currency type (ISO 4217)
ALTER TABLE leads_global 
ADD COLUMN IF NOT EXISTS currency_type VARCHAR(3) DEFAULT 'USD';

-- Job posting URLs from regional boards
ALTER TABLE leads_global 
ADD COLUMN IF NOT EXISTS job_urls TEXT[] DEFAULT '{}';

-- Last scraped region (for tracking)
ALTER TABLE leads_global 
ADD COLUMN IF NOT EXISTS last_scraped_region VARCHAR(50);

-- Scrape count (incremented on each update)
ALTER TABLE leads_global 
ADD COLUMN IF NOT EXISTS scrape_count INTEGER DEFAULT 1;

-- Regional job board sources
ALTER TABLE leads_global 
ADD COLUMN IF NOT EXISTS job_board_sources TEXT[] DEFAULT '{}';

-- ============================================
-- 2. Create Indexes for Performance
-- ============================================

-- Index on country_code for regional filtering
CREATE INDEX IF NOT EXISTS idx_leads_global_country_code 
ON leads_global(country_code);

-- Index on timezone_match for scheduling optimization
CREATE INDEX IF NOT EXISTS idx_leads_global_timezone 
ON leads_global(timezone_match);

-- Composite index for regional queries
CREATE INDEX IF NOT EXISTS idx_leads_global_region_country 
ON leads_global(last_scraped_region, country_code);

-- Index on scrape_count for freshness queries
CREATE INDEX IF NOT EXISTS idx_leads_global_scrape_count 
ON leads_global(scrape_count DESC);

-- ============================================
-- 3. Add Constraints
-- ============================================

-- Timezone must be reasonable (-12 to +14 hours)
ALTER TABLE leads_global 
ADD CONSTRAINT check_timezone_match 
CHECK (timezone_match >= -12 AND timezone_match <= 14);

-- Scrape count must be positive
ALTER TABLE leads_global 
ADD CONSTRAINT check_scrape_count 
CHECK (scrape_count >= 0);

-- ============================================
-- 4. Create View for Regional Analysis
-- ============================================

CREATE OR REPLACE VIEW regional_leads_summary AS
SELECT 
    country_code,
    currency_type,
    timezone_match,
    COUNT(*) as total_leads,
    AVG(pulse_score) as avg_pulse_score,
    AVG(hiring_probability) as avg_hiring_probability,
    COUNT(CASE WHEN pulse_score >= 90 THEN 1 END) as critical_leads,
    MAX(last_seen) as most_recent_activity
FROM leads_global
WHERE pulse_score IS NOT NULL
GROUP BY country_code, currency_type, timezone_match
ORDER BY total_leads DESC;

-- ============================================
-- 5. Create View for Timezone Optimization
-- ============================================

CREATE OR REPLACE VIEW timezone_coverage AS
SELECT 
    timezone_match,
    STRING_AGG(DISTINCT country_code, ', ' ORDER BY country_code) as countries,
    COUNT(*) as total_leads,
    COUNT(CASE WHEN pulse_score >= 80 THEN 1 END) as high_priority_leads
FROM leads_global
GROUP BY timezone_match
ORDER BY timezone_match;

-- ============================================
-- 6. Create Function for Smart Upsert
-- ============================================

CREATE OR REPLACE FUNCTION upsert_global_lead(
    p_company_name VARCHAR,
    p_country_code VARCHAR,
    p_job_count INTEGER,
    p_job_urls TEXT[],
    p_timezone_match INTEGER,
    p_currency_type VARCHAR,
    p_region VARCHAR
)
RETURNS INTEGER AS $$
DECLARE
    v_existing_id INTEGER;
    v_result_count INTEGER;
BEGIN
    -- Check if lead exists (by company name + country)
    SELECT id INTO v_existing_id
    FROM leads_global
    WHERE company_name = p_company_name 
      AND country_code = p_country_code;
    
    IF v_existing_id IS NOT NULL THEN
        -- UPDATE existing record
        UPDATE leads_global
        SET 
            job_count = job_count + p_job_count,
            job_urls = array_cat(job_urls, p_job_urls),
            last_seen = NOW(),
            last_scraped_region = p_region,
            scrape_count = scrape_count + 1
        WHERE id = v_existing_id;
        
        GET DIAGNOSTICS v_result_count = ROW_COUNT;
        RETURN v_result_count;
    ELSE
        -- INSERT new record
        INSERT INTO leads_global (
            company_name,
            country_code,
            timezone_match,
            currency_type,
            job_count,
            job_urls,
            last_scraped_region,
            scrape_count,
            last_seen
        ) VALUES (
            p_company_name,
            p_country_code,
            p_timezone_match,
            p_currency_type,
            p_job_count,
            p_job_urls,
            p_region,
            1,
            NOW()
        );
        
        GET DIAGNOSTICS v_result_count = ROW_COUNT;
        RETURN v_result_count;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 7. Grant Permissions
-- ============================================

-- Grant SELECT on views to authenticated users
GRANT SELECT ON regional_leads_summary TO authenticated;
GRANT SELECT ON timezone_coverage TO authenticated;

-- Grant EXECUTE on upsert function to service role
GRANT EXECUTE ON FUNCTION upsert_global_lead TO service_role;

-- ============================================
-- 8. Add Comments for Documentation
-- ============================================

COMMENT ON COLUMN leads_global.country_code IS 'ISO 3166-1 alpha-2 country code (US, CA, MX, AR, etc.)';
COMMENT ON COLUMN leads_global.timezone_match IS 'Hours offset from EST (0=EST, +2=Argentina, -1=Mexico)';
COMMENT ON COLUMN leads_global.currency_type IS 'ISO 4217 currency code (USD, CAD, MXN, ARS, etc.)';
COMMENT ON COLUMN leads_global.job_urls IS 'Array of job posting URLs from regional boards';
COMMENT ON COLUMN leads_global.last_scraped_region IS 'Last region that updated this record (north_america, central_america, etc.)';
COMMENT ON COLUMN leads_global.scrape_count IS 'Number of times this lead has been scraped (freshness indicator)';

COMMENT ON VIEW regional_leads_summary IS 'Aggregated lead statistics by country for regional analysis';
COMMENT ON VIEW timezone_coverage IS 'Timezone coverage overview for scheduling optimization';

COMMENT ON FUNCTION upsert_global_lead IS 'Smart upsert that increments job_count and appends job_urls for existing leads';

-- ============================================
-- Migration Complete
-- ============================================

DO $$ 
BEGIN
    RAISE NOTICE '✅ Multi-Region schema migration complete!';
    RAISE NOTICE '📊 New columns: country_code, timezone_match, currency_type';
    RAISE NOTICE '🔍 New indexes created for performance';
    RAISE NOTICE '📈 New views: regional_leads_summary, timezone_coverage';
    RAISE NOTICE '⚡ New function: upsert_global_lead()';
END $$;
