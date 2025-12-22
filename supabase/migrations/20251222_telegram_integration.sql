-- =====================================================
-- TELEGRAM BOT INTEGRATION SCHEMA
-- =====================================================
-- Purpose: Store Telegram subscribers and track engagement
-- Cost: $0 (uses Supabase free tier)
-- Author: Senior Backend Developer
-- Date: December 22, 2025
-- =====================================================

-- =====================================================
-- 1. TELEGRAM SUBSCRIBERS TABLE
-- =====================================================
-- Stores all users who have registered via /start command

CREATE TABLE IF NOT EXISTS telegram_subscribers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_id BIGINT NOT NULL UNIQUE,  -- Telegram chat ID (unique per user)
    username TEXT,                    -- Telegram username (optional, can be null)
    first_name TEXT,                  -- User's first name from Telegram
    last_name TEXT,                   -- User's last name from Telegram
    language_code TEXT DEFAULT 'en',  -- User's language preference
    is_active BOOLEAN DEFAULT true,   -- Can be set to false if user blocks bot
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_interaction_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Tracking fields
    total_commands_sent INTEGER DEFAULT 0,
    last_command TEXT,
    
    -- UTM tracking for user acquisition
    utm_source TEXT,
    utm_medium TEXT,
    utm_campaign TEXT
);

-- Index for fast lookups by chat_id (most common query)
CREATE INDEX idx_telegram_chat_id ON telegram_subscribers(chat_id);

-- Index for active subscribers (used in broadcasts)
CREATE INDEX idx_telegram_active ON telegram_subscribers(is_active) WHERE is_active = true;

-- Index for analytics queries
CREATE INDEX idx_telegram_created_at ON telegram_subscribers(created_at DESC);

COMMENT ON TABLE telegram_subscribers IS 'Stores all Telegram bot subscribers with engagement tracking';
COMMENT ON COLUMN telegram_subscribers.chat_id IS 'Unique Telegram chat ID for sending messages';
COMMENT ON COLUMN telegram_subscribers.is_active IS 'False if user blocked bot or unsubscribed';

-- =====================================================
-- 2. TELEGRAM MESSAGE ANALYTICS TABLE
-- =====================================================
-- Tracks all messages sent by the bot for analytics

CREATE TABLE IF NOT EXISTS telegram_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_id BIGINT NOT NULL,
    message_type TEXT NOT NULL,  -- 'daily_signal', 'latest_command', 'welcome', 'error'
    lead_id UUID,                -- Reference to signals table if message contains lead
    message_text TEXT,
    sent_at TIMESTAMPTZ DEFAULT NOW(),
    was_delivered BOOLEAN DEFAULT true,
    error_message TEXT,
    
    -- Analytics fields
    clicked_through BOOLEAN DEFAULT false,  -- Did user click "View Details"?
    clicked_at TIMESTAMPTZ,
    
    FOREIGN KEY (chat_id) REFERENCES telegram_subscribers(chat_id) ON DELETE CASCADE
);

-- Index for analytics queries
CREATE INDEX idx_telegram_messages_type ON telegram_messages(message_type, sent_at DESC);
CREATE INDEX idx_telegram_messages_lead ON telegram_messages(lead_id) WHERE lead_id IS NOT NULL;
CREATE INDEX idx_telegram_messages_clickthrough ON telegram_messages(clicked_through, sent_at DESC);

COMMENT ON TABLE telegram_messages IS 'Tracks all messages sent by bot for analytics and debugging';
COMMENT ON COLUMN telegram_messages.clicked_through IS 'Tracked via UTM parameters on frontend';

-- =====================================================
-- 3. TELEGRAM COMMAND LOG TABLE
-- =====================================================
-- Logs all commands received by the bot

CREATE TABLE IF NOT EXISTS telegram_command_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_id BIGINT NOT NULL,
    command TEXT NOT NULL,  -- '/start', '/latest', etc.
    command_args TEXT,      -- Any arguments passed with command
    received_at TIMESTAMPTZ DEFAULT NOW(),
    processing_time_ms INTEGER,
    success BOOLEAN DEFAULT true,
    error_message TEXT,
    
    FOREIGN KEY (chat_id) REFERENCES telegram_subscribers(chat_id) ON DELETE CASCADE
);

-- Index for analytics
CREATE INDEX idx_telegram_commands ON telegram_command_log(command, received_at DESC);
CREATE INDEX idx_telegram_command_performance ON telegram_command_log(command, processing_time_ms);

COMMENT ON TABLE telegram_command_log IS 'Logs all bot commands for debugging and performance monitoring';

-- =====================================================
-- 4. HELPER FUNCTIONS
-- =====================================================

