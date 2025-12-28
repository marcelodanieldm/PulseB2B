-- SQL: Create email_logs table for monitoring
CREATE TABLE IF NOT EXISTS email_logs (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES profiles(id),
  email_type TEXT NOT NULL,
  status TEXT NOT NULL,
  sent_at TIMESTAMP DEFAULT NOW(),
  opened_at TIMESTAMP,
  bounced_at TIMESTAMP,
  meta JSONB
);
