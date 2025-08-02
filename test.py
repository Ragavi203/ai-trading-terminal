from utils.news_fetcher import NewsFetcher
from utils.sentiment_analyzer import SentimentAnalyzer
from utils.claude_analyzer import ClaudeAnalyzer
from config import STOCKS

def test_pipeline():
    print("Testing the AI pipeline...")
    
    # Test 1: Fetch news
    print("\nTesting news fetcher...")
    news_fetcher = NewsFetcher()
    articles = news_fetcher.get_stock_news('AAPL', days_back=3)
    print(f"Found {len(articles)} articles for AAPL")
    
    if articles:
        print(f"Sample article: {articles[0]['title']}")
    
    # Test 2: Sentiment analysis
    print("\nTesting sentiment analysis...")
    sentiment_analyzer = SentimentAnalyzer()
    analyzed = sentiment_analyzer.analyze_articles(articles[:3])  # Just test 3
    print(f"Analyzed sentiment for {len(analyzed)} articles")
    
    if analyzed:
        sample = analyzed[0]
        print(f"Sample: '{sample['title'][:50]}...' -> Sentiment: {sample['sentiment_score']:.2f}")
    
    # Test 3: Claude summary
    print("\nTesting Claude integration...")
    claude_analyzer = ClaudeAnalyzer()
    summary = claude_analyzer.generate_stock_summary('AAPL', analyzed)
    print(f"Generated Claude summary:")
    print(summary[:200] + "...")

if __name__ == "__main__":
    test_pipeline()