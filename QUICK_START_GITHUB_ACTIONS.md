# 🚀 QUICK START - GitHub Actions Testing

## ✅ Trabajo Completado

Los 17 workflows de GitHub Actions han sido analizados, debuggeados y corregidos.

---

## 📋 CHECKLIST ANTES DE DEPLOYMENT

### 1. Configurar Secretos en GitHub (CRÍTICO)

Ve a tu repositorio en GitHub:
```
Settings → Secrets and variables → Actions → New repository secret
```

**Secretos requeridos:**
- ✅ `SUPABASE_URL` - Tu URL de Supabase
- ✅ `SUPABASE_SERVICE_KEY` - Service role key
- ✅ `TELEGRAM_BOT_TOKEN` - Token del bot de Telegram
- ✅ `TELEGRAM_CHAT_ID` - ID del chat para notificaciones
- ⚠️ `SENDGRID_API_KEY` - Para envío de emails (opcional)
- ⚠️ `GOOGLE_CSE_API_KEY` - Para scraping (opcional)
- ⚠️ `CLEARBIT_API_KEY` - Para enrichment (opcional)

---

## 🧪 TESTING LOCAL (Antes de Push)

### Test 1: Validar Scripts Auxiliares
```bash
python scripts/github_actions_helpers.py generate_lead_report
python scripts/github_actions_helpers.py filter_pulse_90
python scripts/github_actions_helpers.py generate_weekly_stats
```

### Test 2: Debugger de Workflows
```bash
python debug_github_actions.py
```

### Test 3: Simular Workflow Completo
```bash
python simulate_github_workflow.py
```

### Test 4: Flujos Críticos
```bash
python test_critical_flows.py
```

---

## 🚀 TESTING EN GITHUB ACTIONS

### Paso 1: Push de Código
```bash
git add .
git commit -m "Fix: Corrected GitHub Actions workflows YAML syntax"
git push origin main
```

### Paso 2: Testing Manual (Recomendado)

Ve a GitHub → Actions → Selecciona un workflow

**Orden de testing recomendado:**

1. **Test workflows simples primero:**
   - `test-and-report-telegram.yml` - Click "Run workflow"
   - `telegram_daily_broadcast.yml` - Click "Run workflow"

2. **Test workflows de alertas:**
   - `pulse-90-alert.yml` - Click "Run workflow"
   - `regional-arbitrage-alert.yml` - Click "Run workflow"

3. **Test workflows complejos:**
   - `oracle-ghost-automation.yml` - Click "Run workflow"
   - `serverless-ghost-pipeline.yml` - Click "Run workflow"

---

## 📊 MONITOREO

### Ver Logs de Ejecución
```
GitHub → Actions → Click en el workflow → Click en el run → Ver logs
```

### Revisar Errores Comunes

**Error: "Secret not found"**
- ✅ Verifica que el secreto esté configurado en Settings → Secrets

**Error: "No such file or directory"**
- ✅ Verifica que el archivo exista en el repo
- ✅ Verifica la ruta (usar `/` no `\`)

**Error: "Module not found"**
- ✅ Verifica requirements.txt
- ✅ Agrega `pip install <module>` en el workflow

---

## 📁 ARCHIVOS IMPORTANTES

### Scripts Auxiliares:
- `scripts/github_actions_helpers.py` - Funciones para workflows
- `scripts/telegram_alert_service.js` - Servicio de alertas
- `scripts/oracle_funding_detector.py` - Detector Oracle
- `scripts/integrate_pulse_intelligence.py` - Pulse Intelligence

### Scripts de Testing:
- `debug_github_actions.py` - Debugger automático
- `test_workflows_final.py` - Validador rápido
- `simulate_github_workflow.py` - Simulador local
- `test_critical_flows.py` - Test completo de flujos

### Documentación:
- `WORK_COMPLETED_SUMMARY.md` - Resumen del trabajo
- `GITHUB_ACTIONS_DEBUG_REPORT.md` - Reporte técnico
- `GITHUB_ACTIONS_ANALYSIS_SUMMARY.md` - Análisis completo

---

## 🆘 TROUBLESHOOTING

### Problema: Workflow no se ejecuta automáticamente
**Solución:** Verifica el cron schedule en el archivo `.yml`

### Problema: Workflow falla inmediatamente
**Solución:** 
1. Ve a Actions → Click en el run fallido
2. Lee el error en los logs
3. Verifica secretos y dependencias

### Problema: Python module not found
**Solución:** Agrega al workflow:
```yaml
- name: Install dependencies
  run: |
    pip install <module-name>
```

---

## 💡 TIPS

### ✅ Buenas Prácticas:
1. Siempre testear con `workflow_dispatch` antes de confiar en schedules
2. Monitorear primera ejecución de cada workflow
3. Revisar artifacts generados
4. Verificar que las notificaciones lleguen

### ⚠️ Evitar:
1. No ejecutar todos los workflows a la vez
2. No modificar workflows sin testear localmente
3. No hardcodear secretos en el código
4. No usar `python -c` con código multilínea

---

## 📞 SOPORTE

### Recursos:
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- Archivos de documentación en este repo

### Debugging:
```bash
# Ver estado de workflows
python check_workflow_status.py

# Analizar workflows
python debug_github_actions.py

# Simular ejecución local
python simulate_github_workflow.py
```

---

## ✅ STATUS ACTUAL

```
🟢 WORKFLOWS CORREGIDOS Y LISTOS
🟢 SCRIPTS AUXILIARES IMPLEMENTADOS
🟢 DOCUMENTACIÓN COMPLETA
🟡 PENDIENTE: CONFIGURAR SECRETOS EN GITHUB
🟡 PENDIENTE: TESTING EN GITHUB ACTIONS
```

---

**¡Todo listo para deployment! Solo falta configurar los secretos y testear.**

**Última actualización:** 2026-01-02  
**Por:** GitHub Copilot
