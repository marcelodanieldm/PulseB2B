# 🚀 Configuración Completa - Flujos Críticos con Telegram

## 📋 Resumen

Se han configurado **5 workflows automatizados** de GitHub Actions para alertas críticas en Telegram:

| Workflow | Frecuencia | Descripción |
|----------|-----------|-------------|
| 🚨 Critical Funding Alert | Cada 6 horas | Detecta funding rounds con ≥85% hiring probability |
| 🌎 Regional Arbitrage Alert | Cada 8 horas | Detecta expansión US/Canada → LATAM |
| 🎯 High-Value Lead Alert | Cada hora (9 AM - 6 PM) | Detecta leads con 500+ empleados y score ≥250 |
| 🔥 Pulse Score 90+ Alert | Cada 4 horas | Detecta empresas con desperation CRITICAL |
| 📅 Weekly Digest | Lunes 9 AM | Resumen semanal de top 10 oportunidades |

---

## 🔐 Paso 1: Configurar GitHub Secrets

Ve a tu repositorio en GitHub:
```
Settings → Secrets and variables → Actions → New repository secret
```

### Secretos Requeridos:

#### 1. Telegram (OBLIGATORIO)
```
TELEGRAM_BOT_TOKEN=7901617653:AAFlfhbhWw8m4RQH-JP-0OjTvv2Di8n91Oo
TELEGRAM_CHAT_ID=1021613765
```

#### 2. Supabase (Para Oracle, Pulse, Leads)
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key
```

#### 3. Clearbit (Para Lead Enrichment - Opcional)
```
CLEARBIT_API_KEY=your-clearbit-api-key
```

---

## ⚡ Paso 2: Activar Workflows

Una vez configurados los secretos, los workflows se ejecutarán automáticamente:

### ✅ Ejecución Automática:

- **🚨 Critical Funding:** Cada 6 horas (00:00, 06:00, 12:00, 18:00 UTC)
- **🌎 Regional Arbitrage:** Cada 8 horas (00:00, 08:00, 16:00 UTC)
- **🎯 High-Value Leads:** Cada hora durante 9 AM - 6 PM UTC
- **🔥 Pulse 90+:** Cada 4 horas (00:00, 04:00, 08:00, 12:00, 16:00, 20:00 UTC)
- **📅 Weekly Digest:** Lunes a las 9:00 AM UTC

### 🎮 Ejecución Manual:

Puedes ejecutar cualquier workflow manualmente:
```
Actions → [Seleccionar Workflow] → Run workflow
```

---

## 📱 Paso 3: Verificar en Telegram

Después de la primera ejecución, deberías recibir mensajes en Telegram como:

### Ejemplo - Critical Funding Alert:
```
🚨 CRITICAL FUNDING ALERT 🚨

Anthropic AI

💰 Funding: $75,000,000
🎯 Hiring Probability: 92.3% (CRITICAL)
📅 Filed: 3 days ago

🔧 Tech Stack: Python, PyTorch, Kubernetes
🌐 Website: https://anthropic.com

⚡ ACTION REQUIRED:
• Contact CTO/Engineering Lead TODAY
• Reference recent funding round
• Pitch offshore team scaling

📄 View SEC Filing
```

---

## 🧪 Paso 4: Probar Localmente (Opcional)

Si quieres probar antes de hacer push:

### Test de Flujos Críticos:
```bash
# Cargar configuración de Telegram
. .\telegram_config.ps1

# Ejecutar test avanzado (ya lo hiciste)
python test_critical_flows_telegram_advanced.py
```

### Test Individual por Flujo:
```bash
# Critical Funding
python scripts/oracle_funding_detector.py
python scripts/telegram_notifier.py

# Regional Arbitrage
python scripts/regional_nlp_recognizer.py

# High-Value Leads
node scripts/telegram_alert_service.js batch 5

# Pulse 90+
python scripts/integrate_pulse_intelligence.py
node scripts/telegram-alerts.js

# Weekly Digest
python test_critical_flows_telegram_advanced.py
```

---

## 📊 Paso 5: Monitorear Ejecución

### Ver Estado de Workflows:
```
GitHub → Actions → [Seleccionar workflow]
```

### Ver Logs:
- Click en cualquier ejecución
- Cada paso muestra logs detallados
- Artifacts disponibles por 30-90 días

### Métricas en GitHub Summary:
Cada workflow genera un resumen automático:
- Empresas analizadas
- Alertas enviadas
- Tasas de éxito
- Tiempo de ejecución

---

## 🛠️ Personalización Avanzada

### Cambiar Umbrales:

#### Critical Funding Alert:
```yaml
# .github/workflows/critical-funding-alert.yml
env:
  CRITICAL_THRESHOLD: '85'  # Cambiar aquí
