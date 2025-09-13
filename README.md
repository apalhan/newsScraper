# NYT Cooking Scraper 🍳

A comprehensive web scraping application that extracts recipes and cooking news from NYT Cooking, featuring a modern web interface for browsing and searching scraped content.

## ✨ Features

- **Recipe Scraping**: Automatically extracts recipes from NYT Cooking with detailed information
- **News Scraping**: Gathers cooking-related news articles and guides
- **Modern Web Interface**: Beautiful, responsive design with search and filtering capabilities
- **Database Storage**: SQLite database for persistent storage of scraped content
- **Real-time Updates**: Background scraping with progress tracking
- **Advanced Filtering**: Search by cuisine, difficulty, category, and keywords
- **Detailed Views**: Individual pages for recipes and news articles

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Chrome browser (for Selenium WebDriver)
- pip package manager

### Installation

1. **Clone or download the project**
   ```bash
   cd nyt-cooking-scraper
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Open your browser**
   Navigate to `http://localhost:5000`

## 📁 Project Structure

```
nyt-cooking-scraper/
├── app.py                 # Flask web application
├── scraper.py            # Main scraping logic
├── requirements.txt      # Python dependencies
├── templates/            # HTML templates
│   ├── index.html       # Main page
│   ├── recipe_detail.html # Recipe detail page
│   └── news_detail.html # News detail page
├── cooking_data.db      # SQLite database (created automatically)
└── README.md            # This file
```

## 🔧 Configuration

### Scraping Settings

You can modify scraping parameters in `scraper.py`:

```python
# In the main section
recipes = scraper.scrape_recipes(max_pages=3)      # Number of recipe pages to scrape
news = scraper.scrape_cooking_news(max_articles=15) # Number of news articles to scrape
```

### Web Interface Settings

Modify the Flask app settings in `app.py`:

```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

## 📊 Database Schema

### Recipes Table
- `id`: Unique identifier
- `title`: Recipe title
- `url`: Original recipe URL
- `description`: Recipe description
- `ingredients`: Recipe ingredients (JSON)
- `instructions`: Cooking instructions
- `cooking_time`: Estimated cooking time
- `difficulty`: Difficulty level
- `cuisine`: Cuisine type
- `tags`: Recipe tags (JSON)
- `image_url`: Recipe image URL
- `author`: Recipe author
- `published_date`: Publication date
- `scraped_date`: When it was scraped

### Cooking News Table
- `id`: Unique identifier
- `title`: Article title
- `url`: Original article URL
- `summary`: Article summary
- `content`: Full article content
- `author`: Article author
- `published_date`: Publication date
- `category`: Article category
- `image_url`: Article image URL
- `scraped_date`: When it was scraped

## 🎯 Usage

### Starting the Scraper

1. **Via Web Interface**
   - Click the "Start Scraping" button on the homepage
   - Monitor progress through the statistics section

2. **Via Command Line**
   ```bash
   python scraper.py
   ```

### Browsing Content

- **Recipes Tab**: View all scraped recipes with filtering options
- **News Tab**: Browse cooking news and articles
- **Search**: Use the search bar to find specific content
- **Filters**: Apply cuisine, difficulty, and category filters

### Viewing Details

- Click on any recipe or news article to view full details
- Access original content via external links
- View metadata like author, dates, and categories

## 🔍 Search and Filtering

### Recipe Filters
- **Search**: Text search in titles and descriptions
- **Cuisine**: Filter by cuisine type (Italian, French, Asian, etc.)
- **Difficulty**: Filter by difficulty level (Easy, Medium, Hard)

### News Filters
- **Search**: Text search in titles and summaries
- **Category**: Filter by article category

## ⚠️ Important Notes

### Legal Considerations
- This tool is for **educational purposes only**
- Respect NYT Cooking's terms of service
- Don't overload their servers with excessive requests
- Consider implementing rate limiting for production use

### Technical Limitations
- The scraper depends on NYT Cooking's HTML structure
- Changes to their website may break the scraper
- Some content may require authentication
- Image URLs may expire over time

### Performance
- Scraping can take several minutes depending on the number of pages
- The database will grow over time - consider cleanup strategies
- Selenium WebDriver requires Chrome browser

## 🛠️ Troubleshooting

### Common Issues

1. **Chrome Driver Issues**
   ```bash
   # Reinstall ChromeDriver
   pip uninstall webdriver-manager
   pip install webdriver-manager
   ```

2. **Database Errors**
   ```bash
   # Remove and recreate database
   rm cooking_data.db
   python scraper.py
   ```

3. **Scraping Failures**
   - Check internet connection
   - Verify NYT Cooking is accessible
   - Check for website structure changes

### Debug Mode

Enable debug mode in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

## 🔮 Future Enhancements

- [ ] User authentication and favorites
- [ ] Recipe rating and reviews
- [ ] Export functionality (PDF, CSV)
- [ ] Email notifications for new content
- [ ] Advanced analytics dashboard
- [ ] Mobile app version
- [ ] Recipe scaling and unit conversion
- [ ] Integration with recipe management apps

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is for educational purposes. Please respect the terms of service of any websites you scrape.

## 🙏 Acknowledgments

- NYT Cooking for providing excellent culinary content
- Selenium team for web automation tools
- Flask community for the web framework
- Bootstrap team for the UI components

## 📞 Support

If you encounter issues or have questions:

1. Check the troubleshooting section above
2. Review the code comments for guidance
3. Open an issue on the project repository

---

**Happy Cooking! 🍽️**
