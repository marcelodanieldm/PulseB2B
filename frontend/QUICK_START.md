# 🚀 Quick Start - Frontend Dashboard

## Setup en 5 minutos

### 1. Instalar dependencias

```bash
cd frontend
npm install
```

### 2. Configurar tokens

Crea `.env.local`:

```bash
# Mapbox (requerido para el mapa)
NEXT_PUBLIC_MAPBOX_TOKEN=pk.eyJ1IjoidHUtdXNlciIsImEiOiJjbHh4eHh4eHgifQ.xxxxx

# Supabase (opcional - usar datos mock si no está configurado)
NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxx
```

**¿No tienes Mapbox token?**
- Regístrate gratis en https://account.mapbox.com/
- Crea un token con scopes: `styles:read`, `fonts:read`, `tiles:read`

### 3. Ejecutar

```bash
npm run dev
```

Abre → http://localhost:3000

## ✨ Features disponibles inmediatamente

### ✅ Funciona sin backend
- Datos mock pre-cargados con 50 empresas
- Sistema de semáforo funcionando
- Filtros operativos
- Mapa interactivo con Mapbox

### 🗺️ Mapa Global
- Marcadores por ubicación
- Colores según status (🔴🟢🟡🔵)
- Popups con métricas
- Leyenda interactiva

### 📊 Dashboard
- 8 tarjetas de stats
- Vista de mapa y grid
- Búsqueda en tiempo real
- Filtros avanzados

### 📈 Gráficos
- Crecimiento de equipo
- Funding histórico
- Job posts
- Vista combinada

## 🔌 Conectar con tu backend Python

### Opción A: Supabase (Recomendado)

1. **Crear tabla en Supabase**:

```sql
CREATE TABLE hiring_predictions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  company_id TEXT NOT NULL,
  name TEXT NOT NULL,
  hiring_probability FLOAT NOT NULL,
  status TEXT NOT NULL,
  -- ver frontend/README.md para schema completo
);
```

2. **Script Python para subir datos**:

```python
# scripts/push_to_supabase.py
from supabase import create_client
import json

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Cargar predicciones desde tu ML engine
with open('data/predictions/latest_predictions.json', 'r') as f:
    predictions = json.load(f)

# Subir a Supabase
for pred in predictions:
    supabase.table('hiring_predictions').insert(pred).execute()

print(f"✅ {len(predictions)} predictions uploaded!")
```

3. **Frontend lee automáticamente**:

```typescript
// Ya está implementado en src/app/page.tsx
// Descomenta estas líneas:
const { data } = await supabase.from('hiring_predictions').select('*')
setCompanies(data)
```

### Opción B: API REST

1. **Crear endpoint FastAPI**:

```python
# backend/api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/predictions")
async def get_predictions():
    # Retorna tus predicciones
    return load_predictions_from_db()
```

2. **Configurar en frontend**:

```env
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

3. **Llamar desde Next.js**:

```typescript
// src/app/page.tsx - línea 47
const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/predictions`)
const data = await response.json()
setCompanies(data)
```

## 🎯 Casos de uso

### Ver empresas en mapa
1. Click en "Map" (arriba derecha)
2. Hover sobre marcadores
3. Click para ver detalles en popup
4. Click "Ver Detalles Completos" para gráficos

### Filtrar oportunidades golden
1. Sidebar izquierdo → "Traffic Light Status"
2. Click en "🟡 Funding Inminente"
3. Mapa muestra solo empresas con funding <90 días

### Buscar empresas específicas
1. Barra de búsqueda (arriba)
2. Escribe: "San Francisco" o nombre de empresa
3. Resultados en tiempo real

### Ver gráficos de crecimiento
1. Click en cualquier empresa (mapa o grid)
2. Scroll abajo para ver gráficos
3. Alterna entre: Overview, Funding, Team, Jobs

## 🎨 Personalizar

### Cambiar colores de semáforo

```typescript
// tailwind.config.ts
colors: {
  risk: {
    high: '#FF0000',  // Tu color rojo
    low: '#00FF00',   // Tu color verde
  },
}
```

### Modificar lógica de status

```typescript
// src/lib/utils.ts - línea 17
export function getTrafficLightStatus(company) {
  // Tu lógica aquí
  if (company.hiring_probability >= 90) {
    return { status: 'green', reason: '90%+ probabilidad' }
  }
}
```

### Agregar nuevas métricas al card

```typescript
// src/components/CompanyCard.tsx - línea 80
<div className="bg-gradient-to-br from-teal-50 to-cyan-50 p-3 rounded-lg">
  <div className="flex items-center space-x-2 mb-1">
    <YourIcon className="w-4 h-4 text-teal-600" />
    <span className="text-xs font-medium text-gray-600">Tu Métrica</span>
  </div>
  <p className="text-lg font-bold text-gray-900">
    {company.your_metric}
  </p>
</div>
```

## 🐛 Troubleshooting

### Mapa no se muestra
```bash
# Verificar token
echo $NEXT_PUBLIC_MAPBOX_TOKEN

# Debe empezar con "pk."
```

### Error CORS al llamar API
```python
# backend: agregar CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
)
```

### TypeScript errors
```bash
npm run type-check
```

### Build errors
```bash
rm -rf .next
npm run build
```

## 📚 Siguientes pasos

1. **Conectar backend Python** → Ver "Opción A" arriba
2. **Agregar autenticación** → [Auth.js](https://authjs.dev/) o Supabase Auth
3. **Deploy a producción** → [Vercel](https://vercel.com) (1-click)
4. **Real-time updates** → Supabase subscriptions
5. **Notificaciones** → Push notifications para golden companies

## 🎓 Recursos

- **Docs completos**: `frontend/README.md`
- **ML Engine**: `docs/ML_ENGINE.md`
- **Mapbox Docs**: https://docs.mapbox.com/mapbox-gl-js/
- **Next.js Docs**: https://nextjs.org/docs

## 💬 Preguntas frecuentes

**¿Puedo usar sin Supabase?**
→ Sí, los datos mock funcionan perfectamente

**¿Necesito configurar backend Python?**
→ No, para testing usa datos mock. Para producción sí.

**¿Cuánto cuesta Mapbox?**
→ Gratis hasta 50k map loads/mes

**¿Puedo usar Leaflet en vez de Mapbox?**
→ Sí, pero Mapbox tiene mejor UX

**¿Funciona con otras bases de datos?**
→ Sí, adapta `src/app/page.tsx` para tu DB

---

¡Listo para explorar oportunidades IT! 🚀
