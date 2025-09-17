#!/usr/bin/env python3
"""
Job Hunter Scheduler
Runs the job hunter at regular intervals
"""

import time
import subprocess
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_job_hunter():
    """Run the job hunter script"""
    try:
        logger.info("Running job hunter...")
        result = subprocess.run([
            '/home/user/.venv/bin/python', 
            '/home/user/jobHunt_final.py'
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            logger.info("Job hunter completed successfully")
        else:
            logger.error(f"Job hunter failed: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        logger.error("Job hunter timed out")
    except Exception as e:
        logger.error(f"Error running job hunter: {e}")

def main():
    """Main scheduler loop"""
    logger.info("Starting job hunter scheduler...")
    
    # Run immediately on start
    run_job_hunter()
    
    # Then run every hour
    while True:
        try:
            time.sleep(3600)  # 1 hour = 3600 seconds
            run_job_hunter()
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            break
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
            time.sleep(60)  # Wait 1 minute before retrying

if __name__ == "__main__":
    main()