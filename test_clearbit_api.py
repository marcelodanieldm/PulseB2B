"""
Test script for Clearbit API
Prueba las funcionalidades principales de Clearbit
"""
import os
import requests
import json
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración
CLEARBIT_API_KEY = os.getenv('CLEARBIT_API_KEY')

def print_section(title):
    """Imprime un título de sección"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_person_enrichment(email):
    """
    1. Person Enrichment - Enriquece datos de una persona por email
    Obtén información completa sobre una persona
    """
    print_section(f"👤 PERSON ENRICHMENT: {email}")
    
    if not CLEARBIT_API_KEY:
        print("❌ ERROR: CLEARBIT_API_KEY no configurada")
        print("   Obtén tu API key en: https://clearbit.com/")
        return None
    
    try:
        url = "https://person.clearbit.com/v2/people/find"
        params = {'email': email}
        headers = {'Authorization': f'Bearer {CLEARBIT_API_KEY}'}
        
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        if data:
            print(f"✅ Persona encontrada:")
            print(f"   Nombre: {data.get('name', {}).get('fullName', 'N/A')}")
            print(f"   Email: {data.get('email', 'N/A')}")
            
            # Información profesional
            employment = data.get('employment', {})
            if employment:
                print(f"\n   💼 Información Laboral:")
                print(f"      Empresa: {employment.get('name', 'N/A')}")
                print(f"      Cargo: {employment.get('title', 'N/A')}")
                print(f"      Rol: {employment.get('role', 'N/A')}")
                print(f"      Antigüedad: {employment.get('seniority', 'N/A')}")
                print(f"      Dominio: {employment.get('domain', 'N/A')}")
            
            # Geolocalización
            geo = data.get('geo', {})
            if geo:
                print(f"\n   📍 Ubicación:")
                print(f"      Ciudad: {geo.get('city', 'N/A')}")
                print(f"      Estado: {geo.get('state', 'N/A')}")
                print(f"      País: {geo.get('country', 'N/A')}")
            
            # Redes sociales
            print(f"\n   🌐 Redes Sociales:")
            if data.get('linkedin', {}).get('handle'):
                print(f"      LinkedIn: linkedin.com/in/{data.get('linkedin', {}).get('handle')}")
            if data.get('twitter', {}).get('handle'):
                print(f"      Twitter: @{data.get('twitter', {}).get('handle')}")
            if data.get('github', {}).get('handle'):
                print(f"      GitHub: github.com/{data.get('github', {}).get('handle')}")
            
            # Avatar
            if data.get('avatar'):
                print(f"\n   🖼️  Avatar: {data.get('avatar')}")
            
            return data
        else:
            print(f"⚠️  No se encontró información para {email}")
            return None
            
    except requests.exceptions.HTTPError as e:
        print(f"❌ ERROR HTTP: {e}")
        if response.status_code == 401:
            print("   → API key inválida o no configurada")
        elif response.status_code == 402:
            print("   → Créditos insuficientes - plan agotado")
        elif response.status_code == 404:
            print("   → Persona no encontrada en la base de datos")
        elif response.status_code == 422:
            print("   → Email inválido")
        return None
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return None

def test_company_enrichment(domain):
    """
    2. Company Enrichment - Enriquece datos de empresa por dominio
    Obtén información completa sobre una empresa
    """
    print_section(f"🏢 COMPANY ENRICHMENT: {domain}")
    
    if not CLEARBIT_API_KEY:
        print("❌ ERROR: CLEARBIT_API_KEY no configurada")
        return None
    
    try:
        url = "https://company.clearbit.com/v2/companies/find"
        params = {'domain': domain}
        headers = {'Authorization': f'Bearer {CLEARBIT_API_KEY}'}
        
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        if data:
            print(f"✅ Empresa encontrada:")
            print(f"   Nombre: {data.get('name', 'N/A')}")
            print(f"   Dominio: {data.get('domain', 'N/A')}")
            print(f"   Descripción: {data.get('description', 'N/A')[:100]}...")
            
            # Información básica
            print(f"\n   📊 Datos Básicos:")
            print(f"      Fundada: {data.get('foundedYear', 'N/A')}")
            print(f"      Empleados: {data.get('metrics', {}).get('employees', 'N/A')}")
            print(f"      Rango empleados: {data.get('metrics', {}).get('employeesRange', 'N/A')}")
            print(f"      Ingresos estimados: ${data.get('metrics', {}).get('estimatedAnnualRevenue', 'N/A'):,}" if data.get('metrics', {}).get('estimatedAnnualRevenue') else "      Ingresos estimados: N/A")
            
            # Industria
            print(f"\n   🏭 Industria:")
            print(f"      Categoría: {data.get('category', {}).get('industry', 'N/A')}")
            print(f"      Sector: {data.get('category', {}).get('sector', 'N/A')}")
            tags = data.get('tags', [])
            if tags:
                print(f"      Tags: {', '.join(tags[:5])}")
            
            # Ubicación
            print(f"\n   📍 Ubicación:")
            print(f"      Ciudad: {data.get('geo', {}).get('city', 'N/A')}")
            print(f"      Estado: {data.get('geo', {}).get('state', 'N/A')}")
            print(f"      País: {data.get('geo', {}).get('country', 'N/A')}")
            
            # Tecnologías
            tech = data.get('tech', [])
            if tech:
                print(f"\n   💻 Tecnologías usadas:")
                for t in tech[:10]:
                    print(f"      • {t}")
            
            # Redes sociales
            print(f"\n   🌐 Presencia Online:")
            if data.get('site', {}).get('url'):
                print(f"      Website: {data.get('site', {}).get('url')}")
            if data.get('linkedin', {}).get('handle'):
                print(f"      LinkedIn: linkedin.com/company/{data.get('linkedin', {}).get('handle')}")
            if data.get('twitter', {}).get('handle'):
                print(f"      Twitter: @{data.get('twitter', {}).get('handle')}")
            if data.get('facebook', {}).get('handle'):
                print(f"      Facebook: facebook.com/{data.get('facebook', {}).get('handle')}")
            
            # Logo
            if data.get('logo'):
                print(f"\n   🖼️  Logo: {data.get('logo')}")
            
            return data
        else:
            print(f"⚠️  No se encontró información para {domain}")
            return None
            
    except requests.exceptions.HTTPError as e:
        print(f"❌ ERROR HTTP: {e}")
        if response.status_code == 401:
            print("   → API key inválida")
        elif response.status_code == 402:
            print("   → Créditos insuficientes")
        elif response.status_code == 404:
            print("   → Empresa no encontrada")
        return None
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return None

def test_combined_enrichment(email):
    """
    3. Combined Enrichment - Enriquece persona + empresa en una sola llamada
    Optimiza requests combinando ambas APIs
    """
    print_section(f"🔄 COMBINED ENRICHMENT: {email}")
    
    if not CLEARBIT_API_KEY:
        print("❌ ERROR: CLEARBIT_API_KEY no configurada")
        return None
    
    try:
        url = "https://person.clearbit.com/v2/combined/find"
        params = {'email': email}
        headers = {'Authorization': f'Bearer {CLEARBIT_API_KEY}'}
        
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        if data:
            person = data.get('person', {})
            company = data.get('company', {})
            
            print(f"✅ Datos combinados encontrados:")
            
            # Persona
            if person:
                print(f"\n   👤 Persona:")
                print(f"      Nombre: {person.get('name', {}).get('fullName', 'N/A')}")
                print(f"      Email: {person.get('email', 'N/A')}")
                print(f"      Cargo: {person.get('employment', {}).get('title', 'N/A')}")
            
            # Empresa
            if company:
                print(f"\n   🏢 Empresa:")
                print(f"      Nombre: {company.get('name', 'N/A')}")
                print(f"      Dominio: {company.get('domain', 'N/A')}")
                print(f"      Empleados: {company.get('metrics', {}).get('employees', 'N/A')}")
                print(f"      Industria: {company.get('category', {}).get('industry', 'N/A')}")
            
            return data
        else:
            print(f"⚠️  No se encontró información para {email}")
            return None
            
    except requests.exceptions.HTTPError as e:
        print(f"❌ ERROR HTTP: {e}")
        if response.status_code == 404:
            print("   → No se encontró información combinada")
        return None
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return None

def test_logo_api(domain):
    """
    4. Logo API - Obtiene el logo de una empresa
    API gratuita sin autenticación
    """
    print_section(f"🎨 LOGO API: {domain}")
    
    try:
        # Logo API no requiere autenticación
        url = f"https://logo.clearbit.com/{domain}"
        
        print(f"✅ URL del logo: {url}")
        print(f"\n   💡 Puedes usar esta URL directamente en tu app:")
        print(f"      <img src=\"{url}\" alt=\"{domain} logo\" />")
        
        # Verificar si el logo existe
        response = requests.head(url)
        if response.status_code == 200:
            print(f"\n   ✓ Logo disponible")
            print(f"   Tamaño: {response.headers.get('Content-Length', 'N/A')} bytes")
        else:
            print(f"\n   ⚠️ Logo no encontrado (código: {response.status_code})")
        
        return url
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return None

def test_name_to_domain(company_name):
    """
    5. Name to Domain - Encuentra el dominio de una empresa por nombre
    API gratuita sin autenticación
    """
    print_section(f"🔍 NAME TO DOMAIN: {company_name}")
    
    try:
        url = "https://autocomplete.clearbit.com/v1/companies/suggest"
        params = {'query': company_name}
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if data:
            print(f"✅ Encontradas {len(data)} empresas:")
            for i, company in enumerate(data[:5], 1):
                print(f"\n   {i}. {company.get('name')}")
                print(f"      Dominio: {company.get('domain')}")
                print(f"      Logo: {company.get('logo')}")
            
            return data
        else:
            print(f"⚠️  No se encontraron empresas con ese nombre")
            return None
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return None

def check_api_usage():
    """
    6. Risk API - Verificar información (ejemplo con email)
    """
    print_section("📈 INFORMACIÓN DE API")
    
    if not CLEARBIT_API_KEY:
        print("❌ ERROR: CLEARBIT_API_KEY no configurada")
        return None
    
    print("ℹ️  Clearbit no tiene endpoint público de uso")
    print("   Revisa tu dashboard para ver créditos: https://dashboard.clearbit.com/")
    print("\n   💰 Precios de Clearbit:")
    print("      • Enrichment API: ~$0.35 por lookup exitoso")
    print("      • Prospector API: ~$0.50 por búsqueda")
    print("      • Discovery API: ~$2.50 por exportación")
    print("      • Logo API: GRATIS")
    print("      • Name to Domain: GRATIS")

def main():
    """Función principal para ejecutar todas las pruebas"""
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║          CLEARBIT API TEST SUITE                           ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    # Verificar configuración
    if not CLEARBIT_API_KEY:
        print("\n❌ ERROR: No se encontró CLEARBIT_API_KEY en .env")
        print("\n📋 PASOS PARA CONFIGURAR:")
        print("   1. Ve a https://clearbit.com/")
        print("   2. Regístrate para un trial")
        print("   3. Ve a API Settings: https://dashboard.clearbit.com/api")
        print("   4. Copia tu API key")
        print("   5. Agrégala a tu archivo .env:")
        print("      CLEARBIT_API_KEY=sk_tu_api_key_aqui")
        print("\n   💡 TIP: Clearbit ofrece trial gratuito con créditos limitados")
        print("      Luego es $99/mes (500 enrichments) o pay-as-you-go")
    
    # Información
    check_api_usage()
    
    print("\n\n" + "="*60)
    print("  PROBANDO APIs GRATUITAS (sin autenticación)")
    print("="*60)
    
    # PRUEBA 1: Logo API (GRATIS)
    print("\n\n🧪 PRUEBA 1: Logo API")
    test_logo_api('stripe.com')
    
    # PRUEBA 2: Name to Domain (GRATIS)
    print("\n\n🧪 PRUEBA 2: Name to Domain")
    test_name_to_domain('Stripe')
    
    if CLEARBIT_API_KEY:
        print("\n\n" + "="*60)
        print("  PROBANDO APIs DE PAGO (requiere API key)")
        print("="*60)
        
        # PRUEBA 3: Company Enrichment
        print("\n\n🧪 PRUEBA 3: Company Enrichment")
        test_company_enrichment('stripe.com')
        
        # PRUEBA 4: Person Enrichment
        print("\n\n🧪 PRUEBA 4: Person Enrichment")
        test_person_enrichment('patrick@stripe.com')
        
        # PRUEBA 5: Combined Enrichment
        print("\n\n🧪 PRUEBA 5: Combined Enrichment")
        test_combined_enrichment('patrick@stripe.com')
    
    # Resumen final
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║                    PRUEBAS COMPLETADAS                     ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print("\n📚 DOCUMENTACIÓN:")
    print("   → https://clearbit.com/docs")
    print("\n💡 TIP: Las APIs de Logo y Name-to-Domain son GRATUITAS")
    print("   y funcionan sin API key!")
    print("\n🎯 PRÓXIMOS PASOS:")
    print("   1. Obtén API key para probar Enrichment APIs")
    print("   2. Combina con Hunter.io para mejor cobertura")
    print("   3. Usa Logo API para mejorar UI de tu app")

if __name__ == "__main__":
    main()
