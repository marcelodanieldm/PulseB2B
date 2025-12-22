"""
Oracle Output Validator
=======================
Validates CSV output from Oracle Funding Detector before uploading to Supabase.
Checks for data quality, completeness, and correctness.
"""

import pandas as pd
import os
import sys
import glob
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class OracleValidator:
    """Validates Oracle output data quality."""
    
    REQUIRED_COLUMNS = [
        'Company Name',
        'Funding Date',
        'Days Since Filing',
        'Estimated Amount (M)',
        'Tech Stack',
        'Tech Count',
        'Hiring Signals',
        'Hiring Probability (%)',
        'Website',
        'CIK',
        'Filing URL'
    ]
    
    MIN_EXPECTED_ROWS = 1
    MAX_EXPECTED_ROWS = 100
    
    def __init__(self, output_dir: str = 'data/output/oracle'):
        self.output_dir = output_dir
        self.validation_errors = []
        self.validation_warnings = []
    
    def find_latest_csv(self) -> str:
        """Find the most recent Oracle predictions CSV."""
        pattern = os.path.join(self.output_dir, 'oracle_predictions_*.csv')
        files = glob.glob(pattern)
        
        if not files:
            raise FileNotFoundError(f"No Oracle CSV files found in {self.output_dir}")
        
        # Sort by modification time (most recent first)
        latest_file = max(files, key=os.path.getmtime)
        logger.info(f"📄 Found latest CSV: {latest_file}")
        return latest_file
    
    def validate_structure(self, df: pd.DataFrame) -> bool:
        """Validate CSV structure and columns."""
        logger.info("🔍 Validating CSV structure...")
        
        # Check columns exist
        missing_cols = set(self.REQUIRED_COLUMNS) - set(df.columns)
        if missing_cols:
            self.validation_errors.append(f"Missing columns: {missing_cols}")
            return False
        
        # Check row count
        row_count = len(df)
        if row_count < self.MIN_EXPECTED_ROWS:
            self.validation_errors.append(f"Too few rows: {row_count} (min: {self.MIN_EXPECTED_ROWS})")
            return False
        
        if row_count > self.MAX_EXPECTED_ROWS:
            self.validation_warnings.append(f"Unusually high row count: {row_count}")
        
        logger.info(f"✅ Structure valid: {row_count} rows, {len(df.columns)} columns")
        return True
    
    def validate_data_quality(self, df: pd.DataFrame) -> bool:
        """Validate data quality and correctness."""
        logger.info("🔍 Validating data quality...")
        
        is_valid = True
        
        # 1. Check for null company names
        null_companies = df['Company Name'].isnull().sum()
        if null_companies > 0:
            self.validation_errors.append(f"Found {null_companies} null company names")
            is_valid = False
        
        # 2. Check hiring probability range (0-100)
        invalid_probs = df[
            (df['Hiring Probability (%)'] < 0) | 
            (df['Hiring Probability (%)'] > 100)
        ]
        if len(invalid_probs) > 0:
            self.validation_errors.append(f"Found {len(invalid_probs)} invalid probability scores")
            is_valid = False
        
        # 3. Check tech count is positive
        invalid_tech = df[df['Tech Count'] < 0]
        if len(invalid_tech) > 0:
            self.validation_errors.append(f"Found {len(invalid_tech)} negative tech counts")
            is_valid = False
        
        # 4. Check hiring signals is positive
        invalid_signals = df[df['Hiring Signals'] < 0]
        if len(invalid_signals) > 0:
            self.validation_errors.append(f"Found {len(invalid_signals)} negative hiring signals")
            is_valid = False
        
        # 5. Check funding date format
        try:
            pd.to_datetime(df['Funding Date'], format='%Y-%m-%d')
        except Exception as e:
            self.validation_errors.append(f"Invalid funding date format: {str(e)}")
            is_valid = False
        
        # 6. Validate URLs (basic check)
        invalid_urls = df[
            ~df['Website'].str.startswith('http', na=False) & 
            (df['Website'] != '')
        ]
        if len(invalid_urls) > 0:
            self.validation_warnings.append(f"Found {len(invalid_urls)} invalid website URLs")
        
        # 7. Check for duplicate companies
        duplicates = df[df.duplicated(subset=['Company Name', 'Funding Date'], keep=False)]
        if len(duplicates) > 0:
            self.validation_warnings.append(f"Found {len(duplicates)} duplicate entries")
        
        if is_valid:
            logger.info("✅ Data quality checks passed")
        else:
            logger.error("❌ Data quality checks failed")
        
        return is_valid
    
    def validate_business_logic(self, df: pd.DataFrame) -> bool:
        """Validate business logic and scoring consistency."""
        logger.info("🔍 Validating business logic...")
        
        warnings_found = False
        
        # 1. High probability with low signals (suspicious)
        suspicious = df[
            (df['Hiring Probability (%)'] >= 80) & 
            (df['Hiring Signals'] < 3)
        ]
        if len(suspicious) > 0:
            self.validation_warnings.append(
                f"Found {len(suspicious)} companies with high probability but low signals"
            )
            warnings_found = True
        
        # 2. Large funding with low probability (unusual)
        unusual = df[
            df['Estimated Amount (M)'].str.contains(r'\$\d{3,}', regex=True, na=False) & 
            (df['Hiring Probability (%)'] < 50)
        ]
        if len(unusual) > 0:
            self.validation_warnings.append(
                f"Found {len(unusual)} companies with large funding but low probability"
            )
        
        # 3. Check average scores are reasonable
        avg_prob = df['Hiring Probability (%)'].mean()
        if avg_prob < 20:
            self.validation_warnings.append(f"Unusually low average probability: {avg_prob:.1f}%")
            warnings_found = True
        elif avg_prob > 90:
            self.validation_warnings.append(f"Unusually high average probability: {avg_prob:.1f}%")
            warnings_found = True
        
        logger.info(f"📊 Average hiring probability: {avg_prob:.1f}%")
        
        if not warnings_found:
            logger.info("✅ Business logic validation passed")
        
        return True  # Business logic warnings don't fail validation
    
    def generate_validation_report(self, df: pd.DataFrame) -> dict:
        """Generate validation summary report."""
        high_prob = len(df[df['Hiring Probability (%)'] >= 70])
        medium_prob = len(df[(df['Hiring Probability (%)'] >= 40) & (df['Hiring Probability (%)'] < 70)])
        low_prob = len(df[df['Hiring Probability (%)'] < 40])
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_companies': len(df),
            'high_probability_count': high_prob,
            'medium_probability_count': medium_prob,
            'low_probability_count': low_prob,
            'avg_hiring_probability': float(df['Hiring Probability (%)'].mean()),
            'avg_tech_count': float(df['Tech Count'].mean()),
            'validation_errors': self.validation_errors,
            'validation_warnings': self.validation_warnings,
            'status': 'PASSED' if not self.validation_errors else 'FAILED'
        }
        
        return report
    
    def save_report(self, report: dict):
        """Save validation report to JSON."""
        report_path = os.path.join(self.output_dir, 'validation_report.json')
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        logger.info(f"💾 Validation report saved to: {report_path}")
    
    def validate(self) -> bool:
        """
        Run complete validation pipeline.
        
        Returns:
            True if validation passed, False otherwise
        """
        logger.info("\n" + "="*60)
        logger.info("🔮 ORACLE OUTPUT VALIDATION")
        logger.info("="*60 + "\n")
        
        try:
            # Find latest CSV
            csv_path = self.find_latest_csv()
            
            # Load data
            df = pd.read_csv(csv_path)
            logger.info(f"📊 Loaded {len(df)} rows from CSV")
            
            # Run validations
            structure_valid = self.validate_structure(df)
            if not structure_valid:
                logger.error("❌ Structure validation failed - stopping here")
                report = self.generate_validation_report(df)
                self.save_report(report)
                return False
            
            quality_valid = self.validate_data_quality(df)
            self.validate_business_logic(df)  # Always run, warnings only
            
            # Generate report
            report = self.generate_validation_report(df)
            self.save_report(report)
            
            # Print summary
            logger.info("\n" + "="*60)
            logger.info("📊 VALIDATION SUMMARY")
            logger.info("="*60)
            logger.info(f"Status: {report['status']}")
            logger.info(f"Total Companies: {report['total_companies']}")
            logger.info(f"High Probability (70%+): {report['high_probability_count']}")
            logger.info(f"Errors: {len(report['validation_errors'])}")
            logger.info(f"Warnings: {len(report['validation_warnings'])}")
            
            if report['validation_errors']:
                logger.error("\n❌ Validation Errors:")
                for error in report['validation_errors']:
                    logger.error(f"  • {error}")
            
            if report['validation_warnings']:
                logger.warning("\n⚠️  Validation Warnings:")
                for warning in report['validation_warnings']:
                    logger.warning(f"  • {warning}")
            
            logger.info("="*60 + "\n")
            
            return quality_valid
            
        except Exception as e:
            logger.error(f"❌ Validation failed with exception: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main validation function."""
    validator = OracleValidator()
    
    success = validator.validate()
    
    if success:
        logger.info("✅ Validation passed - data ready for upload")
        sys.exit(0)
    else:
        logger.error("❌ Validation failed - data not ready for upload")
        sys.exit(1)


if __name__ == '__main__':
    main()
