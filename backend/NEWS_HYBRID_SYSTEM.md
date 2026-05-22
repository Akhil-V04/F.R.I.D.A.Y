# Hybrid News System (Enhanced)

## Overview
Your news system now has **hybrid behavior** with 80/20 India-to-Global priority, automatic World Monitor opening, and deduplication.

---

## Changes Made

### 1. **Enhanced `get_world_briefing()` in `actions/news_reader.py`**
   - **What changed:** Implemented 80/20 priority (2 Indian + 1-2 Global headlines)
   - **Output order:** India headlines FIRST, then Global headlines
   - **Deduplication:** Prevents showing same story twice
   - **No breaking changes:** Still returns a formatted string

### 2. **World Monitor Integration in `main.py` (ALREADY IN PLACE)**
   ```python
   elif action == "world_briefing":
       speak_streaming("Give me a second boss, let me check...")
       response = get_world_briefing()        # Enhanced function
       open_world_monitor()                   # Opens if not already open
       response += " I've opened the World Monitor so you can track it visually boss."
   ```

### 3. **Smart Window Detection in `actions/web.py` (ALREADY IN PLACE)**
   ```python
   def open_world_monitor():
       # Checks tasklist to see if already open
       if "worldmonitor" in result.stdout.lower():
           return False  # Don't reopen
       webbrowser.open(WORLD_MONITOR_URL)
   ```

---

## How It Works

### When user says: "What's going on?" or "World briefing"

**Flow:**
1. Command parser → routes to `"world_briefing"` action
2. Main.py → Calls `get_world_briefing()` 
3. Enhanced function:
   - Fetches 3 India headlines
   - Fetches 3 Global headlines
   - Takes TOP 2 India headlines (80%)
   - Takes TOP 1-2 Global headlines (20%)
   - Removes duplicates
4. Returns formatted text (India first)
5. Opens World Monitor browser window
6. FRIDAY speaks the briefing

**Output example:**
```
"Here's what's happening in India boss. 
  [Indian headline 1]: [summary]. 
  [Indian headline 2]: [summary]. 
And globally boss. 
  [Global headline 1]: [summary]. 
  [Global headline 2]: [summary]."
```

---

## Configuration

### Priority Settings (in `news_reader.py`)
```python
india_news = get_trending_news("india", 3)  # Fetch 3, use 2
global_news = get_trending_news("global", 3) # Fetch 3, use 1-2

# Line 227: india_news[:2]     # Takes only 2 Indian headlines
# Line 241: global_count >= 2  # Takes max 2 global headlines
```

### Modify priorities:
- **More India content:** Change `india_news[:2]` to `india_news[:3]`
- **More global content:** Change `global_count >= 2` to `global_count >= 3`
- **Fewer headlines:** Change fetch from `(3)` to `(2)`

---

## Features

✅ **80/20 Priority** - 2 India headlines + 1-2 Global  
✅ **Smart Ordering** - India news spoken FIRST  
✅ **No Repetition** - Deduplication by title  
✅ **Window Check** - Don't reopen if already open  
✅ **Fast Execution** - 1-2 second API calls  
✅ **Real-time Data** - NewsAPI.org with RSS fallback  
✅ **Short Summaries** - 100-char max per headline  

---

## Integration Points

| Component | File | Function | Status |
|-----------|------|----------|--------|
| News fetching | `actions/news_reader.py` | `get_world_briefing()` | ✅ Enhanced |
| Main handler | `main.py` | `elif action == "world_briefing"` | ✅ Ready |
| Browser opening | `actions/web.py` | `open_world_monitor()` | ✅ Smart check |
| Command routing | `brain/command_parser.py` | Briefing phrases | ✅ Working |

---

## Testing

### Test the enhanced system:
```bash
# In Python:
from actions.news_reader import get_world_briefing
briefing = get_world_briefing()
print(briefing)
```

### Expected output:
```
"Here's what's happening in India boss. [Indian 1]: [summary]. [Indian 2]: [summary]. 
And globally boss. [Global 1]: [summary]."
```

---

## Future Enhancements

Optional additions:
- Time-based caching (don't refetch same news within 5 min)
- Topic filtering (skip certain categories)
- Sentiment analysis (highlight important stories)
- Custom priority weights (60/40, 75/25, etc.)

