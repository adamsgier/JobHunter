#!/usr/bin/env python3
"""
Multi-Company Job Hunter for GitHub Actions
Enhanced version that monitors both NVIDIA and Intel job postings with:
- Comprehensive dynamic content filtering to prevent false positives
- Double-check mechanism for suspected changes
- Enhanced debugging and environment detection
- Robust cache validation and error handling
"""

import json
import logging
import os
import re
import time
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
        
        # Log response details for debugging
        logger.info(f"Response status: {response.status_code}, Content-Length: {len(response.text)}")
        
        # Remove dynamic content that changes on every request
        content = response.text
        original_length = len(content)
        
        # Count dynamic elements before filtering
        uuid_count = len(re.findall(r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', content))
        session_count = len(re.findall(r'[a-f0-9]{32}', content))
        timestamp_count = len(re.findall(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[.]\d+Z?', content))
        
        # Enhanced dynamic content filtering
        content = re.sub(r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', 'SESSIONID', content)
        content = re.sub(r'[a-f0-9]{32}', 'SESSIONID', content)
        content = re.sub(r'[a-f0-9]{24,}', 'SESSIONID', content)  # Longer hex strings
        content = re.sub(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[.]\d+Z?', 'TIMESTAMP', content)
        content = re.sub(r'_[0-9]{13}', '_TIMESTAMP', content)  # Unix timestamps (ms)
        content = re.sub(r'\b[0-9]{10}\b', 'TIMESTAMP', content)  # Unix timestamps (seconds)
        content = re.sub(r'nonce[^"]*"[^"]*"', 'nonce="NONCE"', content, flags=re.IGNORECASE)
        content = re.sub(r'integrity="[^"]*"', 'integrity="HASH"', content)
        content = re.sub(r'_buildManifest[^:]*:[^,}]+', '_buildManifest:{}', content)
        
        filtered_length = len(content)
        
        # Log filtering statistics
        logger.info(f"Dynamic content filtered - UUIDs: {uuid_count}, Sessions: {session_count}, Timestamps: {timestamp_count}")
        logger.info(f"Content length: {original_length} -> {filtered_length} ({original_length - filtered_length} chars removed)")
        
        hash_value = hashlib.md5(content.encode()).hexdigest()
        logger.info(f"Generated hash: {hash_value}")
        
        return hash_value
    except Exception as e:
        logger.error(f"Error getting page hash: {e}")
        return ""

def load_previous_hash(hash_file: str) -> str:
    """Load previous page hash for a specific company"""
    try:
        if os.path.exists(hash_file):
            with open(hash_file, 'r') as f:
                hash_value = f.read().strip()
            
            # Validate that it's a reasonable MD5 hash
            if len(hash_value) == 32 and all(c in '0123456789abcdef' for c in hash_value.lower()):
                return hash_value
            else:
                logger.warning(f"Invalid hash format in {hash_file}: '{hash_value}' - ignoring")
                return ""
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
        current_time = datetime.now()
        state = {
            "last_check": current_time.isoformat(),
            "last_check_minute": current_time.minute,
            "companies": company_changes,
            "total_checks": 1,
            "timing_info": {
                "hour": current_time.hour,
                "minute": current_time.minute,
                "scheduled_times": [0, 5, 10, 30, 35, 40],
                "on_schedule": current_time.minute in [0, 5, 10, 30, 35, 40]
            }
        }
        
        # Load existing state if available
        if os.path.exists(JOBS_FILE):
            try:
                with open(JOBS_FILE, 'r') as f:
                    existing_state = json.load(f)
                    state["total_checks"] = existing_state.get("total_checks", 0) + 1
                    
                    # Track timing accuracy
                    if "timing_history" not in existing_state:
                        existing_state["timing_history"] = []
                    state["timing_history"] = existing_state["timing_history"][-10:]  # Keep last 10
                    state["timing_history"].append({
                        "time": current_time.isoformat(),
                        "minute": current_time.minute,
                        "on_schedule": current_time.minute in [0, 5, 10, 30, 35, 40]
                    })
            except:
                pass
        
        with open(JOBS_FILE, 'w') as f:
            json.dump(state, f, indent=2)
            
    except Exception as e:
        logger.error(f"Error updating job state: {e}")

def check_company_jobs(company_name: str, company_config: dict) -> dict:
    """Check jobs for a single company with double-check for false positives"""
    logger.info(f"🔍 Checking {company_name} jobs...")
    logger.info(f"URL: {company_config['url']}")
    
    # Get current page hash
    current_hash = get_page_hash(company_config["url"])
    if not current_hash:
        logger.error(f"❌ Failed to get {company_name} page content")
        return {"changed": False, "error": True}
    
    # Compare with previous hash
    previous_hash = load_previous_hash(company_config["hash_file"])
    page_changed = previous_hash and previous_hash != current_hash
    
    # Enhanced logging for debugging
    logger.info(f"{company_name} hash comparison:")
    logger.info(f"  Previous: {previous_hash or 'None (first run)'}")
    logger.info(f"  Current:  {current_hash}")
    logger.info(f"  Changed:  {page_changed}")
    
    # Double-check mechanism for potential false positives
    if page_changed and previous_hash:
        logger.info(f"🔍 Double-checking {company_name} change (waiting 3 seconds)...")
        time.sleep(3)
        
        # Get hash again to verify the change is persistent
        verify_hash = get_page_hash(company_config["url"])
        if verify_hash != current_hash:
            logger.warning(f"⚠️  {company_name} content is unstable (hash changed again during verification)")
            logger.warning(f"Original: {current_hash} -> Verify: {verify_hash}")
            # Use the verification hash as the current one
            current_hash = verify_hash
        else:
            logger.info(f"✅ {company_name} change confirmed (hash stable on recheck)")
    
    # Save current hash
    save_current_hash(current_hash, company_config["hash_file"])
    
    result = {
        "changed": page_changed,
        "first_run": not bool(previous_hash),
        "url": company_config["url"],
        "error": False,
        "current_hash": current_hash,
        "previous_hash": previous_hash or "none"
    }
    
    if page_changed:
        logger.info(f"🔥 {company_name} page content changed!")
        logger.warning(f"CHANGE DETECTED for {company_name}: {previous_hash} -> {current_hash}")
    elif previous_hash:
        logger.info(f"✅ No {company_name} changes detected")
    else:
        logger.info(f"📝 {company_name} first run - baseline established")
    
    return result

def should_run_check() -> bool:
    """Check if enough time has passed since last run to avoid duplicates"""
    if not os.path.exists(JOBS_FILE):
        return True  # First run
    
    try:
        with open(JOBS_FILE, 'r') as f:
            state = json.load(f)
        
        last_check_str = state.get("last_check")
        if not last_check_str:
            return True
        
        last_check = datetime.fromisoformat(last_check_str)
        time_since_last = datetime.now() - last_check
        minutes_since = time_since_last.total_seconds() / 60
        
        # Only run if at least 25 minutes have passed (allows for some overlap)
        if minutes_since >= 25:
            logger.info(f"✅ {minutes_since:.1f} minutes since last run - proceeding")
            return True
        else:
            logger.info(f"⏭️  Only {minutes_since:.1f} minutes since last run - skipping to avoid duplicate")
            return False
            
    except Exception as e:
        logger.error(f"Error checking last run time: {e}")
        return True  # Run if we can't determine last run time

def main():
    """Main job checking function for multiple companies"""
    logger.info("🚀 Starting Multi-Company Job Hunter (GitHub Actions)")
    
    # Check if we should run to avoid duplicate executions
    if not should_run_check():
        logger.info("🚪 Exiting early to prevent duplicate run")
        return
    
    # Debug environment information
    import platform
    import socket
    logger.info(f"Environment info:")
    logger.info(f"  Platform: {platform.system()} {platform.release()}")
    logger.info(f"  Python: {platform.python_version()}")
    logger.info(f"  Hostname: {socket.gethostname()}")
    logger.info(f"  Working directory: {os.getcwd()}")
    logger.info(f"  Current time: {datetime.now().isoformat()}")
    
    # Check existing state files and cache restoration
    cache_restored = True
    for company_name, config in COMPANIES.items():
        hash_file = config["hash_file"]
        if os.path.exists(hash_file):
            with open(hash_file, 'r') as f:
                existing_hash = f.read().strip()
            file_age = time.time() - os.path.getmtime(hash_file)
            logger.info(f"Found existing {company_name} hash: {existing_hash} (age: {file_age:.1f}s)")
        else:
            logger.info(f"No existing {company_name} hash file found")
            cache_restored = False
    
    if os.path.exists(JOBS_FILE):
        file_age = time.time() - os.path.getmtime(JOBS_FILE)
        logger.info(f"Found existing state file: {JOBS_FILE} (age: {file_age:.1f}s)")
    else:
        logger.info(f"No existing state file found: {JOBS_FILE}")
        cache_restored = False
    
    # Detect if we're in GitHub Actions
    is_github_actions = os.getenv('GITHUB_ACTIONS') == 'true'
    github_workflow = os.getenv('GITHUB_WORKFLOW', 'unknown')
    logger.info(f"Running in GitHub Actions: {is_github_actions}")
    if is_github_actions:
        logger.info(f"Triggered by workflow: {github_workflow}")
    
    if is_github_actions and not cache_restored:
        logger.warning("⚠️  Cache may not have been restored properly in GitHub Actions!")
        logger.warning("This could cause false positive change detection.")
    
    # Debug environment variables
    logger.info(f"Telegram config:")
    logger.info(f"  BOT_TOKEN present: {'Yes' if BOT_TOKEN else 'No'}")
    logger.info(f"  CHAT_ID present: {'Yes' if CHAT_ID else 'No'}")
    
    if BOT_TOKEN:
        logger.info(f"  Bot token starts with: {BOT_TOKEN[:10]}...")
    if CHAT_ID:
        logger.info(f"  Chat ID: {CHAT_ID}")
    
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
    
    # Summary for debugging
    current_time = datetime.now()
    logger.info("📊 Run Summary:")
    logger.info(f"  Environment: {'GitHub Actions' if is_github_actions else 'Local'}")
    logger.info(f"  Start time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"  Minute marker: {current_time.minute} (should be near 0,5,10,30,35,40)")
    logger.info(f"  Cache restored: {cache_restored}")
    logger.info(f"  Companies checked: {len(company_results)}")
    logger.info(f"  Changes detected: {sum(1 for r in company_results.values() if r['changed'])}")
    logger.info(f"  First runs: {sum(1 for r in company_results.values() if r['first_run'])}")
    logger.info(f"  Errors: {sum(1 for r in company_results.values() if r.get('error', False))}")
    
    logger.info("✅ Multi-company job check completed")

if __name__ == "__main__":
    main()