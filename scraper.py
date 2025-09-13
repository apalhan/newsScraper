import json
import re
import sqlite3
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from nyt_api_client import NYTAPIClient
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


class NYTCookingScraper:
    def __init__(self):
        self.base_url = "https://cooking.nytimes.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.db_path = "cooking_data.db"
        self.nyt_api = NYTAPIClient()  # Initialize NYT API client
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with tables for recipes and news"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create recipes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT UNIQUE,
                description TEXT,
                ingredients TEXT,
                instructions TEXT,
                cooking_time TEXT,
                difficulty TEXT,
                cuisine TEXT,
                tags TEXT,
                image_url TEXT,
                author TEXT,
                published_date TEXT,
                scraped_date TEXT
            )
        ''')
        
        # Create news table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cooking_news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT UNIQUE,
                summary TEXT,
                content TEXT,
                author TEXT,
                published_date TEXT,
                category TEXT,
                image_url TEXT,
                scraped_date TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def setup_selenium(self):
        """Setup Selenium WebDriver with Chrome"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in background
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    
    def scrape_recipes(self, max_pages=5):
        """Scrape recipes from NYT Cooking"""
        print("Starting recipe scraping...")
        driver = self.setup_selenium()
        
        try:
            recipes = []
            for page in range(1, max_pages + 1):
                print(f"Scraping page {page}...")
                
                if page == 1:
                    url = f"{self.base_url}/recipes"
                else:
                    url = f"{self.base_url}/recipes?page={page}"
                
                driver.get(url)
                time.sleep(3)  # Wait for page to load
                
                # Wait for recipe cards to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='recipe-card']"))
                )
                
                # Find all recipe cards
                recipe_cards = driver.find_elements(By.CSS_SELECTOR, "[data-testid='recipe-card']")
                
                for card in recipe_cards:
                    try:
                        recipe_data = self.extract_recipe_data(card, driver)
                        if recipe_data:
                            recipes.append(recipe_data)
                            self.save_recipe_to_db(recipe_data)
                    except Exception as e:
                        print(f"Error extracting recipe: {e}")
                        continue
                
                time.sleep(2)  # Be respectful to the server
                
        except Exception as e:
            print(f"Error during recipe scraping: {e}")
        finally:
            driver.quit()
        
        print(f"Scraped {len(recipes)} recipes")
        return recipes
    
    def extract_recipe_data(self, card, driver):
        """Extract recipe data from a recipe card"""
        try:
            # Get basic info from card
            title_elem = card.find_element(By.CSS_SELECTOR, "h3, h4, [data-testid='recipe-title']")
            title = title_elem.text.strip() if title_elem else "Untitled Recipe"
            
            # Get recipe URL
            link_elem = card.find_element(By.CSS_SELECTOR, "a")
            recipe_url = link_elem.get_attribute("href")
            
            # Get image URL
            img_elem = card.find_element(By.CSS_SELECTOR, "img")
            image_url = img_elem.get_attribute("src") if img_elem else ""
            
            # Get description/summary
            desc_elem = card.find_element(By.CSS_SELECTOR, "p, [data-testid='recipe-description']")
            description = desc_elem.text.strip() if desc_elem else ""
            
            # Get additional details
            time_elem = card.find_element(By.CSS_SELECTOR, "[data-testid='cooking-time'], .cooking-time")
            cooking_time = time_elem.text.strip() if time_elem else ""
            
            difficulty_elem = card.find_element(By.CSS_SELECTOR, "[data-testid='difficulty'], .difficulty")
            difficulty = difficulty_elem.text.strip() if difficulty_elem else ""
            
            # Get tags/categories
            tag_elems = card.find_elements(By.CSS_SELECTOR, "[data-testid='tag'], .tag, .category")
            tags = [tag.text.strip() for tag in tag_elems if tag.text.strip()]
            
            # Get author
            author_elem = card.find_element(By.CSS_SELECTOR, "[data-testid='author'], .author")
            author = author_elem.text.strip() if author_elem else ""
            
            return {
                'title': title,
                'url': recipe_url,
                'description': description,
                'ingredients': "",  # Will be filled with scraping individual recipe
                'instructions': "",  # Will be filled with scraping individual recipe
                'cooking_time': cooking_time,
                'difficulty': difficulty,
                'cuisine': "",
                'tags': json.dumps(tags),
                'image_url': image_url,
                'author': author,
                'published_date': "",
                'scraped_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error extracting recipe data: {e}")
            return None
    
    def scrape_cooking_news(self, max_articles=20):
        """Scrape cooking news and articles from NYT Cooking"""
        print("Starting cooking news scraping...")
        driver = self.setup_selenium()
        
        try:
            news_articles = []
            url = f"{self.base_url}/guides"
            
            driver.get(url)
            time.sleep(3)
            
            # Find news articles and guides
            article_elements = driver.find_elements(By.CSS_SELECTOR, "article, [data-testid='article'], .article")
            
            for article in article_elements[:max_articles]:
                try:
                    news_data = self.extract_news_data(article, driver)
                    if news_data:
                        news_articles.append(news_data)
                        self.save_news_to_db(news_data)
                except Exception as e:
                    print(f"Error extracting news: {e}")
                    continue
            
        except Exception as e:
            print(f"Error during news scraping: {e}")
        finally:
            driver.quit()
        
        print(f"Scraped {len(news_articles)} news articles")
        return news_articles
    
    def extract_news_data(self, article, driver):
        """Extract news data from an article element"""
        try:
            # Get title
            title_elem = article.find_element(By.CSS_SELECTOR, "h2, h3, [data-testid='article-title']")
            title = title_elem.text.strip() if title_elem else "Untitled Article"
            
            # Get URL
            link_elem = article.find_element(By.CSS_SELECTOR, "a")
            url = link_elem.get_attribute("href")
            
            # Get summary
            summary_elem = article.find_element(By.CSS_SELECTOR, "p, [data-testid='summary']")
            summary = summary_elem.text.strip() if summary_elem else ""
            
            # Get image
            img_elem = article.find_element(By.CSS_SELECTOR, "img")
            image_url = img_elem.get_attribute("src") if img_elem else ""
            
            # Get category
            category_elem = article.find_element(By.CSS_SELECTOR, "[data-testid='category'], .category")
            category = category_elem.text.strip() if category_elem else "General"
            
            # Get author
            author_elem = article.find_element(By.CSS_SELECTOR, "[data-testid='author'], .author")
            author = author_elem.text.strip() if author_elem else ""
            
            return {
                'title': title,
                'url': url,
                'summary': summary,
                'content': summary,  # Basic content for now
                'author': author,
                'published_date': "",
                'category': category,
                'image_url': image_url,
                'scraped_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error extracting news data: {e}")
            return None
    
    def save_recipe_to_db(self, recipe_data):
        """Save recipe data to SQLite database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO recipes 
                (title, url, description, ingredients, instructions, cooking_time, 
                 difficulty, cuisine, tags, image_url, author, published_date, scraped_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                recipe_data['title'], recipe_data['url'], recipe_data['description'],
                recipe_data['ingredients'], recipe_data['instructions'], recipe_data['cooking_time'],
                recipe_data['difficulty'], recipe_data['cuisine'], recipe_data['tags'],
                recipe_data['image_url'], recipe_data['author'], recipe_data['published_date'],
                recipe_data['scraped_date']
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error saving recipe to database: {e}")
    
    def save_news_to_db(self, news_data):
        """Save news data to SQLite database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO cooking_news 
                (title, url, summary, content, author, published_date, category, image_url, scraped_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                news_data['title'], news_data['url'], news_data['summary'],
                news_data['content'], news_data['author'], news_data['published_date'],
                news_data['category'], news_data['image_url'], news_data['scraped_date']
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error saving news to database: {e}")
    
    def get_recipes_from_db(self, limit=50):
        """Retrieve recipes from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM recipes ORDER BY scraped_date DESC LIMIT ?', (limit,))
            recipes = cursor.fetchall()
            
            conn.close()
            
            # Convert to list of dictionaries
            columns = ['id', 'title', 'url', 'description', 'ingredients', 'instructions',
                      'cooking_time', 'difficulty', 'cuisine', 'tags', 'image_url',
                      'author', 'published_date', 'scraped_date']
            
            return [dict(zip(columns, recipe)) for recipe in recipes]
            
        except Exception as e:
            print(f"Error retrieving recipes from database: {e}")
            return []
    
    def get_news_from_db(self, limit=50):
        """Retrieve news from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM cooking_news ORDER BY scraped_date DESC LIMIT ?', (limit,))
            news = cursor.fetchall()
            
            conn.close()
            
            # Convert to list of dictionaries
            columns = ['id', 'title', 'url', 'summary', 'content', 'author',
                      'published_date', 'category', 'image_url', 'scraped_date']
            
            return [dict(zip(columns, news)) for news in news]
            
        except Exception as e:
            print(f"Error retrieving news from database: {e}")
            return []
    
    # NYT API-based methods
    def scrape_cooking_articles_api(self, max_pages=3):
        """Scrape cooking articles using NYT Article Search API"""
        print("Starting NYT API article search...")
        
        try:
            articles = self.nyt_api.search_cooking_content(max_pages=max_pages)
            
            saved_count = 0
            for article in articles:
                formatted_article = self.nyt_api.format_article_for_db(article)
                self.save_news_to_db(formatted_article)
                saved_count += 1
            
            print(f"Saved {saved_count} articles from NYT API")
            return articles
            
        except Exception as e:
            print(f"Error scraping articles via API: {e}")
            return []
    
    def scrape_archive_cooking_content(self, year=2024, month=9):
        """Scrape cooking content from NYT Archive API"""
        print(f"Fetching archive content for {year}/{month}...")
        
        try:
            archive_data = self.nyt_api.get_archive_articles(year, month)
            
            if "error" in archive_data:
                print(f"Archive API error: {archive_data['error']}")
                return []
            
            articles = archive_data.get("response", {}).get("docs", [])
            cooking_articles = []
            
            for article in articles:
                # Filter for cooking-related content
                headline = article.get("headline", {}).get("main", "").lower()
                snippet = article.get("snippet", "").lower()
                
                if any(keyword in headline or keyword in snippet for keyword in 
                      ["cooking", "recipe", "food", "chef", "restaurant", "dining"]):
                    cooking_articles.append(article)
            
            saved_count = 0
            for article in cooking_articles:
                formatted_article = self.nyt_api.format_article_for_db(article)
                self.save_news_to_db(formatted_article)
                saved_count += 1
            
            print(f"Saved {saved_count} cooking articles from archive")
            return cooking_articles
            
        except Exception as e:
            print(f"Error scraping archive content: {e}")
            return []
    
    def scrape_rss_cooking_news(self):
        """Scrape cooking news from NYT RSS feeds"""
        print("Fetching RSS cooking news...")
        
        try:
            rss_data = self.nyt_api.get_rss_feed("food")
            
            if "error" in rss_data:
                print(f"RSS error: {rss_data['error']}")
                return []
            
            # Parse RSS content (basic parsing - could be enhanced)
            content = rss_data.get("content", "")
            
            # For now, just return success status
            # In a full implementation, you'd parse the XML and extract articles
            print("RSS feed fetched successfully")
            return [{"status": "success", "content_length": len(content)}]
            
        except Exception as e:
            print(f"Error fetching RSS feed: {e}")
            return []
    
    def scrape_all_sources(self, max_pages=3, include_archive=True, include_rss=True):
        """Scrape from all available sources: web scraping + APIs"""
        print("Starting comprehensive scraping from all sources...")
        
        results = {
            "web_recipes": [],
            "web_news": [],
            "api_articles": [],
            "archive_articles": [],
            "rss_news": []
        }
        
        # 1. Article Search API
        try:
            results["api_articles"] = self.scrape_cooking_articles_api(max_pages)
        except Exception as e:
            print(f"Article Search API failed: {e}")
        
        # 2. Archive API
        if include_archive:
            try:
                current_date = datetime.now()
                results["archive_articles"] = self.scrape_archive_cooking_content(
                    current_date.year, current_date.month
                )
            except Exception as e:
                print(f"Archive API failed: {e}")
        
        # 3. RSS API
        if include_rss:
            try:
                results["rss_news"] = self.scrape_rss_cooking_news()
            except Exception as e:
                print(f"RSS API failed: {e}")
        
        # 4. Web scraping (fallback)
        try:
            results["web_recipes"] = self.scrape_recipes(max_pages)
            results["web_news"] = self.scrape_cooking_news(max_articles=15)
        except Exception as e:
            print(f"Web scraping failed: {e}")
        
        total_items = sum(len(v) for v in results.values() if isinstance(v, list))
        print(f"Comprehensive scraping completed! Total items: {total_items}")
        
        return results

if __name__ == "__main__":
    scraper = NYTCookingScraper()
    
    # Scrape recipes and news
    print("Starting NYT Cooking scraper...")
    recipes = scraper.scrape_recipes(max_pages=3)
    news = scraper.scrape_cooking_news(max_articles=15)
    
    print(f"Scraping completed! Found {len(recipes)} recipes and {len(news)} news articles.")
