import anthropic
from config import CLAUDE_API_KEY
import json

class ClaudeAnalyzer:
    def __init__(self):
        
        self.client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
    
    def generate_stock_summary(self, symbol, analyzed_articles):
        """Generate AI summary for a stock using Claude"""
        
        # Get articles for this symbol
        stock_articles = [a for a in analyzed_articles if a['symbol'] == symbol]
        
        if not stock_articles:
            return "No recent news found for this stock."
        
        # Prepare article summaries for Claude
        article_texts = []
        for article in stock_articles[:10]:  # Limit to avoid token limits
            article_texts.append({
                'title': article['title'],
                'description': article['description'],
                'sentiment_score': round(article['sentiment_score'], 2),
                'source': article['source'],
                'date': article['published_at'][:10]
            })
        
        prompt = f"""
        Analyze the recent news sentiment for {symbol} stock and provide a concise investment research summary.

        Recent News Articles:
        {json.dumps(article_texts, indent=2)}

        Please provide:
        1. **Overall Sentiment**: Brief assessment of market sentiment
        2. **Key Themes**: Main topics driving the news
        3. **Investment Implications**: What this means for potential investors
        4. **Risk Factors**: Any concerning trends or news

        Keep it concise but insightful. Focus on actionable insights for investors.
        """
        
        try:
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",  # Faster and cheaper
                max_tokens=500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return message.content[0].text
            
        except Exception as e:
            print(f"Error generating Claude summary: {e}")
            return f"Error generating AI summary for {symbol}"
    
    def generate_market_overview(self, all_sentiment_data):
        """Generate overall market sentiment overview"""
        
        prompt = f"""
        Based on this sentiment analysis of major tech stocks, provide a brief market overview:

        Stock Sentiment Summary:
        {json.dumps(all_sentiment_data, indent=2)}

        Provide:
        1. **Market Mood**: Overall sentiment across these stocks
        2. **Leaders & Laggards**: Which stocks have best/worst sentiment
        3. **Trends**: Any patterns you notice
        4. **Outlook**: Brief investment perspective

        Keep it under 200 words and actionable.
        """
        
        try:
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=300,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return message.content[0].text
            
        except Exception as e:
            print(f"Error generating market overview: {e}")
            return "Error generating market overview"