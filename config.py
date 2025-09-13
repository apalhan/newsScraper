# Configuration file for NYT Cooking Scraper

# Scraping Configuration
SCRAPING_CONFIG = {
    'max_pages': 3,           # Maximum number of recipe pages to scrape
    'max_articles': 15,       # Maximum number of news articles to scrape
    'delay_between_pages': 2, # Delay between page requests (seconds)
    'delay_between_items': 1, # Delay between item extractions (seconds)
    'timeout': 10,            # Page load timeout (seconds)
}

# Database Configuration
DATABASE_CONFIG = {
    'path': 'cooking_data.db',
    'backup_enabled': True,
    'backup_interval': 24,    # Hours between backups
}

# Web Application Configuration
WEB_CONFIG = {
    'host': '0.0.0.0',
    'port': 5000,
    'debug': True,
    'threaded': True,
    'secret_key': 'your-secret-key-change-this-in-production'
}

# NYT Cooking URLs
NYT_URLS = {
    'base': 'https://cooking.nytimes.com',
    'recipes': 'https://cooking.nytimes.com/recipes',
    'guides': 'https://cooking.nytimes.com/guides',
    'techniques': 'https://cooking.nytimes.com/guides/1-how-to-cook-grains'
}

# User Agent Configuration
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
]

# Selenium Configuration
SELENIUM_CONFIG = {
    'headless': True,         # Run browser in background
    'window_size': '1920,1080',
    'disable_images': False,  # Set to True to disable image loading for faster scraping
    'disable_javascript': False,  # Set to True to disable JavaScript (may break some sites)
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'scraper.log',
    'max_size': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5
}

# Rate Limiting
RATE_LIMIT_CONFIG = {
    'enabled': True,
    'requests_per_minute': 30,
    'requests_per_hour': 1000
}

# Content Filtering
CONTENT_FILTERS = {
    'min_title_length': 5,
    'min_description_length': 10,
    'exclude_keywords': ['advertisement', 'sponsored', 'promotion'],
    'required_fields': ['title', 'url']
}

# Export Configuration
EXPORT_CONFIG = {
    'formats': ['json', 'csv', 'excel'],
    'default_format': 'json',
    'include_metadata': True,
    'max_export_items': 1000
}
