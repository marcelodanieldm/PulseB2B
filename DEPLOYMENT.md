# 🚀 Deployment Guide

Guía completa para deployar PulseB2B en AWS con arquitectura serverless.

## Prerequisitos

- **AWS Account** con credenciales configuradas
- **AWS CLI** instalado y configurado
- **AWS SAM CLI** instalado
- **Node.js 18+** instalado
- **Cuenta Supabase** creada

## 📋 Paso a Paso

### 1. Configurar AWS CLI

```bash
# Instalar AWS CLI (si no está instalado)
# Windows: https://awscli.amazonaws.com/AWSCLIV2.msi
# macOS: brew install awscli
# Linux: sudo apt install awscli

# Configurar credenciales
aws configure
# AWS Access Key ID: YOUR_KEY
# AWS Secret Access Key: YOUR_SECRET
# Default region: us-east-1
# Default output format: json

# Verificar
aws sts get-caller-identity
```

### 2. Instalar AWS SAM CLI

```bash
# Windows (con Chocolatey)
choco install aws-sam-cli

# macOS
brew tap aws/tap
brew install aws-sam-cli

# Linux
pip install aws-sam-cli

# Verificar
sam --version
```

### 3. Configurar Supabase

```bash
# 1. Ir a https://supabase.com
# 2. Crear nuevo proyecto
# 3. En SQL Editor, ejecutar: supabase/schema.sql
# 4. Ir a Settings > API
# 5. Copiar:
#    - Project URL
#    - service_role key (secret)
```

### 4. Preparar el Proyecto

```bash
cd PulseB2B

# Instalar dependencias Node.js
npm install

# Instalar Playwright
npx playwright install chromium

# Copiar variables de entorno
cp .env.example .env

# Editar .env con tus credenciales
```

### 5. Build del Proyecto

```bash
# SAM build empaqueta todo
sam build

# Output:
# Building codeuri: ...
# Build Succeeded
```

### 6. Deploy (Primera Vez)

```bash
sam deploy --guided
```

Responder las preguntas:

```
Stack Name [pulseb2b-stack]: pulseb2b-production
AWS Region [us-east-1]: us-east-1
Parameter SupabaseUrl []: https://your-project.supabase.co
Parameter SupabaseKey []: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Parameter ProxyMode [free]: free
Parameter SlackWebhookUrl []: https://hooks.slack.com/services/YOUR/WEBHOOK
Parameter DiscordWebhookUrl []: 
Confirm changes before deploy [Y/n]: Y
Allow SAM CLI IAM role creation [Y/n]: Y
Disable rollback [y/N]: N
Save arguments to configuration file [Y/n]: Y
SAM configuration file [samconfig.toml]: samconfig.toml
SAM configuration environment [default]: default
```

Esperar ~5-10 minutos. Output:

```
CloudFormation outputs from deployed stack
--------------------------------------------------------------------------------
Outputs
--------------------------------------------------------------------------------
Key                 ApiGatewayUrl
Description         API Gateway endpoint URL
Value               https://xxxxx.execute-api.us-east-1.amazonaws.com/Prod/

Key                 ScraperFunctionUSEast1Arn
Description         Scraper function ARN for US East 1
Value               arn:aws:lambda:us-east-1:xxxx:function:pulseb2b-scraper-us-east-1
--------------------------------------------------------------------------------

Successfully created/updated stack - pulseb2b-production
```

### 7. Verificar Deployment

```bash
# Listar funciones
aws lambda list-functions --query 'Functions[?contains(FunctionName, `pulseb2b`)].FunctionName'

# Output:
# [
#   "pulseb2b-scraper-us-east-1",
#   "pulseb2b-scraper-eu-west-1",
#   "pulseb2b-scraper-sa-east-1",
#   "pulseb2b-orchestrator"
# ]

# Test manual
aws lambda invoke \
  --function-name pulseb2b-scraper-us-east-1 \
  --payload '{"region":"us-east-1"}' \
  --cli-binary-format raw-in-base64-out \
  response.json

# Ver resultado
cat response.json
```

### 8. Configurar Watchlist

```bash
# Crear script addCompanies.js
node scripts/addCompanies.js
```

**scripts/addCompanies.js:**
```javascript
require('dotenv').config();
const WatchlistManager = require('./webhooks/watchlistManager');

async function main() {
  const manager = new WatchlistManager();
  
  const companies = [
    {
      name: 'Anthropic',
      careers_url: 'https://www.anthropic.com/careers',
      scraper_type: 'greenhouse',
      region: 'us',
      priority: 10,
      notification_channels: ['webhook', 'slack']
    },
    {
      name: 'OpenAI',
      careers_url: 'https://openai.com/careers',
      scraper_type: 'lever',
      region: 'us',
      priority: 10,
      notification_channels: ['webhook', 'slack']
    },
    // Agregar más...
  ];
  
  for (const company of companies) {
    await manager.addCompany(company);
    console.log(`✓ Added ${company.name}`);
  }
}

main().catch(console.error);
```

```bash
node scripts/addCompanies.js
```

### 9. Monitorear Ejecución

```bash
# Ver logs en tiempo real
sam logs -n pulseb2b-scraper-us-east-1 --tail

# O con AWS CLI
aws logs tail /aws/lambda/pulseb2b-scraper-us-east-1 --follow
```

### 10. Deploys Subsecuentes

```bash
# Sin --guided (usa samconfig.toml)
sam build && sam deploy
```

## 🔧 Configuración Post-Deploy

### Actualizar Variables de Entorno

