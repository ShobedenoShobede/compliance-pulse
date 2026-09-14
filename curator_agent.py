import feedparser
import json
import os
import re
from datetime import datetime, timedelta

# --- FREE REGULATORY FEEDS ---
FEEDS = {
    "SEC": "https://www.sec.gov/news/pressreleases.rss",
    "FCA": "https://www.fca.org.uk/news/rss.xml",
    "ESMA": "https://www.esma.europa.eu/press-news/esma-news/rss.xml",
    "Federal Register": "https://www.federalregister.gov/documents/search.rss?conditions%5Bterm%5D=artificial+intelligence",
}

# --- RELEVANCE FILTER ---
KEYWORDS = [
    "artificial intelligence", "AI", "machine learning", "algorithm",
    "compliance", "fintech", "enforcement", "regulation", "guidance",
    "supervisory", "risk management", "automated decision"
]

def is_relevant(text):
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in KEYWORDS)

def fetch_feed(name, url):
    """Fetch and filter entries from a single RSS feed."""
    items = []
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries[:20]:  # Last 20 per feed
            title = entry.get("title", "")
            summary = entry.get("summary", entry.get("description", ""))
            link = entry.get("link", "")
            published = entry.get("published", datetime.now().isoformat())
            
            if is_relevant(title + " " + summary):
                items.append({
                    "source": name,
                    "title": title,
                    "summary": summary[:500],  # Truncate for context
                    "link": link,
                    "published": published,
                    "fetched": datetime.now().isoformat()
                })
    except Exception as e:
        print(f"Error fetching {name}: {e}")
    return items

def main():
    all_items = []
    for name, url in FEEDS.items():
        items = fetch_feed(name, url)
        all_items.extend(items)
        print(f"{name}: {len(items)} relevant items")
    
    # Save raw intel for the writer agent
    with open("raw_intel.json", "w") as f:
        json.dump(all_items, f, indent=2)
    
    print(f"Total: {len(all_items)} items saved to raw_intel.json")

if __name__ == "__main__":
    main()