#!/usr/bin/env python3
"""
NYT API Setup Script
Interactive setup for API keys and configuration
"""

import sys
import os
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from secrets_manager import setup_api_keys, secrets
from nyt_api_client import NYTAPIClient

def test_api_connection():
    """Test the NYT API connection"""
    print("\n🧪 Testing NYT API Connection...")
    
    if not secrets.is_configured('nyt_api_key'):
        print("❌ NYT API key not configured. Please run setup first.")
        return False
    
    try:
        client = NYTAPIClient()
        result = client.search_articles(query="cooking", page=0)
        
        if "error" in result:
            print(f"❌ API Error: {result['error']}")
            return False
        elif "response" in result:
            docs = result["response"].get("docs", [])
            print(f"✅ API Connection successful! Found {len(docs)} articles.")
            return True
        else:
            print("❌ Unexpected API response format")
            return False
            
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def create_gitignore():
    """Create .gitignore file to protect secrets"""
    gitignore_content = """# Secrets and API keys
nyt_secrets.json
.secret_key
*.key

# Environment files
.env
.env.local
.env.production

# Database files
*.db
*.sqlite
*.sqlite3

# Python cache
__pycache__/
*.pyc
*.pyo
*.pyd
.Python

# Virtual environment
venv/
env/
ENV/

# IDE files
.vscode/
.idea/
*.swp
*.swo

# OS files
.DS_Store
Thumbs.db
"""
    
    gitignore_path = Path(".gitignore")
    if not gitignore_path.exists():
        with open(gitignore_path, 'w') as f:
            f.write(gitignore_content)
        print("✅ Created .gitignore file to protect secrets")
    else:
        print("ℹ️  .gitignore already exists")

def main():
    """Main setup function"""
    print("🚀 NYT Cooking Scraper - API Setup")
    print("=" * 50)
    
    # Create .gitignore to protect secrets
    create_gitignore()
    
    # Interactive API key setup
    setup_api_keys()
    
    # Test API connection
    if test_api_connection():
        print("\n🎉 Setup complete! Your NYT API is ready to use.")
        print("\nNext steps:")
        print("1. Run: python app.py")
        print("2. Visit: http://localhost:8080")
        print("3. Use the new API endpoints for reliable data collection")
    else:
        print("\n❌ Setup incomplete. Please check your API key and try again.")
        print("Get your free API key from: https://developer.nytimes.com/")

if __name__ == "__main__":
    main()
