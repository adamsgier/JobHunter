#!/usr/bin/env python3
"""
Test script for the screenshot-based job hunter
Run this locally to test the screenshot functionality
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from jobHunt_screenshot import main, COMPANIES, logger

def test_screenshot_functionality():
    """Test the screenshot functionality locally"""
    
    print("🧪 Testing Screenshot-Based Job Hunter")
    print("=" * 50)
    
    # Check environment
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        print("❌ Missing Telegram credentials in .env file")
        print("Please copy .env.example to .env and fill in your values")
        return False
    
    print(f"✅ Telegram bot configured")
    print(f"✅ Monitoring {len(COMPANIES)} companies")
    
    # Check AI configuration
    gemini_key = os.getenv("GEMINI_API_KEY")
    use_ai = os.getenv("USE_AI_ANALYSIS", "true").lower() == "true"
    
    if gemini_key and use_ai:
        print(f"🤖 Google Gemini AI enabled")
    elif use_ai:
        print(f"⚠️  AI analysis requested but no API key provided")
    else:
        print(f"📊 Using pixel-based comparison only")
    
    # Set test environment variables
    os.environ["SAVE_DEBUG_IMAGES"] = "true"
    os.environ["CHANGE_THRESHOLD"] = "0.5"
    
    print(f"🎯 Change threshold: {os.getenv('CHANGE_THRESHOLD')}%")
    print(f"🖼️  Debug images: {os.getenv('SAVE_DEBUG_IMAGES')}")
    
    try:
        # Run the main function
        main()
        print("\n✅ Test completed successfully!")
        return True
        
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        logger.error(f"Test error: {e}")
        return False

if __name__ == "__main__":
    success = test_screenshot_functionality()
    sys.exit(0 if success else 1)