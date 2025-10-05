# Contributing to AI-Enhanced Job Hunter

Thank you for your interest in contributing! This project welcomes contributions from developers of all skill levels.

## 🚀 **Quick Start for Contributors**

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Test** your changes locally
4. **Commit** with clear messages: `git commit -m 'Add amazing feature'`
5. **Push** to your fork: `git push origin feature/amazing-feature`
6. **Submit** a Pull Request

## 🎯 **Areas for Contribution**

### **🤖 AI & Machine Learning**
- Alternative AI models (Claude, OpenAI, Llama)
- Improved prompt engineering
- Job categorization and filtering
- Sentiment analysis of job descriptions

### **🏢 Company Integrations**
- Additional job sites (Google, Apple, Microsoft, etc.)
- LinkedIn API integration
- Indeed/Glassdoor scrapers
- University career portals

### **🔧 Technical Improvements**
- Performance optimizations
- Better error handling
- Database integration (SQLite, PostgreSQL)
- Docker containerization

### **📱 User Interface**
- Web dashboard for monitoring
- Mobile app integration
- Slack/Discord bot adapters
- REST API for external integrations

### **📊 Analytics & Reporting**
- Job market trend analysis
- Success rate tracking
- Performance metrics dashboard
- Historical data visualization

## 🛠️ **Development Setup**

### **Local Environment**
```bash
# Clone your fork
git clone https://github.com/yourusername/NvidiaJobHunter.git
cd NvidiaJobHunter

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
cd screenshot-version
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your API keys
```

### **Testing Setup**
```bash
# Test basic functionality
python jobHunt_screenshot.py

# Test AI features (requires GEMINI_API_KEY)
export GEMINI_API_KEY=your_key_here
python -c "from ai_vision import create_ai_analyzer; print('AI module working!')"

# Test GitHub Actions locally (optional)
# Install act: https://github.com/nektos/act
act workflow_dispatch
```

## 📝 **Code Style Guidelines**

### **Python Standards**
- Follow PEP 8 style guide
- Use type hints where helpful
- Add docstrings for functions/classes
- Keep functions focused and small

### **Example Code Style**
```python
def analyze_job_changes(
    old_screenshot: bytes, 
    new_screenshot: bytes,
    company_name: str
) -> Dict[str, Any]:
    """
    Analyze differences between job listing screenshots.
    
    Args:
        old_screenshot: Previous screenshot as bytes
        new_screenshot: Current screenshot as bytes  
        company_name: Name of company being monitored
        
    Returns:
        Dictionary with analysis results and metadata
    """
    # Implementation here
    pass
```

### **Documentation Standards**
- Clear, concise comments
- Update README for new features
- Include examples in docstrings
- Document any new environment variables

## 🧪 **Testing Requirements**

### **Before Submitting PRs**
- [ ] Code runs without errors locally
- [ ] New features include basic error handling
- [ ] No hardcoded credentials or secrets
- [ ] Documentation updated for new features
- [ ] Existing functionality still works

### **Recommended Testing**
```bash
# Test different scenarios
python jobHunt_screenshot.py  # Normal run
export USE_AI_ANALYSIS=false && python jobHunt_screenshot.py  # Without AI
export SAVE_DEBUG_IMAGES=true && python jobHunt_screenshot.py  # With debug
```

## 🔒 **Security Guidelines**

### **Critical Rules**
- ❌ **Never commit real API keys or tokens**
- ❌ **Don't hardcode any credentials**
- ❌ **Avoid storing sensitive data in plain text**
- ✅ **Always use environment variables**
- ✅ **Test with dummy/development keys**
- ✅ **Follow principle of least privilege**

### **Security Checklist for PRs**
- [ ] No secrets in code or commits
- [ ] New dependencies are from trusted sources
- [ ] Error messages don't leak sensitive info
- [ ] Input validation for user-provided data
- [ ] Proper handling of API responses

## 📋 **Pull Request Process**

### **PR Description Template**
```markdown
## 🎯 **What This PR Does**
Brief description of changes

## 🔧 **Type of Change**
- [ ] Bug fix
- [ ] New feature  
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## 🧪 **Testing Done**
- [ ] Tested locally
- [ ] Verified existing features work
- [ ] Added error handling
- [ ] Updated documentation

## 📝 **Additional Notes**
Any special considerations or breaking changes
```

### **Review Process**
1. **Automated Checks**: GitHub Actions will test your PR
2. **Code Review**: Maintainer will review code quality
3. **Testing**: Verify functionality works as expected
4. **Documentation**: Ensure docs are updated
5. **Merge**: PR merged after approval

## 🌟 **Feature Request Process**

### **Before Starting Large Features**
1. **Open an Issue** to discuss the feature
2. **Get Feedback** from maintainers
3. **Plan Implementation** approach
4. **Start Development** once aligned

### **Good Feature Ideas**
- **Company-specific filters** (internships, remote, etc.)
- **Advanced notification templates**
- **Integration with calendar apps**
- **Job application tracking**
- **Market trend analysis**

## 🐛 **Bug Report Guidelines**

### **Include in Bug Reports**
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Relevant log output (sanitized of secrets)
- Screenshots if UI-related

### **Bug Report Template**
```markdown
**Describe the bug**
Clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. See error

**Expected behavior**
What you expected to happen.

**Environment**
- OS: [e.g. Ubuntu 22.04]
- Python: [e.g. 3.11.5]
- Version: [commit hash or release]

**Logs**
```
Paste relevant logs here (remove any API keys!)
```
```

## 🏆 **Recognition**

Contributors will be:
- Listed in README contributors section
- Credited in release notes for major contributions
- Given co-maintainer status for significant ongoing contributions

## 📞 **Getting Help**

### **Questions About Contributing**
- Open a Discussion on GitHub
- Check existing Issues and PRs
- Review documentation thoroughly first

### **Stuck on Implementation**
- Describe what you're trying to achieve
- Show what you've tried so far  
- Ask specific questions rather than general "how do I..."

---

**Thank you for helping make job hunting more efficient for everyone!** 🎉