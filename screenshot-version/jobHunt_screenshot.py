#!/usr/bin/env python3
"""
Screenshot-Based Multi-Company Job Hunter
This version uses visual screenshot comparison to detect job changes.
More reliable than text-based methods as it captures visual layout changes.
"""

import json
import logging
import os
import time
import base64
import hashlib
from datetime import datetime
from typing import Dict, Optional
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image, ImageChops
import io

# Import AI vision module
try:
    from ai_vision import create_ai_analyzer
    AI_VISION_AVAILABLE = True
except ImportError:
    AI_VISION_AVAILABLE = False

# Configuration
COMPANIES = {
    "NVIDIA": {
        "url": "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite?q=Student&locationHierarchy1=2fcb99c455831013ea52bbe14cf9326c",
        "screenshot_file": "nvidia_screenshot.txt",
        "selectors": [
            '[data-automation-id="jobPostings"]',
            '[data-automation-id="searchResults"]',
            '.css-1pe6dbz',
            '[role="main"]'
        ]
    },
    "Intel": {
        "url": "https://intel.wd1.myworkdayjobs.com/en-US/External?q=student&locations=1e4a4eb3adf1013563ba9174bf817fcd",
        "screenshot_file": "intel_screenshot.txt",
        "selectors": [
            '[data-automation-id="jobPostings"]',
            '[data-automation-id="searchResults"]',
            '.css-1pe6dbz',
            '[role="main"]'
        ]
    }
}

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
JOBS_FILE = "screenshot_jobs_state.json"

# Settings
CHANGE_THRESHOLD = float(os.getenv("CHANGE_THRESHOLD", "0.5"))  # % of pixels that need to change
SAVE_DEBUG_IMAGES = os.getenv("SAVE_DEBUG_IMAGES", "false").lower() == "true"
USE_AI_ANALYSIS = os.getenv("USE_AI_ANALYSIS", "true").lower() == "true"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize AI analyzer
ai_analyzer = None
if USE_AI_ANALYSIS and AI_VISION_AVAILABLE and GEMINI_API_KEY:
    ai_analyzer = create_ai_analyzer(GEMINI_API_KEY)
    if ai_analyzer.is_enabled():
        logger.info("🤖 AI vision analysis enabled")
    else:
        logger.warning("🤖 AI vision failed to initialize")
elif USE_AI_ANALYSIS:
    logger.warning("🤖 AI analysis requested but not available (missing API key or module)")

def setup_selenium_driver():
    """Setup Selenium Chrome driver optimized for GitHub Actions"""
    chrome_options = Options()
    
    # Essential options for headless operation
    chrome_options.add_argument('--headless=new')  # Use new headless mode
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-web-security')
    chrome_options.add_argument('--allow-running-insecure-content')
    
    # Anti-detection measures
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Performance optimizations
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-plugins')
    chrome_options.add_argument('--disable-images')  # Disable image loading for faster screenshots
    chrome_options.add_argument('--disable-javascript')  # Disable JS for more stable screenshots
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        # Remove webdriver property
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
    except Exception as e:
        logger.error(f"Failed to setup Chrome driver: {e}")
        return None

