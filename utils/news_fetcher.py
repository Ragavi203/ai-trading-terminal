import requests
import pandas as pd
from datetime import datetime, timedelta
from config import NEWS_API_KEY
import time

class NewsFetcher:
    def __init__(self):
        self.api_key = NEWS_API_KEY
        self.base_url = "https://newsapi.org/v2/everything"
    
    def get_stock_news(self, symbol, days_back=7):
        """Fetch news for a specific stock symbol"""
        
        # Calculate date range
        to_date = datetime.now()
        from_date = to_date - timedelta(days=days_back)
        
        # Search terms for the stock
        query = f'"{symbol}" OR "{self.get_company_name(symbol)}"'
        
        params = {
            'q': query,
            'from': from_date.strftime('%Y-%m-%d'),
            'to': to_date.strftime('%Y-%m-%d'),
            'language': 'en',
            'sortBy': 'publishedAt',
            'apiKey': self.api_key,
            'pageSize': 20  # Limit to avoid quota issues
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            articles = data.get('articles', [])
            
            # Process articles
            processed_articles = []
            for article in articles:
                if article['title'] and article['description']:
                    processed_articles.append({
                        'symbol': symbol,
                        'title': article['title'],
                        'description': article['description'],
                        'content': article.get('content', ''),
                        'url': article['url'],
                        'published_at': article['publishedAt'],
                        'source': article['source']['name']
                    })
            
            return processed_articles
            
        except Exception as e:
            print(f"Error fetching news for {symbol}: {e}")
            return []
    
    def get_company_name(self, symbol):
        """Map stock symbols to company names"""
        company_map = {
            'AAPL': 'Apple',
            'TSLA': 'Tesla',
            'GOOGL': 'Google',
            'MSFT': 'Microsoft',
            'AMZN': 'Amazon',
            'NVDA': 'Nvidia',
            'META': 'Meta',
            'NFLX': 'Netflix'
        }
        return company_map.get(symbol, symbol)

    def get_all_stocks_news(self, symbols, days_back=7):
        """Fetch news for multiple stocks"""
        all_articles = []
        
        for symbol in symbols:
            print(f"Fetching news for {symbol}...")
            articles = self.get_stock_news(symbol, days_back)
            all_articles.extend(articles)
            time.sleep(1)  # Be nice to the API
            
        return all_articles