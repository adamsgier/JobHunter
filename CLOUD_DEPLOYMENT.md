# NVIDIA Job Hunter - Cloud Deployment Guide

## 🚀 **GitHub Actions Setup (FREE & RECOMMENDED)**

I've created everything you need to run this in the cloud for free using GitHub Actions!

### **What's Included:**
- ✅ GitHub Actions workflow (`.github/workflows/job-hunter.yml`)
- ✅ Cloud-optimized script (`jobHunt_github.py`)
- ✅ Runs every hour automatically
- ✅ 100% free (2000 minutes/month limit)

### **Setup Steps:**

#### 1. **Create GitHub Repository**
```bash
cd /home/user/nvidia-job-hunter

# Initialize git repo
git init
git add .
git commit -m "Initial NVIDIA Job Hunter setup"

# Create a new repository on GitHub.com, then:
git remote add origin https://github.com/YOUR_USERNAME/nvidia-job-hunter.git
git push -u origin main
```

#### 2. **Add Telegram Secrets to GitHub**
1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** and add:
   - **Name**: `TELEGRAM_BOT_TOKEN` **Value**: `***REMOVED***`
   - **Name**: `TELEGRAM_CHAT_ID` **Value**: `***REMOVED***`

#### 3. **Enable GitHub Actions**
1. Go to **Actions** tab in your repo
2. Click **"I understand my workflows, go ahead and enable them"**
3. The job hunter will start running automatically every hour!

#### 4. **Test Manually (Optional)**
- Go to **Actions** tab → **NVIDIA Job Hunter** workflow
- Click **Run workflow** → **Run workflow** to test immediately

---

## 🎯 **How It Works**

1. **Runs every hour** via GitHub Actions cron schedule
2. **Checks NVIDIA jobs page** for content changes
3. **Sends Telegram notification** when page updates
4. **Tracks state** in repository files
5. **Completely free** - no credit card required

---

## 🔧 **Alternative: Railway Deployment**

If you prefer Railway (500 free hours/month):

### Setup:
1. Sign up at [railway.app](https://railway.app)
2. Connect your GitHub repository
3. Add environment variables:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
4. Deploy with one click

### Railway Configuration File:
```json
{
  "name": "nvidia-job-hunter",
  "build": {
    "commands": ["pip install -r requirements.txt"]
  },
  "deploy": {
    "startCommand": "python scheduler.py"
  }
}
```

---

## 🛠 **Oracle Cloud Always Free VM**

For advanced users who want a full Linux VM:

### Benefits:
- Always free forever
- Full control over environment
- Can run multiple applications

### Setup:
1. Sign up for Oracle Cloud
2. Create Always Free VM instance
3. Install Python and dependencies
4. Upload your scripts
5. Set up cron job

---

## 📊 **Comparison**

| Service | Cost | Complexity | Reliability | Recommended |
|---------|------|------------|-------------|-------------|
| **GitHub Actions** | Free | Easy | High | ✅ **YES** |
| Railway | 500h free | Easy | High | Good backup |
| Oracle Cloud | Free VM | Medium | High | For advanced users |
| Heroku | Limited free | Easy | Medium | Not recommended |

---

## 🚨 **Important Notes**

1. **GitHub Actions is perfect** for scheduled tasks like this
2. **No server maintenance** required
3. **Automatic updates** when you push code changes
4. **Built-in logging** and error tracking
5. **Can easily modify** schedule or add features

---

## ✅ **Ready to Deploy?**

Follow the GitHub Actions setup above - it's the easiest and most reliable option!