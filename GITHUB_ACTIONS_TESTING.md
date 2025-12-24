# 🧪 GitHub Actions Testing Guide

## 📋 Resumen

Esta guía te ayuda a testear tus workflows de GitHub Actions localmente antes de hacer push al repositorio.

## 🚀 Scripts Disponibles

### 1. Test de Validación Completo
```bash
python test_github_actions.py
# o
test_github_actions.bat
```

**Qué hace:**
- ✅ Verifica que todos los archivos requeridos existan
- ✅ Valida la sintaxis de scripts Python
- ✅ Verifica archivos de configuración (package.json, requirements.txt)
- ✅ Lista variables de entorno requeridas (GitHub Secrets)
- ✅ Genera un reporte de resultados

### 2. Simulador de Workflows
```bash
python simulate_github_workflow.py
```

**Qué hace:**
- 🎬 Simula la ejecución paso a paso de workflows específicos
- 📊 Muestra qué pasos se ejecutarían
- ⚠️ Indica qué secrets faltan
- 💡 Proporciona feedback de cada paso

## 📊 Workflows Disponibles

### 🔥 Workflows Principales

1. **Critical Flows Test & Telegram Report**
   - 📅 Cron: Cada lunes a las 9 AM
   - 🎯 Propósito: Testear flujos críticos y reportar a Telegram
   - 📄 Scripts: `test_critical_flows.py`, `send_to_telegram.py`

2. **Ghost Crawler - Daily Scrape**
   - 📅 Cron: Cada 23 horas
   - 🎯 Propósito: Scraping de LinkedIn y scoring con Pulse Intelligence
   - 📄 Scripts: `ghost-crawler.js`, `integrate_pulse_intelligence.py`

3. **Oracle Ghost - Automated Lead Detection**
   - 📅 Cron: Cada 12 horas (00:00 y 12:00 UTC)
   - 🎯 Propósito: Detectar empresas con alta probabilidad de funding
   - 📄 Scripts: `oracle_funding_detector.py`, `validate_oracle_output.py`

4. **Telegram Daily Broadcast**
   - 📅 Cron: Diario a las 8 AM
   - 🎯 Propósito: Enviar resumen diario a Telegram

5. **Weekly Lead Digest**
   - 📅 Cron: Cada domingo a las 10 AM
   - 🎯 Propósito: Resumen semanal de leads

### 🎯 Workflows de Alertas

- **Critical Funding Alert** - Alertas de funding crítico
- **High-Value Lead Alert** - Leads de alto valor
- **Pulse Score 90+ Alert** - Empresas con score >90
- **Regional Arbitrage Alert** - Oportunidades regionales

## 🔑 Secrets Requeridos

Para que los workflows funcionen, necesitas configurar estos secrets en GitHub:

### Telegram
```powershell
$env:TELEGRAM_BOT_TOKEN = "your_bot_token"
$env:TELEGRAM_CHAT_ID = "your_chat_id"
```

### Supabase
```powershell
$env:SUPABASE_URL = "https://your-project.supabase.co"
$env:SUPABASE_SERVICE_KEY = "your_service_key"
```

### Google Custom Search
```powershell
$env:GOOGLE_CSE_API_KEY = "your_api_key"
$env:GOOGLE_CSE_ID = "your_search_engine_id"
```

## 📝 Configurar Secrets en GitHub

1. Ve a tu repositorio en GitHub
2. Click en **Settings** > **Secrets and variables** > **Actions**
3. Click en **New repository secret**
4. Añade cada secret con su nombre y valor

## ✅ Checklist Pre-Deploy

Antes de hacer push, verifica:

- [ ] Todos los scripts Python tienen sintaxis válida
- [ ] Los archivos de requirements están completos
- [ ] package.json es válido
- [ ] Todos los scripts referenciados en workflows existen
- [ ] Los secrets están documentados (aunque no estén en local)
- [ ] Las rutas de archivos son correctas
- [ ] Los cron schedules son los deseados

## 🧪 Testear Localmente

