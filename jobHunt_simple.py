#!/usr/bin/env python3
"""
Alternative NVIDIA Job Hunter using requests + API approach
This version tries to find and use Workday's internal API endpoints.
"""

import json
import logging
import os
import re
import time
from datetime import datetime
from typing import List, Set
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
JOBS_FILE = "nvidia_jobs_simple.json"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SimpleNvidiaJobHunter:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
        })
    
    def find_workday_api_endpoint(self) -> str:
        """Try to find the actual API endpoint used by the website"""
        try:
            # First, get the main page to extract any API endpoints
            main_url = "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite"
            response = self.session.get(main_url)
            
            # Look for API endpoints in the JavaScript
            api_patterns = [
                r'jobs/api/[^"]+',
                r'/api/[^"]+jobs[^"]*',
                r'graphql[^"]*',
                r'jobSearch[^"]*'
            ]
            
            for pattern in api_patterns:
                matches = re.findall(pattern, response.text)
                if matches:
                    logger.info(f"Found potential API endpoint: {matches[0]}")
                    return matches[0]
            
            # Try common Workday API patterns
            possible_endpoints = [
                "https://nvidia.wd5.myworkdayjobs.com/wday/cxs/nvidia/NVIDIAExternalCareerSite/jobs",
                "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite/jobs",
                "https://nvidia.wd5.myworkdayjobs.com/api/NVIDIAExternalCareerSite/jobs"
            ]
            
            for endpoint in possible_endpoints:
                try:
                    test_response = self.session.get(endpoint, timeout=5)
                    if test_response.status_code == 200:
                        logger.info(f"Found working API endpoint: {endpoint}")
                        return endpoint
                except:
                    continue
                    
        except Exception as e:
            logger.error(f"Error finding API endpoint: {e}")
        
        return None
    
    def get_jobs_via_api(self) -> List[dict]:
        """Try to get jobs via API calls"""
        api_endpoint = self.find_workday_api_endpoint()
        if not api_endpoint:
            logger.warning("Could not find API endpoint")
            return []
        
        try:
            # Try different API request formats
            search_params = {
                'q': 'Student',
                'limit': 50,
                'offset': 0
            }
            
            response = self.session.get(api_endpoint, params=search_params)
            
            if response.status_code == 200:
                data = response.json()
                jobs = []
                
                # Parse the response (structure may vary)
                if 'jobPostings' in data:
                    job_list = data['jobPostings']
                elif 'jobs' in data:
                    job_list = data['jobs']
                elif isinstance(data, list):
                    job_list = data
                else:
                    logger.warning("Unknown API response structure")
                    return []
                
                for job in job_list:
                    title = job.get('title', '') or job.get('jobTitle', '')
                    if title and 'student' in title.lower():
                        jobs.append({
                            'title': title,
                            'link': job.get('link', '') or job.get('url', ''),
                            'timestamp': datetime.now().isoformat()
                        })
                
                logger.info(f"Found {len(jobs)} jobs via API")
                return jobs
                
        except Exception as e:
            logger.error(f"Error getting jobs via API: {e}")
        
        return []
    
    def get_jobs_via_rss(self) -> List[dict]:
        """Try to find and use RSS feeds"""
        rss_urls = [
            "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite/jobs.rss",
            "https://nvidia.wd5.myworkdayjobs.com/rss/NVIDIAExternalCareerSite",
        ]
        
        for rss_url in rss_urls:
            try:
                response = self.session.get(rss_url)
                if response.status_code == 200 and 'xml' in response.headers.get('content-type', ''):
                    # Parse RSS (would need feedparser library)
                    logger.info("Found RSS feed - you could use feedparser to parse this")
                    # For now, just check if it exists
                    return []
            except:
                continue
        
        return []
    
    def get_current_jobs(self) -> List[dict]:
        """Try multiple methods to get current job listings"""
        # Try API first
        jobs = self.get_jobs_via_api()
        if jobs:
            return jobs
        
        # Try RSS
        jobs = self.get_jobs_via_rss()
        if jobs:
            return jobs
        
        # If all else fails, suggest manual URL approach
        logger.warning("Could not automatically scrape jobs. Consider using the Selenium version or manual checking.")
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
        logger.info("Starting job check (simple version)...")
        
        current_jobs = self.get_current_jobs()
        if not current_jobs:
            logger.warning("No jobs found with simple scraping methods")
            return
        
        previous_job_titles = self.load_previous_jobs()
        current_job_titles = set(job['title'] for job in current_jobs)
        new_job_titles = current_job_titles - previous_job_titles
        
        if new_job_titles:
            logger.info(f"Found {len(new_job_titles)} new job(s)!")
            for job in current_jobs:
                if job['title'] in new_job_titles:
                    message = f"🚨 New NVIDIA Job: {job['title']}\n{job.get('link', 'Check NVIDIA careers page')}"
                    self.send_telegram_notification(message)
        else:
            logger.info("No new jobs found")
        
        self.save_current_jobs(current_jobs)


def main():
    if not BOT_TOKEN or not CHAT_ID:
        logger.error("Please set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables")
        return
    
    hunter = SimpleNvidiaJobHunter()
    hunter.check_for_new_jobs()


if __name__ == "__main__":
    main()