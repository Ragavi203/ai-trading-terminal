from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import pandas as pd
import numpy as np

class SentimentAnalyzer:
    def __init__(self):
        # Load FinBERT model (specifically trained on financial texts)
        model_name = "ProsusAI/finbert"
        
        try:
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis", 
                model=model_name,
                tokenizer=model_name
            )
            print("✅ FinBERT model loaded successfully!")
        except Exception as e:
            print(f"❌ Error loading FinBERT: {e}")
            # Fallback to general sentiment model
            self.sentiment_pipeline = pipeline("sentiment-analysis")
            print("✅ Using fallback sentiment model")
    
    def analyze_text(self, text):
        """Analyze sentiment of a single text"""
        try:
            # Truncate text if too long
            text = text[:512] if len(text) > 512 else text
            
            result = self.sentiment_pipeline(text)[0]
            
            # Convert to standardized format
            label = result['label'].lower()
            score = result['score']
            
            # Map labels to sentiment scores
            if 'positive' in label or 'bullish' in label:
                sentiment_score = score
            elif 'negative' in label or 'bearish' in label:
                sentiment_score = -score
            else:  # neutral
                sentiment_score = 0
                
            return {
                'sentiment_score': sentiment_score,
                'confidence': score,
                'label': label
            }
            
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return {
                'sentiment_score': 0,
                'confidence': 0,
                'label': 'neutral'
            }
    
    def analyze_articles(self, articles):
        """Analyze sentiment for multiple articles"""
        results = []
        
        for article in articles:
            # Combine title and description for analysis
            text = f"{article['title']} {article['description']}"
            
            sentiment = self.analyze_text(text)
            
            result = {
                **article,
                **sentiment
            }
            
            results.append(result)
        
        return results
    
    def get_stock_sentiment_summary(self, analyzed_articles, symbol):
        """Get overall sentiment summary for a stock"""
        stock_articles = [a for a in analyzed_articles if a['symbol'] == symbol]
        
        if not stock_articles:
            return {
                'symbol': symbol,
                'avg_sentiment': 0,
                'total_articles': 0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0
            }
        
        sentiments = [a['sentiment_score'] for a in stock_articles]
        
        return {
            'symbol': symbol,
            'avg_sentiment': np.mean(sentiments),
            'total_articles': len(stock_articles),
            'positive_count': len([s for s in sentiments if s > 0.1]),
            'negative_count': len([s for s in sentiments if s < -0.1]),
            'neutral_count': len([s for s in sentiments if -0.1 <= s <= 0.1]),
            'latest_articles': stock_articles[:3]  # Most recent 3
        }