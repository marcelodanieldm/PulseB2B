# 🎯 Clearbit API - Guía Rápida de Pruebas

## 📋 Descripción

Clearbit es una de las APIs de enriquecimiento B2B más completas del mercado. Proporciona datos detallados sobre empresas y profesionales, ideal para lead enrichment, prospección y personalización.

## 🚀 Inicio Rápido

### 1. Obtener API Key

1. Regístrate en: https://clearbit.com/
2. Trial gratuito con créditos limitados
3. Ve a: https://dashboard.clearbit.com/api
4. Copia tu API key (formato: `sk_...`)

### 2. Configurar en tu Proyecto

Agrega a tu archivo `.env`:

```env
CLEARBIT_API_KEY=sk_tu_api_key_aqui
```

### 3. Ejecutar Pruebas

```bash
# Windows
test_clearbit.bat

# O directamente
python test_clearbit_api.py
```

## 🔧 Funcionalidades de la API

### 🆓 APIs GRATUITAS (Sin API Key)

#### 1. **Logo API** - Obtener Logos de Empresas
Obtén logos de alta calidad de cualquier empresa.

```html
<!-- Uso directo en HTML -->
<img src="https://logo.clearbit.com/stripe.com" alt="Stripe Logo">
```

**Características:**
- ✅ 100% gratuita
- ✅ No requiere API key
- ✅ Alta calidad (hasta 400x400px)
- ✅ Cache automático
- ✅ Fallback transparente

**Casos de uso:**
- Mostrar logos en dashboards
- Enriquecer listas de empresas
- Mejorar UX de CRM

**Ejemplo:**
```python
test_logo_api('stripe.com')
# → https://logo.clearbit.com/stripe.com
```

---

#### 2. **Name to Domain API** - Encontrar Dominio por Nombre
Busca empresas y obtén su dominio web.

```python
test_name_to_domain('Stripe')
```

**Características:**
- ✅ 100% gratuita
- ✅ No requiere API key
- ✅ Autocompletado inteligente
- ✅ Retorna múltiples resultados

**Casos de uso:**
- Convertir nombre de empresa a dominio
- Autocompletado en formularios
- Validación de empresas

---

### 💰 APIs DE PAGO (Requieren API Key)

#### 3. **Person Enrichment** - Enriquecer Datos de Persona
Obtén información completa sobre una persona por su email.

```python
test_person_enrichment('patrick@stripe.com')
```

**Datos retornados:**
- 👤 Nombre completo
- 💼 Empresa y cargo actual
- 📍 Ubicación (ciudad, país)
- 🌐 Redes sociales (LinkedIn, Twitter, GitHub)
- 🖼️ Avatar/foto
- 📊 Rol y senioridad

**Precio:** ~$0.35 por lookup exitoso

**Casos de uso:**
- Enriquecer leads de formularios
- Personalizar outreach
- Completar perfiles de CRM

---

#### 4. **Company Enrichment** - Enriquecer Datos de Empresa
Obtén información completa sobre una empresa por dominio.

```python
test_company_enrichment('stripe.com')
```

**Datos retornados:**
- 🏢 Nombre y descripción
- 📊 Métricas (empleados, ingresos estimados)
- 🏭 Industria y sector
- 📍 Ubicación y oficinas
- 💻 Stack tecnológico (100+ tecnologías)
- 🌐 Redes sociales
- 🎯 Tags y categorías
- 📅 Año de fundación

**Precio:** ~$0.35 por lookup exitoso

**Casos de uso:**
- Calificación de leads (lead scoring)
- Segmentación de mercado
- Análisis de competencia
- Account-Based Marketing

---

#### 5. **Combined Enrichment** - Persona + Empresa
Enriquece persona y empresa en una sola llamada (optimiza costos).

```python
test_combined_enrichment('patrick@stripe.com')
```

**Beneficios:**
- ✅ Una sola llamada API
- ✅ Un solo cargo
- ✅ Datos relacionados garantizados

---

## 💰 Planes y Pricing

| Plan | Precio | Créditos | Ideal para |
|------|--------|----------|------------|
| **Free Trial** | $0 | Limitados | Testing |
| **Growth** | $99/mes | 500 enrichments | Startups |
| **Business** | $499/mes | 3,000 enrichments | Empresas medianas |
| **Enterprise** | Custom | Unlimited | Grandes empresas |
| **Pay-as-you-go** | Variable | Por uso | Uso esporádico |

### Costos por API:
- **Enrichment API:** ~$0.35 por lookup exitoso
- **Prospector API:** ~$0.50 por búsqueda
- **Discovery API:** ~$2.50 por exportación
- **Logo API:** **GRATIS**
- **Name to Domain:** **GRATIS**

> 💡 **Tip:** Solo pagas por lookups exitosos (cuando se encuentra información)

---

## 🎓 Mejores Prácticas

