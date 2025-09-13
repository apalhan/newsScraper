import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import requests
from simple_secrets import get_nyt_api_key, is_nyt_configured


class NYTAPIClient:
    """New York Times API Client for cooking content"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or get_nyt_api_key()
        self.base_url = "https://api.nytimes.com/svc"
        self.session = requests.Session()
        
        if not self.api_key:
            print("Warning: NYT_API_KEY not found. Please run setup_api_keys() to configure.")
    
    def search_articles(self, query: str = "cooking",
                        begin_date: Optional[str] = None,
                        end_date: Optional[str] = None,
                        page: int = 0,
                        sort: str = "newest") -> Dict:
        """
        Search NYT articles using Article Search API
        
        Args:
            query: Search query (default: "cooking")
            begin_date: Start date in YYYYMMDD format
            end_date: End date in YYYYMMDD format
            page: Page number (0-based)
            sort: Sort order ("newest", "oldest", "relevance")
        """
        if not self.api_key:
            return {"error": "API key not configured"}
        
        url = f"{self.base_url}/search/v2/articlesearch.json"
        
        params = {
            'api-key': self.api_key,
            'q': query,
            'page': page,
            'sort': sort
        }
        
        if begin_date:
            params['begin_date'] = begin_date
        if end_date:
            params['end_date'] = end_date
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"API request failed: {str(e)}"}
    
    def get_archive_articles(self, year: int, month: int) -> Dict:
        """
        Get NYT articles from Archive API
        
        Args:
            year: Year (e.g., 2024)
            month: Month (1-12)
        """
        if not self.api_key:
            return {"error": "API key not configured"}
        
        url = f"{self.base_url}/archive/v1/{year}/{month}.json"
        
        params = {
            'api-key': self.api_key
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Archive API request failed: {str(e)}"}
    
    def get_rss_feed(self, section: str = "food") -> Dict:
        """
        Get NYT RSS feed content
        
        Args:
            section: RSS section (food, dining, etc.)
        """
        rss_url = f"https://rss.nytimes.com/services/xml/rss/nyt/{section}.xml"
        
        try:
            response = self.session.get(rss_url)
            response.raise_for_status()
            return {"success": True, "content": response.text}
        except requests.exceptions.RequestException as e:
            return {"error": f"RSS request failed: {str(e)}"}
    
    def search_cooking_content(self, max_pages: int = 3) -> List[Dict]:
        """
        Search for cooking-related articles and return structured data
        
        Args:
            max_pages: Maximum number of pages to fetch
        """
        articles = []
        
        for page in range(max_pages):
            print(f"Fetching page {page + 1} of cooking articles...")
            
            result = self.search_articles(
                query="cooking OR recipe OR food",
                page=page,
                sort="newest"
            )
            
            if "error" in result:
                print(f"Error on page {page + 1}: {result['error']}")
                break
            
            if "response" in result and "docs" in result["response"]:
                page_articles = result["response"]["docs"]
                articles.extend(page_articles)
                
                # Rate limiting - be respectful
                time.sleep(1)
            else:
                break
        
        return articles
    
    def get_recent_cooking_news(self, days_back: int = 7) -> List[Dict]:
        """
        Get recent cooking news from the last N days
        
        Args:
            days_back: Number of days to look back
        """
        end_date = datetime.now()
        begin_date = end_date - timedelta(days=days_back)
        
        begin_date_str = begin_date.strftime("%Y%m%d")
        end_date_str = end_date.strftime("%Y%m%d")
        
        result = self.search_articles(
            query="cooking news OR food news OR restaurant",
            begin_date=begin_date_str,
            end_date=end_date_str,
            sort="newest"
        )
        
        if "error" in result:
            return []
        
        if "response" in result and "docs" in result["response"]:
            return result["response"]["docs"]
        
        return []
    
    def format_article_for_db(self, article: Dict) -> Dict:
        """
        Format NYT article data for database storage
        
        Args:
            article: Raw article data from NYT API
        """
        return {
            'title': article.get('headline', {}).get('main', ''),
            'url': article.get('web_url', ''),
            'summary': article.get('snippet', ''),
            'content': article.get('lead_paragraph', ''),
            'author': ', '.join([author.get('name', '') for author in article.get('byline', {}).get('person', [])]),
            'published_date': article.get('pub_date', ''),
            'category': 'cooking',
            'image_url': '',
            'scraped_date': datetime.now().isoformat()
        }
