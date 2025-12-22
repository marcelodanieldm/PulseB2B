"""
Supabase Uploader
=================
Uploads validated Oracle predictions to Supabase database.
"""

import pandas as pd
import os
import sys
import glob
import json
from datetime import datetime
from supabase import create_client, Client
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SupabaseUploader:
    """Uploads Oracle predictions to Supabase."""
    
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        logger.info("✅ Supabase client initialized")
    
    def find_latest_csv(self) -> str:
        """Find the most recent validated CSV."""
        output_dir = 'data/output/oracle'
        pattern = os.path.join(output_dir, 'oracle_predictions_*.csv')
        files = glob.glob(pattern)
        
        if not files:
            raise FileNotFoundError(f"No CSV files found in {output_dir}")
        
        latest_file = max(files, key=os.path.getmtime)
        logger.info(f"📄 Found latest CSV: {latest_file}")
        return latest_file
    
    def prepare_records(self, df: pd.DataFrame) -> list:
        """Convert DataFrame to Supabase-compatible records."""
        logger.info("🔄 Preparing records for Supabase...")
        
        records = []
        for _, row in df.iterrows():
            # Parse funding amount
            funding_str = row['Estimated Amount (M)']
            if funding_str != 'Not disclosed' and funding_str:
                try:
                    funding_amount = float(funding_str.replace('$', '').replace('M', '').strip())
                except:
                    funding_amount = None
            else:
                funding_amount = None
            
            # Parse tech stack
            tech_stack = row['Tech Stack']
            if tech_stack and tech_stack != 'Not detected':
                tech_array = [t.strip() for t in tech_stack.split(',')]
            else:
                tech_array = []
            
            record = {
                'company_name': row['Company Name'],
                'funding_date': row['Funding Date'],
                'days_since_filing': int(row['Days Since Filing']),
                'estimated_amount_millions': funding_amount,
                'funding_source': row.get('Funding Source', ''),
                'tech_stack': tech_array,
                'tech_count': int(row['Tech Count']),
                'hiring_signals': int(row['Hiring Signals']),
                'hiring_probability': float(row['Hiring Probability (%)']),
                'website': row['Website'],
                'description': row.get('Description', '')[:500],  # Limit to 500 chars
                'cik': row['CIK'],
                'filing_url': row['Filing URL'],
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            records.append(record)
        
        logger.info(f"✅ Prepared {len(records)} records")
        return records
    
    def upload_batch(self, records: list, batch_size: int = 50) -> dict:
        """Upload records in batches to avoid timeouts."""
        logger.info(f"📤 Uploading {len(records)} records to Supabase...")
        
        uploaded = 0
        failed = 0
        errors = []
        
        # Process in batches
        for i in range(0, len(records), batch_size):
            batch = records[i:i+batch_size]
            
            try:
                # Upsert to avoid duplicates (on company_name + funding_date)
                response = self.supabase.table('oracle_predictions').upsert(
                    batch,
                    on_conflict='company_name,funding_date'
                ).execute()
                
                uploaded += len(batch)
                logger.info(f"  ✓ Uploaded batch {i//batch_size + 1}: {len(batch)} records")
                
            except Exception as e:
                failed += len(batch)
                error_msg = f"Batch {i//batch_size + 1} failed: {str(e)}"
                errors.append(error_msg)
                logger.error(f"  ✗ {error_msg}")
        
        summary = {
            'total_records': len(records),
            'uploaded': uploaded,
            'failed': failed,
            'errors': errors,
            'timestamp': datetime.now().isoformat()
        }
        
        return summary
    
    def save_upload_summary(self, summary: dict):
        """Save upload summary to JSON."""
        output_dir = 'data/output/oracle'
        os.makedirs(output_dir, exist_ok=True)
        
        summary_path = os.path.join(output_dir, 'upload_summary.json')
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"💾 Upload summary saved to: {summary_path}")
    
    def upload(self) -> bool:
        """
        Run complete upload pipeline.
        
        Returns:
            True if upload succeeded, False otherwise
        """
        logger.info("\n" + "="*60)
        logger.info("📤 SUPABASE UPLOAD")
        logger.info("="*60 + "\n")
        
        try:
            # Find and load latest CSV
            csv_path = self.find_latest_csv()
            df = pd.read_csv(csv_path)
            logger.info(f"📊 Loaded {len(df)} rows from CSV")
            
            # Prepare records
            records = self.prepare_records(df)
            
            # Upload to Supabase
            summary = self.upload_batch(records)
            
            # Save summary
            self.save_upload_summary(summary)
            
            # Print results
            logger.info("\n" + "="*60)
            logger.info("📊 UPLOAD SUMMARY")
            logger.info("="*60)
            logger.info(f"Total Records: {summary['total_records']}")
            logger.info(f"Uploaded: {summary['uploaded']}")
            logger.info(f"Failed: {summary['failed']}")
            
            if summary['errors']:
                logger.error("\n❌ Upload Errors:")
                for error in summary['errors']:
                    logger.error(f"  • {error}")
            
            logger.info("="*60 + "\n")
            
            # Success if at least 80% uploaded
            success_rate = summary['uploaded'] / summary['total_records']
            if success_rate >= 0.8:
                logger.info(f"✅ Upload succeeded ({success_rate*100:.1f}% success rate)")
                return True
            else:
                logger.error(f"❌ Upload failed ({success_rate*100:.1f}% success rate)")
                return False
                
        except Exception as e:
            logger.error(f"❌ Upload failed with exception: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main upload function."""
    try:
        uploader = SupabaseUploader()
        success = uploader.upload()
        
        if success:
            logger.info("✅ Upload completed successfully")
            sys.exit(0)
        else:
            logger.error("❌ Upload failed")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
