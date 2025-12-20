-- PulseB2B Supabase Schema
-- Schema para watchlist, jobs, y notificaciones

-- Tabla de empresas en watchlist
CREATE TABLE IF NOT EXISTS watchlist (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name TEXT NOT NULL,
  careers_url TEXT NOT NULL,
  scraper_type TEXT DEFAULT 'generic' CHECK (scraper_type IN ('greenhouse', 'lever', 'workday', 'custom', 'generic')),
  job_selector TEXT,
  region TEXT DEFAULT 'us' CHECK (region IN ('us', 'eu', 'sa', 'ap')),
  priority INTEGER DEFAULT 5 CHECK (priority >= 1 AND priority <= 10),
  webhook_url TEXT,
  notification_channels TEXT[] DEFAULT ARRAY['webhook'],
  active BOOLEAN DEFAULT true,
  metadata JSONB DEFAULT '{}',
  last_scraped_at TIMESTAMPTZ,
  last_job_count INTEGER DEFAULT 0,
  scrape_status TEXT CHECK (scrape_status IN ('success', 'failed', 'never')),
  scrape_attempts INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para watchlist
CREATE INDEX IF NOT EXISTS idx_watchlist_active ON watchlist(active);
CREATE INDEX IF NOT EXISTS idx_watchlist_region ON watchlist(region);
CREATE INDEX IF NOT EXISTS idx_watchlist_priority ON watchlist(priority DESC);
CREATE INDEX IF NOT EXISTS idx_watchlist_last_scraped ON watchlist(last_scraped_at);

-- Tabla de jobs detectados
CREATE TABLE IF NOT EXISTS jobs (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  company_id UUID REFERENCES watchlist(id) ON DELETE CASCADE,
  company_name TEXT NOT NULL,
  title TEXT NOT NULL,
  link TEXT NOT NULL UNIQUE,
  location TEXT,
  department TEXT,
  source TEXT,
  description TEXT,
  salary_range TEXT,
  employment_type TEXT,
  remote_friendly BOOLEAN DEFAULT false,
  metadata JSONB DEFAULT '{}',
  scraped_at TIMESTAMPTZ DEFAULT NOW(),
  notified BOOLEAN DEFAULT false,
  notified_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para jobs
CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company_id);
CREATE INDEX IF NOT EXISTS idx_jobs_link ON jobs(link);
CREATE INDEX IF NOT EXISTS idx_jobs_scraped_at ON jobs(scraped_at DESC);
CREATE INDEX IF NOT EXISTS idx_jobs_notified ON jobs(notified);
CREATE INDEX IF NOT EXISTS idx_jobs_title_search ON jobs USING gin(to_tsvector('english', title));

-- Tabla de notificaciones enviadas
CREATE TABLE IF NOT EXISTS notifications (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  company_id UUID REFERENCES watchlist(id) ON DELETE CASCADE,
  job_count INTEGER NOT NULL,
  channels TEXT[] DEFAULT ARRAY['webhook'],
  status TEXT DEFAULT 'sent' CHECK (status IN ('sent', 'failed', 'pending')),
  error_message TEXT,
  sent_at TIMESTAMPTZ DEFAULT NOW(),
  metadata JSONB DEFAULT '{}'
);

-- Índices para notifications
CREATE INDEX IF NOT EXISTS idx_notifications_company ON notifications(company_id);
CREATE INDEX IF NOT EXISTS idx_notifications_sent_at ON notifications(sent_at DESC);

-- Tabla de logs de scraping
CREATE TABLE IF NOT EXISTS scrape_logs (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  company_id UUID REFERENCES watchlist(id) ON DELETE CASCADE,
  region TEXT,
  proxy_used TEXT,
  jobs_found INTEGER DEFAULT 0,
  new_jobs INTEGER DEFAULT 0,
  success BOOLEAN DEFAULT true,
  error_message TEXT,
  duration_ms INTEGER,
  scraped_at TIMESTAMPTZ DEFAULT NOW(),
  metadata JSONB DEFAULT '{}'
);

-- Índices para scrape_logs
CREATE INDEX IF NOT EXISTS idx_scrape_logs_company ON scrape_logs(company_id);
CREATE INDEX IF NOT EXISTS idx_scrape_logs_scraped_at ON scrape_logs(scraped_at DESC);
CREATE INDEX IF NOT EXISTS idx_scrape_logs_success ON scrape_logs(success);

-- Función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para watchlist
DROP TRIGGER IF EXISTS update_watchlist_updated_at ON watchlist;
CREATE TRIGGER update_watchlist_updated_at
  BEFORE UPDATE ON watchlist
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Vista para estadísticas por empresa
CREATE OR REPLACE VIEW company_stats AS
SELECT 
  w.id,
  w.name,
  w.region,
  w.active,
  w.last_scraped_at,
  COUNT(DISTINCT j.id) as total_jobs,
  COUNT(DISTINCT j.id) FILTER (WHERE j.scraped_at > NOW() - INTERVAL '7 days') as jobs_last_week,
  COUNT(DISTINCT n.id) as total_notifications,
  MAX(n.sent_at) as last_notification_at,
  w.scrape_status,
  w.last_job_count
FROM watchlist w
LEFT JOIN jobs j ON j.company_id = w.id
LEFT JOIN notifications n ON n.company_id = w.id
GROUP BY w.id, w.name, w.region, w.active, w.last_scraped_at, w.scrape_status, w.last_job_count;

-- Vista para jobs recientes
CREATE OR REPLACE VIEW recent_jobs AS
SELECT 
  j.*,
  w.name as company_name,
  w.region,
  w.careers_url
FROM jobs j
JOIN watchlist w ON w.id = j.company_id
WHERE j.scraped_at > NOW() - INTERVAL '30 days'
ORDER BY j.scraped_at DESC;

-- Row Level Security (RLS)
ALTER TABLE watchlist ENABLE ROW LEVEL SECURITY;
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE scrape_logs ENABLE ROW LEVEL SECURITY;

-- Políticas RLS (permitir todo con service_role, lectura con anon)
CREATE POLICY "Allow service role all" ON watchlist FOR ALL TO service_role USING (true);
CREATE POLICY "Allow anon read" ON watchlist FOR SELECT TO anon USING (active = true);

CREATE POLICY "Allow service role all" ON jobs FOR ALL TO service_role USING (true);
CREATE POLICY "Allow anon read" ON jobs FOR SELECT TO anon USING (true);

CREATE POLICY "Allow service role all" ON notifications FOR ALL TO service_role USING (true);
CREATE POLICY "Allow service role all" ON scrape_logs FOR ALL TO service_role USING (true);

-- Función para buscar jobs por texto
CREATE OR REPLACE FUNCTION search_jobs(search_query TEXT)
RETURNS SETOF jobs AS $$
BEGIN
  RETURN QUERY
  SELECT *
  FROM jobs
  WHERE 
    to_tsvector('english', title || ' ' || COALESCE(description, '')) @@ plainto_tsquery('english', search_query)
  ORDER BY scraped_at DESC;
END;
$$ LANGUAGE plpgsql;

-- Función para obtener empresas que necesitan scraping
CREATE OR REPLACE FUNCTION get_companies_needing_scrape(hours_threshold INTEGER DEFAULT 24)
RETURNS SETOF watchlist AS $$
BEGIN
  RETURN QUERY
  SELECT *
  FROM watchlist
  WHERE 
    active = true
    AND (
      last_scraped_at IS NULL 
      OR last_scraped_at < NOW() - (hours_threshold || ' hours')::INTERVAL
    )
  ORDER BY priority DESC, last_scraped_at ASC NULLS FIRST;
END;
$$ LANGUAGE plpgsql;

-- Datos de ejemplo (opcional)
INSERT INTO watchlist (name, careers_url, scraper_type, region, priority, notification_channels) VALUES
  ('Anthropic', 'https://www.anthropic.com/careers', 'greenhouse', 'us', 10, ARRAY['webhook', 'slack']),
  ('OpenAI', 'https://openai.com/careers', 'lever', 'us', 10, ARRAY['webhook', 'slack']),
  ('Mistral AI', 'https://mistral.ai/careers', 'custom', 'eu', 9, ARRAY['webhook']),
  ('Hugging Face', 'https://huggingface.co/careers', 'lever', 'us', 9, ARRAY['webhook', 'discord']),
  ('Cohere', 'https://cohere.com/careers', 'greenhouse', 'us', 8, ARRAY['webhook'])
ON CONFLICT DO NOTHING;

-- Comentarios para documentación
COMMENT ON TABLE watchlist IS 'Lista de empresas a monitorear para detección de nuevas vacantes';
COMMENT ON TABLE jobs IS 'Vacantes detectadas de los sitios de carreras';
COMMENT ON TABLE notifications IS 'Registro de notificaciones enviadas';
COMMENT ON TABLE scrape_logs IS 'Logs de ejecuciones de scraping';
COMMENT ON COLUMN watchlist.scraper_type IS 'Tipo de sistema de careers: greenhouse, lever, workday, custom, generic';
COMMENT ON COLUMN watchlist.priority IS 'Prioridad de scraping (1-10, mayor = más importante)';
COMMENT ON COLUMN watchlist.notification_channels IS 'Canales de notificación: webhook, slack, discord, email, telegram';
