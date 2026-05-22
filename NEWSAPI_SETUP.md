# NewsAPI Setup Guide

## Problem Fixed
❌ Old: API key was set to `"public"` → 401 Unauthorized errors  
✅ New: API key now loaded from `config.py` → Proper authentication

---

## How to Get Your Free API Key

### Step 1: Go to NewsAPI.org
Visit: https://newsapi.org/

### Step 2: Sign Up (Free)
- Click "Get API Key" 
- Sign up with email or GitHub
- Verify your email
- You'll get your **free API key**

### Step 3: Copy Your API Key
You'll see a key like: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`

---

## Configure FRIDAY

### Update `config.py`
Open `config.py` and find this line:
```python
NEWSAPI_KEY = "YOUR_API_KEY_HERE"  # Replace with your actual API key from newsapi.org
```

Replace `YOUR_API_KEY_HERE` with your actual key:
```python
NEWSAPI_KEY = "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
```

**That's it!** No other changes needed.

---

## What You Get (Free Tier)

| Feature | Limit |
|---------|-------|
| Requests per day | 100 |
| Countries | All (including India 🇮🇳) |
| Categories | All (general, business, sports, tech, etc.) |
| Search | 30 days lookback |
| Latency | ~500ms per request |
| HTTPS | ✅ Yes |

---

## How It's Used in FRIDAY

### India News
```python
country = "in"  # Uses country code
```

### Global News  
```python
country = "us"  # Default global news
```

Both automatically use your **authenticated API key** from `config.py`.

---

## Verify It's Working

### Test command:
```bash
python -c "from actions.news_reader import get_world_briefing; print(get_world_briefing())"
```

### Expected output:
- Should show Indian headlines + summaries
- Should show Global headlines + summaries  
- No 401 errors

### If still getting 401:
1. Check your API key is correct in `config.py`
2. Verify it at: https://newsapi.org/ (logged in)
3. Ensure no extra spaces in the key

---

## How Authentication Works Now

```
config.py:
  NEWSAPI_KEY = "your_actual_key"
         ↓
news_reader.py:
  from config import Config
  NEWSAPI_KEY = Config.NEWSAPI_KEY
         ↓
API Request:
  params = {"apiKey": NEWSAPI_KEY, ...}
         ↓
Response: 200 OK ✅
```

---

## Future: Environment Variables (Optional)

If you want extra security, you can also use environment variables:

**In `.env` file:**
```
NEWSAPI_KEY=your_actual_key
```

**In `config.py`:**
```python
import os
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "YOUR_API_KEY_HERE")
```

But for now, storing in `config.py` is fine for local development.

---

## Troubleshooting

| Error | Solution |
|-------|----------|
| 401 Unauthorized | Check API key in config.py |
| 429 Too Many Requests | You've hit daily limit (100 requests) |
| Connection timeout | newsapi.org server issue (try again later) |
| Empty results | Category/country combo has no news |

---

## That's All!
Once you add your API key to `config.py`, your news system will work perfectly with:
- ✅ Real-time India news
- ✅ Real-time Global news  
- ✅ Hybrid 80/20 priority
- ✅ Smart World Monitor opening
- ✅ No authentication errors

Enjoy! 🚀
