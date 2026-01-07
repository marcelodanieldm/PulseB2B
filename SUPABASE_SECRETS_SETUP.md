# 🔐 Configuración de Secrets de Supabase en GitHub

## ❌ Error Actual
```
ValueError: Missing Supabase credentials
```

Este error indica que **los secrets de Supabase NO están configurados** en tu repositorio de GitHub.

---

## ✅ Solución: Configurar GitHub Secrets

### Paso 1: Obtener tus credenciales de Supabase

1. Ve a [supabase.com](https://supabase.com/dashboard)
2. Selecciona tu proyecto
3. Ve a **Settings** → **API**
4. Copia los siguientes valores:
   - **Project URL** (ej: `https://tuproyecto.supabase.co`)
   - **service_role key** (bajo "Project API keys")

### Paso 2: Configurar Secrets en GitHub

1. Ve a tu repositorio: `https://github.com/marcelodanieldm/PulseB2B`
2. Click en **Settings** (arriba derecha)
3. En el menú izquierdo: **Secrets and variables** → **Actions**
4. Click en **New repository secret**
5. Agrega los siguientes secrets:

#### Secret 1: SUPABASE_URL
- **Name:** `SUPABASE_URL`
- **Value:** Tu Project URL (ej: `https://lyjnpinwnptahrsawblz.supabase.co`)

#### Secret 2: SUPABASE_SERVICE_KEY
- **Name:** `SUPABASE_SERVICE_KEY`
- **Value:** Tu service_role key (cadena larga que empieza con `eyJ...`)

---

## 🔍 Verificación

Después de configurar los secrets:

1. **Verifica que los secrets existen:**
   - Ve a `Settings` → `Secrets and variables` → `Actions`
   - Deberías ver: `SUPABASE_URL` y `SUPABASE_SERVICE_KEY`

2. **Re-ejecuta el workflow fallido:**
   - Ve a `Actions` tab
   - Busca el workflow "Generate Daily Teaser" que falló
   - Click en "Re-run jobs" → "Re-run failed jobs"

---

## 📋 Secrets Requeridos por el Proyecto

Tu proyecto PulseB2B requiere estos secrets para funcionar:

### 🔴 CRÍTICOS (Requeridos)
- ✅ `SUPABASE_URL` - URL de tu proyecto Supabase
- ✅ `SUPABASE_SERVICE_KEY` - Service key de Supabase
- ⚠️ `TELEGRAM_BOT_TOKEN` - Token del bot de Telegram
- ⚠️ `TELEGRAM_CHAT_ID` - ID del chat de Telegram

### 🟡 IMPORTANTES (Opcionales pero recomendados)
- `GOOGLE_CSE_API_KEY` - Para búsquedas
- `SENDGRID_API_KEY` - Para emails
- `CLEARBIT_API_KEY` - Para enriquecimiento

---

## 🐛 Troubleshooting

### El workflow sigue fallando después de agregar los secrets
1. **Verifica que los nombres sean exactos:** `SUPABASE_SERVICE_KEY` (no `SUPABASE_KEY`)
2. **Verifica que no haya espacios:** Copia y pega cuidadosamente
3. **Verifica que el secret sea el correcto:** Debe ser el `service_role` key, NO el `anon` key
4. **Re-ejecuta el workflow:** Los secrets no se actualizan en workflows en progreso

### ¿Dónde encuentro mis credenciales de Supabase?
```
Supabase Dashboard → Tu Proyecto → Settings → API
```

### ¿Qué key debo usar?
Usa el **service_role key** (tiene más permisos). 
**NO** uses el `anon` key para workflows de backend.

---

## 📝 Notas Técnicas

- El script `src/telegram_teaser_generator.py` acepta **dos nombres** para compatibilidad:
  - `SUPABASE_SERVICE_KEY` (recomendado)
  - `SUPABASE_SERVICE_ROLE_KEY` (alternativo)
  
- El workflow `generate_daily_teaser.yml` pasa ambas variables automáticamente

- Si solo tienes uno de los dos secrets configurados, el script lo detectará automáticamente

---

## 📞 Soporte

Si sigues teniendo problemas:
1. Revisa los logs del workflow en Actions
2. Verifica que tu proyecto de Supabase esté activo
3. Confirma que las credenciales sean válidas probando localmente:
   ```python
   import os
   from supabase import create_client
   
   url = "TU_SUPABASE_URL"
   key = "TU_SERVICE_KEY"
   supabase = create_client(url, key)
   print("✅ Conexión exitosa")
   ```
