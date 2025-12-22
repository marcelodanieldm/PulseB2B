-- ================================================
-- PulseB2B Email Tracking Schema
-- Created: 2025-12-22
-- Purpose: Track email clicks and manage tracking tokens
-- ================================================

-- ===================
-- 1. Email Tracking Tokens Table
-- ===================

CREATE TABLE IF NOT EXISTS email_tracking_tokens (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  token VARCHAR(32) NOT NULL UNIQUE,
  user_id UUID NOT NULL,
  company_id UUID NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  expires_at TIMESTAMPTZ NOT NULL,
  is_used BOOLEAN DEFAULT FALSE,
  used_at TIMESTAMPTZ,
  CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT fk_company FOREIGN KEY (company_id) REFERENCES leads_global(id) ON DELETE CASCADE
);

-- Indexes for tracking tokens
CREATE INDEX IF NOT EXISTS idx_tracking_tokens_token ON email_tracking_tokens(token);
CREATE INDEX IF NOT EXISTS idx_tracking_tokens_user ON email_tracking_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_tracking_tokens_company ON email_tracking_tokens(company_id);
CREATE INDEX IF NOT EXISTS idx_tracking_tokens_expires ON email_tracking_tokens(expires_at);

-- ===================
-- 2. Email Clicks Table
-- ===================

CREATE TABLE IF NOT EXISTS email_clicks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  company_id UUID NOT NULL,
  tracking_token VARCHAR(32) NOT NULL,
  clicked_at TIMESTAMPTZ DEFAULT NOW(),
  ip_address VARCHAR(45),
  user_agent TEXT,
  referrer TEXT,
  CONSTRAINT fk_click_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT fk_click_company FOREIGN KEY (company_id) REFERENCES leads_global(id) ON DELETE CASCADE,
  CONSTRAINT fk_click_token FOREIGN KEY (tracking_token) REFERENCES email_tracking_tokens(token) ON DELETE CASCADE
);

-- Indexes for email clicks
CREATE INDEX IF NOT EXISTS idx_email_clicks_user ON email_clicks(user_id);
CREATE INDEX IF NOT EXISTS idx_email_clicks_company ON email_clicks(company_id);
CREATE INDEX IF NOT EXISTS idx_email_clicks_clicked_at ON email_clicks(clicked_at DESC);
CREATE INDEX IF NOT EXISTS idx_email_clicks_token ON email_clicks(tracking_token);

-- ===================
-- 3. Email Campaign Logs Table
-- ===================

CREATE TABLE IF NOT EXISTS email_campaign_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  campaign_date DATE NOT NULL,
  total_recipients INTEGER NOT NULL,
  emails_sent INTEGER NOT NULL,
  emails_failed INTEGER NOT NULL,
  top_companies JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ,
  status VARCHAR(20) DEFAULT 'pending',
  error_message TEXT
);

-- Index for campaign logs
CREATE INDEX IF NOT EXISTS idx_campaign_logs_date ON email_campaign_logs(campaign_date DESC);
CREATE INDEX IF NOT EXISTS idx_campaign_logs_status ON email_campaign_logs(status);

-- ===================
-- 4. Users Table Extensions (if not exists)
-- ===================

-- Add email notification preferences to users table (if columns don't exist)
DO $$ 
BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='email_notifications_enabled') THEN
    ALTER TABLE users ADD COLUMN email_notifications_enabled BOOLEAN DEFAULT TRUE;
  END IF;
  
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='is_active') THEN
    ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE;
  END IF;
  
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='first_name') THEN
    ALTER TABLE users ADD COLUMN first_name VARCHAR(100);
  END IF;
  
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='last_name') THEN
    ALTER TABLE users ADD COLUMN last_name VARCHAR(100);
  END IF;
  
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='is_premium') THEN
    ALTER TABLE users ADD COLUMN is_premium BOOLEAN DEFAULT FALSE;
  END IF;
END $$;

-- ===================
-- 5. Views for Analytics
-- ===================

-- View: Click analytics by company
CREATE OR REPLACE VIEW company_click_analytics AS
SELECT 
  lg.id AS company_id,
  lg.company_name,
  lg.country_code,
  lg.pulse_score,
  COUNT(ec.id) AS total_clicks,
  COUNT(DISTINCT ec.user_id) AS unique_users,
  MAX(ec.clicked_at) AS last_click,
  ROUND(AVG(EXTRACT(EPOCH FROM (ec.clicked_at - ett.created_at)) / 3600), 2) AS avg_hours_to_click
FROM leads_global lg
LEFT JOIN email_clicks ec ON lg.id = ec.company_id
LEFT JOIN email_tracking_tokens ett ON ec.tracking_token = ett.token
GROUP BY lg.id, lg.company_name, lg.country_code, lg.pulse_score;

-- View: User engagement analytics
CREATE OR REPLACE VIEW user_engagement_analytics AS
SELECT 
  u.id AS user_id,
  u.email,
  u.first_name,
  u.last_name,
  u.is_premium,
  COUNT(ec.id) AS total_clicks,
  COUNT(DISTINCT ec.company_id) AS unique_companies_clicked,
  MAX(ec.clicked_at) AS last_click,
  MIN(ec.clicked_at) AS first_click
FROM users u
LEFT JOIN email_clicks ec ON u.id = ec.user_id
WHERE u.email_notifications_enabled = TRUE
GROUP BY u.id, u.email, u.first_name, u.last_name, u.is_premium;

