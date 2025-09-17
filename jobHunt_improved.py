#!/usr/bin/env python3
"""
Improved NVIDIA Job Hunter
Monitors NVIDIA careers page for new job postings and sends notifications via Telegram.
"""

import json
import logging
import os
import time
from datetime import datetime
from typing import List, Set
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
NVIDIA_JOBS_URL = "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite?q=Student&locationHierarchy1=2fcb99c455831013ea52bbe14cf9326c"
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
JOBS_FILE = "nvidia_jobs.json"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('job_hunter.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class NvidiaJobHunter:
    def __init__(self):
        self.driver = None
        
    def setup_driver(self):
        """Setup Chrome WebDriver with appropriate options"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in background
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            logger.info("WebDriver setup completed")
            return True
        except Exception as e:
            logger.error(f"Failed to setup WebDriver: {e}")
            return False
    
    def get_current_jobs(self) -> List[dict]:
        """Scrape current job listings from NVIDIA careers page"""
        if not self.driver:
            if not self.setup_driver():
                return []
        
        try:
            logger.info("Loading NVIDIA careers page...")
            self.driver.get(NVIDIA_JOBS_URL)
            
            # Wait for the page to load and jobs to appear
            wait = WebDriverWait(self.driver, 20)
            
            # Wait for job listings to load (adjust selector based on actual page structure)
            job_elements = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-automation-id='jobTitle']"))
            )
            
            jobs = []
            for element in job_elements:
                try:
                    title = element.text.strip()
                    job_link = element.get_attribute("href") or ""
                    
                    if title:  # Only add jobs with valid titles
                        jobs.append({
                            "title": title,
                            "link": job_link,
                            "timestamp": datetime.now().isoformat()
                        })
                except Exception as e:
                    logger.warning(f"Error extracting job data: {e}")
                    continue
            
            logger.info(f"Found {len(jobs)} current job listings")
            return jobs
            
        except TimeoutException:
            logger.error("Timeout waiting for job listings to load")
            # Try alternative selectors
            try:
                job_elements = self.driver.find_elements(By.CSS_SELECTOR, "a[data-automation-id='jobTitle']")
                if not job_elements:
                    # Fallback to more generic selectors
                    job_elements = self.driver.find_elements(By.CSS_SELECTOR, "[role='listitem'] a")
                
                jobs = []
                for element in job_elements:
                    title = element.text.strip()
                    if title and "student" in title.lower():
                        jobs.append({
                            "title": title,
                            "link": element.get_attribute("href") or "",
                            "timestamp": datetime.now().isoformat()
                        })
                
                logger.info(f"Found {len(jobs)} jobs using fallback method")
                return jobs
                
            except Exception as e:
                logger.error(f"Failed to find jobs with fallback method: {e}")
                return []
                
        except Exception as e:
            logger.error(f"Error scraping jobs: {e}")
            return []
    
    def load_previous_jobs(self) -> Set[str]:
        """Load previously seen job titles from file"""
        try:
            if os.path.exists(JOBS_FILE):
                with open(JOBS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return set(job['title'] for job in data.get('jobs', []))
            return set()
        except Exception as e:
            logger.error(f"Error loading previous jobs: {e}")
            return set()
    
    def save_current_jobs(self, jobs: List[dict]):
        """Save current jobs to file"""
        try:
            data = {
                "last_updated": datetime.now().isoformat(),
                "jobs": jobs
            }
            with open(JOBS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(jobs)} jobs to {JOBS_FILE}")
        except Exception as e:
            logger.error(f"Error saving jobs: {e}")
    
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
                "disable_web_page_preview": True
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
        logger.info("Starting job check...")
        
        # Get current jobs
        current_jobs = self.get_current_jobs()
        if not current_jobs:
            logger.warning("No jobs found - this might indicate a scraping issue")
            return
        
        # Load previously seen jobs
        previous_job_titles = self.load_previous_jobs()
        
        # Find new jobs
        current_job_titles = set(job['title'] for job in current_jobs)
        new_job_titles = current_job_titles - previous_job_titles
        
        if new_job_titles:
            logger.info(f"Found {len(new_job_titles)} new job(s)!")
            
            # Send notification for each new job
            for job in current_jobs:
                if job['title'] in new_job_titles:
                    message = (
                        f"🚨 <b>New NVIDIA Job Posted!</b>\n\n"
                        f"<b>Title:</b> {job['title']}\n"
                        f"<b>Link:</b> {job['link'] or 'Check NVIDIA careers page'}\n\n"
                        f"<a href='{NVIDIA_JOBS_URL}'>View all NVIDIA student jobs</a>"
                    )
                    self.send_telegram_notification(message)
                    time.sleep(1)  # Rate limiting
        else:
            logger.info("No new jobs found")
        
        # Save current jobs for next check
        self.save_current_jobs(current_jobs)
        
        logger.info(f"Job check completed. Total jobs: {len(current_jobs)}")
    
    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver closed")


def main():
    """Main entry point"""
    if not BOT_TOKEN or not CHAT_ID:
        logger.error("Please set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables")
        return
    
    hunter = NvidiaJobHunter()
    try:
        hunter.check_for_new_jobs()
    finally:
        hunter.cleanup()


if __name__ == "__main__":
    main()