```bash
# Via AWS CLI
aws lambda update-function-configuration \
  --function-name pulseb2b-scraper-us-east-1 \
  --environment Variables="{
    SUPABASE_URL=https://new-url.supabase.co,
    SUPABASE_KEY=new-key,
    SLACK_WEBHOOK_URL=https://hooks.slack.com/...
  }"
```

### Ajustar Frecuencia de Scraping

```yaml
# En template.yaml
Events:
  ScheduledEvent:
    Type: Schedule
    Properties:
      Schedule: rate(2 hours)  # Cambiar aquí
```

```bash
sam build && sam deploy
```

### Aumentar Timeout o Memoria

```yaml
# En template.yaml > Globals > Function
Timeout: 900  # Segundos (max 15 min)
MemorySize: 3008  # MB (más memoria = más CPU)
```

## 📊 Monitoreo y Alertas

### CloudWatch Dashboard

```bash
# Crear dashboard personalizado
aws cloudwatch put-dashboard \
  --dashboard-name PulseB2B \
  --dashboard-body file://cloudwatch-dashboard.json
```

**cloudwatch-dashboard.json:**
```json
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/Lambda", "Invocations", {"stat": "Sum"}],
          [".", "Errors", {"stat": "Sum"}],
          [".", "Duration", {"stat": "Average"}]
        ],
        "period": 300,
        "stat": "Average",
        "region": "us-east-1",
        "title": "Lambda Metrics"
      }
    }
  ]
}
```

### Alarmas CloudWatch

```bash
# Alarma si hay errores
aws cloudwatch put-metric-alarm \
  --alarm-name pulseb2b-errors \
  --alarm-description "Alert on Lambda errors" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 1 \
  --alarm-actions arn:aws:sns:us-east-1:ACCOUNT_ID:alerts
```

## 💰 Optimización de Costos

### 1. Ajustar Memoria Lambda

```yaml
# Menos memoria = más barato (pero más lento)
MemorySize: 2048  # En vez de 3008
```

### 2. Reducir Frecuencia

```yaml
# De cada 4 horas a cada 6 horas
Schedule: rate(6 hours)
```

### 3. Limitar Empresas por Ejecución

```javascript
// En lambda/scraper.js
const config = {
  maxCompanies: 5  // En vez de 10
};
```

### 4. Cleanup de Datos Antiguos

```sql
-- Crear función programada en Supabase
CREATE OR REPLACE FUNCTION cleanup_old_data()
RETURNS void AS $$
BEGIN
  -- Eliminar jobs > 90 días
  DELETE FROM jobs WHERE scraped_at < NOW() - INTERVAL '90 days';
  
  -- Eliminar logs > 30 días
  DELETE FROM scrape_logs WHERE scraped_at < NOW() - INTERVAL '30 days';
END;
$$ LANGUAGE plpgsql;

-- Programar con pg_cron (Supabase Pro)
SELECT cron.schedule('cleanup', '0 2 * * *', 'SELECT cleanup_old_data()');
```

## 🐛 Troubleshooting

### Error: "Rate exceeded"

**Causa:** Demasiados requests a sitios web.

**Solución:**
1. Aumentar delays en [scrapers/jobScraper.js](scrapers/jobScraper.js)
2. Activar proxies: `PROXY_MODE=free`
3. Reducir `maxCompanies`

### Error: "Timeout"

**Causa:** Lambda timeout (15 min max).

**Solución:**
1. Reducir `maxCompanies` por ejecución
2. Optimizar selectores CSS en watchlist
3. Distribuir carga con orchestrator

### Error: "Memory exceeded"

**Causa:** Playwright necesita mucha memoria.

**Solución:**
```yaml
MemorySize: 3008  # Máximo para Lambda
```

### Error: "Supabase connection"

**Causa:** Credenciales incorrectas o red.

**Verificar:**
```bash
curl https://your-project.supabase.co/rest/v1/watchlist \
  -H "apikey: YOUR_KEY" \
  -H "Authorization: Bearer YOUR_KEY"
```

## 🔄 Actualizar Stack

### Cambiar Parámetros

```bash
# Re-ejecutar con nuevos parámetros
sam deploy --guided

# O editar samconfig.toml y:
sam deploy
```

### Eliminar Stack Completo

```bash
# ⚠️ Esto elimina TODO
aws cloudformation delete-stack --stack-name pulseb2b-production

# Verificar eliminación
aws cloudformation describe-stacks --stack-name pulseb2b-production
```

## 🌍 Deploy Multi-Región

Para deploy en múltiples regiones AWS:

```bash
# Deploy en us-east-1
sam deploy --region us-east-1 --stack-name pulseb2b-us

# Deploy en eu-west-1
sam deploy --region eu-west-1 --stack-name pulseb2b-eu

# Deploy en sa-east-1
sam deploy --region sa-east-1 --stack-name pulseb2b-sa
```

Cada región tendrá sus propias funciones Lambda.

## ✅ Checklist de Deploy

- [ ] AWS CLI configurado
- [ ] SAM CLI instalado
- [ ] Supabase proyecto creado
- [ ] Schema SQL ejecutado en Supabase
- [ ] Variables de entorno configuradas en .env
- [ ] `npm install` ejecutado
- [ ] `sam build` exitoso
- [ ] `sam deploy --guided` completado
- [ ] Funciones Lambda verificadas
- [ ] Empresas agregadas a watchlist
- [ ] Primera ejecución testeada
- [ ] Webhooks configurados (opcional)
- [ ] CloudWatch alarmas configuradas (opcional)

---

**¡Deployment completo!** 🎉

Tus Lambda functions ahora ejecutan cada 4-6 horas automáticamente. Monitorea en CloudWatch Logs.
