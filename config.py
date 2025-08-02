import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys - works both locally and on Streamlit Cloud
try:
    # Try Streamlit secrets first (for cloud deployment)
    NEWS_API_KEY = st.secrets["NEWS_API_KEY"]
    CLAUDE_API_KEY = st.secrets["CLAUDE_API_KEY"]
except:
    # Fall back to environment variables (for local development)
    NEWS_API_KEY = os.getenv('NEWS_API_KEY')
    CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')

# Stock symbols to track
STOCKS = ['AAPL', 'TSLA', 'GOOGL', 'MSFT', 'AMZN', 'NVDA', 'META', 'NFLX']

# News sources
NEWS_SOURCES = [
    'reuters', 'bloomberg', 'cnbc', 'financial-times', 
    'the-wall-street-journal', 'business-insider'
]
