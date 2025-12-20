# PulseB2B Frontend

🚀 **Next.js 14 Dashboard** para visualizar oportunidades de contratación IT a nivel global con sistema de semáforo inteligente.

## 🎯 Características

### 🗺️ Mapa Interactivo Global
- **Mapbox GL** con marcadores interactivos
- Sistema de semáforo visual:
  - 🔴 **Rojo**: Alto riesgo (cierre/despidos)
  - 🟢 **Verde**: Alta probabilidad de contratación (≥70%)
  - 🟡 **Dorado**: Funding reciente (<90 días) - ¡Oportunidad golden!
  - 🔵 **Azul**: Estable
- Marcadores con tamaño dinámico según probabilidad
- Popups detallados con métricas clave
- Clustering automático de empresas por región

### 📊 Dashboard Analytics
- **8 tarjetas estadísticas** en tiempo real:
  - Total de empresas
  - Empresas con alta probabilidad
  - Funding reciente
  - Empresas en riesgo
  - Probabilidad promedio
  - Jobs activos
  - Hot leads (≥80%)
  - Tasa de conversión

### 📈 Gráficos Interactivos (Recharts)
- **4 tipos de visualizaciones**:
  - Overview combinado (Team Size + Funding + Jobs)
  - Área de funding histórico
  - Crecimiento de equipo
  - Jobs publicados (gráfico de barras)
- Tooltips personalizados
- Animaciones fluidas

### 🔍 Filtros Avanzados
- **Traffic Light Status**: Filtro por color de semáforo
- **Probabilidad**: Rango 0-100%
- **Regiones**: North America, South America, Europe, Asia Pacific
- **Funding Stage**: Pre-Seed → Series D+
- **Funding Amount**: $0 - $100M
- Botón de reset rápido

### 🎴 Company Cards
- Diseño moderno con gradientes
- Métricas en tiempo real:
  - Funding total y etapa
  - Team size y crecimiento (3 meses)
  - Job velocity
  - Tech churn y senior departures
- Animaciones con Framer Motion
- Badge de "Featured" para empresas golden

## 🛠️ Stack Tecnológico

```json
{
  "framework": "Next.js 14.0.4 (App Router)",
  "language": "TypeScript 5.3.3",
  "styling": "Tailwind CSS 3.4.0",
  "maps": "Mapbox GL 3.1.0 + react-map-gl 7.1.7",
  "charts": "Recharts 2.10.3",
  "database": "Supabase JS 2.39.3",
  "animations": "Framer Motion 10.18.0",
  "state": "Zustand 4.4.7",
  "icons": "lucide-react 0.344.0"
}
```

## 📦 Instalación

### Prerrequisitos
- Node.js 18+ 
- npm/yarn/pnpm
- Mapbox Access Token
- Supabase Project

### 1. Instalar dependencias

```bash
cd frontend
npm install
# o
yarn install
# o
pnpm install
```

### 2. Configurar variables de entorno

Copia `.env.example` a `.env.local`:

```bash
cp .env.example .env.local
```

Edita `.env.local` con tus credenciales:

```env
# Mapbox
NEXT_PUBLIC_MAPBOX_TOKEN=tu_mapbox_token_aqui

# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://tu-proyecto.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=tu_anon_key_aqui

# Backend API (opcional)
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ML_API_URL=http://localhost:8000/predict
```

### 3. Obtener tokens necesarios

