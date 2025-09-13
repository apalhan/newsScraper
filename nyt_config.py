"""
NYT API Configuration
Get your API key from: https://developer.nytimes.com/
"""

import os

# NYT API Configuration
NYT_API_KEY = os.getenv('NYT_API_KEY', 'm9mGWBTgfKJ1F0Zb9X1d9TDLyurgQIAI')

# API Settings
NYT_API_BASE_URL = "https://api.nytimes.com/svc"
NYT_RSS_BASE_URL = "https://rss.nytimes.com/services/xml/rss/nyt"

# Rate limiting settings
API_REQUEST_DELAY = 1  # seconds between requests
MAX_PAGES_DEFAULT = 3
MAX_ARTICLES_DEFAULT = 15

# Cooking-related keywords for filtering
COOKING_KEYWORDS = [
    "cooking", "recipe", "food", "chef", "restaurant", 
    "dining", "kitchen", "cuisine", "ingredient", "meal"
]