### ✅ DO
- **Cache agresivamente** - Los datos no cambian frecuentemente
- **Usa Combined API** - Optimiza costos combinando person + company
- **Usa APIs gratuitas** - Logo y Name-to-Domain no tienen costo
- **Maneja 404s** - No todos los emails/dominios tienen datos
- **Implement fallbacks** - Combina con Hunter.io o FullContact

### ❌ DON'T
- **No consultes repetidamente** - Cache por al menos 30 días
- **No confíes en 100% cobertura** - ~30-40% de emails tienen datos
- **No ignores rate limits** - 600 requests/min en Growth plan
- **No uses para B2C** - Clearbit es especializado en B2B

---

## 📊 Integración con tu Sistema

Clearbit ya está integrado como fuente principal en tu sistema:

```javascript
// Ver: scripts/lead_enrichment_service.js
async function enrichWithClearbit(email) {
  const response = await axios.get(
    `https://person.clearbit.com/v2/combined/find`,
    {
      params: { email },
      headers: { Authorization: `Bearer ${CLEARBIT_API_KEY}` }
    }
  );
  
  return response.data;
}
```

**Flujo actual:**
1. **Clearbit** (primary) → Datos más completos
2. Hunter.io (fallback) → Si Clearbit no encuentra
3. Basic DNS (validation) → Fallback final

---

## 🔍 Comparación: Clearbit vs Hunter.io

| Característica | Clearbit | Hunter.io |
|---------------|----------|-----------|
| **Datos de Persona** | ⭐⭐⭐⭐⭐ Muy completo | ⭐⭐⭐ Básico |
| **Datos de Empresa** | ⭐⭐⭐⭐⭐ Excelente | ⭐⭐⭐ Bueno |
| **Stack Tecnológico** | ✅ Sí (100+ techs) | ❌ No |
| **Búsqueda de Emails** | ❌ No | ✅ Sí (especialidad) |
| **Verificación Email** | ❌ No | ✅ Sí |
| **Precio** | $$$ Más caro | $ Más económico |
| **Cobertura** | ~30-40% | ~40-50% |
| **Plan Gratuito** | Trial limitado | 50 req/mes |
| **Logo API** | ✅ Gratis | ❌ No |

**Recomendación:** 
- Usa **Clearbit** para enriquecimiento profundo
- Usa **Hunter.io** para encontrar/verificar emails
- Combina ambos para máxima cobertura

---

## 🔍 Ejemplos de Casos de Uso

### Caso 1: Enriquecer Lead desde Formulario Web
```python
# Usuario se registra con: john@acme.com

# 1. Obtener datos completos
data = test_combined_enrichment('john@acme.com')

# Ahora tienes:
# - Nombre: John Doe
# - Cargo: VP of Engineering
# - Empresa: Acme Corp
# - Tamaño: 500-1000 empleados
# - Industria: SaaS
# - Tecnologías: Python, AWS, React
# - LinkedIn, Twitter, GitHub
# - Logo de empresa

# 2. Usar para lead scoring
score = calculate_lead_score(
    company_size=data['company']['metrics']['employees'],
    industry=data['company']['category']['industry'],
    role=data['person']['employment']['role']
)
```

### Caso 2: Enriquecer Lista de Empresas Target
```python
target_companies = ['stripe.com', 'shopify.com', 'square.com']

for domain in target_companies:
    company_data = test_company_enrichment(domain)
    
    # Filtrar por criterios
    if (company_data['metrics']['employees'] > 500 and
        'fintech' in company_data['tags']):
        
        # Empresa califica - agregar a pipeline
        crm.add_to_pipeline(company_data)
```

### Caso 3: Personalizar Email Outreach
```python
# Tienes email: sarah@techcorp.com

person = test_person_enrichment('sarah@techcorp.com')

# Personalizar mensaje
email_template = f"""
Hi {person['name']['givenName']},

I noticed {person['employment']['name']} is using {person['employment']['company']['tech'][0]}
for your stack. As a {person['employment']['title']}, you might be interested in...
"""
```

### Caso 4: Autocompletar Empresa en Formulario
```html
<!-- Usuario empieza a escribir "Str..." -->
<input type="text" id="company-search" placeholder="Company name">

<script>
// Llamar a Name-to-Domain API
fetch('https://autocomplete.clearbit.com/v1/companies/suggest?query=Str')
  .then(res => res.json())
  .then(companies => {
    // Mostrar sugerencias:
    // - Stripe
    // - Stripe Payments
    // - Strapi
  });
