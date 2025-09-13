#!/usr/bin/env python3
"""
Simple Setup Script - Configure API key from existing config
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

try:
    from nyt_config import NYT_API_KEY
    from simple_secrets import secrets
    
    print("🔧 Simple API Setup")
    print("=" * 25)
    
    if NYT_API_KEY and len(NYT_API_KEY) > 10:
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
            print("\nNext steps:")
            print("1. Your Flask app is already running at http://localhost:8080")
            print("2. Try the new API endpoints:")
            print("   - POST /api/scrape-nyt-api")
            print("   - POST /api/scrape-all")
        else:
            print(f"❌ API test failed: {result.get('error', 'Unknown error')}")
    else:
        print("❌ No valid API key found in nyt_config.py")
        print("Please check your API key configuration")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please install dependencies: pip install -r requirements.txt")
except Exception as e:
    print(f"❌ Setup error: {e}")