### Test Rápido
```bash
# Validar todo
python test_github_actions.py
```

### Test de Workflow Específico
```bash
# Simular workflow interactivamente
python simulate_github_workflow.py

# Selecciona el workflow que quieres simular
```

### Test Manual de Scripts Individuales
```bash
# Test de flujos críticos
python test_critical_flows.py

# Test de Oracle
python scripts/oracle_funding_detector.py

# Test de Pulse Intelligence
python scripts/integrate_pulse_intelligence.py --help
```

## 🚀 Deployment Workflow

1. **Test Local**
   ```bash
   python test_github_actions.py
   ```

2. **Commit & Push**
   ```bash
   git add .
   git commit -m "Update workflows"
   git push origin main
   ```

3. **Configurar Secrets en GitHub**
   - Ve a Settings > Secrets > Actions
   - Añade todos los secrets requeridos

4. **Verificar en GitHub Actions**
   - Ve a la pestaña **Actions**
   - Verifica que los workflows estén listados
   - Click en un workflow > **Run workflow** para trigger manual

5. **Monitor Ejecuciones**
   - Ve a Actions > Selecciona una ejecución
   - Revisa los logs de cada step
   - Verifica que no haya errores

## 🐛 Troubleshooting

### Error: Script not found
```
❌ scripts/some_script.py not found
```
**Solución:** Verifica que el archivo existe en la ruta correcta

### Error: Syntax error in Python script
```
❌ Syntax error in test_critical_flows.py
```
**Solución:** 
```bash
python -m py_compile test_critical_flows.py
```

### Error: Secrets not set
```
❌ NOT SET: TELEGRAM_BOT_TOKEN
```
**Solución:** Configura el secret en GitHub Settings o localmente para test

### Workflow no se ejecuta
- Verifica el cron schedule está en UTC
- Verifica que el workflow esté en `.github/workflows/`
- Verifica que el archivo YAML sea válido
- Revisa la pestaña Actions en GitHub

## 📊 Resultados del Test

Después de ejecutar `test_github_actions.py`, encontrarás:

- **Salida en consola:** Resultados en tiempo real
- **Reporte guardado:** `data/output/github_actions_test_report.txt`

### Interpretando Resultados

```
📊 Tests Run: 15
✅ Passed: 15
❌ Failed: 0
📈 Success Rate: 100.0%
```

- **100%:** ✅ Todo listo para deploy
- **80-99%:** ⚠️ Revisar errores menores
- **<80%:** ❌ Faltan archivos o hay errores críticos

## 💡 Tips

1. **Test frecuentemente:** Ejecuta tests antes de cada commit importante
2. **Simula primero:** Usa `simulate_github_workflow.py` para entender el flujo
3. **Verifica cron schedules:** Asegúrate que los horarios son correctos (UTC)
4. **Monitor Actions:** Revisa la pestaña Actions después del primer deploy
5. **Usa workflow_dispatch:** Permite trigger manual para testing

## 🔗 Resources

- [GitHub Actions Docs](https://docs.github.com/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [Encrypted Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Cron Schedule](https://crontab.guru/)

## 📞 Comandos Útiles

```bash
# Validar sintaxis YAML
python -c "import yaml; yaml.safe_load(open('.github/workflows/daily_scrape.yml'))"

# Listar todos los workflows
ls .github/workflows/

# Test de un script específico
python -m pytest tests/

# Ver secrets configurados localmente
$env:TELEGRAM_BOT_TOKEN  # PowerShell
echo $TELEGRAM_BOT_TOKEN # Bash
```

## 🎯 Next Steps

1. ✅ Ejecuta `test_github_actions.py`
2. ✅ Revisa y corrige errores
3. ✅ Simula workflows con `simulate_github_workflow.py`
4. ✅ Configura secrets en GitHub
5. ✅ Push y verifica en Actions tab
6. ✅ Monitor primera ejecución
7. ✅ Ajusta cron schedules si es necesario

---

**Creado:** 2025-12-24  
**Última actualización:** 2025-12-24