-- View: Weekly campaign summary
CREATE OR REPLACE VIEW weekly_campaign_summary AS
SELECT 
  DATE_TRUNC('week', campaign_date) AS week_start,
  COUNT(*) AS campaigns_sent,
  SUM(total_recipients) AS total_recipients,
  SUM(emails_sent) AS total_sent,
  SUM(emails_failed) AS total_failed,
  ROUND(AVG(emails_sent::FLOAT / NULLIF(total_recipients, 0) * 100), 2) AS avg_success_rate
FROM email_campaign_logs
WHERE status = 'completed'
GROUP BY DATE_TRUNC('week', campaign_date)
ORDER BY week_start DESC;

-- ===================
-- 6. Functions
-- ===================

-- Function: Record email campaign
CREATE OR REPLACE FUNCTION record_email_campaign(
  p_campaign_date DATE,
  p_total_recipients INTEGER,
  p_emails_sent INTEGER,
  p_emails_failed INTEGER,
  p_top_companies JSONB
) RETURNS UUID AS $$
DECLARE
  v_campaign_id UUID;
BEGIN
  INSERT INTO email_campaign_logs (
    campaign_date,
    total_recipients,
    emails_sent,
    emails_failed,
    top_companies,
    completed_at,
    status
  ) VALUES (
    p_campaign_date,
    p_total_recipients,
    p_emails_sent,
    p_emails_failed,
    p_top_companies,
    NOW(),
    'completed'
  ) RETURNING id INTO v_campaign_id;
  
  RETURN v_campaign_id;
END;
$$ LANGUAGE plpgsql;

-- Function: Get click-through rate for a campaign date
CREATE OR REPLACE FUNCTION get_campaign_ctr(p_campaign_date DATE)
RETURNS TABLE(
  total_tokens INTEGER,
  total_clicks INTEGER,
  unique_clickers INTEGER,
  ctr NUMERIC
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    COUNT(DISTINCT ett.token)::INTEGER AS total_tokens,
    COUNT(ec.id)::INTEGER AS total_clicks,
    COUNT(DISTINCT ec.user_id)::INTEGER AS unique_clickers,
    ROUND(
      (COUNT(DISTINCT ec.user_id)::FLOAT / NULLIF(COUNT(DISTINCT ett.user_id), 0)) * 100,
      2
    ) AS ctr
  FROM email_tracking_tokens ett
  LEFT JOIN email_clicks ec ON ett.token = ec.tracking_token
  WHERE DATE(ett.created_at) = p_campaign_date;
END;
$$ LANGUAGE plpgsql;

-- Function: Cleanup expired tokens (older than 30 days)
CREATE OR REPLACE FUNCTION cleanup_expired_tokens()
RETURNS INTEGER AS $$
DECLARE
  v_deleted_count INTEGER;
BEGIN
  DELETE FROM email_tracking_tokens
  WHERE expires_at < NOW()
  RETURNING COUNT(*) INTO v_deleted_count;
  
  RETURN v_deleted_count;
END;
$$ LANGUAGE plpgsql;

-- ===================
-- 7. Row Level Security (Optional)
-- ===================

-- Enable RLS on tables
ALTER TABLE email_clicks ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_tracking_tokens ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_campaign_logs ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own clicks
CREATE POLICY user_own_clicks ON email_clicks
  FOR SELECT
  USING (auth.uid() = user_id);

-- Policy: Users can only see their own tokens
CREATE POLICY user_own_tokens ON email_tracking_tokens
  FOR SELECT
  USING (auth.uid() = user_id);

-- Policy: Only admins can view campaign logs (optional)
-- CREATE POLICY admin_campaign_logs ON email_campaign_logs
--   FOR ALL
--   USING (auth.jwt() ->> 'role' = 'admin');

-- ===================
-- 8. Sample Data (for testing)
-- ===================

-- Insert sample user (if users table is empty)
-- INSERT INTO users (email, first_name, last_name, is_premium, email_notifications_enabled, is_active)
-- VALUES ('test@example.com', 'Test', 'User', FALSE, TRUE, TRUE)
-- ON CONFLICT DO NOTHING;

-- ===================
-- 9. Helpful Queries
-- ===================

-- Get top 5 most clicked companies
-- SELECT * FROM company_click_analytics ORDER BY total_clicks DESC LIMIT 5;

-- Get engagement stats for all users
-- SELECT * FROM user_engagement_analytics WHERE total_clicks > 0 ORDER BY total_clicks DESC;

-- Get last week's campaign summary
-- SELECT * FROM weekly_campaign_summary LIMIT 4;

-- Get CTR for today's campaign
-- SELECT * FROM get_campaign_ctr(CURRENT_DATE);

-- Cleanup expired tokens
-- SELECT cleanup_expired_tokens();

-- ================================================
-- End of Email Tracking Schema
-- ================================================

-- Migration complete message
DO $$
BEGIN
  RAISE NOTICE '✅ Email tracking schema migration completed successfully';
  RAISE NOTICE '📊 Tables created: email_tracking_tokens, email_clicks, email_campaign_logs';
  RAISE NOTICE '📈 Views created: company_click_analytics, user_engagement_analytics, weekly_campaign_summary';
  RAISE NOTICE '⚙️  Functions created: record_email_campaign, get_campaign_ctr, cleanup_expired_tokens';
END $$;