-- Function to register or update a Telegram subscriber
CREATE OR REPLACE FUNCTION register_telegram_subscriber(
    p_chat_id BIGINT,
    p_username TEXT DEFAULT NULL,
    p_first_name TEXT DEFAULT NULL,
    p_last_name TEXT DEFAULT NULL,
    p_language_code TEXT DEFAULT 'en'
)
RETURNS UUID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_subscriber_id UUID;
BEGIN
    -- Insert or update subscriber
    INSERT INTO telegram_subscribers (
        chat_id,
        username,
        first_name,
        last_name,
        language_code,
        is_active,
        last_interaction_at
    )
    VALUES (
        p_chat_id,
        p_username,
        p_first_name,
        p_last_name,
        p_language_code,
        true,
        NOW()
    )
    ON CONFLICT (chat_id) DO UPDATE SET
        username = COALESCE(EXCLUDED.username, telegram_subscribers.username),
        first_name = COALESCE(EXCLUDED.first_name, telegram_subscribers.first_name),
        last_name = COALESCE(EXCLUDED.last_name, telegram_subscribers.last_name),
        language_code = COALESCE(EXCLUDED.language_code, telegram_subscribers.language_code),
        is_active = true,  -- Reactivate if user returns after blocking
        last_interaction_at = NOW()
    RETURNING id INTO v_subscriber_id;
    
    RETURN v_subscriber_id;
END;
$$;

-- Function to log bot commands
CREATE OR REPLACE FUNCTION log_telegram_command(
    p_chat_id BIGINT,
    p_command TEXT,
    p_command_args TEXT DEFAULT NULL,
    p_processing_time_ms INTEGER DEFAULT NULL,
    p_success BOOLEAN DEFAULT true,
    p_error_message TEXT DEFAULT NULL
)
RETURNS UUID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_log_id UUID;
BEGIN
    -- Update subscriber stats
    UPDATE telegram_subscribers
    SET 
        total_commands_sent = total_commands_sent + 1,
        last_command = p_command,
        last_interaction_at = NOW()
    WHERE chat_id = p_chat_id;
    
    -- Log the command
    INSERT INTO telegram_command_log (
        chat_id,
        command,
        command_args,
        processing_time_ms,
        success,
        error_message
    )
    VALUES (
        p_chat_id,
        p_command,
        p_command_args,
        p_processing_time_ms,
        p_success,
        p_error_message
    )
    RETURNING id INTO v_log_id;
    
    RETURN v_log_id;
END;
$$;

