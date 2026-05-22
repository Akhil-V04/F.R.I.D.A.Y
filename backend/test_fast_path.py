"""
Test fast_path_check integration in command_parser.py and qwen_executor.py
"""

from brain.command_parser import fast_path_check
import time

print("=" * 70)
print("Fast Path Check Test - Direct Command Routing")
print("=" * 70)
print()

# Test cases: (user_input, expected_tool, expected_params)
test_cases = [
    # News/World Briefing
    ("what's going on", "get_world_briefing", {}),
    ("world news", "get_world_briefing", {}),
    ("tell me what's happening", "get_world_briefing", {}),
    ("news", "get_world_briefing", {}),
    
    # Time
    ("what time is it", "get_time", {}),
    ("time", "get_time", {}),
    ("tell me the time", "get_time", {}),
    
    # Date
    ("what's the date", "get_date", {}),
    ("today", "get_date", {}),
    ("what date is it", "get_date", {}),
    
    # Battery
    ("battery", "get_battery", {}),
    ("check charge", "get_battery", {}),
    ("battery level", "get_battery", {}),
    
    # Screenshot
    ("screenshot", "take_screenshot", {}),
    ("take a screenshot", "take_screenshot", {}),
    
    # Chrome
    ("open chrome", "open_app", {"app": "chrome"}),
    
    # Spotify
    ("open spotify", "open_app", {"app": "spotify"}),
    
    # Screen Read
    ("what do you see", "read_screen", {}),
    ("read screen", "read_screen", {}),
    ("screen", "read_screen", {}),
]

passed = 0
failed = 0

print("[TEST] Running fast_path_check tests...\n")
for user_input, expected_tool, expected_params in test_cases:
    result = fast_path_check(user_input)
    
    if result is None:
        print(f"✗ FAIL: '{user_input}'")
        print(f"  Expected: {expected_tool}")
        print(f"  Got: None\n")
        failed += 1
    else:
        tool = result.get("tool")
        params = result.get("params", {})
        
        if tool == expected_tool and params == expected_params:
            print(f"✓ PASS: '{user_input}' -> {tool}")
            passed += 1
        else:
            print(f"✗ FAIL: '{user_input}'")
            print(f"  Expected: {expected_tool} with params {expected_params}")
            print(f"  Got: {tool} with params {params}\n")
            failed += 1

print()
print("=" * 70)
print(f"Results: {passed} PASSED, {failed} FAILED out of {len(test_cases)} tests")
print("=" * 70)
print()

# Test execution time
print("[PERFORMANCE] Testing response time of fast_path_check...\n")
test_command = "what time is it"
iterations = 1000

start = time.time()
for _ in range(iterations):
    result = fast_path_check(test_command)
end = time.time()

total_time_ms = (end - start) * 1000
avg_time_ms = total_time_ms / iterations

print(f"Command: '{test_command}'")
print(f"Iterations: {iterations}")
print(f"Total time: {total_time_ms:.2f}ms")
print(f"Average time per call: {avg_time_ms:.4f}ms")
print(f"Target: < 100ms for single execution")
print(f"Status: {'✓ PASS' if avg_time_ms < 1 else '⚠ May need optimization'}")
print()

# Test that non-matching commands return None
print("[COVERAGE] Testing non-matching patterns (should return None)...\n")
non_matching = [
    "send me an email",
    "can you help me with coding",
    "set a timer for 5 minutes",
    "set an alarm for 7 am",
    "ask brain something",
]

none_count = 0
for cmd in non_matching:
    result = fast_path_check(cmd)
    if result is None:
        print(f"✓ Correctly returned None: '{cmd}'")
        none_count += 1
    else:
        print(f"✗ Unexpectedly matched: '{cmd}' -> {result}")

print()
print(f"Non-matching commands: {none_count}/{len(non_matching)} correctly returned None")
print()
print("=" * 70)
print("✓ Fast Path Check Integration Test Complete")
print("=" * 70)
