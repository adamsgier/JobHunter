#!/usr/bin/env python3
"""
GitHub Actions optimized version of the job hunter
Simplified for cloud deployment without local file dependencies
"""

import json
import logging
import os
import re
import hashlib
from datetime import datetime
import requests

# Configuration from environment variables
COMPANIES = {
    "NVIDIA": {
        "url": "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite?q=Student&locationHierarchy1=2fcb99c455831013ea52bbe14cf9326c",
        "hash_file": "nvidia_page_hash.txt"
    },
    "Intel": {
        "url": "https://intel.wd1.myworkdayjobs.com/en-US/External?q=student&locations=1e4a4eb3adf1013563ba9174bf817fcd",
        "hash_file": "intel_page_hash.txt"
    }
}

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
JOBS_FILE = "jobs_state.json"

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_page_hash(url: str) -> str:
    """Get a hash of the page content, filtering out dynamic elements"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Remove dynamic content that changes on every request
        content = response.text
        
        # Remove session IDs and other dynamic identifiers
        content = re.sub(r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', 'SESSIONID', content)
        content = re.sub(r'[a-f0-9]{32}', 'SESSIONID', content)
        content = re.sub(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[.]\d+Z?', 'TIMESTAMP', content)
        content = re.sub(r'_[0-9]{13}', '_TIMESTAMP', content)  # Unix timestamps
        
        return hashlib.md5(content.encode()).hexdigest()
    except Exception as e:
        logger.error(f"Error getting page hash: {e}")
        return ""

def load_previous_hash(hash_file: str) -> str:
    """Load previous page hash for a specific company"""
    try:
        if os.path.exists(hash_file):
            with open(hash_file, 'r') as f:
                return f.read().strip()
    except Exception as e:
        logger.error(f"Error loading previous hash from {hash_file}: {e}")
    return ""

def save_current_hash(hash_value: str, hash_file: str):
    """Save current page hash for a specific company"""
    try:
        with open(hash_file, 'w') as f:
            f.write(hash_value)
    except Exception as e:
        logger.error(f"Error saving hash to {hash_file}: {e}")

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

def update_job_state(company_changes: dict):
    """Update job tracking state for all companies"""
    try:
        state = {
            "last_check": datetime.now().isoformat(),
            "companies": company_changes,
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

def check_company_jobs(company_name: str, company_config: dict) -> dict:
    """Check jobs for a single company"""
    logger.info(f"🔍 Checking {company_name} jobs...")
    
    # Get current page hash
    current_hash = get_page_hash(company_config["url"])
    if not current_hash:
        logger.error(f"❌ Failed to get {company_name} page content")
        return {"changed": False, "error": True}
    
    # Compare with previous hash
    previous_hash = load_previous_hash(company_config["hash_file"])
    page_changed = previous_hash and previous_hash != current_hash
    
    # Save current hash
    save_current_hash(current_hash, company_config["hash_file"])
    
    result = {
        "changed": page_changed,
        "first_run": not bool(previous_hash),
        "url": company_config["url"],
        "error": False
    }
    
    if page_changed:
        logger.info(f"🔥 {company_name} page content changed!")
    elif previous_hash:
        logger.info(f"✅ No {company_name} changes detected")
    else:
        logger.info(f"📝 {company_name} first run - baseline established")
    
    return result

def main():
    """Main job checking function for multiple companies"""
    logger.info("🚀 Starting Multi-Company Job Hunter (GitHub Actions)")
    
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
    
    # Check all companies
    company_results = {}
    any_changes = False
    first_run_companies = []
    
    for company_name, company_config in COMPANIES.items():
        result = check_company_jobs(company_name, company_config)
        company_results[company_name] = result
        
        if result["changed"]:
            any_changes = True
        elif result["first_run"]:
            first_run_companies.append(company_name)
    
    # Send notifications based on results
    if any_changes:
        # Send notification for companies with changes
        changed_companies = [name for name, result in company_results.items() if result["changed"]]
        
        message = f"🚨 <b>Job Updates Detected!</b>\n\n"
        
        for company in changed_companies:
            config = COMPANIES[company]
            message += f"🔥 <b>{company}</b> jobs page has been updated!\n"
            message += f"🔗 <a href=\"{config['url']}\">Check {company} Jobs</a>\n\n"
        
        message += f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
        message += f"🤖 Automated check (every 30 minutes)"
        
        send_telegram_notification(message)
        
    elif first_run_companies:
        # Send welcome message for first runs
        welcome_msg = f"🤖 <b>Multi-Company Job Hunter Activated!</b>\n\n"
        welcome_msg += f"Now monitoring student job postings from:\n"
        
        for company_name, company_config in COMPANIES.items():
            welcome_msg += f"• <b>{company_name}</b>\n"
            welcome_msg += f"  🔗 <a href=\"{company_config['url']}\">Jobs Page</a>\n"
        
        welcome_msg += f"\n⏰ Running every 30 minutes via GitHub Actions\n"
        welcome_msg += f"🔕 You'll only receive notifications when jobs change"
        
        send_telegram_notification(welcome_msg)
        
    else:
        # No changes detected for any company
        logger.info("✅ No changes detected for any company - no notification sent")
    
    # Update tracking state
    update_job_state(company_results)
    
    logger.info("✅ Multi-company job check completed")

if __name__ == "__main__":
    main()