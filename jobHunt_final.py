#!/usr/bin/env python3
"""
Final NVIDIA Job Hunter - Multiple Approaches
This version tries different methods to find job postings.
"""

import json
import logging
import os
import time
import hashlib
from datetime import datetime
from typing import List, Set, Optional
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
NVIDIA_JOBS_URL = "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite?q=Student&locationHierarchy1=2fcb99c455831013ea52bbe14cf9326c"
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
JOBS_FILE = "nvidia_jobs_final.json"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('job_hunter_final.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FinalJobHunter:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_page_hash(self, url: str) -> Optional[str]:
        """Get a hash of the page content to detect changes"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Create hash of the content
            content_hash = hashlib.md5(response.text.encode()).hexdigest()
            return content_hash
            
        except Exception as e:
            logger.error(f"Error getting page hash: {e}")
            return None
    
    def check_for_page_changes(self) -> bool:
        """Check if the job page has changed since last check"""
        current_hash = self.get_page_hash(NVIDIA_JOBS_URL)
        if not current_hash:
            return False
        
        hash_file = "nvidia_page_hash.txt"
        
        try:
            # Load previous hash
            if os.path.exists(hash_file):
                with open(hash_file, 'r') as f:
                    previous_hash = f.read().strip()
            else:
                previous_hash = ""
            
            # Save current hash
            with open(hash_file, 'w') as f:
                f.write(current_hash)
            
            # Check if changed
            if previous_hash and previous_hash != current_hash:
                logger.info("Page content has changed!")
                return True
            elif not previous_hash:
                logger.info("First run - saving page hash")
                return False
            else:
                logger.info("No changes detected in page content")
                return False
                
        except Exception as e:
            logger.error(f"Error checking page changes: {e}")
            return False
    
    def search_alternative_sources(self) -> List[dict]:
        """Search for NVIDIA student jobs on alternative sites"""
        sources = [
            {
                'name': 'Indeed',
                'url': 'https://www.indeed.com/jobs?q=NVIDIA+student&sort=date',
                'search_terms': ['nvidia', 'student', 'intern']
            },
            {
                'name': 'LinkedIn',
                'url': 'https://www.linkedin.com/jobs/search/?keywords=NVIDIA%20student',
                'search_terms': ['nvidia', 'student', 'intern']
            }
        ]
        
        jobs = []
        for source in sources:
            try:
                logger.info(f"Checking {source['name']} for NVIDIA jobs...")
                # Note: This is a placeholder - actual scraping would need
                # more sophisticated handling for these sites
                
                # For demo purposes, we'll just log that we checked
                logger.info(f"Would check {source['url']} for jobs")
                
            except Exception as e:
                logger.error(f"Error checking {source['name']}: {e}")
        
        return jobs
    
    def manual_job_entry(self) -> List[dict]:
        """Allow manual entry of job postings for testing"""
        # This could be expanded to read from a manual input file
        # or accept jobs via Telegram bot commands
        return []
    
    def load_previous_state(self) -> dict:
        """Load previous job state from file"""
        try:
            if os.path.exists(JOBS_FILE):
                with open(JOBS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {"jobs": [], "last_check": None}
        except Exception as e:
            logger.error(f"Error loading previous state: {e}")
            return {"jobs": [], "last_check": None}
    
    def save_current_state(self, jobs: List[dict], page_changed: bool):
        """Save current state to file"""
        try:
            data = {
                "last_updated": datetime.now().isoformat(),
                "page_changed": page_changed,
                "jobs": jobs,
                "last_check": datetime.now().isoformat()
            }
            with open(JOBS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved state with {len(jobs)} jobs")
        except Exception as e:
            logger.error(f"Error saving state: {e}")
    
    def send_telegram_notification(self, message: str) -> bool:
        """Send notification via Telegram bot"""
        if not BOT_TOKEN or not CHAT_ID:
            logger.error("Telegram bot token or chat ID not configured")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": CHAT_ID,
                "text": message,
                "parse_mode": "HTML",
                "disable_web_page_preview": False
            }
            
            response = requests.post(url, data=payload, timeout=10)
            response.raise_for_status()
            
            logger.info("Telegram notification sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {e}")
            return False
    
    def check_for_new_jobs(self):
        """Main function to check for new job postings"""
        logger.info("Starting comprehensive job check...")
        
        # Method 1: Check for page changes
        page_changed = self.check_for_page_changes()
        
        if page_changed:
            message = (
                f"🔍 <b>NVIDIA Jobs Page Updated!</b>\n\n"
                f"The NVIDIA student jobs page has been updated. "
                f"New positions may be available.\n\n"
                f"<a href=\"{NVIDIA_JOBS_URL}\">Check Jobs Page</a>\n\n"
                f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            self.send_telegram_notification(message)
        
        # Method 2: Check alternative sources (placeholder)
        alt_jobs = self.search_alternative_sources()
        
        # Method 3: Manual entries (if any)
        manual_jobs = self.manual_job_entry()
        
        # Combine all jobs
        all_jobs = alt_jobs + manual_jobs
        
        # Save state
        self.save_current_state(all_jobs, page_changed)
        
        logger.info("Job check completed")
        
        # Send status report
        if not page_changed and not all_jobs:
            status_message = (
                f"✅ <b>Job Check Complete</b>\n\n"
                f"No changes detected on NVIDIA careers page.\n"
                f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                f"<a href=\"{NVIDIA_JOBS_URL}\">Manual Check</a>"
            )
            self.send_telegram_notification(status_message)


def test_telegram():
    """Test Telegram configuration"""
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ Telegram not configured")
        print("Please set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env file")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": "🤖 NVIDIA Job Hunter test message - configuration working!"
        }
        
        response = requests.post(url, data=payload, timeout=10)
        response.raise_for_status()
        print("✅ Telegram test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Telegram test failed: {e}")
        return False


def main():
    """Main entry point"""
    print("NVIDIA Job Hunter - Final Version")
    print("=" * 40)
    
    # Test configuration
    if not test_telegram():
        return
    
    hunter = FinalJobHunter()
    hunter.check_for_new_jobs()


if __name__ == "__main__":
    main()