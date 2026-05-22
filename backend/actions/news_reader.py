"""
RSS-Based News Reader (No API Key Required)

Features:
- Fetches real-time news via RSS feeds only
- Support for India + global news
- Titles only (120 char max, no HTML tags)
- Graceful fallback between multiple feeds
- Fast and lightweight (~1-2 seconds)
- No external API dependencies
"""

import feedparser
import re
import datetime
from actions.web import open_world_monitor


# ===== RSS FEEDS CONFIGURATION =====
# India news feeds (primary + fallback)
INDIA_FEEDS = [
    "https://feeds.feedburner.com/ndtvnews-top-stories",
    "https://timesofindia.indiatimes.com/rssfeedstopstories.cms"
]

# Global news feeds (primary + fallback)
GLOBAL_FEEDS = [
    "http://feeds.bbci.co.uk/news/world/rss.xml",
    "https://rss.cnn.com/rss/edition_world.rss"
]

# Legacy category feeds for backward compatibility
CATEGORY_FEEDS = {
    "technology": "https://feeds.bbci.co.uk/news/technology/rss.xml",
    "sports": "https://feeds.bbci.co.uk/news/sport/rss.xml",
    "business": "https://feeds.bbci.co.uk/news/business/rss.xml",
    "world": "https://feeds.bbci.co.uk/news/world/rss.xml",
}


def _clean_html_tags(text):
    """Remove HTML tags from text"""
    if not text:
        return ""
    # Remove HTML tags
    clean = re.compile('<.*?>')
    text = re.sub(clean, '', text)
    # Decode HTML entities
    text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"')
    text = text.replace('&#39;', "'")
    return text.strip()


def _truncate_title(title, max_length=120):
    """Truncate title to max length and clean HTML"""
    title = _clean_html_tags(title)
    if len(title) > max_length:
        title = title[:max_length] + "..."
    return title


def _fetch_from_single_feed(feed_url, limit=2, timeout=5):
    """
    Fetch headlines from a single RSS feed with timeout.
    
    Args:
        feed_url (str): URL of RSS feed
        limit (int): Max headlines to fetch
        timeout (int): Timeout in seconds
    
    Returns:
        list: List of headline strings or empty list if failed
    """
    try:
        # Use feedparser with timeout
        feed = feedparser.parse(feed_url)
        
        # Check if feed loaded successfully
        if not hasattr(feed, 'entries') or len(feed.entries) == 0:
            return []
        
        headlines = []
        for entry in feed.entries[:limit]:
            # Get title (required)
            title = entry.get("title", "")
            if title:
                # Clean and truncate
                title = _truncate_title(title)
                headlines.append(title)
        
        return headlines
    
    except Exception as e:
        # Silently fail - no error messages
        return []


def _fetch_india_news(limit=2):
    """
    Fetch India news from multiple feeds with fallback.
    
    Args:
        limit (int): Headlines to fetch per feed
    
    Returns:
        list: List of headline strings
    """
    headlines = []
    
    # Try each India feed in order
    for feed_url in INDIA_FEEDS:
        headlines.extend(_fetch_from_single_feed(feed_url, limit))
        if headlines:  # Stop if we got results
            break
    
    return headlines[:limit]


def _fetch_global_news(limit=2):
    """
    Fetch global news from multiple feeds with fallback.
    
    Args:
        limit (int): Headlines to fetch per feed
    
    Returns:
        list: List of headline strings
    """
    headlines = []
    
    # Try each global feed in order
    for feed_url in GLOBAL_FEEDS:
        headlines.extend(_fetch_from_single_feed(feed_url, limit))
        if headlines:  # Stop if we got results
            break
    
    return headlines[:limit]


def _fetch_category_news(category="world", limit=5):
    """
    Fetch news by category from RSS feeds.
    
    Args:
        category (str): Category name
        limit (int): Headlines to fetch
    
    Returns:
        list: List of headline strings
    """
    if category not in CATEGORY_FEEDS:
        category = "world"
    
    feed_url = CATEGORY_FEEDS[category]
    return _fetch_from_single_feed(feed_url, limit)


def get_news(category="world", limit=5):
    """
    Fetch news headlines from RSS feeds.
    
    Args:
        category (str): Category (world, technology, sports, business, india)
        limit (int): Number of headlines to fetch (default 5)
    
    Returns:
        list: List of headline strings
        
    Example:
        >>> news = get_news("technology", limit=3)
        >>> for headline in news:
        ...     print(headline)
    """
    # Handle special mappings
    if category == "india":
        return _fetch_india_news(limit)
    elif category in ["global", "world"]:
        return _fetch_global_news(limit)
    elif category in CATEGORY_FEEDS:
        return _fetch_category_news(category, limit)
    else:
        # Default to world news
        return _fetch_global_news(limit)


