#!/usr/bin/env python3
"""
LedgerLite Launcher Script

This script provides an easy way to run LedgerLite without needing to remember
the module path or activate virtual environments manually.

Usage:
    python run_ledgerlite.py

Or make it executable and run directly:
    chmod +x run_ledgerlite.py
    ./run_ledgerlite.py
"""

import sys
import os
from pathlib import Path

def main():
    """Main launcher function."""
    print("🚀 Starting LedgerLite...")
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent.absolute()
    
    # Change to the project directory
    os.chdir(script_dir)
    
    # Add the project root to Python path
    sys.path.insert(0, str(script_dir))
    
    try:
        # Import and run the main application
        from ledgerlite.app.main import main as app_main
        
        print("✅ LedgerLite loaded successfully!")
        print("📱 Opening application window...")
        
        # Run the application
        exit_code = app_main()
        
        print("👋 LedgerLite closed.")
        sys.exit(exit_code)
        
    except ImportError as e:
        print(f"❌ Error: Could not import LedgerLite modules.")
        print(f"   Details: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Make sure you're in the correct directory")
        print("   2. Install dependencies: pip install -e .")
        print("   3. Check that all required packages are installed")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Error: Failed to start LedgerLite.")
        print(f"   Details: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Check that the database is properly initialized")
        print("   2. Make sure all dependencies are installed")
        print("   3. Try running: python -m ledgerlite.app.main")
        sys.exit(1)

if __name__ == "__main__":
    main()


