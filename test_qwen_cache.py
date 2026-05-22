"""
Test SmartCache integration in qwen_executor.py
Verifies cache hit/miss behavior for command execution
"""

from brain.qwen_executor import _cache
import json

print("=" * 60)
print("SmartCache Integration Test for Qwen Executor")
print("=" * 60)
print()

# Pre-populate cache with test commands
print("[SETUP] Pre-populating cache with test commands...")
test_commands = [
    ("open chrome", "Chrome opened", "open_app", 120),
    ("open firefox", "Firefox opened", "open_app", 115),
    ("take a screenshot", "Screenshot saved to Desktop", "take_screenshot", 250),
    ("what time is it", "It's 3:45 PM", "get_time", 50),
]

for cmd, result, tool, response_ms in test_commands:
    _cache.set(cmd, result, tool, response_ms=response_ms)

print(f"✓ Added {len(test_commands)} commands to cache")
print()

# Test cache retrieval
print("[TEST 1] Cache Retrieval (Exact Match)")
print("-" * 60)
cached = _cache.get("open chrome")
if cached:
    print(f"✓ Found in cache: {cached['result']}")
    print(f"  Tool: {cached['tool']}")
    print(f"  Usage count: {cached['usage_count']}")
    print(f"  Avg response time: {cached['avg_response_ms']}ms")
else:
    print("✗ NOT found in cache")
print()

# Test fuzzy matching
print("[TEST 2] Fuzzy Matching (85%+ similarity)")
print("-" * 60)
test_variations = [
    "please open chrome",
    "hey open chrome boss",
    "can you open chrome",
    "OPEN CHROME",
]

for variation in test_variations:
    cached = _cache.get(variation)
    if cached:
        print(f"✓ Matched: '{variation}' -> {cached['result']}")
    else:
        print(f"✗ Not matched: '{variation}'")
print()

# Test NO_CACHE_TOOLS
print("[TEST 3] Tools That Should NOT Be Cached")
print("-" * 60)
print("NO_CACHE_TOOLS:", end=" ")
from brain.qwen_executor import NO_CACHE_TOOLS
print(NO_CACHE_TOOLS)
print()
print("These tools will skip cache storage (real-time data):")
for tool in NO_CACHE_TOOLS:
    print(f"  - {tool}")
print()

# Test cache statistics
print("[TEST 4] Cache Statistics")
print("-" * 60)
print(_cache.get_stats())
print()
print(f"Cache size: {_cache.get_size()} entries")
print(f"Most used commands: {_cache.get_most_used(limit=3)}")
print()

# Show cache file
print("[TEST 5] Cache File Contents (Sample)")
print("-" * 60)
try:
    with open("memory/command_cache.json", "r") as f:
        cache_data = json.load(f)
    
    # Show first 3 entries
    shown = 0
    for key, value in cache_data.items():
        if shown >= 3:
            break
        print(f"Key: {key}")
        
        # Handle both new and legacy cache formats
        result = value.get('result') or value.get('response', 'N/A')
        tool = value.get('tool') or value.get('action', 'N/A')
        usage = value.get('usage_count') or value.get('count', 0)
        
        if isinstance(result, str):
            result_str = result[:60] + "..." if len(result) > 60 else result
        else:
            result_str = str(result)[:60] + "..."
        
        print(f"  Result: {result_str}")
        print(f"  Tool: {tool}")
        print(f"  Usage: {usage} times")
        print()
        shown += 1
    
    print(f"Total cached entries: {len(cache_data)}")
except Exception as e:
    print(f"Error reading cache file: {e}")
print()

print("=" * 60)
print("✓ SmartCache Integration Test Complete")
print("=" * 60)
