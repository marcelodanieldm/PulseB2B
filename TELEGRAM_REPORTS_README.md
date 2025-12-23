# 📱 Sistema de Reportes de Telegram - PulseB2B

Envía automáticamente los resultados de validación de flujos críticos a tu canal/chat de Telegram.

---

## 🚀 Quick Start (5 minutos)

### 1. Crear Bot de Telegram

1. Abre Telegram y busca **@BotFather**
2. Envía `/newbot`
3. Sigue las instrucciones (nombre y username)
4. Copia el **token** que te da (ej: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Obtener tu Chat ID

1. Busca **@userinfobot** en Telegram
2. Envía `/start`
3. El bot te responderá con tu **chat_id** (ej: `987654321`)

### 3. Configurar

**Opción A: Variables de Entorno (Recomendado)**

```bash
# Windows (PowerShell)
$env:TELEGRAM_BOT_TOKEN="tu-token-aqui"
$env:TELEGRAM_CHAT_ID="tu-chat-id-aqui"

# Windows (CMD)
set TELEGRAM_BOT_TOKEN=tu-token-aqui
set TELEGRAM_CHAT_ID=tu-chat-id-aqui

# Linux/Mac
export TELEGRAM_BOT_TOKEN="tu-token-aqui"
export TELEGRAM_CHAT_ID="tu-chat-id-aqui"
```

**Opción B: Editar Script**

Abre `send_to_telegram.py` y edita:

```python
TELEGRAM_BOT_TOKEN = 'tu-token-aqui'
TELEGRAM_CHAT_ID = 'tu-chat-id-aqui'
```

### 4. Instalar Dependencia

```bash
pip install python-telegram-bot
```

### 5. Enviar Informe

**Windows:**
```bash
send_telegram_report.bat
```

**Linux/Mac:**
```bash
python send_to_telegram.py
```

---

## 📊 Tipos de Informes

### 1. Informe Simple (Recomendado)

Resumen conciso con resultados principales.

```bash
python send_to_telegram.py
```

**Archivo:** `data/output/telegram_report.txt`

✅ Formato HTML de Telegram
✅ ~800 caracteres
✅ Perfecto para notificaciones rápidas

---

### 2. Informe Detallado

Análisis completo con todas las métricas.

```bash
python send_to_telegram.py --detailed
```

**Archivo:** `data/output/telegram_detailed_report.txt`

✅ Formato HTML de Telegram
✅ ~2,500 caracteres
✅ Incluye métricas técnicas

---

### 3. Mensaje Completo

Informe exhaustivo con toda la información del sistema.

**Archivo:** `data/output/telegram_mensaje_completo.txt`

✅ Formato HTML de Telegram
✅ ~6,500 caracteres (se envía en partes)
✅ Incluye casos de uso, tecnologías, etc.

---

## 🎯 Uso Automático

### Integrar con Tests

Modificar `test_critical_flows.py` al final:

```python
if __name__ == '__main__':
    exit_code = main()
    
    # Auto-send to Telegram after tests
    if exit_code == 0:
        import subprocess
        subprocess.run([sys.executable, 'send_to_telegram.py'])
    
    sys.exit(exit_code)
```

### GitHub Actions

Agregar al workflow `.github/workflows/test-critical-flows.yml`:

```yaml
name: Test & Report to Telegram

on:
  schedule:
    - cron: '0 0 * * 1'  # Lunes a medianoche
  workflow_dispatch:

jobs:
  test-and-report:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install scikit-learn numpy pandas python-telegram-bot
      
      - name: Run tests
        run: python test_critical_flows.py
      
      - name: Send to Telegram
        env:
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
        run: python send_to_telegram.py
```

**Configurar Secrets en GitHub:**
1. Ve a Settings → Secrets → Actions
2. Agrega `TELEGRAM_BOT_TOKEN`
3. Agrega `TELEGRAM_CHAT_ID`

---

## 📝 Formato HTML de Telegram

Los informes usan HTML markup de Telegram:

```html
<b>Texto en negrita</b>
<i>Texto en cursiva</i>
<code>Código inline</code>
<pre>Bloque de código</pre>
```

**Emojis Soportados:**
- ✅ ❌ ⚠️ 🎯 🚀 📊 📈 🧠 🌎 🔮 🔗
- 💡 📱 ⏱️ 💾 🔧 📋 📄 🎉

---

## 🔍 Troubleshooting

### Error: "python-telegram-bot not installed"

```bash
pip install python-telegram-bot
```

### Error: "TELEGRAM_BOT_TOKEN not configured"

Verifica que hayas configurado las variables de entorno o editado el script.

```bash
# Verificar en PowerShell
echo $env:TELEGRAM_BOT_TOKEN

# Verificar en CMD
echo %TELEGRAM_BOT_TOKEN%
```

### Error: "Chat not found"

El chat_id debe ser un número (sin comillas en variables de entorno).
Verifica que sea correcto con @userinfobot.

### Mensaje Demasiado Largo

El script divide automáticamente mensajes >4096 caracteres.
Si prefieres mensajes cortos, usa la versión simple:

```bash
python send_to_telegram.py  # Sin --detailed
```

---

## 💡 Casos de Uso

### 1. Reporte Semanal

Configura un cron job o tarea programada:

**Linux/Mac (crontab):**
```cron
0 9 * * 1 cd /path/to/PulseB2B && python test_critical_flows.py && python send_to_telegram.py
```

**Windows (Task Scheduler):**
- Crear tarea programada
- Trigger: Semanal (lunes 9 AM)
- Action: `send_telegram_report.bat`

### 2. Notificación Post-Deploy

Agregar a tus scripts de deployment:

```bash
#!/bin/bash
# deploy.sh

echo "Deploying..."
# ... deployment commands ...

echo "Running validation tests..."
python test_critical_flows.py

if [ $? -eq 0 ]; then
    echo "Sending success report to Telegram..."
    python send_to_telegram.py
fi
```

### 3. Integración CI/CD

Ver sección **GitHub Actions** arriba.

---

## 📱 Ejemplo de Mensaje

```
🚀 PULSEB2B - TEST DE FLUJOS CRÍTICOS 🚀

📅 23 de December, 2025 - 12:21

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 RESULTADOS GENERALES:
✅ Tests Pasados: 13/14
📈 Tasa de Éxito: 92.9%
⏱️ Tiempo: 9.1s

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🧠 PULSE INTELLIGENCE ENGINE
   ✅ Critical Scoring: 91/100
   ✅ Red Flags Detection
   ✅ Tech Stack Analysis
   Detecta empresas con necesidad urgente de hiring

🌎 REGIONAL SYSTEM
   ✅ Entity Recognition: 95/100
   ✅ US/Canada → LATAM Expansion
   ✅ Critical Opportunities
   Identifica arbitrage regional en LATAM

🎯 STATUS: OPERATIVO ✅

💡 Sistema de inteligencia de mercado automatizado
Para detectar oportunidades de hiring en tiempo real
```

---

## 🛠️ Archivos del Sistema

```
PulseB2B/
├── test_critical_flows.py          # Script principal de tests
├── send_to_telegram.py              # Envío a Telegram
├── send_telegram_report.bat         # Helper Windows
├── TELEGRAM_REPORTS_README.md       # Esta guía
└── data/output/
    ├── telegram_report.txt          # Informe simple
    ├── telegram_detailed_report.txt # Informe detallado
    ├── telegram_mensaje_completo.txt # Mensaje completo
    └── critical_flows_report.json   # Datos JSON
```

---

## 🎯 Próximos Pasos

1. ✅ Configurar bot de Telegram
2. ✅ Ejecutar `python test_critical_flows.py`
3. ✅ Enviar informe con `send_telegram_report.bat`
4. 🔄 Automatizar con GitHub Actions
5. 📊 Configurar dashboard de métricas

---

## 📞 Soporte

Si tienes problemas:

1. Verifica que el bot esté configurado correctamente
2. Asegúrate de que el chat_id sea correcto
3. Revisa que las dependencias estén instaladas
4. Verifica los logs de error

**Documentación Telegram Bot API:**
https://core.telegram.org/bots/api

---

🚀 **PulseB2B - Market Intelligence Platform**
📱 Reportes automáticos vía Telegram