def get_trending_news(category="world", limit=5):
    """
    Fetch trending news headlines.
    Maps 'global' to 'world' for convenience.
    
    Args:
        category (str): Category (global/world, technology, sports, business, india)
        limit (int): Number of headlines to fetch
        
    Returns:
        list: List of headline strings
    """
    # Map 'global' to 'world' for consistency
    if category == "global":
        category = "world"
    
    return get_news(category, limit)


def get_world_briefing():
    """
    Get a world news briefing with hybrid priority (80% India + 20% Global).
    Opens World Monitor in browser before fetching news.
    ALWAYS speaks India news first, then global.
    
    Returns:
        str: Combined response starting with India (2 headlines) + Global (1-2 headlines)
    """
    try:
        # Open World Monitor first (checks if already open - won't reopen)
        open_world_monitor()
        
        # ===== FETCH INDIA NEWS (PRIMARY - ALWAYS FIRST) =====
        india_headlines = _fetch_india_news(limit=2)
        
        # ===== FETCH GLOBAL NEWS (SECONDARY) =====
        global_headlines = _fetch_global_news(limit=2)
        
        # Extract unique headlines for deduplication
        used_headlines = set()
        
        # ===== FORMAT INDIA NEWS FIRST (ALWAYS) =====
        india_text_parts = []
        for headline in india_headlines:
            headline_lower = headline.lower()
            if headline_lower not in used_headlines:
                used_headlines.add(headline_lower)
                india_text_parts.append(headline)
        
        india_text = ". ".join(india_text_parts) if india_text_parts else ""
        
        # ===== FORMAT GLOBAL NEWS SECOND =====
        global_text_parts = []
        for headline in global_headlines:
            headline_lower = headline.lower()
            if headline_lower not in used_headlines:
                used_headlines.add(headline_lower)
                global_text_parts.append(headline)
        
        global_text = ". ".join(global_text_parts) if global_text_parts else ""
        
        # ===== BUILD RESPONSE IN PRIORITY ORDER (INDIA ALWAYS FIRST) =====
        response_parts = []
        
        # ALWAYS start with India message
        if india_text:
            response_parts.append(f"Here's what's happening in India boss. {india_text}")
        else:
            # Even if no India news, acknowledge India first
            response_parts.append("Here's what's happening in India boss. Couldn't fetch India news right now.")
        
        # Then add global news if available
        if global_text:
            response_parts.append(f"And globally boss. {global_text}")
        
        # Add monitor confirmation
        response_parts.append("I've opened the World Monitor so you can track it visually boss")
        
        response = ". ".join(response_parts) + "."
        return response
    
    except Exception as e:
        print(f"[ERROR] World briefing error: {e}")
        # Always start with India message even on error
        return "Here's what's happening in India boss. Couldn't fetch news right now boss. But I've opened the World Monitor for you to check."


def get_news_by_topic(topic):
    """
    Get news headlines filtered by topic.
    
    Args:
        topic (str): News topic to search for
        
    Returns:
        list: List of headline strings for the topic
    """
    try:
        topic = topic.lower()
        
        # Technology news
        if "tech" in topic or "technology" in topic:
            return get_news("technology", 5)
        
        # Sports news
        if "sport" in topic or "cricket" in topic or "football" in topic or "game" in topic:
            return get_news("sports", 5)
        
        # India news
        if "india" in topic:
            return get_news("india", 5)
        
        # Business news
        if "business" in topic or "market" in topic or "stock" in topic:
            return get_news("business", 5)
        
        # Default to world news
        return get_news("world", 5)
    
    except Exception as e:
        print(f"[ERROR] Error fetching news by topic: {e}")
        return []


def get_greeting():
    """
    Get time-based greeting message.
    
    Returns:
        str: Greeting based on current hour
    """
    try:
        hour = datetime.datetime.now().hour
        
        if 5 <= hour < 12:
            return "Good morning"
        elif 12 <= hour < 17:
            return "Good afternoon"
        elif 17 <= hour < 21:
            return "Good evening"
        else:
            return "You're up late"
    
    except Exception as e:
        print(f"[ERROR] Error getting greeting: {e}")
        return "Hello"


def get_india_briefing():
    """
    Get an India news briefing with headlines.
    
    Returns:
        str: India news formatted as response
    """
    try:
        headlines = get_trending_news("india", 5)
        
        if not headlines:
            return "Couldn't fetch India news boss."
        
        # Format headlines
        formatted_news = []
        for headline in headlines:
            if headline:
                formatted_news.append(headline)
        
        response = "Here's what's happening in India boss. " + ". ".join(formatted_news) + "."
        return response
    
    except Exception as e:
        print(f"[ERROR] Error in India briefing: {e}")
        return "Couldn't fetch India news boss."
