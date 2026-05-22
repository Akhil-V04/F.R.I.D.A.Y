class Config:
    ASSISTANT_NAME = "FRIDAY"
    WAKE_WORDS = ["friday", "edith"]
    OLLAMA_MODEL = "qwen2.5:7b"
    OLLAMA_URL = "http://localhost:11434/api/generate"
    VOICE_RATE = 175
    VOICE_VOLUME = 1.0
    MEMORY_PATH = "memory/memory.json"
    WORLD_MONITOR_URL = "https://www.worldmonitor.app/?lat=20.0000&lon=0.0000&zoom=1.57&view=mena&timeRange=7d&layers=conflicts,hotspots,sanctions,weather,outages,natural,iranAttacks"
    
    # NewsAPI Configuration
    # Get free API key from: https://newsapi.org/
    # Free tier: 100 requests/day, includes India + Global news
    NEWSAPI_KEY = "YOUR_API_KEY_HERE"  # Replace with your actual API key from newsapi.org
    NEWSAPI_URL = "https://newsapi.org/v2/top-headlines"