def wait_for_page_load(driver, timeout=20):
    """Wait for page to fully load"""
    try:
        # Wait for body to be present
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Wait for any loading indicators to disappear
        loading_selectors = [
            '[data-automation-id="loadingIndicator"]',
            '.loading',
            '.spinner',
            '[aria-label="Loading"]'
        ]
        
        for selector in loading_selectors:
            try:
                WebDriverWait(driver, 5).until_not(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
            except:
                pass  # Loading indicator might not exist
                
        # Additional wait for dynamic content
        time.sleep(3)
        return True
        
    except Exception as e:
        logger.warning(f"Page load wait failed: {e}")
        return False

def find_job_container(driver, selectors):
    """Find the main job listings container"""
    for selector in selectors:
        try:
            container = driver.find_element(By.CSS_SELECTOR, selector)
            if container and container.is_displayed():
                return container
        except:
            continue
    return None

def take_screenshot(url: str, company_name: str, company_config: dict) -> Optional[str]:
    """Take a screenshot of the job page and return base64 encoded image"""
    driver = setup_selenium_driver()
    if not driver:
        return None
    
    try:
        logger.info(f"📸 Taking screenshot of {company_name} job page...")
        
        # Navigate to the page
        driver.get(url)
        
        # Wait for page to load
        if not wait_for_page_load(driver):
            logger.warning(f"Page load timeout for {company_name}, proceeding anyway")
        
        # Try to find and focus on job listings container
        job_container = find_job_container(driver, company_config["selectors"])
        
        if job_container:
            logger.info(f"✅ Found job container for {company_name}")
            # Scroll to job container
            driver.execute_script("arguments[0].scrollIntoView(true);", job_container)
            time.sleep(2)
            
            # Take screenshot of the specific container
            screenshot_png = job_container.screenshot_as_png
            screenshot_method = "container"
        else:
            logger.info(f"📄 Using full page screenshot for {company_name}")
            # Take full page screenshot
            screenshot_png = driver.get_screenshot_as_png()
            screenshot_method = "fullpage"
        
        # Convert to base64 for storage
        screenshot_b64 = base64.b64encode(screenshot_png).decode('utf-8')
        
        # Calculate size info
        size_kb = len(screenshot_png) / 1024
        logger.info(f"📸 Screenshot captured for {company_name}: {size_kb:.1f}KB ({screenshot_method})")
        
        return screenshot_b64
        
    except Exception as e:
        logger.error(f"❌ Error taking screenshot of {company_name}: {e}")
        return None
    finally:
        try:
            driver.quit()
        except:
            pass

def compare_screenshots(screenshot1_b64: str, screenshot2_b64: str, company_name: str) -> dict:
    """Compare two screenshots and return detailed difference analysis"""
    try:
        if not screenshot1_b64 or not screenshot2_b64:
            return {
                "changed": True, 
                "reason": "Missing screenshot data",
                "change_percentage": 100.0
            }
        
        # Decode base64 images
        img1_data = base64.b64decode(screenshot1_b64)
        img2_data = base64.b64decode(screenshot2_b64)
        
        img1 = Image.open(io.BytesIO(img1_data))
        img2 = Image.open(io.BytesIO(img2_data))
        
        # Log image information
        logger.info(f"Comparing {company_name} screenshots: {img1.size} vs {img2.size}")
        
        # Handle size differences
        if img1.size != img2.size:
            logger.info(f"📐 {company_name} screenshot size changed: {img1.size} -> {img2.size}")
            # Resize the newer image to match the older one for comparison
            img2 = img2.resize(img1.size, Image.Resampling.LANCZOS)
        
        # Convert to same mode if different
        if img1.mode != img2.mode:
            img2 = img2.convert(img1.mode)
        
        # Calculate pixel difference
        diff = ImageChops.difference(img1, img2)
        
        # Convert difference to grayscale for analysis
        diff_gray = diff.convert('L')
        histogram = diff_gray.histogram()
        
        # Calculate change statistics
        total_pixels = sum(histogram)
        changed_pixels = sum(histogram[1:])  # All non-zero values (pixels that changed)
        change_percentage = (changed_pixels / total_pixels) * 100 if total_pixels > 0 else 0
        
        # Determine if change is significant
        is_changed = change_percentage > CHANGE_THRESHOLD
        
        # Calculate additional metrics
        max_diff = max(histogram[1:]) if changed_pixels > 0 else 0
        avg_change = sum(i * histogram[i] for i in range(1, 256)) / changed_pixels if changed_pixels > 0 else 0
        
        result = {
            "changed": is_changed,
            "change_percentage": round(change_percentage, 3),
            "threshold": CHANGE_THRESHOLD,
            "total_pixels": total_pixels,
            "changed_pixels": changed_pixels,
            "max_diff_intensity": max_diff,
            "avg_change_intensity": round(avg_change, 2),
            "reason": f"{change_percentage:.3f}% pixels changed (threshold: {CHANGE_THRESHOLD}%)"
        }
        
        # Add AI analysis if available
        ai_result = None
        if ai_analyzer and ai_analyzer.is_enabled() and is_changed:
            logger.info(f"🤖 Running AI analysis for {company_name}...")
            ai_result = ai_analyzer.analyze_screenshots(img1_data, img2_data, company_name)
            
            # Override pixel-based decision with AI analysis if confident enough
            if ai_result.get("confidence", 0) > 0.7:
                ai_has_changes = ai_result.get("has_changes", False)
                if ai_has_changes != is_changed:
                    logger.info(f"🤖 AI override for {company_name}: pixel={is_changed} -> AI={ai_has_changes}")
                    result["changed"] = ai_has_changes
                    result["ai_override"] = True
                    result["reason"] = f"AI analysis: {ai_result.get('description', 'Unknown')}"
        
        # Add AI analysis to result
        if ai_result:
            result["ai_analysis"] = {
                "has_changes": ai_result.get("has_changes"),
                "description": ai_result.get("description"),
                "confidence": ai_result.get("confidence"),
                "details": ai_result.get("details", [])
            }
        
        if result["changed"]:
            logger.info(f"🔍 {company_name} visual change detected: {result['reason']}")
        else:
            logger.info(f"✅ {company_name} no significant visual changes: {result['reason']}")
        
        # Save debug images if enabled
        if SAVE_DEBUG_IMAGES and (result["changed"] or os.getenv("SAVE_ALL_DEBUG", "false").lower() == "true"):
            try:
                timestamp = int(time.time())
                diff_path = f"debug_{company_name.lower()}_diff_{timestamp}.png"
                diff.save(diff_path)
                logger.info(f"💾 Saved debug difference image: {diff_path}")
            except Exception as e:
                logger.warning(f"Failed to save debug image: {e}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Error comparing screenshots for {company_name}: {e}")
        return {
            "changed": True, 
            "reason": f"Comparison error: {str(e)}",
            "change_percentage": 100.0
        }

def load_previous_screenshot(company_config: dict) -> Optional[str]:
    """Load previous screenshot from file"""
    screenshot_file = company_config["screenshot_file"]
    try:
        if os.path.exists(screenshot_file):
            with open(screenshot_file, 'r') as f:
                screenshot_data = f.read().strip()
            
            # Validate base64 format (check length and basic base64 characters)
            if len(screenshot_data) > 100:
                # Basic validation for base64 format
                import re
                if re.match(r'^[A-Za-z0-9+/]*={0,2}$', screenshot_data):
                    return screenshot_data
                else:
                    logger.warning(f"Invalid base64 format in {screenshot_file}, ignoring")
                    return None
            else:
                logger.warning(f"Screenshot file {screenshot_file} too short, ignoring")
                return None
    except Exception as e:
        logger.error(f"Error loading previous screenshot from {screenshot_file}: {e}")
    return None

def save_screenshot(screenshot_b64: str, company_config: dict):
    """Save screenshot to file"""
    screenshot_file = company_config["screenshot_file"]
    try:
        with open(screenshot_file, 'w') as f:
            f.write(screenshot_b64)
        
        size_kb = len(screenshot_b64) * 3 / 4 / 1024  # Rough base64 to binary size
        logger.info(f"💾 Saved screenshot to {screenshot_file} ({size_kb:.1f}KB)")
    except Exception as e:
        logger.error(f"Error saving screenshot to {screenshot_file}: {e}")

def should_run_check() -> bool:
    """Check if script should run - simplified without duplicate prevention"""
    # Always run when scheduled - no duplicate prevention needed with single schedule
    logger.info("✅ Running scheduled job check")
    return True

def check_company_jobs(company_name: str, company_config: dict) -> dict:
    """Check jobs for a single company using screenshot comparison"""
    logger.info(f"🔍 Checking {company_name} jobs with screenshot method...")
    logger.info(f"URL: {company_config['url']}")
    
    # Take current screenshot
    current_screenshot = take_screenshot(company_config["url"], company_name, company_config)
    if not current_screenshot:
        logger.error(f"❌ Failed to capture screenshot for {company_name}")
        return {"changed": False, "error": True, "method": "screenshot"}
    
    # Load previous screenshot
    previous_screenshot = load_previous_screenshot(company_config)
    
    if not previous_screenshot:
        # First run - save baseline
        save_screenshot(current_screenshot, company_config)
        
        # Run AI analysis on first screenshot if available
        ai_baseline = None
        if ai_analyzer and ai_analyzer.is_enabled():
            logger.info(f"🤖 Analyzing baseline screenshot for {company_name}...")
            screenshot_bytes = base64.b64decode(current_screenshot)
            ai_baseline = ai_analyzer.analyze_single_screenshot(screenshot_bytes, company_name, is_baseline=True)
        
        logger.info(f"📝 {company_name} first screenshot - baseline established")
        result = {
            "changed": False,
            "first_run": True,
            "url": company_config["url"],
            "error": False,
            "method": "screenshot",
            "reason": "First run - baseline established"
        }
        
        if ai_baseline:
            result["ai_baseline"] = ai_baseline
            
        return result
    
    # Compare screenshots
    comparison = compare_screenshots(previous_screenshot, current_screenshot, company_name)
    
    # Enhanced logging
    logger.info(f"{company_name} screenshot comparison:")
    logger.info(f"  Changed: {comparison['changed']}")
    logger.info(f"  Reason: {comparison['reason']}")
    
    # Double-check mechanism for screenshot changes
    if comparison["changed"]:
        logger.info(f"🔍 Double-checking {company_name} screenshot change...")
        time.sleep(5)
        
        verify_screenshot = take_screenshot(company_config["url"], company_name, company_config)
        if verify_screenshot:
            verify_comparison = compare_screenshots(current_screenshot, verify_screenshot, company_name)
            if verify_comparison["changed"] and verify_comparison["change_percentage"] > 1.0:
                logger.warning(f"⚠️  {company_name} page is visually unstable")
                logger.warning(f"Original vs Verify: {verify_comparison['change_percentage']:.3f}% difference")
                # Use the verification screenshot as it might be more stable
                current_screenshot = verify_screenshot
                comparison = compare_screenshots(previous_screenshot, current_screenshot, company_name)
            else:
                logger.info(f"✅ {company_name} screenshot change confirmed (stable on recheck)")
    
    # Save current screenshot
    save_screenshot(current_screenshot, company_config)
    
    result = {
        "changed": comparison["changed"],
        "first_run": False,
        "url": company_config["url"],
        "error": False,
        "method": "screenshot",
        "change_percentage": comparison.get("change_percentage", 0),
        "threshold": CHANGE_THRESHOLD,
        "reason": comparison.get("reason", "Unknown"),
        "comparison_details": comparison
    }
    
    if comparison["changed"]:
        logger.info(f"🔥 {company_name} visual content changed!")
        logger.warning(f"CHANGE DETECTED for {company_name}: {comparison['reason']}")
    else:
        logger.info(f"✅ No visual changes detected for {company_name}")
    
    return result

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

def update_job_state(company_results: dict):
    """Update job tracking state for all companies"""
    try:
        current_time = datetime.now()
        state = {
            "last_check": current_time.isoformat(),
            "detection_method": "screenshot",
            "change_threshold": CHANGE_THRESHOLD,
            "companies": company_results,
            "total_checks": 1,
            "timing_info": {
                "hour": current_time.hour,
                "minute": current_time.minute,
                "on_schedule": current_time.minute in [0, 5, 10, 30, 35, 40]
            }
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
    logger.info("🚀 Starting Screenshot-Based Multi-Company Job Hunter")
    
    # Environment information
    import platform
    import socket
    logger.info(f"Environment info:")
    logger.info(f"  Platform: {platform.system()} {platform.release()}")
    logger.info(f"  Python: {platform.python_version()}")
    logger.info(f"  Hostname: {socket.gethostname()}")
    logger.info(f"  Working directory: {os.getcwd()}")
    logger.info(f"  Current time: {datetime.now().isoformat()}")
    logger.info(f"  Detection method: Screenshot comparison")
    logger.info(f"  Change threshold: {CHANGE_THRESHOLD}%")
    
    # Check existing screenshot files
    for company_name, config in COMPANIES.items():
        screenshot_file = config["screenshot_file"]
        if os.path.exists(screenshot_file):
            file_size = os.path.getsize(screenshot_file)
            logger.info(f"Found existing {company_name} screenshot: {file_size} bytes")
        else:
            logger.info(f"No existing {company_name} screenshot found")
    
    # Debug environment variables
    is_github_actions = os.getenv('GITHUB_ACTIONS') == 'true'
    logger.info(f"Running in GitHub Actions: {is_github_actions}")
    logger.info(f"Telegram config:")
    logger.info(f"  BOT_TOKEN present: {'Yes' if BOT_TOKEN else 'No'}")
    logger.info(f"  CHAT_ID present: {'Yes' if CHAT_ID else 'No'}")
    
    if not BOT_TOKEN or not CHAT_ID:
        logger.error("❌ Missing Telegram credentials")
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
        changed_companies = [name for name, result in company_results.items() if result["changed"]]
        
        message = f"📸 <b>Visual Job Updates Detected!</b>\n\n"
        
        for company in changed_companies:
            config = COMPANIES[company]
            result = company_results[company]
            message += f"🔥 <b>{company}</b> jobs page has visual changes!\n"
            
            # Add AI analysis if available
            if "ai_analysis" in result:
                ai_analysis = result["ai_analysis"]
                message += f"\n🤖 <b>AI Analysis:</b>\n"
                
                if ai_analysis.get("description"):
                    message += f"📝 {ai_analysis['description']}\n"
                
                if ai_analysis.get("confidence", 0) > 0:
                    message += f"🎯 Confidence: {ai_analysis['confidence']*100:.0f}%\n"
                
                # Add specific details if available
                if ai_analysis.get("details") and isinstance(ai_analysis["details"], list):
                    if ai_analysis["details"]:
                        message += f"🔍 <b>Specific Changes:</b>\n"
                        for detail in ai_analysis["details"][:3]:  # Limit to 3 details to avoid long messages
                            message += f"  • {detail}\n"
                
                # Add change status
                if ai_analysis.get("has_changes") is not None:
                    status = "✅ Changes Confirmed" if ai_analysis["has_changes"] else "❌ No Meaningful Changes"
                    message += f"🔎 AI Assessment: {status}\n"
                
                # Show error if AI analysis failed
                if ai_analysis.get("error"):
                    message += f"⚠️ AI Error: {ai_analysis['error']}\n"
            else:
                message += f"\n🔍 <b>Detection Method:</b> Pixel-based comparison only\n"
            
            message += f"📊 Change: {result.get('change_percentage', 0):.2f}% of pixels\n"
            message += f"🔗 <a href=\"{config['url']}\">Check {company} Jobs</a>\n\n"
        
        message += f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
        message += f"🎯 Detection: Screenshot comparison (threshold: {CHANGE_THRESHOLD}%)\n"
        message += f"🤖 Automated visual monitoring"
        
        send_telegram_notification(message)
        
    elif first_run_companies:
        welcome_msg = f"📸 <b>Screenshot-Based Job Hunter Activated!</b>\n\n"
        welcome_msg += f"Now monitoring visual changes in job postings from:\n"
        
        for company_name, company_config in COMPANIES.items():
            welcome_msg += f"• <b>{company_name}</b>\n"
            welcome_msg += f"  🔗 <a href=\"{company_config['url']}\">Jobs Page</a>\n"
        
        welcome_msg += f"\n🎯 Using screenshot comparison (threshold: {CHANGE_THRESHOLD}%)\n"
        if ai_analyzer and ai_analyzer.is_enabled():
            welcome_msg += f"🤖 Enhanced with Google Gemini AI analysis\n"
        welcome_msg += f"⏰ Running every 30 minutes via GitHub Actions\n"
        welcome_msg += f"🔕 You'll only receive notifications when visual changes occur"
        
        send_telegram_notification(welcome_msg)
        
    else:
        logger.info("✅ No visual changes detected for any company - no notification sent")
    
    # Update tracking state
    update_job_state(company_results)
    
    # Summary
    current_time = datetime.now()
    logger.info("📊 Run Summary:")
    logger.info(f"  Environment: {'GitHub Actions' if is_github_actions else 'Local'}")
    logger.info(f"  Start time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"  Detection method: Screenshot comparison")
    logger.info(f"  Change threshold: {CHANGE_THRESHOLD}%")
    logger.info(f"  Companies checked: {len(company_results)}")
    logger.info(f"  Visual changes detected: {sum(1 for r in company_results.values() if r['changed'])}")
    logger.info(f"  First runs: {sum(1 for r in company_results.values() if r['first_run'])}")
    logger.info(f"  Errors: {sum(1 for r in company_results.values() if r.get('error', False))}")
    
    logger.info("✅ Screenshot-based job check completed")

if __name__ == "__main__":
    main()