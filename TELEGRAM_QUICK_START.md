# 🚀 QUICK START - Sistema de Reportes Telegram

## ⚡ Inicio Rápido (5 minutos)

### 1️⃣ Configurar Bot (2 min)

```bash
setup_telegram_reports.bat
```

Sigue los pasos en pantalla:
- Crea bot con @BotFather
- Obtén chat ID con @userinfobot
- El script lo configura todo automáticamente

### 2️⃣ Enviar Primer Reporte (1 min)

```bash
send_telegram_report.bat
```

¡Listo! Revisa tu Telegram 📱

---

## 📱 Comandos Útiles

### Envío Básico

```bash
# Simple (recomendado)
python send_to_telegram.py

# Detallado
python send_to_telegram.py --detailed

# Compacto
python send_to_telegram.py --format compact

# Ejecutivo
python send_to_telegram.py --format executive

# Alerta
python send_to_telegram.py --format alert
```

### Generar Formatos Personalizados

```bash
python customize_telegram_messages.py
```

### Ejecutar Tests + Enviar

```bash
send_telegram_report.bat
```

---

## 🤖 GitHub Actions (Opcional)

### Paso 1: Configurar Secrets

En GitHub → Settings → Secrets → Actions:

- **TELEGRAM_BOT_TOKEN** = `tu-token-del-bot`
- **TELEGRAM_CHAT_ID** = `tu-chat-id`

### Paso 2: Push del Código

```bash
git add .
git commit -m "Add Telegram automation"
git push
```

### Paso 3: Ejecutar Manualmente

GitHub → Actions → "Critical Flows Test" → Run workflow

✅ Se ejecutará automáticamente cada lunes a las 9 AM

---

## 📊 Formatos Disponibles

| Comando | Tamaño | Descripción |
|---------|--------|-------------|
| `python send_to_telegram.py` | 1.4 KB | Estándar (recomendado) |
| `--format compact` | 0.1 KB | Ultra corto para móviles |
| `--format executive` | 0.8 KB | Resumen ejecutivo |
| `--format alert` | 0.3 KB | Estilo alerta crítica |
| `--format technical` | 0.9 KB | Detalle técnico |
| `--detailed` | 5.6 KB | Completo exhaustivo |

---

## 💡 Tips

### Ver Configuración Actual

```bash
type .env
```

### Reconfigurar

```bash
setup_telegram_reports.bat
```

### Ver Últimos Reportes

```bash
dir data\output\telegram_*.txt
```

---

## 📞 Problemas Comunes

### ❌ "Bot not found"
→ Envía `/start` a tu bot en Telegram

### ❌ "Module not found"
→ `pip install python-telegram-bot`

### ❌ "File not found"
→ Ejecuta primero: `python test_critical_flows.py`

---

## 📚 Documentación Completa

- **[TELEGRAM_IMPLEMENTATION_FINAL.md](TELEGRAM_IMPLEMENTATION_FINAL.md)** - Guía completa
- **[GITHUB_ACTIONS_TELEGRAM.md](GITHUB_ACTIONS_TELEGRAM.md)** - Automatización
- **[TELEGRAM_REPORTS_README.md](TELEGRAM_REPORTS_README.md)** - Uso básico

---

## ✅ Checklist

- [ ] Bot configurado con @BotFather
- [ ] Chat ID obtenido
- [ ] `.env` creado
- [ ] Primer mensaje enviado
- [ ] Tests ejecutándose
- [ ] (Opcional) GitHub Actions configurado

---

🎯 **¡Listo en 5 minutos!** 🎯
