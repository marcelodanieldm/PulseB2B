"""
Pulse Intelligence Integration
-------------------------------
Integrates the Pulse Intelligence Module with existing Oracle Funding Detector.
Replaces basic scoring with advanced NLP-based desperation analysis.

Usage:
    python integrate_pulse_intelligence.py --input data/oracle_output.csv --output data/pulse_enhanced.csv
"""

import sys
import argparse
import pandas as pd
from datetime import datetime
from pathlib import Path
import json

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from pulse_intelligence import PulseIntelligenceEngine


class PulseIntegrator:
    """
    Integrates Pulse Intelligence with Oracle detector output.
    """
    
    def __init__(self, verbose: bool = True):
        self.engine = PulseIntelligenceEngine()
        self.verbose = verbose
        
    def enhance_oracle_data(self, oracle_df: pd.DataFrame) -> pd.DataFrame:
        """
        Enhance Oracle CSV output with Pulse Intelligence scores.
        
        Args:
            oracle_df: DataFrame from oracle_funding_detector.py
            
        Returns:
            Enhanced DataFrame with Pulse scores and signals
        """
        if self.verbose:
            print("🧠 Enhancing Oracle data with Pulse Intelligence...\n")
        
        enhanced_rows = []
        
        for idx, row in oracle_df.iterrows():
            if self.verbose and idx % 10 == 0:
                print(f"   Processing {idx + 1}/{len(oracle_df)}...")
            
            # Combine all text content
            text_content = f"""
            {row.get('company_name', '')}
            {row.get('industry', '')}
            {row.get('description', '')}
            {row.get('tech_stack', '')}
            {row.get('website_content', '')}
            """
            
            # Check if SEC funding exists
            sec_funding = row.get('funding_amount', 0) > 0
            
            # Run Pulse Intelligence
            try:
                pulse_result = self.engine.calculate_pulse_score(
                    sec_funding_detected=sec_funding,
                    text_content=text_content,
                    job_posts=None  # Could integrate job scraping here
                )
                
                # Add Pulse fields to row
                enhanced_row = row.to_dict()
                enhanced_row['pulse_score'] = pulse_result['pulse_score']
                enhanced_row['desperation_level'] = pulse_result['desperation_level']
                enhanced_row['urgency'] = pulse_result['urgency']
                enhanced_row['expansion_density'] = pulse_result['signals']['growth']['expansion_density']
                enhanced_row['tech_diversity_score'] = pulse_result['signals']['technology']['diversity_score']
                enhanced_row['has_red_flags'] = pulse_result['signals']['red_flags']['is_risky']
                enhanced_row['recommendation'] = pulse_result['recommendation']
                enhanced_row['pulse_timestamp'] = pulse_result['timestamp']
                
                # Store full analysis as JSON string
                enhanced_row['pulse_full_analysis'] = json.dumps(pulse_result['signals'])
                
                enhanced_rows.append(enhanced_row)
                
            except Exception as e:
                if self.verbose:
                    print(f"⚠️  Failed to analyze {row.get('company_name', 'Unknown')}: {e}")
                # Keep original row if Pulse fails
                enhanced_rows.append(row.to_dict())
        
        enhanced_df = pd.DataFrame(enhanced_rows)
        
        if self.verbose:
            print(f"\n✅ Enhanced {len(enhanced_df)} companies with Pulse Intelligence")
            print(f"\nDesperation Level Distribution:")
            if 'desperation_level' in enhanced_df.columns:
                print(enhanced_df['desperation_level'].value_counts())
        
        return enhanced_df
    
    def generate_priority_report(self, enhanced_df: pd.DataFrame, output_dir: Path):
        """
        Generate actionable priority reports for sales team.
        
        Args:
            enhanced_df: Enhanced DataFrame with Pulse scores
            output_dir: Directory to save reports
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Critical opportunities (80+ score, no red flags)
        critical = enhanced_df[
            (enhanced_df['pulse_score'] >= 80) & 
            (enhanced_df['has_red_flags'] == False)
        ].sort_values('pulse_score', ascending=False)
        
        if len(critical) > 0:
            critical_path = output_dir / f'critical_opportunities_{timestamp}.csv'
            critical.to_csv(critical_path, index=False)
            print(f"\n🔥 {len(critical)} CRITICAL opportunities → {critical_path}")
        
        # High priority (60-79 score, no red flags)
        high = enhanced_df[
            (enhanced_df['pulse_score'] >= 60) & 
            (enhanced_df['pulse_score'] < 80) &
            (enhanced_df['has_red_flags'] == False)
        ].sort_values('pulse_score', ascending=False)
        
        if len(high) > 0:
            high_path = output_dir / f'high_priority_{timestamp}.csv'
            high.to_csv(high_path, index=False)
            print(f"⚡ {len(high)} HIGH priority opportunities → {high_path}")
        
        # Red flags to avoid
        red_flags = enhanced_df[enhanced_df['has_red_flags'] == True]
        if len(red_flags) > 0:
            flags_path = output_dir / f'red_flags_{timestamp}.csv'
            red_flags.to_csv(flags_path, index=False)
            print(f"⚠️  {len(red_flags)} companies with RED FLAGS → {flags_path}")
        
        # Summary statistics
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_companies': len(enhanced_df),
            'critical_opportunities': len(critical),
            'high_priority': len(high),
            'moderate': len(enhanced_df[(enhanced_df['pulse_score'] >= 40) & (enhanced_df['pulse_score'] < 60)]),
            'low_priority': len(enhanced_df[enhanced_df['pulse_score'] < 40]),
            'red_flags': len(red_flags),
            'average_pulse_score': float(enhanced_df['pulse_score'].mean()),
            'median_pulse_score': float(enhanced_df['pulse_score'].median()),
            'desperation_breakdown': enhanced_df['desperation_level'].value_counts().to_dict()
        }
        
        summary_path = output_dir / f'pulse_summary_{timestamp}.json'
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n📊 Summary statistics → {summary_path}")
        print(f"\n   Average Pulse Score: {summary['average_pulse_score']:.1f}/100")
        print(f"   Actionable Leads: {summary['critical_opportunities'] + summary['high_priority']}")
        print(f"   Red Flags to Avoid: {summary['red_flags']}")


def main():
    parser = argparse.ArgumentParser(
        description='Integrate Pulse Intelligence with Oracle detector output'
    )
    parser.add_argument(
        '--input',
        type=str,
        required=True,
        help='Path to Oracle CSV output'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Path for enhanced CSV output (default: data/output/pulse_enhanced.csv)'
    )
    parser.add_argument(
        '--reports-dir',
        type=str,
        default='data/output/pulse_reports',
        help='Directory for priority reports'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress verbose output'
    )
    
    args = parser.parse_args()
    
    # Load Oracle data
    print(f"📂 Loading Oracle data from {args.input}...")
    try:
        oracle_df = pd.read_csv(args.input)
        print(f"   Loaded {len(oracle_df)} companies\n")
    except Exception as e:
        print(f"❌ Failed to load input file: {e}")
        sys.exit(1)
    
    # Initialize integrator
    integrator = PulseIntegrator(verbose=not args.quiet)
    
    # Enhance with Pulse Intelligence
    enhanced_df = integrator.enhance_oracle_data(oracle_df)
    
    # Save enhanced data
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = Path('data/output/pulse_enhanced.csv')
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    enhanced_df.to_csv(output_path, index=False)
    print(f"\n💾 Enhanced data saved → {output_path}")
    
    # Generate priority reports
    reports_dir = Path(args.reports_dir)
    integrator.generate_priority_report(enhanced_df, reports_dir)
    
    print("\n✅ Pulse Intelligence integration complete!")
    print("\n📋 Next Steps:")
    print("   1. Review critical_opportunities_*.csv for immediate outreach")
    print("   2. Schedule high_priority_*.csv for 48-72h followup")
    print("   3. Avoid companies in red_flags_*.csv")
    print("   4. Upload enhanced data to Supabase for dashboard")


if __name__ == '__main__':
    main()