```

#### Pulse Score Alert:
```yaml
# .github/workflows/pulse-90-alert.yml
env:
  PULSE_THRESHOLD: '90'  # Cambiar aquí
```

#### High-Value Leads:
```yaml
# .github/workflows/high-value-lead-alert.yml
env:
  SCORE_THRESHOLD: '250'  # Cambiar aquí
```

### Cambiar Frecuencia:

Edita el `cron` en cada workflow:

```yaml
schedule:
  # Cada 6 horas
  - cron: '0 */6 * * *'
  
  # Cada día a las 9 AM
  - cron: '0 9 * * *'
  
  # Cada lunes a las 9 AM
  - cron: '0 9 * * 1'
  
  # Cada hora 9 AM - 6 PM
  - cron: '0 9-18 * * *'
```

**Herramienta útil:** [crontab.guru](https://crontab.guru/)

---

## 🚨 Anti-Spam Features

Todos los workflows incluyen protección contra spam:

1. **Deduplicación 24h:** No envía la misma empresa dos veces en 24 horas
2. **Límite de alertas:** Máximo 5-10 alertas por ejecución
3. **Filtrado inteligente:** Solo alertas críticas (≥85%, ≥90%, ≥250)
4. **Alert log:** Mantiene historial en `data/output/alert_log.json`

---

## 📈 Dashboard de Métricas (Opcional)

Para visualizar todas las métricas:

### Opción 1: GitHub Actions Dashboard
- Ve a Actions → All workflows
- Puedes ver estado de todos los workflows

### Opción 2: Supabase Dashboard
Si tienes Supabase configurado, ve a:
```
https://app.supabase.com/project/[tu-proyecto]/editor
```

---

## 🔍 Troubleshooting

### ❌ "Telegram not configured"
**Solución:** Verificar que `TELEGRAM_BOT_TOKEN` y `TELEGRAM_CHAT_ID` estén configurados en GitHub Secrets

### ❌ "No critical opportunities found"
**Solución:** Normal si no hay datos recientes. Espera a la siguiente ejecución o ejecuta manualmente.

### ❌ "Module not found"
**Solución:** Verifica que todas las dependencias estén en `requirements.txt` y se instalen correctamente.

### ❌ Rate limit de Telegram
**Solución:** Los workflows ya limitan a 5-10 mensajes por ejecución. Si persiste, aumenta delay entre mensajes.

---

## ✅ Checklist de Activación

- [ ] Configurar `TELEGRAM_BOT_TOKEN` en GitHub Secrets
- [ ] Configurar `TELEGRAM_CHAT_ID` en GitHub Secrets
- [ ] Configurar `SUPABASE_URL` en GitHub Secrets (opcional)
- [ ] Configurar `SUPABASE_SERVICE_KEY` en GitHub Secrets (opcional)
- [ ] Hacer push de los workflows a GitHub
- [ ] Ejecutar un workflow manualmente para probar
- [ ] Verificar que llegue el mensaje a Telegram
- [ ] Esperar ejecuciones automáticas programadas
- [ ] Revisar logs y métricas en GitHub Actions

---

## 🎯 Próximos Pasos Recomendados

1. **Configurar Supabase** para persistencia de datos
2. **Agregar más fuentes de datos** (Twitter, LinkedIn, Product Hunt)
3. **Crear dashboard web** para visualizar oportunidades
4. **Integrar CRM** para tracking de leads
5. **Añadir respuestas automáticas** en Telegram (bot interactivo)

---

## 📚 Documentación Relacionada

- [TELEGRAM_IMPLEMENTATION_FINAL.md](../TELEGRAM_IMPLEMENTATION_FINAL.md)
- [GITHUB_ACTIONS_TELEGRAM.md](../GITHUB_ACTIONS_TELEGRAM.md)
- [TELEGRAM_QUICK_START.md](../TELEGRAM_QUICK_START.md)
- [test_critical_flows_telegram_advanced.py](../test_critical_flows_telegram_advanced.py)

---

## 💡 Tips Finales

1. **No commits innecesarios:** Los workflows se ejecutan automáticamente, no necesitas hacer push cada vez
2. **Revisa Artifacts:** Todos los reportes se guardan como artifacts en GitHub (30-90 días)
3. **Weekly Digest es key:** El resumen semanal te da overview de todo el sistema
4. **Personaliza mensajes:** Puedes editar los formatos de mensajes en cada workflow
5. **Monitor tokens:** Cada ejecución muestra cuántos tokens de API se consumieron

---

## 🚀 ¡Listo para Producción!

Tu sistema de alertas está completamente automatizado y listo para detectar oportunidades 24/7. 

**¡Ahora solo necesitas hacer push a GitHub y los workflows comenzarán a ejecutarse automáticamente!** 🎉
