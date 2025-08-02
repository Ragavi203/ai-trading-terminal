import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')

# Stock symbols to track
STOCKS = ['AAPL', 'TSLA', 'GOOGL', 'MSFT', 'AMZN', 'NVDA', 'META', 'NFLX']

# News sources
NEWS_SOURCES = [
    'reuters', 'bloomberg', 'cnbc', 'financial-times', 
    'the-wall-street-journal', 'business-insider'
]