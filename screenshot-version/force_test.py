#!/usr/bin/env python3
"""
Force Run Test - Bypass timing restrictions to test AI functionality
"""

import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from jobHunt_screenshot import main, logger
    
    def force_test_run():
        """Force a run by temporarily removing state file"""
        state_file = "screenshot_jobs_state.json"
        
        print("🚀 Force Testing AI-Enhanced Job Hunter")
        print("=" * 50)
        
        # Backup state file if it exists
        backup_file = None
        if os.path.exists(state_file):
            import time
            backup_file = f"{state_file}.backup_{int(time.time())}"
            os.rename(state_file, backup_file)
            print(f"📦 Backed up state to: {backup_file}")
        
        try:
            # Run the main function
            main()
        except Exception as e:
            print(f"❌ Error during test run: {e}")
        finally:
            # Restore backup if we made one
            if backup_file and os.path.exists(backup_file):
                if os.path.exists(state_file):
                    os.remove(state_file)
                os.rename(backup_file, state_file)
                print(f"🔄 Restored original state file")

    if __name__ == '__main__':
        force_test_run()
        
except ImportError as e:
    print(f"❌ Import error: {e}")