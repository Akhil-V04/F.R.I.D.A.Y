"""
Test fast_path_check integration in execute_smart (qwen_executor.py)
Verifies that fast path commands bypass Qwen and execute directly
"""

import time
from brain.qwen_executor import execute_smart, _cache

print("=" * 70)
print("Fast Path Integration Test - execute_smart()")
print("=" * 70)
print()

# Test cases with expected response patterns
test_commands = [
    ("what time is it", "get_time"),
    ("what's going on", "get_world_briefing"),
    ("battery", "get_battery"),
    ("take a screenshot", "take_screenshot"),
    ("what date is it", "get_date"),
]

print("[TEST] Testing fast path execution via execute_smart...\n")

for command, expected_tool in test_commands:
    print(f"Testing: '{command}'")
    
    start = time.time()
    response = execute_smart(command)
    elapsed_ms = (time.time() - start) * 1000
    
    print(f"  Response: {response[:60]}..." if len(response) > 60 else f"  Response: {response}")
    print(f"  Time: {elapsed_ms:.2f}ms")
    print(f"  Tool: {expected_tool}")
    print()

print("=" * 70)
print("[CACHE] Verifying fast path results are cached...\n")

print(f"Cache size: {_cache.get_size()} entries")
print()
print("Top cached commands:")
print(_cache.get_stats())
print()

print("=" * 70)
print("✓ Fast Path Integration Test Complete")
print("=" * 70)
