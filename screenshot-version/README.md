# Screenshot-Based Job Hunter

This version uses visual screenshot comparison to detect changes in job listings, making it more reliable than text-based hash comparison.

## Features

- 📸 **Visual Detection**: Takes screenshots and compares them pixel by pixel
- 🤖 **AI-Enhanced Analysis**: Google Gemini Flash provides intelligent change analysis (optional)
- 🎯 **Smart Targeting**: Focuses on job listing areas when possible
- 🔍 **Hybrid Detection**: Combines pixel comparison with AI understanding
- 📊 **Adjustable Sensitivity**: Configurable change threshold
- 🐛 **Debug Support**: Can save difference images for analysis
- 🚀 **Multi-Company**: Monitors both NVIDIA and Intel simultaneously
- ⏰ **Reliable Scheduling**: Multiple cron schedules to ensure 30-minute intervals
- 💡 **Context-Aware**: AI understands job-specific changes vs. page animations

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Chrome (for local testing)

**Ubuntu/Debian:**
```bash
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt-get update
sudo apt-get install google-chrome-stable
```

**macOS:**
```bash
brew install --cask google-chrome
```

### 3. Configure Environment

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and fill in your values:
```bash
TELEGRAM_BOT_TOKEN=***REMOVED***
TELEGRAM_CHAT_ID=***REMOVED***

# Optional: AI Enhancement (Recommended)
GEMINI_API_KEY=your_gemini_api_key_here
USE_AI_ANALYSIS=true

# Detection Settings
CHANGE_THRESHOLD=0.5
SAVE_DEBUG_IMAGES=false
```

### 4. Get Gemini API Key (Optional but Recommended)

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a free API key
3. Add it to your `.env` file as `GEMINI_API_KEY`

**Why use AI analysis?**
- 🎯 **Smarter Detection**: Understands job content vs. page animations
- 🚫 **Fewer False Positives**: Ignores timestamps, session IDs, loading states
- 📝 **Detailed Descriptions**: Get explanations of what actually changed
- 💰 **Free Tier**: 1500 requests/day (enough for 31 days of 30-minute checks)

### 4. Test Locally

```bash
python test_screenshot.py
```

## Configuration

### Environment Variables

**Required:**
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
- `TELEGRAM_CHAT_ID`: Your Telegram chat ID

**AI Enhancement (Optional):**
- `GEMINI_API_KEY`: Google Gemini API key for intelligent analysis
- `USE_AI_ANALYSIS`: Enable/disable AI analysis (default: true)

**Detection Settings:**
- `CHANGE_THRESHOLD`: Sensitivity (0.1 = very sensitive, 2.0 = less sensitive)
- `SAVE_DEBUG_IMAGES`: Set to `true` to save difference images
- `SAVE_ALL_DEBUG`: Set to `true` to save images even when no changes

### GitHub Actions Variables

Set these in your repository:

**Secrets:**
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `GEMINI_API_KEY` (optional, for AI analysis)

**Variables (optional):**
- `USE_AI_ANALYSIS` (default: true)
- `CHANGE_THRESHOLD` (default: 0.5)
- `SAVE_DEBUG_IMAGES` (default: false)

## How It Works

### Screenshot Process
1. **Navigate**: Opens each company's job page in headless Chrome
2. **Target**: Tries to find job listing containers for focused screenshots
3. **Capture**: Takes screenshot of job area or full page
4. **Store**: Saves screenshot as base64 in text file

### Comparison Process
1. **Load**: Retrieves previous screenshot from storage
2. **Compare**: Calculates pixel-by-pixel differences
3. **Analyze**: Determines if changes exceed threshold
4. **Verify**: Double-checks changes for stability
5. **Notify**: Sends Telegram alert if significant changes found

### Change Detection
- Compares screenshots using PIL (Python Imaging Library)
- Calculates percentage of changed pixels
- Uses configurable threshold (default 0.5%)
- Handles size differences automatically
- Provides detailed change statistics

### AI-Enhanced Analysis (Google Gemini Flash)

When enabled, the system uses both pixel comparison AND AI analysis:

1. **Pixel Analysis**: Fast detection of visual differences
2. **AI Analysis**: Intelligent understanding of change context
3. **Smart Override**: AI can override pixel decisions when confident
4. **Detailed Reports**: Get explanations like "New software engineer internship position added"

**AI Capabilities:**
- 🎯 **Context Understanding**: Knows the difference between new jobs and page animations
- 🚫 **False Positive Reduction**: Ignores timestamps, session IDs, loading states
- 📝 **Rich Descriptions**: Explains what actually changed in job listings
- 🔍 **Baseline Analysis**: Describes job page content during first run

## Advantages over Hash Method

✅ **Visual Changes**: Detects layout changes, new job cards, visual updates  
✅ **AI Understanding**: Contextual analysis of job-related changes  
✅ **More Reliable**: Less affected by dynamic session IDs and timestamps  
✅ **Comprehensive**: Captures changes that might not appear in raw HTML  
✅ **Debugging**: Can save difference images to see exactly what changed  
✅ **Stable**: Ignores minor text changes that don't affect job listings  

## File Structure

```
screenshot-version/
├── jobHunt_screenshot.py      # Main screenshot hunter script
├── ai_vision.py              # Google Gemini AI analysis module
├── test_screenshot.py         # Local testing script  
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
├── .github/workflows/        # GitHub Actions workflow
└── README.md                # This file
```

## Generated Files

During operation, these files are created:
- `nvidia_screenshot.txt` - NVIDIA page screenshot (base64)
- `intel_screenshot.txt` - Intel page screenshot (base64)  
- `screenshot_jobs_state.json` - State and timing information
- `debug_*_diff_*.png` - Difference images (if debug enabled)

## Scheduling

The workflow runs every 30 minutes with backup schedules:
- `0,30 * * * *` - Primary schedule (every 30 minutes)
- `5,35 * * * *` - Backup (+5 minute offset)
- `10,40 * * * *` - Backup (+10 minute offset)

Includes duplicate prevention to avoid multiple notifications.

## Troubleshooting

### Chrome Issues
If Chrome fails to start, ensure all dependencies are installed:
```bash
sudo apt-get install -y libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libxss1 libasound2
```

### Sensitivity Tuning
- **Too many false positives**: Increase `CHANGE_THRESHOLD` (try 1.0 or 2.0)
- **Missing real changes**: Decrease `CHANGE_THRESHOLD` (try 0.1 or 0.2)
- **Debug changes**: Set `SAVE_DEBUG_IMAGES=true` to see what's changing

### Memory Issues
Screenshots are stored as base64 text (~100-500KB each). If you encounter memory issues:
- Enable debug images to see screenshot sizes
- Consider reducing screenshot quality in the code
- Monitor GitHub Actions cache usage

## Monitoring

The script provides detailed logging:
- Screenshot capture success/failure
- Change detection results with percentages  
- Timing information and duplicate prevention
- Environment detection and configuration
- Error handling and debugging information

Check GitHub Actions logs for detailed execution information.