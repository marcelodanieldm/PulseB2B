"""
Telegram Notifier
=================
Sends critical alerts to Telegram when companies exceed 85% hiring probability.
"""

import pandas as pd
import os
import sys
import glob
import json
import requests
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Sends Telegram notifications for critical leads."""
    
    CRITICAL_THRESHOLD = 85.0  # 85% hiring probability
    
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not self.bot_token or not self.chat_id:
            raise ValueError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set")
        
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
        logger.info("✅ Telegram client initialized")
    
    def test_connection(self) -> bool:
        """Test Telegram bot connection."""
        try:
            response = requests.get(f"{self.api_url}/getMe", timeout=10)
            if response.status_code == 200:
                bot_info = response.json()
                logger.info(f"✅ Bot connected: @{bot_info['result']['username']}")
                return True
            else:
                logger.error(f"❌ Bot connection failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Bot connection error: {str(e)}")
            return False
    
    def send_message(self, text: str, parse_mode: str = 'HTML') -> bool:
        """Send a message to Telegram."""
        try:
            payload = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': parse_mode,
                'disable_web_page_preview': False
            }
            
            response = requests.post(
                f"{self.api_url}/sendMessage",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                return True
            else:
                logger.error(f"❌ Message send failed: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Message send error: {str(e)}")
            return False
    
    def format_company_alert(self, row: pd.Series) -> str:
        """Format a company alert message."""
        # Parse funding amount
        funding = row['Estimated Amount (M)']
        if funding != 'Not disclosed':
            funding_display = f"💰 <b>Funding:</b> {funding}"
        else:
            funding_display = "💰 <b>Funding:</b> Not disclosed"
        
        # Format tech stack
        tech_stack = row['Tech Stack']
        if tech_stack and tech_stack != 'Not detected':
            techs = tech_stack.split(', ')[:5]  # First 5
            tech_display = ', '.join(techs)
            if len(tech_stack.split(', ')) > 5:
                tech_display += '...'
        else:
            tech_display = 'Not detected'
        
        # Build message
        message = f"""
🚨 <b>CRITICAL LEAD ALERT</b> 🚨

<b>{row['Company Name']}</b>

🎯 <b>Hiring Probability:</b> {row['Hiring Probability (%)']}% (CRITICAL)
📅 <b>Filed:</b> {row['Funding Date']} ({row['Days Since Filing']} days ago)
{funding_display}

🔧 <b>Tech Stack:</b> {tech_display}
📊 <b>Hiring Signals:</b> {row['Hiring Signals']} detected

🌐 <b>Website:</b> {row['Website']}

<b>⚡ ACTION REQUIRED:</b>
• Contact CTO/Head of Engineering TODAY
• Reference recent funding round
• Pitch offshore team scaling

<a href="{row['Filing URL']}">📄 View SEC Filing</a>
"""
        return message.strip()
    
    def format_summary_message(self, df: pd.DataFrame, critical_count: int) -> str:
        """Format summary message."""
        high_prob = len(df[df['Hiring Probability (%)'] >= 70])
        avg_prob = df['Hiring Probability (%)'].mean()
        
        message = f"""
🔮 <b>Oracle Ghost - Daily Summary</b>

📊 <b>Run Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}

<b>Results:</b>
• Total Companies: {len(df)}
• High Probability (70%+): {high_prob}
• <b>Critical Alerts (85%+): {critical_count}</b>
• Average Score: {avg_prob:.1f}%

🎯 <b>Status:</b> {'🔥 HOT LEADS DETECTED!' if critical_count > 0 else '✅ Scan complete'}

💡 Check your dashboard for full details.
"""
        return message.strip()
    
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
    
    def notify(self) -> bool:
        """
        Send notifications for critical leads.
        
        Returns:
            True if notifications sent successfully, False otherwise
        """
        logger.info("\n" + "="*60)
        logger.info("🔔 TELEGRAM NOTIFICATIONS")
        logger.info("="*60 + "\n")
        
        try:
            # Test connection
            if not self.test_connection():
                logger.error("❌ Telegram connection failed - skipping notifications")
                return False
            
            # Load latest data
            csv_path = self.find_latest_csv()
            df = pd.read_csv(csv_path)
            logger.info(f"📊 Loaded {len(df)} companies")
            
            # Find critical leads
            critical_df = df[df['Hiring Probability (%)'] >= self.CRITICAL_THRESHOLD]
            critical_df = critical_df.sort_values('Hiring Probability (%)', ascending=False)
            
            logger.info(f"🚨 Found {len(critical_df)} CRITICAL leads (≥{self.CRITICAL_THRESHOLD}%)")
            
            sent_count = 0
            failed_count = 0
            
            # Send individual alerts for critical leads (max 5 to avoid spam)
            max_alerts = min(5, len(critical_df))
            for idx, row in critical_df.head(max_alerts).iterrows():
                logger.info(f"📤 Sending alert for: {row['Company Name']} ({row['Hiring Probability (%)']}%)")
                
                message = self.format_company_alert(row)
                
                if self.send_message(message):
                    sent_count += 1
                    logger.info(f"  ✅ Alert sent successfully")
                else:
                    failed_count += 1
                    logger.error(f"  ❌ Alert failed to send")
            
            if len(critical_df) > max_alerts:
                logger.info(f"⚠️  Skipped {len(critical_df) - max_alerts} additional alerts (spam prevention)")
            
            # Send daily summary
            logger.info("📤 Sending daily summary...")
            summary = self.format_summary_message(df, len(critical_df))
            
            if self.send_message(summary):
                logger.info("  ✅ Summary sent successfully")
            else:
                logger.warning("  ⚠️  Summary failed to send")
            
            # Save notification log
            self.save_notification_log(df, critical_df, sent_count, failed_count)
            
            # Print results
            logger.info("\n" + "="*60)
            logger.info("📊 NOTIFICATION SUMMARY")
            logger.info("="*60)
            logger.info(f"Critical Leads Found: {len(critical_df)}")
            logger.info(f"Alerts Sent: {sent_count}")
            logger.info(f"Alerts Failed: {failed_count}")
            logger.info("="*60 + "\n")
            
            return sent_count > 0 or len(critical_df) == 0  # Success if no critical leads or sent some
            
        except Exception as e:
            logger.error(f"❌ Notification failed with exception: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def save_notification_log(self, df: pd.DataFrame, critical_df: pd.DataFrame, 
                             sent: int, failed: int):
        """Save notification log."""
        output_dir = 'data/output/oracle'
        log = {
            'timestamp': datetime.now().isoformat(),
            'total_companies': len(df),
            'critical_leads': len(critical_df),
            'alerts_sent': sent,
            'alerts_failed': failed,
            'critical_companies': critical_df['Company Name'].tolist() if len(critical_df) > 0 else []
        }
        
        log_path = os.path.join(output_dir, 'notification_log.json')
        with open(log_path, 'w') as f:
            json.dump(log, f, indent=2)
        
        logger.info(f"💾 Notification log saved to: {log_path}")


def main():
    """Main notification function."""
    try:
        notifier = TelegramNotifier()
        success = notifier.notify()
        
        if success:
            logger.info("✅ Notifications sent successfully")
            sys.exit(0)
        else:
            logger.warning("⚠️  Notifications completed with issues")
            sys.exit(0)  # Don't fail the pipeline
            
    except Exception as e:
        logger.error(f"❌ Fatal error: {str(e)}")
        sys.exit(0)  # Don't fail the pipeline


if __name__ == '__main__':
    main()
