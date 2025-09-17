# NVIDIA Job Hunter - Setup Guide

## Issues with Your Original Script

1. **Dynamic Content**: Workday jobs sites load content with JavaScript, so `requests` + `BeautifulSoup` can't see the actual job listings
2. **Wrong CSS Selector**: The class `css-1142bqn` doesn't exist on the page
3. **Security**: Bot token should not be hardcoded in the script
4. **Logic Bug**: The script overwrites jobs.txt with HTML instead of job titles

## Solutions Provided

### ✅ Option 1: Final Working Solution (Recommended)
- **File**: `jobHunt_final.py`
- **Pros**: Detects page changes, works reliably, comprehensive
- **Method**: Monitors page content changes using hash comparison

### Option 2: Selenium-based Script
- **File**: `jobHunt_improved.py`
- **Pros**: Can handle JavaScript-rendered content
- **Cons**: Requires Chrome/Chromium browser, may be blocked

### Option 3: RSS/API-based Script
- **File**: `jobHunt_rss.py`
- **Pros**: Faster, no browser required
- **Cons**: NVIDIA's RSS doesn't work properly

## Quick Start (Recommended)

1. **Install dependencies**:
   ```bash
   pip install requests python-dotenv
   ```

2. **Configure Telegram** (copy your existing values to `.env`):
   ```bash
   echo "TELEGRAM_BOT_TOKEN=***REMOVED***" > .env
   echo "TELEGRAM_CHAT_ID=***REMOVED***" >> .env
   ```

3. **Test the script**:
   ```bash
   python3 jobHunt_final.py
   ```

4. **Run continuously**:
   ```bash
   # Option A: Use scheduler script
   python3 scheduler.py
   
   # Option B: Set up cron job
   crontab -e
   # Add: 0 * * * * cd /home/user && python3 jobHunt_final.py
   ```

## How It Works

The final solution monitors the NVIDIA jobs page by:
1. **Hash Comparison**: Creates a hash of the page content and compares it to previous runs
2. **Change Detection**: If the page content changes, it sends a Telegram notification
3. **Reliable Monitoring**: Works even when direct job scraping fails due to JavaScript/anti-bot measures

## Setup Instructions

### 1. Install Dependencies

```bash
# Install Python packages
pip install selenium python-dotenv requests beautifulsoup4

# For Selenium version, install Chrome/Chromium
sudo apt-get update
sudo apt-get install chromium-browser chromium-chromedriver
```

### 2. Configure Environment Variables

1. Copy `.env.example` to `.env`
2. Get your Telegram bot token:
   - Message @BotFather on Telegram
   - Create a new bot with `/newbot`
   - Copy the token
3. Get your chat ID:
   - Message @userinfobot on Telegram
   - Copy your chat ID
4. Update `.env` file with your values

### 3. Test the Script

```bash
# Test the improved version
python3 jobHunt_improved.py

# Or test the simple version
python3 jobHunt_simple.py
```

### 4. Set up Automatic Running

Create a cron job to run the script periodically:

```bash
# Edit crontab
crontab -e

# Add line to run every hour
0 * * * * cd /home/user && /home/user/.venv/bin/python jobHunt_improved.py

# Or every 30 minutes
*/30 * * * * cd /home/user && /home/user/.venv/bin/python jobHunt_improved.py
```

## Alternative Approaches

If the scripts don't work due to NVIDIA's anti-bot measures:

### 1. RSS Feeds
Check if NVIDIA provides RSS feeds:
- `https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite/jobs.rss`

### 2. LinkedIn Job Alerts
- Set up LinkedIn job alerts for NVIDIA student positions
- Use IFTTT to forward LinkedIn emails to Telegram

### 3. Manual URL Monitoring
- Create a simple script that checks if the URL returns different content
- Less precise but harder to block

### 4. Third-party Job Aggregators
- Monitor sites like Indeed, Glassdoor that aggregate NVIDIA jobs
- Often have better APIs or RSS feeds

## Troubleshooting

### Common Issues:
1. **Selenium fails**: Install `chromium-chromedriver` package
2. **No jobs found**: Website structure may have changed, update selectors
3. **Telegram not working**: Check bot token and chat ID
4. **Rate limiting**: Add delays between requests

### Debug Mode:
Change logging level in the script:
```python
logging.basicConfig(level=logging.DEBUG)
```

## Security Notes

- Never commit your `.env` file to version control
- Use environment variables for sensitive data
- Consider using Telegram bot commands to control the script
- Rotate your bot token periodically

## Legal Considerations

- Respect robots.txt and rate limits
- Don't overload the website with requests
- Consider reaching out to NVIDIA about official job notification APIs