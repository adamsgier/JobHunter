#!/usr/bin/env python3
"""
Working NVIDIA Job Hunter using RSS feeds
This version uses NVIDIA's RSS feed to monitor job postings.
"""

import json
import logging
import os
import time
from datetime import datetime
from typing import List, Set
import requests
import feedparser
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
RSS_URL = "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite/jobs.rss"
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
JOBS_FILE = "nvidia_jobs_rss.json"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('job_hunter_rss.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class RSSJobHunter:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_current_jobs(self) -> List[dict]:
        """Get current job listings from RSS feed"""
        try:
            logger.info("Fetching jobs from RSS feed...")
            
            # Parse RSS feed
            feed = feedparser.parse(RSS_URL)
            
            if feed.bozo:
                logger.warning("RSS feed may have issues")
            
            jobs = []
            for entry in feed.entries:
                title = entry.title
                link = entry.link
                
                # Filter for student/intern positions
                if any(keyword in title.lower() for keyword in ['student', 'intern', 'graduate', 'university', 'campus']):
                    jobs.append({
                        'title': title,
                        'link': link,
                        'timestamp': datetime.now().isoformat(),
                        'published': getattr(entry, 'published', ''),
                        'summary': getattr(entry, 'summary', '')
                    })
            
            logger.info(f"Found {len(jobs)} relevant jobs from RSS feed")
            return jobs
            
        except Exception as e:
            logger.error(f"Error fetching RSS feed: {e}")
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
        logger.info("Starting job check via RSS...")
        
        current_jobs = self.get_current_jobs()
        if not current_jobs:
            logger.warning("No relevant jobs found in RSS feed")
            return
        
        previous_job_titles = self.load_previous_jobs()
        current_job_titles = set(job['title'] for job in current_jobs)
        new_job_titles = current_job_titles - previous_job_titles
        
        if new_job_titles:
            logger.info(f"Found {len(new_job_titles)} new job(s)!")
            
            for job in current_jobs:
                if job['title'] in new_job_titles:
                    message = (
                        f"🚨 <b>New NVIDIA Job Posted!</b>\n\n"
                        f"<b>Title:</b> {job['title']}\n"
                        f"<b>Link:</b> <a href=\"{job['link']}\">Apply Here</a>\n"
                    )
                    
                    if job.get('summary'):
                        # Truncate summary if too long
                        summary = job['summary'][:200] + "..." if len(job['summary']) > 200 else job['summary']
                        message += f"\n<b>Description:</b> {summary}\n"
                    
                    message += f"\n<a href=\"{RSS_URL}\">View RSS Feed</a>"
                    
                    self.send_telegram_notification(message)
                    time.sleep(1)  # Rate limiting
        else:
            logger.info("No new jobs found")
        
        self.save_current_jobs(current_jobs)
        logger.info(f"Job check completed. Total relevant jobs: {len(current_jobs)}")


def main():
    """Main entry point"""
    if not BOT_TOKEN or not CHAT_ID:
        logger.error("Please set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables")
        print("Set up your .env file with:")
        print("TELEGRAM_BOT_TOKEN=your_bot_token")
        print("TELEGRAM_CHAT_ID=your_chat_id")
        return
    
    hunter = RSSJobHunter()
    hunter.check_for_new_jobs()


if __name__ == "__main__":
    main()