# 🤖 Automatización con GitHub Actions - Telegram Reports

Configura GitHub Actions para ejecutar tests automáticamente y enviar resultados a Telegram.

---

## 🚀 Quick Setup (5 minutos)

### 1. Configurar Secrets en GitHub

1. Ve a tu repositorio en GitHub
2. Click en **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Agrega estos dos secrets:

**Secret 1:**
- Name: `TELEGRAM_BOT_TOKEN`
- Value: Tu token del bot (ej: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

**Secret 2:**
- Name: `TELEGRAM_CHAT_ID`  
- Value: Tu chat ID (ej: `987654321`)

### 2. Verificar el Workflow

El archivo ya está creado en:
```
.github/workflows/test-and-report-telegram.yml
```

### 3. Activar el Workflow

Haz commit y push de los cambios:

```bash
git add .github/workflows/test-and-report-telegram.yml
git add test_critical_flows.py send_to_telegram.py
git commit -m "Add automated Telegram reporting"
git push
```

### 4. Probar Manualmente

1. Ve a tu repo en GitHub
2. Click en **Actions**
3. Selecciona "Critical Flows Test & Telegram Report"
4. Click **Run workflow**
5. Revisa tu Telegram para el informe

---

## ⚙️ Configuración del Workflow

### Horario Automático

El workflow está configurado para ejecutarse:
- **Cada lunes a las 9 AM UTC**

Para cambiar el horario, edita el `cron` en el archivo:

```yaml
schedule:
  - cron: '0 9 * * 1'  # Min Hora DíaMes Mes DíaSemana
```

**Ejemplos:**
```yaml
'0 0 * * *'     # Diario a medianoche
'0 9 * * 1-5'   # Lunes a Viernes a las 9 AM
'0 */6 * * *'   # Cada 6 horas
'0 9,17 * * *'  # Dos veces al día: 9 AM y 5 PM
```

### Ejecución en Push

Para ejecutar en cada push a `main`, descomenta estas líneas:

```yaml
push:
  branches: [ main ]
```

---

## 📊 Qué Hace el Workflow

1. **Checkout del código** - Clona el repositorio
2. **Setup Python 3.11** - Configura el ambiente
3. **Instala dependencias** - sklearn, pandas, python-telegram-bot
4. **Ejecuta tests** - `python test_critical_flows.py`
5. **Genera reportes** - Crea archivos en `data/output/`
6. **Envía a Telegram** - `python send_to_telegram.py`
7. **Sube artifacts** - Guarda reportes por 30 días

---

## 🎯 Workflows Adicionales Sugeridos

### Workflow 1: Test Diario con Resumen Semanal

Crea: `.github/workflows/daily-test-weekly-summary.yml`

```yaml
name: Daily Tests with Weekly Summary

on:
  schedule:
    # Tests diarios a las 9 AM
    - cron: '0 9 * * *'
    # Resumen semanal los viernes a las 5 PM
    - cron: '0 17 * * 5'

jobs:
  daily-test:
    if: github.event.schedule == '0 9 * * *'
    runs-on: ubuntu-latest
    steps:
      # ... ejecutar tests normales ...
      
  weekly-summary:
    if: github.event.schedule == '0 17 * * 5'
    runs-on: ubuntu-latest
    steps:
      # ... enviar resumen detallado ...
```

### Workflow 2: Alertas de Fallos Críticos

Crea: `.github/workflows/critical-alerts.yml`

```yaml
name: Critical System Alerts

on:
  schedule:
    - cron: '0 */4 * * *'  # Cada 4 horas

jobs:
  health-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install deps
        run: pip install scikit-learn numpy pandas python-telegram-bot
      
      - name: Run tests
        id: tests
        run: python test_critical_flows.py
        continue-on-error: true
      
      - name: Send alert if failed
        if: steps.tests.outputs.test_status != '0'
        env:
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
        run: |
          python send_to_telegram.py --format alert
```

### Workflow 3: Deploy + Test + Report

Crea: `.github/workflows/deploy-test-report.yml`

```yaml
name: Deploy, Test & Report

on:
  push:
    branches: [ production ]

jobs:
  deploy-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy to production
        run: |
          # Tu script de deployment
          echo "Deploying..."
      
      - name: Run smoke tests
        run: python test_critical_flows.py
      
      - name: Report to Telegram
        env:
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
        run: |
          python send_to_telegram.py --format executive
```

---

## 🔍 Monitoreo de Workflows

### Ver Estado de Ejecuciones

```bash
# Listar workflows
gh workflow list

# Ver runs recientes
gh run list --workflow=test-and-report-telegram.yml

# Ver logs de último run
gh run view --log
```

### Notificaciones de GitHub

Configura notificaciones de GitHub Actions:

1. Settings → Notifications
2. Actions → Check "Send notifications for failed workflows"

---

## 📱 Personalizar Mensajes según Resultado

Modifica `send_to_telegram.py` para enviar diferentes formatos:

```python
# Al final de send_to_telegram.py

import json
results_file = Path('data/output/critical_flows_report.json')
with open(results_file) as f:
    results = json.load(f)

success_rate = results['passed_tests'] / results['total_tests'] * 100

# Decidir qué formato enviar
if success_rate >= 95:
    format_type = 'compact'  # Todo perfecto, mensaje corto
elif success_rate >= 85:
    format_type = 'simple'   # Normal
else:
    format_type = 'alert'    # Problemas, formato alerta
```

---

## 🎨 Formatos de Mensaje Disponibles

Ejecuta primero para generar todos los formatos:

```bash
python customize_telegram_messages.py
```

Esto crea:
- `telegram_simple_format.txt` - Básico
- `telegram_executive_format.txt` - Para managers
- `telegram_technical_format.txt` - Técnico detallado
- `telegram_alert_format.txt` - Estilo alerta
- `telegram_compact_format.txt` - Ultra compacto

Luego en el workflow usa:

```yaml
- name: Send appropriate format
  run: |
    python customize_telegram_messages.py
    python send_to_telegram.py --format executive
```

---

## 💡 Tips de Optimización

### Cache de Dependencias

El workflow ya incluye cache de pip:

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.11'
    cache: 'pip'  # ← Esto cachea las dependencias
```

### Conditional Execution

Solo enviar si hay cambios significativos:

```yaml
- name: Check if significant changes
  id: check
  run: |
    # Lógica para determinar si enviar
    if [ "$(git diff HEAD~1 -- tests/)" ]; then
      echo "send=true" >> $GITHUB_OUTPUT
    fi

- name: Send to Telegram
  if: steps.check.outputs.send == 'true'
  run: python send_to_telegram.py
```

### Rate Limiting

Para evitar spam, agregar delay entre mensajes:

```yaml
- name: Send reports with delay
  run: |
    python send_to_telegram.py --format simple
    sleep 5
    python send_to_telegram.py --format executive
```

---

## 🐛 Troubleshooting

### Error: "Secrets not found"

Verifica que los secrets estén configurados:
```bash
gh secret list
```

Deben aparecer:
- TELEGRAM_BOT_TOKEN
- TELEGRAM_CHAT_ID

### Error: "pip install failed"

Agrega timeout y retry:

```yaml
- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install --timeout=60 --retries=3 scikit-learn numpy pandas python-telegram-bot
```

### Workflow no se ejecuta

1. Verifica que el archivo esté en `.github/workflows/`
2. Asegúrate de que el cron sea correcto (en UTC)
3. Revisa en Actions → All workflows

### Mensajes no llegan a Telegram

1. Verifica que el bot esté iniciado con /start
2. Revisa los logs del workflow en GitHub
3. Verifica que CHAT_ID sea correcto

---

## 📊 Ejemplo de Configuración Completa

### Paso a Paso Final

```bash
# 1. Configurar bot (si no lo hiciste)
setup_telegram_reports.bat

# 2. Generar formatos personalizados
python customize_telegram_messages.py

# 3. Test local
python test_critical_flows.py
python send_to_telegram.py

# 4. Commit y push
git add .github/workflows/
git add send_to_telegram.py test_critical_flows.py
git add customize_telegram_messages.py
git commit -m "Setup automated Telegram reporting"
git push

# 5. Configurar secrets en GitHub (web)
# - TELEGRAM_BOT_TOKEN
# - TELEGRAM_CHAT_ID

# 6. Ejecutar manualmente primero
# GitHub → Actions → Run workflow

# 7. Verificar Telegram
# Deberías recibir el mensaje
```

---

## 🎯 Resultado Final

Después de configurar, tendrás:

✅ Tests automáticos cada lunes a las 9 AM
✅ Reportes enviados a Telegram automáticamente
✅ Histórico de 30 días de reportes
✅ Ejecución manual disponible
✅ Múltiples formatos de mensaje
✅ Sin costos (GitHub Actions free tier)

---

## 📞 Recursos

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Crontab Guru](https://crontab.guru/) - Para construir expresiones cron

---

🚀 **Listo! Tu sistema ahora está completamente automatizado** 🚀
