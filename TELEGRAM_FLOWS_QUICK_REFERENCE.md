# 🎯 Referencia Rápida - Telegram Automation Flows

## 📊 Vista General del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                    PULSEB2B AUTOMATION SYSTEM                    │
│                   Alertas Críticas en Tiempo Real                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │      GitHub Actions Workflows            │
        │      (Ejecutan automáticamente)          │
        └─────────────────────────────────────────┘
                              │
        ┌─────────────────────┴──────────────────────┐
        │                                            │
        ▼                                            ▼
┌──────────────┐                            ┌──────────────┐
│   DETECTORES │                            │  PROCESADORES│
│              │                            │              │
│ • Oracle     │                            │ • Pulse Intl │
│ • Regional   │                            │ • Lead Score │
│ • Web Scrape │                            │ • Filter     │
└──────────────┘                            └──────────────┘
        │                                            │
        └─────────────────────┬──────────────────────┘
                              ▼
                    ┌────────────────┐
                    │  FILTROS       │
                    │                │
                    │ • Score ≥85%   │
                    │ • Score ≥90    │
                    │ • Priority ≥250│
                    └────────────────┘
                              │
                              ▼
                    ┌────────────────┐
                    │  FORMATTER     │
                    │                │
                    │ • HTML Markup  │
                    │ • Dedup 24h    │
                    │ • Max 5-10     │
                    └────────────────┘
                              │
                              ▼
                    ┌────────────────┐
                    │   TELEGRAM     │
                    │    📱 BOT      │
                    │                │
                    │ • Alertas      │
                    │ • Digest       │
                    └────────────────┘
```

---

## ⏰ Calendario de Ejecución

### Cada Hora
| Hora (UTC) | Workflows Activos |
|------------|-------------------|
| 00:00 | 🚨 Funding + 🌎 Regional + 🔥 Pulse |
| 04:00 | 🔥 Pulse |
| 06:00 | 🚨 Funding |
| 08:00 | 🌎 Regional |
| 09:00 | 🎯 Leads + 📅 Digest (solo Lunes) |
| 10:00 | 🎯 Leads |
| 12:00 | 🚨 Funding + 🔥 Pulse |
| 14:00 | 🎯 Leads |
| 16:00 | 🌎 Regional + 🔥 Pulse |
| 18:00 | 🚨 Funding + 🎯 Leads |
| 20:00 | 🔥 Pulse |

---

## 🚨 Tipos de Alertas y Ejemplos

### 1. Critical Funding Alert
**Trigger:** Funding ≥$10M + Hiring Probability ≥85%

**Formato:**
```
🚨 CRITICAL FUNDING ALERT 🚨

[Company Name]

💰 Funding: $75,000,000
🎯 Hiring Probability: 92.3% (CRITICAL)
📅 Filed: 3 days ago

🔧 Tech Stack: Python, PyTorch, Kubernetes
🌐 Website: https://company.com

⚡ ACTION REQUIRED:
• Contact CTO/Engineering Lead TODAY
• Reference recent funding round
• Pitch offshore team scaling

📄 View SEC Filing
```

---

### 2. Regional Arbitrage Alert
**Trigger:** US/Canada expansion to LATAM + Score ≥60

**Formato:**
```
🌎 REGIONAL ARBITRAGE ALERT 🌎

[Company Name]

📍 Expansion: US → Mexico, Brazil
💰 Funding: $95,000,000
📊 Arbitrage Score: 95/100

💡 Cost Savings: ~65% vs US salaries
🎯 Critical Score: 95/100

⚡ IMMEDIATE ACTION:
• Target regions: Mexico, Brazil
• Pitch LATAM hiring expertise
• Reference expansion news
• Contact within 24 hours
```

---

### 3. High-Value Lead Alert
**Trigger:** Lead signup + 500+ employees + Score ≥250

**Formato:**
```
🚨 HIGH VALUE PROSPECT ALERT! 🚨

🎯 Lead Score: 285.5 (CRITICAL)

👤 Contact Information:
• Name: Sarah Johnson
• Email: cto@acme.com
• Title: CTO
• Signed up: 12/23/2025, 4:35 PM

🏢 Company Profile:
• Name: Acme Software Solutions
• Industry: Software Development
• Size: 850 employees ⭐
• Revenue: $75.0M

💡 Why High Value?
• ✅ Software Factory
• ✅ 500+ Employees
• ✅ CRITICAL Priority Tier

⚡ SALES ACTION:
• Contact within 1 hour
• Personalized demo offer
• Reference company size + industry
```

---

### 4. Pulse Score 90+ Alert
**Trigger:** Pulse Intelligence Score ≥90

**Formato:**
```
🔥🔥 CRITICAL OPPORTUNITY 🔥🔥

[Company Name]
Pulse Score: 94/100
Desperation: CRITICAL

📊 Signals:
• Expansion Density: 75%
• Tech Stack: 18 technologies
• Hiring Probability: 89%

💡 Contact immediately - Company desperately hiring

🔗 https://company.com

⏰ Detected: Dec 23, 2025 4:35 PM
```

---

### 5. Weekly Digest
**Trigger:** Lunes 9:00 AM UTC (automático)

**Formato:**
```
📅 WEEKLY DIGEST - PulseB2B

Week of December 23, 2025

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 SUMMARY:
• Total Companies: 127
• Critical Alerts: 8
• Avg Pulse Score: 76.4/100

📈 ALERT BREAKDOWN:
• 💰 Funding Rounds: 3
• 🌎 Regional Expansion: 2
• 🎯 High-Value Leads: 3
• 🔥 Pulse 90+ Scores: 0

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔥 TOP 3 OPPORTUNITIES:

   1. Anthropic AI - 94/100 (Funding)
   2. Stripe Inc. - 95/100 (Regional)
   3. Databricks - 93/100 (Pulse)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 Sistema automatizado de detección
