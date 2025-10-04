#!/usr/bin/env python3
"""
Test AI Analysis Functionality
Forces a run to test the AI vision analysis
"""

import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from jobHunt_screenshot import check_company_jobs, COMPANIES, logger, ai_analyzer
    
    def test_ai_analysis():
        """Test AI analysis on existing screenshots"""
        print("🤖 Testing AI Analysis Functionality")
        print("=" * 50)
        
        if not ai_analyzer or not ai_analyzer.is_enabled():
            print("❌ AI analyzer not available")
            return
            
        print("✅ AI analyzer is enabled")
        
        # Test with existing screenshots if available
        for company_name, company_config in COMPANIES.items():
            screenshot_file = company_config["screenshot_file"]
            
            if os.path.exists(screenshot_file):
                print(f"\n📸 Testing {company_name} screenshot analysis...")
                
                try:
                    # Load screenshot
                    with open(screenshot_file, 'r') as f:
                        screenshot_b64 = f.read().strip()
                    
                    # Convert to bytes for AI analysis
                    import base64
                    image_bytes = base64.b64decode(screenshot_b64)
                    
                    # Analyze single screenshot
                    result = ai_analyzer.analyze_single_screenshot(
                        image_bytes, company_name, is_baseline=False
                    )
                    
                    print(f"  📊 Job count: {result.get('job_count', 'Unknown')}")
                    print(f"  📝 Description: {result.get('description', 'No description')}")
                    print(f"  🏷️  Categories: {result.get('categories', [])}")
                    
                except Exception as e:
                    print(f"  ❌ Error analyzing {company_name}: {e}")
            else:
                print(f"⏭️  {company_name} screenshot not found, skipping...")
        
        print(f"\n🎯 AI analysis test completed!")

    if __name__ == '__main__':
        test_ai_analysis()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all dependencies are installed")