-- Function to get latest high-scoring lead
CREATE OR REPLACE FUNCTION get_latest_telegram_lead()
RETURNS TABLE (
    lead_id UUID,
    company_name TEXT,
    desperation_score INTEGER,
    company_insight TEXT,
    tech_stack TEXT[],
    country TEXT,
    funding_range TEXT,
    hiring_velocity TEXT
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.id,
        s.company_name,
        s.desperation_score,
        s.company_insight,
        s.tech_stack,
        s.country,
        -- Format funding range for Telegram message
        CASE 
            WHEN s.funding_stage = 'Series A' THEN '$2M-$15M'
            WHEN s.funding_stage = 'Series B' THEN '$10M-$60M'
            WHEN s.funding_stage = 'Series C+' THEN '$50M+'
            ELSE 'Undisclosed'
        END as funding_range,
        CASE 
            WHEN s.hiring_velocity > 20 THEN '🔥 URGENT'
            WHEN s.hiring_velocity > 10 THEN '📈 High'
            ELSE '✓ Active'
        END as hiring_velocity
    FROM signals s
    WHERE s.created_at >= NOW() - INTERVAL '24 hours'
      AND s.desperation_score >= 70  -- Only high-quality leads
    ORDER BY s.desperation_score DESC, s.created_at DESC
    LIMIT 1;
END;
$$;

-- Function to get all active subscribers for broadcast
CREATE OR REPLACE FUNCTION get_telegram_broadcast_list()
RETURNS TABLE (
    chat_id BIGINT,
    first_name TEXT,
    username TEXT,
    language_code TEXT
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ts.chat_id,
        ts.first_name,
        ts.username,
        ts.language_code
    FROM telegram_subscribers ts
    WHERE ts.is_active = true
    ORDER BY ts.created_at ASC;  -- Respect order of subscription
END;
$$;

-- Function to mark subscriber as inactive (blocked bot)
CREATE OR REPLACE FUNCTION deactivate_telegram_subscriber(p_chat_id BIGINT)
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    UPDATE telegram_subscribers
    SET is_active = false
    WHERE chat_id = p_chat_id;
END;
$$;

-- Function to log message delivery
CREATE OR REPLACE FUNCTION log_telegram_message(
    p_chat_id BIGINT,
    p_message_type TEXT,
    p_lead_id UUID DEFAULT NULL,
    p_message_text TEXT DEFAULT NULL,
    p_was_delivered BOOLEAN DEFAULT true,
    p_error_message TEXT DEFAULT NULL
)
RETURNS UUID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_message_id UUID;
BEGIN
    INSERT INTO telegram_messages (
        chat_id,
        message_type,
        lead_id,
        message_text,
        was_delivered,
        error_message
    )
    VALUES (
        p_chat_id,
        p_message_type,
        p_lead_id,
        p_message_text,
        p_was_delivered,
        p_error_message
    )
    RETURNING id INTO v_message_id;
    
    RETURN v_message_id;
END;
$$;

-- =====================================================
-- 5. ANALYTICS VIEWS
-- =====================================================

-- View: Daily subscriber growth
CREATE OR REPLACE VIEW telegram_growth_stats AS
SELECT 
    DATE(created_at) as signup_date,
    COUNT(*) as new_subscribers,
    SUM(COUNT(*)) OVER (ORDER BY DATE(created_at)) as total_subscribers
FROM telegram_subscribers
GROUP BY DATE(created_at)
ORDER BY signup_date DESC;

COMMENT ON VIEW telegram_growth_stats IS 'Daily subscriber acquisition metrics';

-- View: Command usage statistics
CREATE OR REPLACE VIEW telegram_command_stats AS
SELECT 
    command,
    COUNT(*) as usage_count,
    AVG(processing_time_ms) as avg_processing_ms,
    MAX(processing_time_ms) as max_processing_ms,
    ROUND(100.0 * SUM(CASE WHEN success THEN 1 ELSE 0 END) / COUNT(*), 2) as success_rate_pct
FROM telegram_command_log
WHERE received_at >= NOW() - INTERVAL '30 days'
GROUP BY command
ORDER BY usage_count DESC;

COMMENT ON VIEW telegram_command_stats IS 'Bot command performance metrics (last 30 days)';

-- View: Message delivery metrics
CREATE OR REPLACE VIEW telegram_delivery_stats AS
SELECT 
    message_type,
    COUNT(*) as total_sent,
    SUM(CASE WHEN was_delivered THEN 1 ELSE 0 END) as delivered_count,
    SUM(CASE WHEN clicked_through THEN 1 ELSE 0 END) as clicked_count,
    ROUND(100.0 * SUM(CASE WHEN was_delivered THEN 1 ELSE 0 END) / COUNT(*), 2) as delivery_rate_pct,
    ROUND(100.0 * SUM(CASE WHEN clicked_through THEN 1 ELSE 0 END) / NULLIF(SUM(CASE WHEN was_delivered THEN 1 ELSE 0 END), 0), 2) as click_through_rate_pct
FROM telegram_messages
WHERE sent_at >= NOW() - INTERVAL '30 days'
GROUP BY message_type
ORDER BY total_sent DESC;

COMMENT ON VIEW telegram_delivery_stats IS 'Message delivery and engagement metrics (last 30 days)';

-- View: Active subscribers summary
CREATE OR REPLACE VIEW telegram_active_summary AS
SELECT 
    COUNT(*) FILTER (WHERE is_active = true) as active_subscribers,
    COUNT(*) FILTER (WHERE is_active = false) as inactive_subscribers,
    COUNT(*) as total_subscribers,
    ROUND(100.0 * COUNT(*) FILTER (WHERE is_active = true) / NULLIF(COUNT(*), 0), 2) as active_rate_pct,
    AVG(total_commands_sent) FILTER (WHERE is_active = true) as avg_commands_per_user,
    MAX(last_interaction_at) FILTER (WHERE is_active = true) as most_recent_interaction
FROM telegram_subscribers;

COMMENT ON VIEW telegram_active_summary IS 'Overall bot health and engagement metrics';

-- =====================================================
-- 6. GRANT PERMISSIONS
-- =====================================================

-- Grant access to authenticated users (for reading their own data)
GRANT SELECT ON telegram_subscribers TO authenticated;
GRANT SELECT ON telegram_messages TO authenticated;
GRANT SELECT ON telegram_command_log TO authenticated;

-- Grant access to service role (for Edge Functions)
GRANT ALL ON telegram_subscribers TO service_role;
GRANT ALL ON telegram_messages TO service_role;
GRANT ALL ON telegram_command_log TO service_role;

-- Grant execute on functions to service role
GRANT EXECUTE ON FUNCTION register_telegram_subscriber TO service_role;
GRANT EXECUTE ON FUNCTION log_telegram_command TO service_role;
GRANT EXECUTE ON FUNCTION get_latest_telegram_lead TO service_role;
GRANT EXECUTE ON FUNCTION get_telegram_broadcast_list TO service_role;
GRANT EXECUTE ON FUNCTION deactivate_telegram_subscriber TO service_role;
GRANT EXECUTE ON FUNCTION log_telegram_message TO service_role;

-- =====================================================
-- 7. SEED DATA (FOR TESTING)
-- =====================================================

-- Insert a test subscriber (comment out in production)
-- INSERT INTO telegram_subscribers (chat_id, username, first_name, language_code)
-- VALUES (123456789, 'testuser', 'Test User', 'en');

-- =====================================================
-- DEPLOYMENT NOTES
-- =====================================================
-- 1. Apply this migration: supabase db push
-- 2. Deploy Edge Function: supabase functions deploy telegram-webhook
-- 3. Set Telegram Bot Token secret: supabase secrets set TELEGRAM_BOT_TOKEN=your_token
-- 4. Configure webhook: curl -X POST https://api.telegram.org/bot<TOKEN>/setWebhook \
--    -H "Content-Type: application/json" \
--    -d '{"url": "https://<project-ref>.supabase.co/functions/v1/telegram-webhook"}'
-- 5. Test with /start command in Telegram
-- =====================================================
