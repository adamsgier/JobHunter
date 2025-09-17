#!/usr/bin/env python3
"""
GitHub Actions optimized version of the job hunter
Simplified for cloud deployment without local file dependencies
"""

import json
import logging
import os
import hashlib
from datetime import datetime
import requests

# Configuration from environment variables
NVIDIA_JOBS_URL = "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite?q=Student&locationHierarchy1=2fcb99c455831013ea52bbe14cf9326c"
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
JOBS_FILE = "nvidia_jobs_state.json"
HASH_FILE = "page_hash.txt"

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_page_hash(url: str) -> str:
    """Get a hash of the page content"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return hashlib.md5(response.text.encode()).hexdigest()
    except Exception as e:
        logger.error(f"Error getting page hash: {e}")
        return ""

def load_previous_hash() -> str:
    """Load previous page hash"""
    try:
        if os.path.exists(HASH_FILE):
            with open(HASH_FILE, 'r') as f:
                return f.read().strip()
    except Exception as e:
        logger.error(f"Error loading previous hash: {e}")
    return ""

def save_current_hash(hash_value: str):
    """Save current page hash"""
    try:
        with open(HASH_FILE, 'w') as f:
            f.write(hash_value)
    except Exception as e:
        logger.error(f"Error saving hash: {e}")

def send_telegram_notification(message: str) -> bool:
    """Send notification via Telegram"""
    if not BOT_TOKEN or not CHAT_ID:
        logger.error("Telegram credentials not configured")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        }
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        logger.info("✅ Telegram notification sent")
        return True
        
    except Exception as e:
        logger.error(f"❌ Telegram notification failed: {e}")
        return False

def update_job_state(page_changed: bool):
    """Update job tracking state"""
    try:
        state = {
            "last_check": datetime.now().isoformat(),
            "page_changed": page_changed,
            "total_checks": 1
        }
        
        # Load existing state if available
        if os.path.exists(JOBS_FILE):
            try:
                with open(JOBS_FILE, 'r') as f:
                    existing_state = json.load(f)
                    state["total_checks"] = existing_state.get("total_checks", 0) + 1
            except:
                pass
        
        with open(JOBS_FILE, 'w') as f:
            json.dump(state, f, indent=2)
            
    except Exception as e:
        logger.error(f"Error updating job state: {e}")

def main():
    """Main job checking function"""
    logger.info("🚀 Starting NVIDIA Job Hunter (GitHub Actions)")
    
    # Debug environment variables
    logger.info(f"Environment check:")
    logger.info(f"TELEGRAM_BOT_TOKEN present: {'Yes' if BOT_TOKEN else 'No'}")
    logger.info(f"TELEGRAM_CHAT_ID present: {'Yes' if CHAT_ID else 'No'}")
    
    if BOT_TOKEN:
        logger.info(f"Bot token starts with: {BOT_TOKEN[:10]}...")
    if CHAT_ID:
        logger.info(f"Chat ID: {CHAT_ID}")
    
    if not BOT_TOKEN or not CHAT_ID:
        logger.error("❌ Missing Telegram credentials in GitHub secrets")
        logger.error("Please ensure TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are set in repository secrets")
        return
    
    # Get current page hash
    current_hash = get_page_hash(NVIDIA_JOBS_URL)
    if not current_hash:
        logger.error("❌ Failed to get page content")
        return
    
    # Compare with previous hash
    previous_hash = load_previous_hash()
    page_changed = previous_hash and previous_hash != current_hash
    
    # Save current hash
    save_current_hash(current_hash)
    
    if page_changed:
        logger.info("🔥 Page content changed - sending notification")
        message = (
            f"🚨 <b>NVIDIA Jobs Page Updated!</b>\n\n"
            f"The NVIDIA student jobs page has been updated. "
            f"New positions may be available!\n\n"
            f"🔗 <a href=\"{NVIDIA_JOBS_URL}\">Check Jobs Now</a>\n\n"
            f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
            f"🤖 Automated by GitHub Actions"
        )
        send_telegram_notification(message)
    elif previous_hash:
        logger.info("✅ No changes detected")
        # Optionally send daily status (uncomment if desired)
        # if datetime.now().hour == 9:  # 9 AM UTC daily status
        #     status_msg = f"✅ Daily Status: No new NVIDIA jobs detected\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}"
        #     send_telegram_notification(status_msg)
    else:
        logger.info("📝 First run - baseline established")
        welcome_msg = (
            f"🤖 <b>NVIDIA Job Hunter Activated!</b>\n\n"
            f"I'm now monitoring NVIDIA's student job postings and will notify you of any changes.\n\n"
            f"🔗 <a href=\"{NVIDIA_JOBS_URL}\">Current Jobs Page</a>\n\n"
            f"⏰ Running every hour via GitHub Actions"
        )
        send_telegram_notification(welcome_msg)
    
    # Update tracking state
    update_job_state(page_changed)
    
    logger.info("✅ Job check completed")

if __name__ == "__main__":
    main()