#### Mapbox Token
1. Crea una cuenta en [Mapbox](https://account.mapbox.com/)
2. Ve a [Access Tokens](https://account.mapbox.com/access-tokens/)
3. Crea un nuevo token con scope `styles:read`, `fonts:read`, `tiles:read`
4. Copia el token a `NEXT_PUBLIC_MAPBOX_TOKEN`

#### Supabase Credentials
1. Crea un proyecto en [Supabase](https://supabase.com/)
2. Ve a Settings → API
3. Copia la `URL` y `anon/public key`
4. Pega en `.env.local`

### 4. Configurar base de datos (Supabase)

Crea la tabla `hiring_predictions` en Supabase SQL Editor:

```sql
-- Create hiring_predictions table
CREATE TABLE hiring_predictions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  company_id TEXT NOT NULL,
  name TEXT NOT NULL,
  city TEXT NOT NULL,
  country TEXT NOT NULL,
  latitude FLOAT NOT NULL,
  longitude FLOAT NOT NULL,
  region TEXT NOT NULL,
  industry TEXT,
  team_size INTEGER,
  team_size_growth_3m INTEGER,
  total_funding BIGINT,
  funding_stage TEXT,
  last_funding_date TIMESTAMP,
  funding_recency INTEGER,
  active_job_posts INTEGER,
  job_post_velocity FLOAT,
  tech_churn FLOAT,
  senior_departures INTEGER,
  hiring_probability FLOAT NOT NULL,
  confidence FLOAT NOT NULL,
  label TEXT NOT NULL,
  status TEXT NOT NULL,
  status_reason TEXT,
  predicted_at TIMESTAMP DEFAULT NOW(),
  last_updated TIMESTAMP DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_hiring_predictions_status ON hiring_predictions(status);
CREATE INDEX idx_hiring_predictions_probability ON hiring_predictions(hiring_probability DESC);
CREATE INDEX idx_hiring_predictions_region ON hiring_predictions(region);
CREATE INDEX idx_hiring_predictions_company_id ON hiring_predictions(company_id);

-- Enable Row Level Security (opcional)
ALTER TABLE hiring_predictions ENABLE ROW LEVEL SECURITY;

-- Create policy to allow public read access (ajustar según necesidades)
CREATE POLICY "Allow public read access" ON hiring_predictions
  FOR SELECT USING (true);
```

### 5. Ejecutar en desarrollo

```bash
npm run dev
# o
yarn dev
# o
pnpm dev
```

Abre [http://localhost:3000](http://localhost:3000)

## 🏗️ Estructura del Proyecto

```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx            # Dashboard principal
│   │   └── globals.css         # Estilos globales
│   ├── components/
│   │   ├── OpportunitiesMap.tsx    # Mapa interactivo con Mapbox
│   │   ├── CompanyCard.tsx         # Card de empresa
│   │   ├── GrowthChart.tsx         # Gráficos de crecimiento
│   │   ├── FilterPanel.tsx         # Panel de filtros
│   │   └── DashboardStats.tsx      # Tarjetas de estadísticas
│   ├── lib/
│   │   ├── utils.ts            # Funciones utilitarias
│   │   └── supabase.ts         # Cliente Supabase
│   └── types/
│       └── index.ts            # TypeScript types
├── public/                     # Assets estáticos
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── next.config.js
└── .env.local                  # Variables de entorno
```

## 🎨 Componentes Principales

### OpportunitiesMap
Mapa global con marcadores interactivos:
```tsx
<OpportunitiesMap
  companies={companies}
  filters={filters}
  selectedCompany={selectedCompany}
  onCompanySelect={setSelectedCompany}
/>
```

### CompanyCard
Card de empresa con métricas:
```tsx
<CompanyCard
  company={company}
  onClick={() => handleClick(company)}
  featured={company.status === 'golden'}
/>
```

### GrowthChart
Gráficos interactivos con Recharts:
```tsx
<GrowthChart
  companyName={company.name}
  metrics={growthMetrics}
/>
```

### FilterPanel
Panel de filtros avanzados:
```tsx
<FilterPanel
  filters={filters}
  onFiltersChange={setFilters}
  onReset={resetFilters}
/>
```

## 🔗 Integración con Backend Python

### Opción 1: API REST

Crear endpoint en tu backend Python:

```python
# backend/api/main.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

@app.get("/api/predictions")
async def get_predictions():
    # Leer desde base de datos o ejecutar ML pipeline
    predictions = load_predictions_from_db()
    return predictions
```

Llamar desde Next.js:

```typescript
// frontend/src/app/page.tsx
const loadCompanies = async () => {
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/predictions`);
  const data = await response.json();
  setCompanies(data);
};
```

### Opción 2: Supabase + Python Script

1. Script Python escribe a Supabase:

```python
# scripts/push_to_supabase.py
from supabase import create_client
import os

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def push_predictions(predictions):
    for pred in predictions:
        supabase.table('hiring_predictions').upsert(pred).execute()
```

2. Frontend lee desde Supabase:

```typescript
// frontend/src/app/page.tsx
import { supabase } from '@/lib/supabase';

const loadCompanies = async () => {
  const { data, error } = await supabase
    .from('hiring_predictions')
    .select('*')
    .order('hiring_probability', { ascending: false });
  
  if (data) setCompanies(data);
};
```

## 🚀 Deployment

### Vercel (Recomendado)

1. Push tu código a GitHub
2. Conecta tu repo en [Vercel](https://vercel.com)
3. Configura variables de entorno:
   - `NEXT_PUBLIC_MAPBOX_TOKEN`
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
4. Deploy automático

```bash
npm run build
vercel --prod
```

### Netlify

```bash
npm run build
netlify deploy --prod --dir=.next
```

### Docker

```dockerfile
# Dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
```

```bash
docker build -t pulseb2b-frontend .
docker run -p 3000:3000 --env-file .env.local pulseb2b-frontend
```

## 🎯 Uso

### 1. Vista de Mapa
- Explora empresas en el mapa global
- Haz clic en marcadores para ver detalles
- Usa la leyenda para entender los colores

### 2. Vista de Grid
- Cambia a vista de tarjetas
- Scroll para ver todas las empresas
- Click en tarjeta para ver gráficos de crecimiento

### 3. Filtros
- Filtra por status de semáforo
- Ajusta rango de probabilidad
- Selecciona regiones específicas
- Filtra por etapa de funding

### 4. Buscar
- Busca por nombre de empresa
- Busca por ciudad o país
- Resultados en tiempo real

## 🔧 Personalización

### Cambiar colores del semáforo

Edita [tailwind.config.ts](tailwind.config.ts):

```typescript
colors: {
  risk: {
    high: '#EF4444',    // Rojo
    medium: '#F59E0B',  // Amarillo
    low: '#10B981',     // Verde
  },
  opportunity: {
    funding: '#F59E0B',   // Dorado
    hiring: '#10B981',    // Verde
    stable: '#3B82F6',    // Azul
    declining: '#EF4444', // Rojo
  },
}
```

### Modificar lógica de semáforo

Edita [src/lib/utils.ts](src/lib/utils.ts) → `getTrafficLightStatus()`:

```typescript
export function getTrafficLightStatus(company: Company) {
  // Tu lógica personalizada aquí
  if (company.hiring_probability >= 80) {
    return { status: 'green', reason: 'Hot lead!' };
  }
  // ...
}
```

## 📝 Scripts

```bash
# Desarrollo
npm run dev

# Build de producción
npm run build

# Preview de producción
npm start

# Linting
npm run lint

# Type checking
npm run type-check
```

## 🐛 Troubleshooting

### Error: "Mapbox token not found"
→ Verifica que `NEXT_PUBLIC_MAPBOX_TOKEN` esté en `.env.local`

### Error: "Supabase connection failed"
→ Verifica URL y API key en `.env.local`
→ Asegúrate de que la tabla `hiring_predictions` existe

### Mapa no se muestra
→ Verifica tu token de Mapbox
→ Revisa la consola del navegador para errores
→ Asegúrate de que `mapbox-gl` CSS está importado

### Datos no se cargan
→ Verifica que Supabase tenga datos en `hiring_predictions`
→ Revisa las políticas de Row Level Security
→ Verifica la conexión en Network tab

## 📚 Recursos

- [Next.js Documentation](https://nextjs.org/docs)
- [Mapbox GL JS](https://docs.mapbox.com/mapbox-gl-js/)
- [Recharts Documentation](https://recharts.org/)
- [Supabase Documentation](https://supabase.com/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Framer Motion](https://www.framer.com/motion/)

## 🤝 Contribuir

1. Fork el proyecto
2. Crea tu feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

MIT License - ver [LICENSE](LICENSE) para más detalles

## 👥 Autores

- **Daniel M.** - *ML Engine & Frontend* - [marcelodanieldm](https://github.com/marcelodanieldm)

---

**Made with ❤️ using Next.js 14, TypeScript, and Mapbox**
