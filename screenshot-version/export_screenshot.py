#!/usr/bin/env python3
"""
Export Screenshot Tool
Converts base64 screenshots to viewable PNG images
"""

import base64
import os
import sys
from datetime import datetime

def export_screenshot(screenshot_file, output_name=None):
    """Export base64 screenshot to PNG file"""
    if not os.path.exists(screenshot_file):
        print(f"❌ Screenshot file not found: {screenshot_file}")
        return False
    
    try:
        # Read base64 data
        with open(screenshot_file, 'r') as f:
            base64_data = f.read().strip()
        
        # Decode base64 to image data
        image_data = base64.b64decode(base64_data)
        
        # Generate output filename if not provided
        if not output_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            company = os.path.basename(screenshot_file).replace('_screenshot.txt', '')
            output_name = f"{company}_screenshot_{timestamp}.png"
        
        # Save as PNG
        with open(output_name, 'wb') as f:
            f.write(image_data)
        
        file_size = len(image_data) / 1024  # KB
        print(f"✅ Screenshot exported: {output_name} ({file_size:.1f}KB)")
        return True
        
    except Exception as e:
        print(f"❌ Error exporting screenshot: {e}")
        return False

def main():
    """Export all available screenshots"""
    print("🖼️  Screenshot Export Tool")
    print("=" * 40)
    
    # List of possible screenshot files
    screenshot_files = [
        'nvidia_screenshot.txt',
        'intel_screenshot.txt'
    ]
    
    exported_count = 0
    
    # Export each available screenshot
    for screenshot_file in screenshot_files:
        if os.path.exists(screenshot_file):
            company = screenshot_file.replace('_screenshot.txt', '').upper()
            print(f"\n📸 Exporting {company} screenshot...")
            if export_screenshot(screenshot_file):
                exported_count += 1
        else:
            company = screenshot_file.replace('_screenshot.txt', '').upper()
            print(f"⏭️  {company} screenshot not found, skipping...")
    
    print(f"\n📊 Summary: {exported_count} screenshots exported")
    
    if exported_count > 0:
        print("\n💡 Tips:")
        print("   - Use any image viewer to open the PNG files")
        print("   - In WSL, you can use: explorer.exe . (to open current folder)")
        print("   - Or copy files to Windows: cp *.png /mnt/c/Users/YourName/Desktop/")

if __name__ == '__main__':
    main()