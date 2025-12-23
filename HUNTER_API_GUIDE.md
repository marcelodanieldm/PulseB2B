# 🎯 Hunter.io API - Guía Rápida de Pruebas

## 📋 Descripción

Hunter.io es una API para encontrar y verificar direcciones de correo electrónico profesionales. Es ideal para lead enrichment y prospección B2B.

## 🚀 Inicio Rápido

### 1. Obtener API Key (GRATUITA)

1. Regístrate en: https://hunter.io/users/sign_up
2. Plan gratuito: **50 requests/mes** (sin tarjeta)
3. Ve a tu dashboard: https://hunter.io/api
4. Copia tu API key

### 2. Configurar en tu Proyecto

Agrega a tu archivo `.env`:

```env
HUNTER_API_KEY=tu_api_key_aqui
```

### 3. Ejecutar Pruebas

```bash
# Windows
test_hunter.bat

# O directamente
python test_hunter_api.py
```

## 🔧 Funcionalidades de la API

### 1. **Domain Search** - Buscar Emails de una Empresa
Encuentra todos los emails asociados a un dominio.

```python
# Ejemplo
test_domain_search('stripe.com')
```

**Resultado:**
- Lista de emails encontrados
- Nombres y cargos de las personas
- Patrón de emails de la empresa (ej: {first}.{last}@company.com)
- Score de confianza (0-100%)

**Casos de uso:**
- Prospección inicial de empresa
- Encontrar contactos en empresa target
- Identificar estructura de emails

---

### 2. **Email Finder** - Encontrar Email Específico
Busca el email de una persona específica en una empresa.

```python
# Ejemplo
test_email_finder('stripe.com', 'Patrick', 'Collison')
```

**Resultado:**
- Email predicho/encontrado
- Score de confianza
- Número de fuentes que validan el email

**Casos de uso:**
- Encontrar email de un decisor específico
- Buscar contacto directo con persona clave
- Personalización de outreach

---

### 3. **Email Verifier** - Verificar si Email Existe
Valida si una dirección de email existe y es válida.

```python
# Ejemplo
test_email_verifier('patrick@stripe.com')
```

**Resultado:**
- Status: `valid`, `invalid`, `accept_all`, `unknown`
- Score: 0-100%
- Checks: SMTP, MX Records, formato

**Casos de uso:**
- Limpiar listas de emails
- Validar antes de enviar campaña
- Reducir bounce rate

---

### 4. **Email Count** - Contar Emails de Dominio
Cuenta cuántos emails hay disponibles para un dominio.

```python
# Ejemplo
test_email_count('stripe.com')
```

**Resultado:**
- Total de emails
- Emails personales vs genéricos

**Casos de uso:**
- Evaluar tamaño de empresa
- Decidir si vale la pena hacer domain search completo

---

### 5. **Account Info** - Ver Uso de API
Revisa tu consumo de requests y límites.

```python
# Ejemplo
check_api_usage()
```

**Resultado:**
- Plan actual
- Requests usados/disponibles
- Fecha de reset

---

## 💰 Planes y Pricing

| Plan | Requests/mes | Precio | Ideal para |
|------|--------------|--------|------------|
| **Free** | 50 | $0 | Testing y desarrollo |
| **Starter** | 1,000 | $49 | Pequeñas empresas |
| **Growth** | 5,000 | $149 | Empresas medianas |
| **Business** | 20,000 | $399 | Empresas grandes |

> 💡 **Tip:** Comienza con el plan gratuito para probar. 50 requests son suficientes para validar la API.

---

## 🎓 Mejores Prácticas

### ✅ DO
- **Cache resultados** - No consultar el mismo dominio múltiples veces
- **Batch processing** - Agrupa requests para usar eficientemente tu cuota
- **Verificar emails** - Siempre verifica antes de enviar emails masivos
- **Combinar con otras APIs** - Usa Clearbit o FullContact como complemento

### ❌ DON'T
- **No hagas spam** - Respeta las políticas de privacidad
- **No excedas tu cuota** - Monitorea tu uso regularmente
- **No confíes 100% en scores bajos** - Emails con score <50% pueden ser válidos

---

## 📊 Integración con tu Sistema

Hunter.io ya está integrado en tu sistema de lead enrichment:

```javascript
// Ver: scripts/lead_enrichment_service.js
async function enrichWithHunter(domain) {
  const response = await axios.get(`https://api.hunter.io/v2/domain-search`, {
    params: {
      domain: domain,
      api_key: HUNTER_API_KEY,
      limit: 10
    }
  });
  
  return response.data;
}
```

**Flujo actual:**
1. Clearbit (primary) → Datos completos de empresa
2. Hunter.io (fallback) → Si Clearbit falla
3. Basic DNS (validation) → Fallback final

---

## 🔍 Ejemplos de Casos de Uso

### Caso 1: Prospección de Nueva Empresa
```python
# 1. Descubrir emails del dominio
domain_data = test_domain_search('targetcompany.com')

# 2. Identificar decisores (ej: CTOs, CEOs)
# 3. Usar Email Finder para contactos específicos
email = test_email_finder('targetcompany.com', 'John', 'Doe')

# 4. Verificar email antes de contactar
verification = test_email_verifier(email['email'])
```

### Caso 2: Limpieza de Lista de Emails
```python
email_list = ['contact1@company.com', 'contact2@company.com']

for email in email_list:
    result = test_email_verifier(email)
    if result['status'] == 'valid' and result['score'] > 70:
        # Email válido - mantener
        valid_emails.append(email)
    else:
        # Email dudoso - remover
        invalid_emails.append(email)
```

### Caso 3: Enriquecimiento de Lead desde Email
```python
# Tienes: john.doe@company.com
# Extraer dominio
domain = email.split('@')[1]

# Buscar información de la empresa
company_data = test_domain_search(domain)

# Ahora tienes:
# - Nombre de empresa
# - Otros contactos
# - Patrón de emails
# - Tamaño aproximado (por cantidad de emails)
```

---

## 🐛 Troubleshooting

### Error: API Key Invalid
```
❌ ERROR HTTP: 401
→ API key inválida o no configurada
```
**Solución:** Verifica que `HUNTER_API_KEY` esté en tu `.env`

### Error: Rate Limit Exceeded
```
❌ ERROR HTTP: 429
→ Límite de requests excedido
```
**Solución:** 
- Espera hasta el reset mensual
- Upgrade a plan pago
- Implementa caching para reducir requests

### No se Encuentran Emails
```
⚠️ No se encontraron emails para example.com
```
**Posibles causas:**
- Dominio muy nuevo o pequeño
- Empresa no tiene presencia pública
- Emails no están indexados públicamente

---

## 📚 Recursos

- **Documentación oficial:** https://hunter.io/api-documentation/v2
- **Dashboard:** https://hunter.io/api
- **Status page:** https://status.hunter.io
- **Changelog:** https://hunter.io/changelog

---

## 🎯 Próximos Pasos

1. ✅ Ejecuta `test_hunter.bat` para probar la API
2. ✅ Prueba con dominios de tus empresas target
3. ✅ Integra en tu flujo de lead enrichment existente
4. ✅ Combina con Clearbit para datos más completos
5. ✅ Implementa caching para optimizar uso de cuota

---

## 💡 Tips Avanzados

### Optimizar Uso de API

```python
# Cachear resultados en base de datos
def get_company_emails(domain):
    # 1. Buscar en cache primero
    cached = db.get_cached_domain(domain)
    if cached and not is_expired(cached):
        return cached
    
    # 2. Si no hay cache, llamar API
    result = test_domain_search(domain)
    
    # 3. Guardar en cache (30 días)
    db.cache_domain(domain, result, expire_days=30)
    
    return result
```

### Combinar con Otras Fuentes

```python
def enrich_lead_complete(email):
    # 1. Hunter - Verificar email
    verified = test_email_verifier(email)
    
    # 2. Clearbit - Datos de persona
    person_data = clearbit.enrich_person(email)
    
    # 3. LinkedIn - Perfil profesional
    linkedin_data = linkedin.search_profile(person_data['name'])
    
    return {
        'email_valid': verified['status'] == 'valid',
        'email_score': verified['score'],
        'person': person_data,
        'linkedin': linkedin_data
    }
```

---

**¿Preguntas?** Revisa la documentación oficial o abre un issue en el repo.