Actualizado cada 12 horas via GitHub Actions
```

---

## 🎛️ Configuración de Umbrales

### Cambiar en Workflows

| Workflow | Variable | Valor Default | Ubicación |
|----------|----------|---------------|-----------|
| Critical Funding | `CRITICAL_THRESHOLD` | 85 | `.github/workflows/critical-funding-alert.yml` |
| Regional Arbitrage | `MIN_SCORE` | 60 | `.github/workflows/regional-arbitrage-alert.yml` |
| High-Value Leads | `SCORE_THRESHOLD` | 250 | `.github/workflows/high-value-lead-alert.yml` |
| Pulse 90+ | `PULSE_THRESHOLD` | 90 | `.github/workflows/pulse-90-alert.yml` |
| Weekly Digest | `TOP_COUNT` | 10 | `.github/workflows/weekly-digest.yml` |

### Cambiar Frecuencia (Cron)

```yaml
# Cada 6 horas
schedule:
  - cron: '0 */6 * * *'

# Cada día a las 9 AM
schedule:
  - cron: '0 9 * * *'

# Cada lunes a las 9 AM
schedule:
  - cron: '0 9 * * 1'

# Cada hora 9 AM - 6 PM
schedule:
  - cron: '0 9-18 * * *'
```

---

## 🔐 Secretos Requeridos

| Secret Name | Descripción | Ejemplo | Requerido |
|-------------|-------------|---------|-----------|
| `TELEGRAM_BOT_TOKEN` | Token del bot de Telegram | `123456789:ABCdef...` | ✅ SÍ |
| `TELEGRAM_CHAT_ID` | ID del chat/canal | `123456789` | ✅ SÍ |
| `SUPABASE_URL` | URL de Supabase | `https://xxx.supabase.co` | ⚠️ Opcional |
| `SUPABASE_SERVICE_KEY` | Service key de Supabase | `eyJhbGci...` | ⚠️ Opcional |
| `CLEARBIT_API_KEY` | API key de Clearbit | `sk_abc123...` | ⚠️ Opcional |

---

## 📊 Métricas del Sistema

### Por Workflow (Ejemplo Semanal)

```
┌─────────────────────┬──────────┬────────────┬─────────────┐
│ Workflow            │ Runs     │ Avg Time   │ Alerts Sent │
├─────────────────────┼──────────┼────────────┼─────────────┤
│ Critical Funding    │ 28/week  │ ~5 min     │ 3-5/run     │
│ Regional Arbitrage  │ 21/week  │ ~3 min     │ 1-2/run     │
│ High-Value Leads    │ 70/week  │ ~2 min     │ 0-2/run     │
│ Pulse 90+           │ 42/week  │ ~4 min     │ 2-4/run     │
│ Weekly Digest       │ 1/week   │ ~2 min     │ 1/run       │
└─────────────────────┴──────────┴────────────┴─────────────┘

Total: ~160 runs/week
Avg: ~23 runs/day
Peak: 9 AM - 6 PM UTC (business hours)
```

---

## 🚀 Comandos Rápidos

### Test Local
```bash
# Cargar configuración
. .\telegram_config.ps1

# Ejecutar test completo
python test_critical_flows_telegram_advanced.py

# Test individual
python scripts/oracle_funding_detector.py
python scripts/telegram_notifier.py
```

### GitHub Actions
```bash
# Ver workflows
gh workflow list

# Ejecutar workflow manualmente
gh workflow run "Weekly Digest"

# Ver última ejecución
gh run list --workflow="Weekly Digest"

# Ver logs
gh run view [run-id] --log
```

### Configurar Secretos
```bash
# Con GitHub CLI
gh secret set TELEGRAM_BOT_TOKEN

# Con script helper
python configure_github_secrets.py

# Manual en navegador
# Settings → Secrets → Actions → New secret
```

---

## 🐛 Troubleshooting Rápido

| Problema | Solución |
|----------|----------|
| ❌ Telegram not configured | Verifica secretos en GitHub Settings |
| ❌ No critical opportunities | Normal si no hay datos, espera siguiente ejecución |
| ❌ Module not found | Verifica requirements.txt instalado |
| ❌ Rate limit Telegram | Workflows ya limitan a 5-10 msg, aumenta delay |
| ❌ Workflow not running | Verifica cron syntax en archivo .yml |
| ⚠️ Authentication failed | Re-autentica: `gh auth login` |

---

## 📈 Roadmap de Mejoras

- [ ] Dashboard web para visualizar métricas
- [ ] Integración con CRM (Salesforce/HubSpot)
- [ ] Bot interactivo con respuestas en Telegram
- [ ] Alertas por email como backup
- [ ] Machine Learning para score prediction
- [ ] Integración con LinkedIn Sales Navigator
- [ ] Webhook a Slack/Discord
- [ ] API REST para consultas externas

---

## 📞 Links Útiles

- **Cron Generator:** https://crontab.guru/
- **GitHub CLI:** https://cli.github.com/
- **Telegram Bot API:** https://core.telegram.org/bots/api
- **GitHub Actions Docs:** https://docs.github.com/actions

---

## ✅ Quick Start Checklist

- [ ] Bot de Telegram creado (@BotFather)
- [ ] Token y Chat ID obtenidos
- [ ] Secretos configurados en GitHub
- [ ] Workflows pusheados al repositorio
- [ ] Test manual ejecutado con éxito
- [ ] Primera alerta recibida en Telegram
- [ ] Weekly Digest configurado
- [ ] Monitoring activo en GitHub Actions

---

**¡Sistema listo para producción!** 🚀

Los 5 flujos críticos están completamente automatizados y enviarán alertas a Telegram 24/7.
