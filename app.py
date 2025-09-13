import sqlite3
import threading

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from scraper import NYTCookingScraper

app = Flask(__name__)
CORS(app)

# Global scraper instance
scraper = NYTCookingScraper()

@app.route('/')
def index():
    """Main page with recipes and news"""
    return render_template('index.html')

@app.route('/api/recipes')
def get_recipes():
    """API endpoint to get recipes"""
    try:
        limit = request.args.get('limit', 50, type=int)
        search = request.args.get('search', '')
        cuisine = request.args.get('cuisine', '')
        difficulty = request.args.get('difficulty', '')
        
        recipes = scraper.get_recipes_from_db(limit=1000)  # Get all for filtering
        
        # Apply filters
        if search:
            recipes = [r for r in recipes if search.lower() in r['title'].lower() or
                    search.lower() in r['description'].lower()]
        
        if cuisine:
            recipes = [r for r in recipes if cuisine.lower() in r['cuisine'].lower()]
        
        if difficulty:
            recipes = [r for r in recipes if difficulty.lower() in r['difficulty'].lower()]
        
        # Limit results
        recipes = recipes[:limit]
        
        return jsonify({
            'success': True,
            'recipes': recipes,
            'count': len(recipes)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/news')
def get_news():
    """API endpoint to get cooking news"""
    try:
        limit = request.args.get('limit', 50, type=int)
        category = request.args.get('category', '')
        search = request.args.get('search', '')
        
        news = scraper.get_news_from_db(limit=1000)  # Get all for filtering
        
        # Apply filters
        if search:
            news = [n for n in news if search.lower() in n['title'].lower() or
                    search.lower() in n['summary'].lower()]
        
        if category:
            news = [n for n in news if category.lower() in n['category'].lower()]
        
        # Limit results
        news = news[:limit]
        
        return jsonify({
            'success': True,
            'news': news,
            'count': len(news)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/scrape', methods=['POST'])
def start_scraping():
    """Start scraping in background"""
    try:
        data = request.get_json()
        max_pages = data.get('max_pages', 3)
        max_articles = data.get('max_articles', 15)
        
        # Start scraping in background thread
        def scrape_background():
            try:
                scraper.scrape_recipes(max_pages=max_pages)
                scraper.scrape_cooking_news(max_articles=max_articles)
            except Exception as e:
                print(f"Background scraping error: {e}")
        
        thread = threading.Thread(target=scrape_background)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Scraping started in background'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/scrape-nyt-api', methods=['POST'])
def start_nyt_api_scraping():
    """Start NYT API-based scraping in background"""
    try:
        data = request.get_json()
        max_pages = data.get('max_pages', 3)
        include_archive = data.get('include_archive', True)
        include_rss = data.get('include_rss', True)
        
        # Start API scraping in background thread
        def scrape_api_background():
            try:
                scraper.scrape_cooking_articles_api(max_pages=max_pages)
                if include_archive:
                    scraper.scrape_archive_cooking_content()
                if include_rss:
                    scraper.scrape_rss_cooking_news()
            except Exception as e:
                print(f"Background API scraping error: {e}")
        
        thread = threading.Thread(target=scrape_api_background)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'NYT API scraping started in background'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/scrape-all', methods=['POST'])
def start_comprehensive_scraping():
    """Start comprehensive scraping from all sources"""
    try:
        data = request.get_json()
        max_pages = data.get('max_pages', 3)
        include_archive = data.get('include_archive', True)
        include_rss = data.get('include_rss', True)
        
        # Start comprehensive scraping in background thread
        def scrape_all_background():
            try:
                results = scraper.scrape_all_sources(
                    max_pages=max_pages,
                    include_archive=include_archive,
                    include_rss=include_rss
                )
                print(f"Comprehensive scraping results: {results}")
            except Exception as e:
                print(f"Background comprehensive scraping error: {e}")
        
        thread = threading.Thread(target=scrape_all_background)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Comprehensive scraping started in background'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stats')
def get_stats():
    """Get database statistics"""
    try:
        conn = sqlite3.connect(scraper.db_path)
        cursor = conn.cursor()
        
        # Get recipe count
        cursor.execute('SELECT COUNT(*) FROM recipes')
        recipe_count = cursor.fetchone()[0]
        
        # Get news count
        cursor.execute('SELECT COUNT(*) FROM cooking_news')
        news_count = cursor.fetchone()[0]
        
        # Get latest scrape date
        cursor.execute('SELECT MAX(scraped_date) FROM recipes')
        latest_recipe_date = cursor.fetchone()[0]
        
        cursor.execute('SELECT MAX(scraped_date) FROM cooking_news')
        latest_news_date = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_recipes': recipe_count,
                'total_news': news_count,
                'latest_recipe_scrape': latest_recipe_date,
                'latest_news_scrape': latest_news_date
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/recipe/<int:recipe_id>')
def recipe_detail(recipe_id):
    """Recipe detail page"""
    try:
        conn = sqlite3.connect(scraper.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM recipes WHERE id = ?', (recipe_id,))
        recipe = cursor.fetchone()
        conn.close()
        
        if recipe:
            columns = ['id', 'title', 'url', 'description', 'ingredients', 'instructions',
                        'cooking_time', 'difficulty', 'cuisine', 'tags', 'image_url',
                        'author', 'published_date', 'scraped_date']
            recipe_dict = dict(zip(columns, recipe))
            return render_template('recipe_detail.html', recipe=recipe_dict)
        else:
            return "Recipe not found", 404
            
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/news/<int:news_id>')
def news_detail(news_id):
    """News detail page"""
    try:
        conn = sqlite3.connect(scraper.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM cooking_news WHERE id = ?', (news_id,))
        news = cursor.fetchone()
        conn.close()
        
        if news:
            columns = ['id', 'title', 'url', 'summary', 'content', 'author',
                        'published_date', 'category', 'image_url', 'scraped_date']
            news_dict = dict(zip(columns, news))
            return render_template('news_detail.html', news=news_dict)
        else:
            return "News article not found", 404
            
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8080)
