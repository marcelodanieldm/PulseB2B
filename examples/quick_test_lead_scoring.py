"""
Quick Test - Lead Scoring System
Test con 10 empresas usando datos mock (sin web scraping)
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.lead_scoring import (
    load_companies_data,
    scrape_employee_data,
    calculate_hpi_scores,
    generate_report
)

def main():
    print("🚀 PulseB2B Lead Scoring - Quick Test")
    print("="*60)
    print("\nUsando datos MOCK (sin web scraping) para testing rápido\n")
    
    # Paths
    input_csv = Path(__file__).parent.parent / 'data' / 'input' / 'companies_latam.csv'
    output_dir = Path(__file__).parent.parent / 'data' / 'output' / 'lead_scoring'
    
    # Load first 10 companies
    print("📊 Cargando empresas...")
    companies_df = load_companies_data(str(input_csv))
    companies_df = companies_df.head(10)
    print(f"✓ {len(companies_df)} empresas cargadas\n")
    
    # Generate mock employee data
    print("👥 Generando datos mock de empleados...")
    enriched_df = scrape_employee_data(companies_df, use_scraper=False)
    print(f"✓ Datos generados\n")
    
    # Calculate HPI
    print("🎯 Calculando Hiring Potential Index...")
    results_df = calculate_hpi_scores(enriched_df)
    print(f"✓ HPI calculado para {len(results_df)} empresas\n")
    
    # Generate reports
    print("📄 Generando reportes...")
    generate_report(results_df, output_dir)
    
    print("\n✅ Test completado exitosamente!")
    print(f"\n📁 Reportes guardados en: {output_dir}")
    print("\nPara ver resultados:")
    print(f"  - Reporte principal: {output_dir}/lead_scoring_report_*.csv")
    print(f"  - Estadísticas: {output_dir}/summary_stats_*.json")

if __name__ == "__main__":
    main()
