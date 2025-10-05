# Security & Privacy Policy

## 🔒 **Data Protection**

This project is designed with privacy and security as core principles:

### **What Data We Handle**
- ✅ **Public job listings** - Only monitors publicly available job postings
- ✅ **Screenshots** - Temporary images stored locally/cache only
- ✅ **Change detection metadata** - Timestamps and hash comparisons
- ❌ **No personal data** - No user profiles, resumes, or personal information
- ❌ **No tracking** - No analytics, cookies, or user behavior monitoring

### **Where Data is Stored**
- **Local Development**: Screenshots and state files in your local directory
- **GitHub Actions**: Temporary cache (auto-deleted after 7 days)
- **No External Services**: Data never leaves your control

## 🔑 **API Key Security**

### **Required API Keys**
1. **Telegram Bot Token** - For notifications only
2. **Google Gemini API Key** - For AI analysis (optional)

### **Security Best Practices**
- ✅ **Environment Variables**: All keys stored as env vars, never hardcoded
- ✅ **GitHub Secrets**: Encrypted storage for CI/CD
- ✅ **Minimal Permissions**: Keys have read-only access where possible
- ✅ **Rate Limited**: Respects all service rate limits

### **Key Rotation**
- Rotate API keys monthly for best security
- Monitor usage in respective dashboards
- Disable keys immediately if compromised

## 🛡️ **Repository Security**

### **Safe to Fork/Star**
- ✅ **No secrets in code** - All sensitive data in env vars
- ✅ **Template files only** - `.env.example` contains safe templates
- ✅ **Proper .gitignore** - Excludes all sensitive files

### **Before Contributing**
- Never commit real API keys or tokens
- Use `.env.example` for documentation
- Test with dummy/development keys only

## 🌐 **External Service Compliance**

### **Websites Monitored**
- **NVIDIA Careers**: Public job listings only
- **Intel Careers**: Public job listings only
- **Rate Limiting**: Respectful crawling with delays
- **robots.txt**: Compliant with site policies

### **API Services Used**
- **Telegram Bot API**: Official API, no user data shared
- **Google Gemini API**: Images processed, not stored
- **GitHub Actions**: Standard CI/CD, follows GitHub ToS

## ⚖️ **Legal Considerations**

### **Terms of Service**
- Monitors only publicly available job listings
- Respects website rate limits and robots.txt
- No circumvention of access controls
- Educational/personal use only

### **Data Protection (GDPR/CCPA)**
- No personal data collection
- No cookies or tracking
- Users control all their data
- Easy to delete (just remove repository)

### **Liability**
- Use at your own risk
- No warranty or guarantee of service
- Users responsible for compliance with local laws

## 🚨 **Security Reporting**

Found a security issue? Please report responsibly:

1. **Don't** create public issues for security problems
2. **Do** contact the maintainer directly
3. **Include** clear reproduction steps
4. **Allow** time for fixes before disclosure

## 🔍 **Transparency**

### **What This Code Does**
- Takes screenshots of job listing pages
- Compares images to detect changes
- Uses AI to filter out irrelevant changes
- Sends notifications via Telegram
- Caches state between runs

### **What This Code Doesn't Do**
- Collect personal information
- Store user data externally
- Track usage or analytics
- Access private/protected content
- Circumvent security measures

## ✅ **Security Checklist for Users**

Before using this project:

- [ ] Create dedicated Telegram bot (don't reuse existing)
- [ ] Use environment variables for all keys
- [ ] Enable 2FA on all service accounts
- [ ] Review code before running locally
- [ ] Monitor API usage in dashboards
- [ ] Set up repository secrets properly
- [ ] Keep dependencies updated

## 🔄 **Regular Security Maintenance**

### **Monthly Tasks**
- Rotate API keys
- Review GitHub Actions logs
- Update dependencies
- Check for security advisories

### **Automated Security**
- GitHub Dependabot enabled for dependency updates
- GitHub Security Advisories monitoring
- Automated secret scanning (GitHub native)

---

**This project prioritizes your privacy and security. All design decisions favor keeping your data under your control.**