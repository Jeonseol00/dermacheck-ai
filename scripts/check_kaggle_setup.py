#!/usr/bin/env python3
"""
Quick checker to verify Kaggle API is setup correctly
"""

import os
from pathlib import Path
import subprocess

def check_kaggle_cli():
    """Check if kaggle CLI is installed"""
    try:
        result = subprocess.run(['kaggle', '--version'], 
                              capture_output=True, text=True, timeout=5)
        print(f"✅ Kaggle CLI installed: {result.stdout.strip()}")
        return True
    except FileNotFoundError:
        print("❌ Kaggle CLI not installed!")
        print("   Install: pip install kaggle")
        return False
    except Exception as e:
        print(f"❌ Error checking Kaggle CLI: {e}")
        return False

def check_api_token():
    """Check if API token is configured"""
    token_path = Path.home() / ".kaggle" / "kaggle.json"
    
    if not token_path.exists():
        print("❌ Kaggle API token NOT found!")
        print("\n📝 Setup Steps:")
        print("1. Go to: https://www.kaggle.com/account")
        print("2. Scroll to 'API' section")
        print("3. Click 'Create New Token'")
        print("4. Download kaggle.json")
        print("5. Run these commands:")
        print("   mkdir -p ~/.kaggle")
        print("   mv ~/Downloads/kaggle.json ~/.kaggle/")
        print("   chmod 600 ~/.kaggle/kaggle.json")
        return False
    
    # Check permissions
    perms = oct(token_path.stat().st_mode)[-3:]
    if perms != '600':
        print(f"⚠️ Token permissions incorrect: {perms}")
        print("   Fix: chmod 600 ~/.kaggle/kaggle.json")
        return False
    
    print(f"✅ API token configured: {token_path}")
    return True

def test_api_connection():
    """Test API connection by listing datasets"""
    try:
        result = subprocess.run(['kaggle', 'datasets', 'list', '-s', 'skin'],
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ API connection working!")
            return True
        else:
            print(f"❌ API error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def main():
    print("🔍 Kaggle API Setup Checker\n")
    
    cli_ok = check_kaggle_cli()
    token_ok = check_api_token()
    
    if cli_ok and token_ok:
        print("\n🔌 Testing connection...")
        connection_ok = test_api_connection()
        
        if connection_ok:
            print("\n✅ ALL CHECKS PASSED!")
            print("\n🚀 Ready to download! Run:")
            print("   ./scripts/download_all_datasets.sh")
            return True
    
    print("\n❌ Setup incomplete. Fix issues above first.")
    return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
