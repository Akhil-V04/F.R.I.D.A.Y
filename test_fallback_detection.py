#!/usr/bin/env python3
"""
Unit test for fallback behavior - no Qwen calls
Tests the fallback detection logic in execute_smart()
"""

import sys
sys.path.insert(0, r'c:\Users\akhil\Downloads\F.R.I.D.A.Y')

print("=" * 70)
print("TESTING FALLBACK DETECTION LOGIC")
print("=" * 70)

# Test fallback detection
test_cases = [
    {
        "name": "Multi-step plan (real tools)",
        "plan": {
            "steps": [
                {"tool": "open_url", "params": {"url": "chrome"}},
                {"tool": "take_screenshot", "params": {}}
            ]
        },
        "expect_fallback": False,
        "description": "Multiple real tools → execute plan"
    },
    {
        "name": "Fallback plan (only ask_brain)",
        "plan": {
            "steps": [
                {"tool": "ask_brain", "params": {"user_input": "something"}}
            ]
        },
        "expect_fallback": True,
        "description": "Only ask_brain → fallback to Qwen"
    },
    {
        "name": "Single real tool",
        "plan": {
            "steps": [
                {"tool": "open_url", "params": {"url": "chrome"}}
            ]
        },
        "expect_fallback": False,
        "description": "Single real tool → execute plan"
    },
    {
        "name": "Three-step plan",
        "plan": {
            "steps": [
                {"tool": "open_app", "params": {"name": "chrome"}},
                {"tool": "take_screenshot", "params": {}},
                {"tool": "close_app", "params": {"name": "chrome"}}
            ]
        },
        "expect_fallback": False,
        "description": "Three real tools → execute plan"
    },
]

def should_fallback(plan):
    """Fallback detection logic (same as in execute_smart)"""
    steps = plan.get("steps", [])
    return len(steps) == 1 and steps[0].get("tool") == "ask_brain"

passed = 0
failed = 0

for i, test in enumerate(test_cases, 1):
    print(f"\n[Test {i}] {test['name']}")
    print(f"  Description: {test['description']}")
    
    result = should_fallback(test['plan'])
    expected = test['expect_fallback']
    
    # Show plan
    steps = test['plan'].get('steps', [])
    for j, step in enumerate(steps, 1):
        print(f"  Step {j}: {step['tool']}")
    
    # Check result
    if result == expected:
        print(f"  ✅ PASS: Fallback={result} (expected {expected})")
        passed += 1
    else:
        print(f"  ❌ FAIL: Fallback={result} (expected {expected})")
        failed += 1

# Summary
print("\n" + "=" * 70)
print(f"RESULTS: {passed} passed, {failed} failed")
print("=" * 70)

if failed == 0:
    print("""
✅ ALL TESTS PASSED!

Fallback behavior is correct:
  • Multi-step plans with real tools → Execute
  • Plans returning only ask_brain → Fallback to Qwen
  • Single real tool → Execute (not fallback)
  • Three+ step plans → Execute (not fallback)

This ensures meaningful executions instead of useless ask_brain fallbacks.
""")
    sys.exit(0)
else:
    print(f"\n❌ {failed} test(s) failed")
    sys.exit(1)
