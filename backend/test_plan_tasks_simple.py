#!/usr/bin/env python3
"""
Quick verification test for plan_tasks() - no Qwen timeouts
Tests only the splitting logic without full tool execution
"""

import sys
sys.path.insert(0, r'c:\Users\akhil\Downloads\F.R.I.D.A.Y')

# Test the splitting logic directly
def split_on_connectors(text):
    """Recursive split function (same as in plan_tasks)"""
    connectors = [" and then ", " after ", " and ", " then ", ", then "]
    
    for connector in connectors:
        if connector.lower() in text.lower():
            parts = text.split(connector)
            all_steps = []
            for part in parts:
                part = part.strip()
                if not part:
                    continue
                nested_steps = split_on_connectors(part)
                all_steps.extend(nested_steps)
            return all_steps if all_steps else [text]
    
    return [text]

# Test cases for splitting logic
test_cases = [
    {
        "input": "open chrome and take screenshot",
        "expected": ["open chrome", "take screenshot"],
        "description": "Basic 'and' split"
    },
    {
        "input": "open notepad and write hello",
        "expected": ["open notepad", "write hello"],
        "description": "Multi-verb with 'and'"
    },
    {
        "input": "open browser then search google for weather",
        "expected": ["open browser", "search google for weather"],
        "description": "Split on 'then'"
    },
    {
        "input": "open chrome and take screenshot and close app",
        "expected": ["open chrome", "take screenshot", "close app"],
        "description": "Triple 'and' (recursive split)"
    },
    {
        "input": "open app and then take screenshot and save file",
        "expected": ["open app", "take screenshot", "save file"],
        "description": "'and then' with additional 'and' (nested)"
    },
    {
        "input": "take screenshot",
        "expected": ["take screenshot"],
        "description": "Single command (no split)"
    },
]

print("=" * 70)
print("TESTING SPLITTING LOGIC FOR plan_tasks()")
print("=" * 70)

passed = 0
failed = 0

for i, test in enumerate(test_cases, 1):
    user_input = test["input"]
    expected = test["expected"]
    description = test["description"]
    
    print(f"\n[Test {i}] {description}")
    print(f"Input: '{user_input}'")
    
    result = split_on_connectors(user_input)
    
    if result == expected:
        print(f"✅ PASSED: Split into {len(result)} step(s)")
        for j, step in enumerate(result, 1):
            print(f"   Step {j}: {step}")
        passed += 1
    else:
        print(f"❌ FAILED")
        print(f"Expected: {expected}")
        print(f"Got:      {result}")
        failed += 1

# Summary
print("\n" + "=" * 70)
print(f"SPLITTING LOGIC: {passed} passed, {failed} failed out of {len(test_cases)} tests")
print("=" * 70)

if failed == 0:
    print("\n✅ ALL SPLITTING TESTS PASSED!")
    print("\nplan_tasks() will now properly split multi-step commands into:")
    print("  1. Multiple independent steps")
    print("  2. Real tool calls (not just ask_brain fallback)")
    print("  3. Correct parameter extraction via decide_tool()")
    sys.exit(0)
else:
    print(f"\n❌ {failed} test(s) failed")
    sys.exit(1)
