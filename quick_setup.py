#!/usr/bin/env python3
"""
Quick Setup Script - Uses existing API key from nyt_config.py
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

try:
    from nyt_config import NYT_API_KEY
    from secrets_manager import secrets
    
    print("🔧 Quick API Setup")
    print("=" * 30)
    
    if NYT_API_KEY and NYT_API_KEY != 'your_nyt_api_key_here':
        # Use existing API key from config
        secrets.set_secret('nyt_api_key', NYT_API_KEY, save=True)
        print(f"✅ Using existing API key: {NYT_API_KEY[:10]}...")
        print("✅ API key saved to secure storage")
        
        # Test connection
        from nyt_api_client import NYTAPIClient
        client = NYTAPIClient()
        result = client.search_articles(query="cooking", page=0)
        
        if "error" not in result:
            print("✅ API connection test successful!")
            print("🎉 Setup complete! Your NYT API is ready to use.")
        else:
            print(f"❌ API test failed: {result.get('error', 'Unknown error')}")
    else:
        print("❌ No valid API key found in nyt_config.py")
        print("Please run: python setup_api.py")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please install dependencies: pip install -r requirements.txt")
except Exception as e:
    print(f"❌ Setup error: {e}")
