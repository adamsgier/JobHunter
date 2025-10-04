#!/usr/bin/env python3
"""
Check Available Gemini Models
"""

import os
from dotenv import load_dotenv

load_dotenv()

try:
    import google.generativeai as genai
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ No GEMINI_API_KEY found")
        exit(1)
    
    genai.configure(api_key=api_key)
    
    print("📋 Available Gemini Models:")
    print("=" * 40)
    
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"✅ {model.name}")
        else:
            print(f"⚪ {model.name} (no generateContent)")
            
except Exception as e:
    print(f"❌ Error: {e}")