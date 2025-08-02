import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np
import time

# Import our custom modules
from utils.news_fetcher import NewsFetcher
from utils.sentiment_analyzer import SentimentAnalyzer  
from utils.claude_analyzer import ClaudeAnalyzer
from config import STOCKS

# Page config - DARK THEME
st.set_page_config(
    page_title="🚀 AI Trading Terminal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for that cyberpunk trading terminal look
st.markdown("""
<style>
/* Import futuristic font */
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');

/* Main background and styling */
.stApp {
    background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
    color: #00ff41;
    font-family: 'Orbitron', monospace;
}

/* Sidebar styling */
.css-1d391kg {
    background: rgba(0, 0, 0, 0.8);
    border-right: 2px solid #00ff41;
}

/* Metrics styling */
.metric-container {
    background: rgba(0, 255, 65, 0.1);
    border: 1px solid #00ff41;
    border-radius: 10px;
    padding: 15px;
    margin: 10px 0;
    box-shadow: 0 0 20px rgba(0, 255, 65, 0.3);
    backdrop-filter: blur(10px);
}

/* Custom title styling */
.terminal-title {
    font-family: 'Orbitron', monospace;
    font-size: 3rem;
    font-weight: 900;
    text-align: center;
    background: linear-gradient(45deg, #00ff41, #00ccff, #ff0080);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0 0 30px rgba(0, 255, 65, 0.5);
    margin-bottom: 30px;
}

/* Glowing buttons */
.stButton > button {
    background: linear-gradient(45deg, #00ff41, #00ccff);
    color: #000;
    border: none;
    border-radius: 25px;
    padding: 10px 25px;
    font-family: 'Orbitron', monospace;
    font-weight: bold;
    box-shadow: 0 0 20px rgba(0, 255, 65, 0.5);
    transition: all 0.3s ease;
}

.stButton > button:hover {
    transform: scale(1.05);
    box-shadow: 0 0 30px rgba(0, 255, 65, 0.8);
}

/* Selectbox styling */
.stSelectbox > div > div {
    background: rgba(0, 0, 0, 0.7);
    border: 1px solid #00ff41;
    color: #00ff41;
}

/* Alert boxes */
.sentiment-positive {
    background: rgba(0, 255, 65, 0.2);
    border-left: 5px solid #00ff41;
    padding: 15px;
    border-radius: 5px;
}

.sentiment-negative {
    background: rgba(255, 0, 128, 0.2);
    border-left: 5px solid #ff0080;
    padding: 15px;
    border-radius: 5px;
}

.sentiment-neutral {
    background: rgba(0, 204, 255, 0.2);
    border-left: 5px solid #00ccff;
    padding: 15px;
    border-radius: 5px;
}

/* Loading animation */
@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
}

.loading {
    animation: pulse 1.5s infinite;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'sentiment_data' not in st.session_state:
    st.session_state.sentiment_data = None
if 'market_data' not in st.session_state:
    st.session_state.market_data = None

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_market_data(symbols):
    """Load real-time market data"""
    market_data = {}
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d")
            info = ticker.info
            
            current_price = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
            change = current_price - prev_close
            change_pct = (change / prev_close) * 100
            
            market_data[symbol] = {
                'current_price': current_price,
                'change': change,
                'change_pct': change_pct,
                'volume': hist['Volume'].iloc[-1],
                'market_cap': info.get('marketCap', 0),
                'hist': hist
            }
        except Exception as e:
            st.error(f"Error loading data for {symbol}: {e}")
            
    return market_data

@st.cache_data(ttl=1800)  # Cache for 30 minutes
def load_sentiment_data():
    """Load and analyze sentiment data"""
    with st.spinner("🤖 AI is analyzing market sentiment..."):
        news_fetcher = NewsFetcher()
        sentiment_analyzer = SentimentAnalyzer()
        
        all_sentiment_data = {}
        
        for symbol in STOCKS:
            # Get news
            articles = news_fetcher.get_stock_news(symbol, days_back=3)
            
            if articles:
                # Analyze sentiment
                analyzed = sentiment_analyzer.analyze_articles(articles)
                summary = sentiment_analyzer.get_stock_sentiment_summary(analyzed, symbol)
                
                all_sentiment_data[symbol] = {
                    'summary': summary,
                    'articles': analyzed[:5]  # Top 5 articles
                }
            else:
                all_sentiment_data[symbol] = {
                    'summary': {
                        'symbol': symbol,
                        'avg_sentiment': 0,
                        'total_articles': 0,
                        'positive_count': 0,
                        'negative_count': 0,
                        'neutral_count': 0
                    },
                    'articles': []
                }
                
    return all_sentiment_data

def create_sentiment_gauge(sentiment_score, symbol):
    """Create a cool sentiment gauge"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = sentiment_score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"{symbol} Sentiment", 'font': {'color': '#00ff41', 'size': 16}},
        delta = {'reference': 0, 'increasing': {'color': "#00ff41"}, 'decreasing': {'color': "#ff0080"}},
        gauge = {
            'axis': {'range': [-1, 1], 'tickcolor': "#00ff41"},
            'bar': {'color': "#00ccff"},
            'steps': [
                {'range': [-1, -0.3], 'color': "rgba(255, 0, 128, 0.3)"},
                {'range': [-0.3, 0.3], 'color': "rgba(0, 204, 255, 0.3)"},
                {'range': [0.3, 1], 'color': "rgba(0, 255, 65, 0.3)"}
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': sentiment_score
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#00ff41', 'family': 'Orbitron'},
        height=300
    )
    
    return fig

def create_price_chart(symbol, market_data):
    """Create an awesome price chart"""
    hist = market_data[symbol]['hist']
    
    fig = go.Figure()
    
    # Candlestick chart
    fig.add_trace(go.Candlestick(
        x=hist.index,
        open=hist['Open'],
        high=hist['High'],
        low=hist['Low'],
        close=hist['Close'],
        name=symbol,
        increasing_line_color='#00ff41',
        decreasing_line_color='#ff0080'
    ))
    
    # Volume bar chart
    fig.add_trace(go.Bar(
        x=hist.index,
        y=hist['Volume'],
        name='Volume',
        yaxis='y2',
        opacity=0.3,
        marker_color='#00ccff'
    ))
    
    fig.update_layout(
        title=f'{symbol} Price Action',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0.1)',
        font={'color': '#00ff41', 'family': 'Orbitron'},
        xaxis={'gridcolor': 'rgba(0, 255, 65, 0.2)'},
        yaxis={'gridcolor': 'rgba(0, 255, 65, 0.2)', 'title': 'Price ($)'},
        yaxis2={'overlaying': 'y', 'side': 'right', 'title': 'Volume'},
        height=400
    )
    
    return fig

def create_sentiment_heatmap(sentiment_data):
    """Create a sentiment heatmap"""
    symbols = list(sentiment_data.keys())
    sentiments = [sentiment_data[symbol]['summary']['avg_sentiment'] for symbol in symbols]
    
    # Create a matrix for heatmap
    matrix = np.array(sentiments).reshape(2, 4)  # 2x4 grid for 8 stocks
    
    fig = go.Figure(data=go.Heatmap(
        z=matrix,
        x=symbols[:4],
        y=['Row 1', 'Row 2'],
        colorscale=[
            [0, '#ff0080'],      # Negative - Hot Pink
            [0.5, '#00ccff'],    # Neutral - Cyan  
            [1, '#00ff41']       # Positive - Green
        ],
        colorbar=dict(
            title=dict(text="Sentiment Score", font=dict(color='#00ff41'))
        ),
        text=[[f"{symbols[j]}<br>{sentiments[j]:.2f}" for j in range(4)],
              [f"{symbols[j+4]}<br>{sentiments[j+4]:.2f}" for j in range(4)]],
        texttemplate="%{text}",
        textfont={"size": 12, "color": "white"},
        hovertemplate='<b>%{text}</b><extra></extra>'
    ))
    
    fig.update_layout(
        title='📊 Market Sentiment Heatmap',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#00ff41', 'family': 'Orbitron'},
        height=300
    )
    
    return fig

# MAIN APP
def main():
    # Epic title
    st.markdown('<h1 class="terminal-title">🚀 AI TRADING TERMINAL</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #00ccff;">Real-time sentiment analysis powered by Claude AI</p>', unsafe_allow_html=True)
    
    # Sidebar controls
    with st.sidebar:
        st.markdown("### 🎛️ CONTROL PANEL")
        
        selected_stock = st.selectbox("🎯 Select Stock", STOCKS, index=0)
        
        if st.button("🚀 REFRESH DATA", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        auto_refresh = st.checkbox("⚡ Auto-refresh (30s)")
        
        if auto_refresh:
            time.sleep(30)
            st.rerun()
    
    # Load data
    if not st.session_state.data_loaded:
        with st.spinner("🔄 Loading market data..."):
            st.session_state.market_data = load_market_data(STOCKS)
            st.session_state.sentiment_data = load_sentiment_data()
            st.session_state.data_loaded = True
    
    market_data = st.session_state.market_data
    sentiment_data = st.session_state.sentiment_data
    
    # Top metrics row
    cols = st.columns(4)
    
    for i, symbol in enumerate(STOCKS[:4]):
        with cols[i]:
            if symbol in market_data:
                price = market_data[symbol]['current_price']
                change = market_data[symbol]['change']
                change_pct = market_data[symbol]['change_pct']
                sentiment = sentiment_data[symbol]['summary']['avg_sentiment']
                
                # Color based on change
                color = "#00ff41" if change >= 0 else "#ff0080"
                arrow = "📈" if change >= 0 else "📉"
                
                st.markdown(f"""
                <div class="metric-container">
                    <h3 style="color: {color};">{arrow} {symbol}</h3>
                    <h2 style="color: white;">${price:.2f}</h2>
                    <p style="color: {color};">{change:+.2f} ({change_pct:+.1f}%)</p>
                    <p style="color: #00ccff;">Sentiment: {sentiment:.2f}</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Main dashboard
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Price chart
        if selected_stock in market_data:
            price_fig = create_price_chart(selected_stock, market_data)
            st.plotly_chart(price_fig, use_container_width=True)
        
        # Sentiment heatmap
        heatmap_fig = create_sentiment_heatmap(sentiment_data)
        st.plotly_chart(heatmap_fig, use_container_width=True)
    
    with col2:
        # Sentiment gauge
        if selected_stock in sentiment_data:
            sentiment_score = sentiment_data[selected_stock]['summary']['avg_sentiment']
            gauge_fig = create_sentiment_gauge(sentiment_score, selected_stock)
            st.plotly_chart(gauge_fig, use_container_width=True)
        
        # AI Analysis
        st.markdown("### 🤖 AI ANALYSIS")
        
        if st.button("🧠 Generate Claude Analysis"):
            with st.spinner("Claude is thinking..."):
                claude_analyzer = ClaudeAnalyzer()
                analysis = claude_analyzer.generate_stock_summary(
                    selected_stock, 
                    sentiment_data[selected_stock]['articles']
                )
                
                # Style based on sentiment
                sentiment_score = sentiment_data[selected_stock]['summary']['avg_sentiment']
                if sentiment_score > 0.1:
                    css_class = "sentiment-positive"
                elif sentiment_score < -0.1:
                    css_class = "sentiment-negative"
                else:
                    css_class = "sentiment-neutral"
                
                st.markdown(f'<div class="{css_class}">{analysis}</div>', unsafe_allow_html=True)
    
    # Recent news section
    st.markdown("### 📰 RECENT NEWS SENTIMENT")
    
    if selected_stock in sentiment_data and sentiment_data[selected_stock]['articles']:
        for article in sentiment_data[selected_stock]['articles'][:3]:
            sentiment = article['sentiment_score']
            emoji = "🟢" if sentiment > 0.1 else "🔴" if sentiment < -0.1 else "🟡"
            
            with st.expander(f"{emoji} {article['title'][:80]}..."):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**Source:** {article['source']}")
                    st.write(f"**Published:** {article['published_at'][:10]}")
                    st.write(article['description'])
                    st.markdown(f"[Read Full Article]({article['url']})")
                with col2:
                    st.metric("Sentiment", f"{sentiment:.2f}", f"{article['label'].title()}")

if __name__ == "__main__":
    main()