# NVIDIA Job Hunter - Files Overview

## Main Scripts

| File | Description | Status |
|------|-------------|---------|
| `jobHunt_final.py` | ✅ **RECOMMENDED** - Final working solution using page change detection | Working |
| `jobHunt_improved.py` | Selenium-based scraper (requires Chrome) | Alternative |
| `jobHunt_rss.py` | RSS feed-based scraper | Limited (RSS doesn't work) |
| `jobHunt_simple.py` | API endpoint-based scraper | Limited |
| `jobHunt.py` | ❌ Original script (has issues) | Broken |

## Utility Scripts

| File | Description |
|------|-------------|
| `scheduler.py` | Runs job hunter continuously every hour |

## Configuration Files

| File | Description |
|------|-------------|
| `.env` | Environment variables (Telegram credentials) |
| `.env.example` | Template for environment variables |
| `README.md` | Complete setup and usage guide |

## Generated Files

| File | Description |
|------|-------------|
| `jobs.txt` | Job listings from original script |
| `nvidia_jobs_final.json` | Job state from final script |
| `nvidia_page_hash.txt` | Page hash for change detection |
| `*.log` | Log files from script runs |

## Quick Start

```bash
cd /home/user/nvidia-job-hunter

# Test the working solution
python3 jobHunt_final.py

# Run continuously
python3 scheduler.py
```

## Next Steps

1. Set up cron job for automatic running
2. Customize notification messages
3. Add more job sources
4. Implement job filtering by keywords