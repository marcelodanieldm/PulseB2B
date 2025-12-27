# PulseB2B Automation & Backend Logic

## 1. Daily Signal (GitHub Actions)
- **Archivo:** `.github/workflows/daily-signal.yml`
- **Script:** `scripts/send_daily_signal.py`
- **Función:** Todos los días, selecciona el lead con mayor score (>90) y lo envía por Telegram usando el bot.
- **Variables de entorno necesarias:**
  - `SUPABASE_URL`, `SUPABASE_KEY` (API Supabase)
  - `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` (Bot Telegram)
- **Cómo funciona:**
  - El workflow ejecuta el script Python, que consulta Supabase y envía el mensaje al canal/grupo configurado.

## 2. Weekly Radar (GitHub Actions)
- **Archivo:** `.github/workflows/weekly-radar.yml`
- **Script:** `scripts/generate_weekly_radar.py`
- **Función:** Cada domingo, selecciona los 10 mejores leads por región, genera un PDF y lo sube a Supabase Storage.
- **Variables de entorno necesarias:**
  - `SUPABASE_URL`, `SUPABASE_KEY`
- **Cómo funciona:**
  - El script consulta Supabase, genera el PDF con `reportlab` y lo sube a Storage vía API REST.

## 3. Webhooks API Logic (Supabase Edge Function)
- **Archivo:** `supabase_webhook_trigger.js`
- **Función:** Cuando se inserta un nuevo lead, revisa los webhooks activos y, si el lead coincide con los filtros del cliente, hace un POST asíncrono al endpoint del cliente.
- **Variables de entorno necesarias:**
  - `SUPABASE_URL`, `SUPABASE_KEY`
- **Cómo funciona:**
  - Se despliega como Edge Function en Supabase. Se invoca desde un trigger o manualmente.

## 4. Security (RLS Policies)
- **Archivo:** `supabase_rls.sql`
- **Función:** Restringe el acceso a `contact_info` y exportación de CSV solo a usuarios con el flag `pro_plan` en la tabla `profiles`.
- **Cómo funciona:**
  - Ejecutar el SQL en el editor de políticas de Supabase.

## 5. Estructura de archivos
```
.github/workflows/daily-signal.yml
.github/workflows/weekly-radar.yml
scripts/send_daily_signal.py
scripts/generate_weekly_radar.py
supabase_webhook_trigger.js
supabase_rls.sql
```

## 6. Despliegue y pruebas
- **GitHub Actions:**
  - Configura los secrets en el repositorio (`SUPABASE_URL`, `SUPABASE_KEY`, etc).
  - Los workflows se ejecutan automáticamente según el cron o manualmente desde la UI de Actions.
- **Scripts Python:**
  - Se ejecutan automáticamente por los workflows.
  - Puedes probarlos localmente exportando las variables de entorno y ejecutando `python scripts/send_daily_signal.py`.
- **Edge Function:**
  - Sube `supabase_webhook_trigger.js` a Supabase Edge Functions.
  - Configura triggers en Supabase para llamar a la función al insertar leads.
- **RLS Policies:**
  - Ejecuta el SQL en el panel de Supabase para activar las políticas.

## 7. Notas
- Todos los scripts usan solo dependencias estándar y requests/reportlab.
- El PDF semanal se guarda en la ruta `weekly_radar/YYYY-MM-DD.pdf` en Supabase Storage.
- Los webhooks deben estar registrados en la tabla `webhooks` con filtros en formato JSON.

---

¿Dudas o necesitas ejemplos de despliegue para algún componente?