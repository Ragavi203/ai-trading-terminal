from config import NEWS_API_KEY, CLAUDE_API_KEY

print("Testing config...")
print(f"NEWS_API_KEY: {NEWS_API_KEY[:10] if NEWS_API_KEY else 'None'}...")
print(f"CLAUDE_API_KEY: {CLAUDE_API_KEY[:10] if CLAUDE_API_KEY else 'None'}...")