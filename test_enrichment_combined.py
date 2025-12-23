"""
Test script combinado: Hunter.io + Clearbit API
Muestra cómo ambas APIs se complementan para lead enrichment
"""
import os
import requests
import json
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración
HUNTER_API_KEY = os.getenv('HUNTER_API_KEY')
CLEARBIT_API_KEY = os.getenv('CLEARBIT_API_KEY')

def print_section(title):
    """Imprime un título de sección"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_subsection(title):
    """Imprime un subtítulo"""
    print(f"\n   {title}")
    print("   " + "-"*65)

def super_enrichment(email):
    """
    Super Enrichment: Combina Hunter.io + Clearbit
    Maximiza la información obtenida usando ambas APIs
    """
    print_section(f"🚀 SUPER ENRICHMENT: {email}")
    
    result = {
        'email': email,
        'person': {},
        'company': {},
        'verification': {},
        'sources': []
    }
    
    # ===== CLEARBIT: Datos completos de persona + empresa =====
    print_subsection("1️⃣ CLEARBIT - Person + Company Enrichment")
    
    if CLEARBIT_API_KEY:
        try:
            url = "https://person.clearbit.com/v2/combined/find"
            headers = {'Authorization': f'Bearer {CLEARBIT_API_KEY}'}
            
            response = requests.get(url, params={'email': email}, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            if data and data.get('person'):
                person = data['person']
                company = data.get('company', {})
                
                result['person'] = {
                    'name': person.get('name', {}).get('fullName'),
                    'first_name': person.get('name', {}).get('givenName'),
                    'last_name': person.get('name', {}).get('familyName'),
                    'title': person.get('employment', {}).get('title'),
                    'role': person.get('employment', {}).get('role'),
                    'seniority': person.get('employment', {}).get('seniority'),
                    'location': f"{person.get('geo', {}).get('city', '')}, {person.get('geo', {}).get('country', '')}",
                    'linkedin': person.get('linkedin', {}).get('handle'),
                    'twitter': person.get('twitter', {}).get('handle'),
                    'github': person.get('github', {}).get('handle'),
                    'avatar': person.get('avatar')
                }
                
                result['company'] = {
                    'name': company.get('name'),
                    'domain': company.get('domain'),
                    'description': company.get('description'),
                    'employees': company.get('metrics', {}).get('employees'),
                    'employees_range': company.get('metrics', {}).get('employeesRange'),
                    'industry': company.get('category', {}).get('industry'),
                    'sector': company.get('category', {}).get('sector'),
                    'founded_year': company.get('foundedYear'),
                    'tech_stack': company.get('tech', [])[:10],  # Primeras 10 tecnologías
                    'logo': company.get('logo')
                }
                
                result['sources'].append('clearbit')
                
                print("   ✅ Clearbit: Datos encontrados")
                print(f"      • Persona: {result['person']['name']}")
                print(f"      • Cargo: {result['person']['title']}")
                print(f"      • Empresa: {result['company']['name']}")
                print(f"      • Industria: {result['company']['industry']}")
            else:
                print("   ⚠️  Clearbit: No se encontraron datos")
                
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                print("   ⚠️  Clearbit: Persona no encontrada (404)")
            elif response.status_code == 402:
                print("   ⚠️  Clearbit: Créditos agotados (402)")
            else:
                print(f"   ❌ Clearbit: Error {response.status_code}")
        except Exception as e:
            print(f"   ❌ Clearbit: {str(e)[:60]}...")
    else:
        print("   ⚠️  Clearbit: API key no configurada (skip)")
    
    # ===== HUNTER.IO: Verificación de email =====
    print_subsection("2️⃣ HUNTER.IO - Email Verification")
    
    if HUNTER_API_KEY:
        try:
            url = "https://api.hunter.io/v2/email-verifier"
            params = {
                'email': email,
                'api_key': HUNTER_API_KEY
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('data'):
                verify = data['data']
                
                result['verification'] = {
                    'status': verify.get('status'),
                    'score': verify.get('score'),
                    'result': verify.get('result'),
                    'smtp_check': verify.get('smtp_check'),
                    'mx_records': verify.get('mx_records')
                }
                
                result['sources'].append('hunter')
                
                status_emoji = {
                    'valid': '✅',
                    'invalid': '❌',
                    'accept_all': '⚠️',
                    'unknown': '❓'
                }
                
                emoji = status_emoji.get(verify.get('status'), '❓')
                print(f"   {emoji} Hunter: Email {verify.get('status')}")
                print(f"      • Score: {verify.get('score')}/100")
                print(f"      • SMTP: {verify.get('smtp_check')}")
            else:
                print("   ⚠️  Hunter: No se pudo verificar")
                
        except Exception as e:
            print(f"   ❌ Hunter: {str(e)[:60]}...")
    else:
        print("   ⚠️  Hunter: API key no configurada (skip)")
    
    # ===== HUNTER.IO: Fallback si Clearbit no encontró empresa =====
    if not result['company'].get('name') and HUNTER_API_KEY:
        print_subsection("3️⃣ HUNTER.IO - Company Fallback")
        
        try:
            domain = email.split('@')[1]
            url = "https://api.hunter.io/v2/domain-search"
            params = {
                'domain': domain,
                'api_key': HUNTER_API_KEY,
                'limit': 1
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('data'):
                company_data = data['data']
                
                result['company'] = {
                    'name': company_data.get('organization'),
                    'domain': company_data.get('domain'),
                    'email_pattern': company_data.get('pattern'),
                    'total_emails': company_data.get('emails')
                }
                
                if 'hunter' not in result['sources']:
                    result['sources'].append('hunter')
                
                print(f"   ✅ Hunter: Datos de empresa encontrados")
                print(f"      • Empresa: {result['company']['name']}")
                print(f"      • Patrón email: {result['company']['email_pattern']}")
            else:
                print("   ⚠️  Hunter: No se encontró empresa")
                
        except Exception as e:
            print(f"   ❌ Hunter: {str(e)[:60]}...")
    
    # ===== CLEARBIT LOGO (Gratis) =====
    print_subsection("4️⃣ CLEARBIT LOGO API (Free)")
    
    if result['company'].get('domain'):
        domain = result['company']['domain']
        logo_url = f"https://logo.clearbit.com/{domain}"
        result['company']['logo'] = logo_url
        
        print(f"   ✅ Logo URL: {logo_url}")
    else:
        print("   ⚠️  No hay dominio para obtener logo")
    
    return result

def display_enrichment_result(result):
    """Muestra el resultado final del enrichment"""
    print_section("📊 RESULTADO FINAL DEL ENRICHMENT")
    
    print(f"\n   📧 Email: {result['email']}")
    print(f"   🔍 Fuentes usadas: {', '.join(result['sources']) if result['sources'] else 'Ninguna'}")
    
    # Persona
    if result['person'].get('name'):
        print(f"\n   👤 PERSONA:")
        print(f"      • Nombre: {result['person']['name']}")
        print(f"      • Cargo: {result['person']['title'] or 'N/A'}")
        print(f"      • Rol: {result['person']['role'] or 'N/A'}")
        print(f"      • Senioridad: {result['person']['seniority'] or 'N/A'}")
        print(f"      • Ubicación: {result['person']['location'] or 'N/A'}")
        
        if result['person'].get('linkedin'):
            print(f"      • LinkedIn: linkedin.com/in/{result['person']['linkedin']}")
        if result['person'].get('twitter'):
            print(f"      • Twitter: @{result['person']['twitter']}")
    else:
        print(f"\n   👤 PERSONA: No encontrada")
    
    # Empresa
    if result['company'].get('name'):
        print(f"\n   🏢 EMPRESA:")
        print(f"      • Nombre: {result['company']['name']}")
        print(f"      • Dominio: {result['company']['domain'] or 'N/A'}")
        
        if result['company'].get('description'):
            desc = result['company']['description'][:80] + "..." if len(result['company'].get('description', '')) > 80 else result['company'].get('description', '')
            print(f"      • Descripción: {desc}")
        
        if result['company'].get('employees'):
            print(f"      • Empleados: {result['company']['employees']}")
        elif result['company'].get('employees_range'):
            print(f"      • Empleados: {result['company']['employees_range']}")
        
        print(f"      • Industria: {result['company'].get('industry') or 'N/A'}")
        
        if result['company'].get('tech_stack') and len(result['company']['tech_stack']) > 0:
            techs = ', '.join(result['company']['tech_stack'][:5])
            print(f"      • Tech Stack: {techs}")
        
        if result['company'].get('logo'):
            print(f"      • Logo: {result['company']['logo']}")
    else:
        print(f"\n   🏢 EMPRESA: No encontrada")
    
    # Verificación
    if result['verification'].get('status'):
        print(f"\n   ✅ VERIFICACIÓN:")
        print(f"      • Estado: {result['verification']['status']}")
        print(f"      • Score: {result['verification']['score']}/100")
        print(f"      • SMTP Check: {result['verification']['smtp_check']}")
    else:
        print(f"\n   ✅ VERIFICACIÓN: No realizada")
    
    # Lead Score (ejemplo)
    score = calculate_lead_score(result)
    print(f"\n   ⭐ LEAD SCORE: {score}/100")

def calculate_lead_score(result):
    """Calcula un lead score básico basado en los datos"""
    score = 0
    
    # Email verificado (+30)
    if result['verification'].get('status') == 'valid':
        score += 30
    elif result['verification'].get('score', 0) > 70:
        score += 20
    
    # Cargo senior (+20)
    seniority = result['person'].get('seniority', '').lower()
    if 'executive' in seniority or 'director' in seniority or 'vp' in seniority:
        score += 20
    elif 'manager' in seniority:
        score += 10
    
    # Empresa mediana/grande (+20)
    employees = result['company'].get('employees', 0)
    if employees > 500:
        score += 20
    elif employees > 50:
        score += 10
    
    # Industria tech (+15)
    industry = result['company'].get('industry', '').lower()
    tech_keywords = ['software', 'technology', 'saas', 'internet', 'computer']
    if any(keyword in industry for keyword in tech_keywords):
        score += 15
    
    # LinkedIn disponible (+15)
    if result['person'].get('linkedin'):
        score += 15
    
    return min(score, 100)  # Max 100

def compare_apis():
    """Muestra comparación de las APIs"""
    print_section("📊 COMPARACIÓN: HUNTER.IO vs CLEARBIT")
    
    comparison = """
   ╔═══════════════════════╦═══════════════════╦═══════════════════╗
   ║ Característica        ║ Hunter.io         ║ Clearbit          ║
   ╠═══════════════════════╬═══════════════════╬═══════════════════╣
   ║ Búsqueda Emails       ║ ✅ Especialidad   ║ ❌ No             ║
   ║ Verificación Email    ║ ✅ Excelente      ║ ❌ No             ║
   ║ Datos Persona         ║ ⭐⭐⭐ Básico      ║ ⭐⭐⭐⭐⭐ Completo  ║
   ║ Datos Empresa         ║ ⭐⭐⭐ Bueno       ║ ⭐⭐⭐⭐⭐ Excelente ║
   ║ Tech Stack            ║ ❌ No             ║ ✅ 100+ techs     ║
   ║ Logo API              ║ ❌ No             ║ ✅ Gratis         ║
   ║ Plan Gratuito         ║ ✅ 50 req/mes     ║ ⚠️ Trial limitado ║
   ║ Precio                ║ $ Económico       ║ $$$ Premium       ║
   ║ Cobertura             ║ ~40-50%           ║ ~30-40%           ║
   ╚═══════════════════════╩═══════════════════╩═══════════════════╝
   
   💡 RECOMENDACIÓN: Usa ambas APIs en combinación
      • Hunter.io: Buscar y verificar emails
      • Clearbit: Enriquecer con datos completos
      • Logo API: Mejorar UI (gratis)
   """
    print(comparison)

def main():
    """Función principal"""
    print("\n")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║          SUPER ENRICHMENT: HUNTER.IO + CLEARBIT                    ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    
    # Verificar configuración
    print("\n📋 CONFIGURACIÓN:")
    print(f"   • Hunter.io API: {'✅ Configurada' if HUNTER_API_KEY else '❌ No configurada'}")
    print(f"   • Clearbit API: {'✅ Configurada' if CLEARBIT_API_KEY else '❌ No configurada'}")
    
    if not HUNTER_API_KEY and not CLEARBIT_API_KEY:
        print("\n❌ ERROR: No hay APIs configuradas")
        print("\n   Agrega al menos una API key en tu .env:")
        print("   • HUNTER_API_KEY=tu_key (https://hunter.io/api)")
        print("   • CLEARBIT_API_KEY=tu_key (https://clearbit.com)")
        return
    
    # Mostrar comparación
    compare_apis()
    
    # PRUEBA 1: Email conocido (Stripe)
    print("\n\n" + "🧪"*35)
    print("   PRUEBA 1: Email Conocido (Patrick Collison - Stripe)")
    print("🧪"*35)
    result1 = super_enrichment('patrick@stripe.com')
    display_enrichment_result(result1)
    
    # PRUEBA 2: Otro ejemplo
    print("\n\n" + "🧪"*35)
    print("   PRUEBA 2: Otro Email")
    print("🧪"*35)
    result2 = super_enrichment('john@example.com')  # Cambia por email real
    display_enrichment_result(result2)
    
    # Resumen final
    print("\n")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║                         PRUEBAS COMPLETADAS                        ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    
    print("\n🎯 PRÓXIMOS PASOS:")
    print("   1. Obtén API keys de ambos servicios")
    print("   2. Implementa caching para optimizar costos")
    print("   3. Integra en tu sistema de lead enrichment")
    print("   4. Usa Logo API para mejorar tu UI")
    
    print("\n📚 RECURSOS:")
    print("   • Hunter.io: https://hunter.io/api-documentation/v2")
    print("   • Clearbit: https://clearbit.com/docs")
    print("   • Logo API: https://clearbit.com/logo")

if __name__ == "__main__":
    main()