</script>
```

---

## 🐛 Troubleshooting

### Error: API Key Invalid (401)
```
❌ ERROR HTTP: 401
→ API key inválida o no configurada
```
**Solución:** Verifica que tu `CLEARBIT_API_KEY` empiece con `sk_`

### Error: Payment Required (402)
```
❌ ERROR HTTP: 402
→ Créditos insuficientes - plan agotado
```
**Solución:** 
- Upgrade tu plan en dashboard
- Espera al reset mensual
- Activa pay-as-you-go

### Error: Not Found (404)
```
❌ ERROR HTTP: 404
→ Persona no encontrada en la base de datos
```
**Esto es NORMAL:** 
- Solo 30-40% de emails tienen datos
- Implementa fallback a Hunter.io
- No es un error de tu código

### Logo no Carga
```
⚠️ Logo no encontrado (código: 404)
```
**Solución:**
- Usa logo por defecto
- Verifica que el dominio sea correcto
- Algunos dominios pequeños no tienen logo

---

## 🎨 Usar Logo API en tu Frontend

### React
```jsx
function CompanyLogo({ domain }) {
  const logoUrl = `https://logo.clearbit.com/${domain}`;
  
  return (
    <img 
      src={logoUrl} 
      alt={`${domain} logo`}
      onError={(e) => {
        e.target.src = '/default-logo.png'; // Fallback
      }}
    />
  );
}
```

### CSS Background
```css
.company-logo {
  background-image: url('https://logo.clearbit.com/stripe.com');
  background-size: contain;
  background-repeat: no-repeat;
  width: 100px;
  height: 100px;
}
```

### Diferentes Tamaños
```html
<!-- Agregar parámetro de tamaño -->
<img src="https://logo.clearbit.com/stripe.com?size=200">
```

---

## 🔄 Webhooks y Streaming

Clearbit también ofrece:

### 1. **Reveal API** - Identificar Visitantes Anónimos
Identifica empresas que visitan tu website (por IP).

### 2. **Prospector API** - Encontrar Contactos
Busca personas en empresas target con filtros avanzados.

### 3. **Discovery API** - Encontrar Empresas
Busca empresas que cumplan criterios específicos.

*Estas APIs requieren planes enterprise. Consulta documentación para más info.*

---

## 📚 Recursos

- **Documentación:** https://clearbit.com/docs
- **Dashboard:** https://dashboard.clearbit.com/
- **API Status:** https://status.clearbit.com/
- **Changelog:** https://clearbit.com/changelog
- **Pricing:** https://clearbit.com/pricing

---

## 💡 Tips Avanzados

### Optimizar Costos con Cache Inteligente

```python
import time
from datetime import datetime, timedelta

def get_enriched_data(email, cache_days=90):
    # 1. Buscar en cache
    cached = db.get_cached(email)
    
    if cached:
        cached_date = cached['updated_at']
        age = datetime.now() - cached_date
        
        # Cache válido por 90 días
        if age < timedelta(days=cache_days):
            return cached['data']
    
    # 2. No hay cache válido - llamar API
    try:
        data = test_combined_enrichment(email)
        
        # 3. Guardar en cache
        db.cache_enrichment(
            email=email,
            data=data,
            expires_at=datetime.now() + timedelta(days=cache_days)
        )
        
        return data
    except:
        # 4. Si falla, intentar fallback
        return try_fallback_enrichment(email)
```

### Combinar Clearbit + Hunter.io

```python
def super_enrichment(email):
    result = {
        'email': email,
        'person': None,
        'company': None,
        'verified': False
    }
    
    # 1. Clearbit - Datos completos
    try:
        clearbit_data = test_combined_enrichment(email)
        result['person'] = clearbit_data.get('person')
        result['company'] = clearbit_data.get('company')
    except:
        pass
    
    # 2. Hunter - Verificar email
    try:
        hunter_verify = test_email_verifier(email)
        result['verified'] = hunter_verify['status'] == 'valid'
    except:
        pass
    
    # 3. Si Clearbit falló, intentar Hunter para empresa
    if not result['company']:
        domain = email.split('@')[1]
        hunter_company = test_domain_search(domain)
        result['company'] = {
            'name': hunter_company.get('organization'),
            'domain': domain
        }
    
    return result
```

### Enriquecimiento Asíncrono (para grandes volúmenes)

```python
import asyncio
import aiohttp

async def enrich_batch(emails):
    async with aiohttp.ClientSession() as session:
        tasks = []
        
        for email in emails:
            task = enrich_async(session, email)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

async def enrich_async(session, email):
    url = "https://person.clearbit.com/v2/combined/find"
    headers = {'Authorization': f'Bearer {CLEARBIT_API_KEY}'}
    
    async with session.get(url, params={'email': email}, headers=headers) as response:
        if response.status == 200:
            return await response.json()
        return None

# Uso
emails = ['email1@company.com', 'email2@company.com', ...]
results = asyncio.run(enrich_batch(emails))
```

---

## 🎯 Próximos Pasos

1. ✅ Ejecuta `test_clearbit.bat` para probar la API
2. ✅ Comienza con Logo API (gratis) para familiarizarte
3. ✅ Solicita trial para probar Enrichment APIs
4. ✅ Implementa caching para optimizar costos
5. ✅ Combina con Hunter.io para mejor cobertura
6. ✅ Usa Logo API en tu frontend inmediatamente

---

**¿Preguntas?** Revisa la [documentación oficial](https://clearbit.com/docs) o contacta su soporte.
