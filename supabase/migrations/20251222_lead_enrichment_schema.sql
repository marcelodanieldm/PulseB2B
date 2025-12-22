-- Lead Enrichment & Scoring Database Schema
-- Tracks company enrichment data and lead priority scores

-- ============================================================================
-- COMPANY ENRICHMENT TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS company_enrichment (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL UNIQUE,
  email_domain VARCHAR(255),
  
  -- Company profile
  company_name VARCHAR(255),
  employee_count INTEGER,
  employee_range VARCHAR(50),
  industry VARCHAR(255),
  sector VARCHAR(255),
  estimated_revenue BIGINT,
  
  -- Additional data
  tech_stack TEXT[],
  description TEXT,
  founded_year INTEGER,
  location VARCHAR(255),
  
  -- URLs
  logo_url TEXT,
  linkedin_url TEXT,
  twitter_url TEXT,
  
  -- Metadata
  enrichment_source VARCHAR(50), -- 'clearbit', 'hunter', 'basic'
  is_generic_provider BOOLEAN DEFAULT FALSE,
  enriched_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Foreign keys
  CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Indexes for company_enrichment
CREATE INDEX idx_company_enrichment_user_id ON company_enrichment(user_id);
CREATE INDEX idx_company_enrichment_domain ON company_enrichment(email_domain);
CREATE INDEX idx_company_enrichment_employee_count ON company_enrichment(employee_count DESC NULLS LAST);
CREATE INDEX idx_company_enrichment_industry ON company_enrichment(industry);
CREATE INDEX idx_company_enrichment_generic ON company_enrichment(is_generic_provider) WHERE is_generic_provider = FALSE;

-- ============================================================================
-- LEAD SCORES TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS lead_scores (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL UNIQUE,
  
  -- Total score and tier
  total_score DECIMAL(10, 2) NOT NULL,
  priority_tier VARCHAR(20) NOT NULL, -- 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'MINIMAL'
  
  -- Score breakdown
  employee_score INTEGER DEFAULT 0,
  industry_score INTEGER DEFAULT 0,
  role_score INTEGER DEFAULT 0,
  revenue_multiplier DECIMAL(3, 2) DEFAULT 1.0,
  software_factory_bonus INTEGER DEFAULT 0,
  tech_stack_score INTEGER DEFAULT 0,
  
  -- Flags
  is_software_factory BOOLEAN DEFAULT FALSE,
  is_high_value_prospect BOOLEAN DEFAULT FALSE,
  
  -- Metadata
  scored_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Foreign keys
  CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Indexes for lead_scores
CREATE INDEX idx_lead_scores_user_id ON lead_scores(user_id);
CREATE INDEX idx_lead_scores_total_score ON lead_scores(total_score DESC);
CREATE INDEX idx_lead_scores_priority_tier ON lead_scores(priority_tier);
CREATE INDEX idx_lead_scores_high_value ON lead_scores(is_high_value_prospect) WHERE is_high_value_prospect = TRUE;
CREATE INDEX idx_lead_scores_scored_at ON lead_scores(scored_at DESC);

-- ============================================================================
-- LEAD ALERTS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS lead_alerts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  
  -- Alert details
  alert_type VARCHAR(50) NOT NULL, -- 'high_value_prospect', 'weekly_digest', 'critical_tier'
  alert_tier VARCHAR(20), -- 'CRITICAL', 'HIGH', etc.
  lead_score DECIMAL(10, 2),
  
  -- Message
  message_sent TEXT,
  
  -- Delivery
  sent_to VARCHAR(255), -- Telegram chat ID, email, etc.
  sent_at TIMESTAMPTZ,
  delivery_status VARCHAR(20) DEFAULT 'sent', -- 'sent', 'failed', 'pending'
  
  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Foreign keys
  CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Indexes for lead_alerts
CREATE INDEX idx_lead_alerts_user_id ON lead_alerts(user_id);
CREATE INDEX idx_lead_alerts_alert_type ON lead_alerts(alert_type);
CREATE INDEX idx_lead_alerts_sent_at ON lead_alerts(sent_at DESC);
CREATE INDEX idx_lead_alerts_delivery_status ON lead_alerts(delivery_status);

-- ============================================================================
-- USERS TABLE EXTENSIONS
-- ============================================================================

-- Add columns to users table if they don't exist
ALTER TABLE users ADD COLUMN IF NOT EXISTS job_title VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS company VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS enrichment_completed BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_enriched_at TIMESTAMPTZ;

-- Index for enrichment status
CREATE INDEX IF NOT EXISTS idx_users_enrichment_completed ON users(enrichment_completed) WHERE enrichment_completed = FALSE;

-- ============================================================================
-- VIEWS
-- ============================================================================

-- View: High-value prospects with full details
CREATE OR REPLACE VIEW high_value_prospects AS
SELECT 
  u.id,
  u.email,
  u.first_name,
  u.last_name,
  u.job_title,
  u.created_at as signup_date,
  
  ce.company_name,
  ce.employee_count,
  ce.industry,
  ce.estimated_revenue,
  ce.location,
  ce.linkedin_url,
  
  ls.total_score,
  ls.priority_tier,
  ls.is_software_factory,
  ls.is_high_value_prospect,
  ls.scored_at
FROM users u
INNER JOIN company_enrichment ce ON u.id = ce.user_id
INNER JOIN lead_scores ls ON u.id = ls.user_id
WHERE ls.is_high_value_prospect = TRUE
ORDER BY ls.total_score DESC;

-- View: Lead pipeline by tier
CREATE OR REPLACE VIEW lead_pipeline_summary AS
SELECT 
  ls.priority_tier,
  COUNT(*) as lead_count,
  AVG(ls.total_score) as avg_score,
  COUNT(CASE WHEN ls.is_high_value_prospect THEN 1 END) as high_value_count,
  COUNT(CASE WHEN ce.employee_count >= 500 THEN 1 END) as large_company_count
FROM lead_scores ls
LEFT JOIN company_enrichment ce ON ls.user_id = ce.user_id
GROUP BY ls.priority_tier
ORDER BY 
  CASE ls.priority_tier
    WHEN 'CRITICAL' THEN 1
    WHEN 'HIGH' THEN 2
    WHEN 'MEDIUM' THEN 3
    WHEN 'LOW' THEN 4
    WHEN 'MINIMAL' THEN 5
  END;

-- View: Recent signups with enrichment status
CREATE OR REPLACE VIEW recent_signups_enriched AS
SELECT 
  u.id,
  u.email,
  u.first_name,
  u.last_name,
  u.created_at as signup_date,
  u.enrichment_completed,
  
  ce.company_name,
  ce.employee_count,
  ce.industry,
  
  ls.total_score,
  ls.priority_tier,
  ls.is_high_value_prospect
FROM users u
LEFT JOIN company_enrichment ce ON u.id = ce.user_id
LEFT JOIN lead_scores ls ON u.id = ls.user_id
WHERE u.created_at >= NOW() - INTERVAL '7 days'
ORDER BY u.created_at DESC;

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Function: Get lead enrichment status
CREATE OR REPLACE FUNCTION get_lead_enrichment_status(p_user_id UUID)
RETURNS TABLE (
  has_enrichment BOOLEAN,
  has_score BOOLEAN,
  is_high_value BOOLEAN,
  score DECIMAL,
  tier VARCHAR
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    EXISTS(SELECT 1 FROM company_enrichment WHERE user_id = p_user_id) as has_enrichment,
    EXISTS(SELECT 1 FROM lead_scores WHERE user_id = p_user_id) as has_score,
    COALESCE(ls.is_high_value_prospect, FALSE) as is_high_value,
    ls.total_score as score,
    ls.priority_tier as tier
  FROM users u
  LEFT JOIN lead_scores ls ON u.id = ls.user_id
  WHERE u.id = p_user_id;
END;
$$ LANGUAGE plpgsql;

-- Function: Get top leads by score
CREATE OR REPLACE FUNCTION get_top_leads(p_limit INTEGER DEFAULT 20)
RETURNS TABLE (
  user_id UUID,
  email VARCHAR,
  full_name TEXT,
  company_name VARCHAR,
  employee_count INTEGER,
  total_score DECIMAL,
  priority_tier VARCHAR,
  is_high_value BOOLEAN
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    u.id as user_id,
    u.email,
    CONCAT(u.first_name, ' ', u.last_name) as full_name,
    ce.company_name,
    ce.employee_count,
    ls.total_score,
    ls.priority_tier,
    ls.is_high_value_prospect as is_high_value
  FROM users u
  INNER JOIN lead_scores ls ON u.id = ls.user_id
  LEFT JOIN company_enrichment ce ON u.id = ce.user_id
  ORDER BY ls.total_score DESC
  LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Function: Check if user needs enrichment
CREATE OR REPLACE FUNCTION needs_enrichment(p_user_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
  v_enriched BOOLEAN;
  v_last_enriched TIMESTAMPTZ;
BEGIN
  SELECT enrichment_completed, last_enriched_at
  INTO v_enriched, v_last_enriched
  FROM users
  WHERE id = p_user_id;
  
  -- Need enrichment if not completed or older than 30 days
  RETURN v_enriched IS NULL 
    OR v_enriched = FALSE 
    OR v_last_enriched < NOW() - INTERVAL '30 days';
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================

-- Enable RLS on new tables
ALTER TABLE company_enrichment ENABLE ROW LEVEL SECURITY;
ALTER TABLE lead_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE lead_alerts ENABLE ROW LEVEL SECURITY;

-- Policy: Users can read their own enrichment data
CREATE POLICY "Users can read own enrichment"
ON company_enrichment FOR SELECT
USING (auth.uid() = user_id);

-- Policy: Users can read their own scores
CREATE POLICY "Users can read own scores"
ON lead_scores FOR SELECT
USING (auth.uid() = user_id);

-- Policy: Admins can read all enrichment data
CREATE POLICY "Admins can read all enrichment"
ON company_enrichment FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM users
    WHERE id = auth.uid()
    AND role = 'admin'
  )
);

-- Policy: Admins can read all lead scores
CREATE POLICY "Admins can read all lead scores"
ON lead_scores FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM users
    WHERE id = auth.uid()
    AND role = 'admin'
  )
);

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Trigger: Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_company_enrichment_updated_at
BEFORE UPDATE ON company_enrichment
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_lead_scores_updated_at
BEFORE UPDATE ON lead_scores
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- SAMPLE QUERIES
-- ============================================================================

-- Query: Get all high-value prospects
-- SELECT * FROM high_value_prospects;

-- Query: Get lead pipeline summary
-- SELECT * FROM lead_pipeline_summary;

-- Query: Get recent signups (last 7 days)
-- SELECT * FROM recent_signups_enriched;

-- Query: Get top 20 leads
-- SELECT * FROM get_top_leads(20);

-- Query: Check if user needs enrichment
-- SELECT needs_enrichment('user-uuid-here');

-- Query: Get lead enrichment status
-- SELECT * FROM get_lead_enrichment_status('user-uuid-here');

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Composite index for high-value prospect filtering
CREATE INDEX idx_lead_scores_high_value_composite 
ON lead_scores(is_high_value_prospect, total_score DESC) 
WHERE is_high_value_prospect = TRUE;

-- Composite index for software factory filtering
CREATE INDEX idx_lead_scores_software_factory_composite 
ON lead_scores(is_software_factory, priority_tier) 
WHERE is_software_factory = TRUE;

-- Index for company size filtering
CREATE INDEX idx_company_enrichment_large_companies 
ON company_enrichment(employee_count DESC) 
WHERE employee_count >= 500;

-- ============================================================================
-- ANALYTICS QUERIES
-- ============================================================================

-- Average score by industry
-- SELECT 
--   ce.industry,
--   COUNT(*) as lead_count,
--   AVG(ls.total_score) as avg_score,
--   MAX(ls.total_score) as max_score
-- FROM company_enrichment ce
-- INNER JOIN lead_scores ls ON ce.user_id = ls.user_id
-- WHERE ce.industry IS NOT NULL
-- GROUP BY ce.industry
-- ORDER BY avg_score DESC;

-- Score distribution by employee count ranges
-- SELECT 
--   CASE 
--     WHEN ce.employee_count >= 1000 THEN '1000+'
--     WHEN ce.employee_count >= 500 THEN '500-999'
--     WHEN ce.employee_count >= 250 THEN '250-499'
--     WHEN ce.employee_count >= 100 THEN '100-249'
--     WHEN ce.employee_count >= 50 THEN '50-99'
--     ELSE '<50'
--   END as employee_range,
--   COUNT(*) as lead_count,
--   AVG(ls.total_score) as avg_score
-- FROM company_enrichment ce
-- INNER JOIN lead_scores ls ON ce.user_id = ls.user_id
-- GROUP BY 1
-- ORDER BY avg_score DESC;

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

-- Verify tables created
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('company_enrichment', 'lead_scores', 'lead_alerts')
ORDER BY table_name;
