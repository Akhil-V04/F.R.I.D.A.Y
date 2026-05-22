#!/usr/bin/env python3
"""
Test script to verify plan_tasks() generates real multi-step actions
"""

import sys
sys.path.insert(0, r'c:\Users\akhil\Downloads\F.R.I.D.A.Y')

from brain.ollama import plan_tasks

# Test cases
test_cases = [
    {
        "input": "open chrome and take screenshot",
        "expected_step_count": 2,
        "description": "Basic multi-step with 'and'"
    },
    {
        "input": "open notepad and write hello",
        "expected_step_count": 2,
        "description": "Multi-step with action verbs"
    },
    {
        "input": "open browser then search google for weather",
        "expected_step_count": 2,
        "description": "Multi-step with 'then'"
    },
    {
        "input": "open spotify and play music",
        "expected_step_count": 2,
        "description": "Multi-step app control"
    },
    {
        "input": "take screenshot",
        "expected_step_count": 1,
        "description": "Single-step command (no splitting)"
    },
    {
        "input": "open chrome and then take screenshot and close app",
        "expected_step_count": 3,
        "description": "Three-step command with 'and then'"
    },
]

print("=" * 70)
print("TESTING plan_tasks() - REAL MULTI-STEP ACTION GENERATION")
print("=" * 70)

passed = 0
failed = 0

for i, test in enumerate(test_cases, 1):
    user_input = test["input"]
    expected_steps = test["expected_step_count"]
    description = test["description"]
    
    print(f"\n[Test {i}] {description}")
    print(f"Input: '{user_input}'")
    
    try:
        result = plan_tasks(user_input)
        
        # Validate structure
        if "steps" not in result:
            print(f"❌ FAILED: Missing 'steps' key in result")
            failed += 1
            continue
        
        steps = result["steps"]
        
        # Check if it's still just ask_brain (the old broken behavior)
        if len(steps) == 1 and steps[0]["tool"] == "ask_brain":
            if expected_steps == 1:
                # This is expected for single-step commands
                print(f"✅ PASSED: Single step correctly identified")
                print(f"   Tool: {steps[0]['tool']}")
                passed += 1
            else:
                print(f"❌ FAILED: Got ask_brain fallback instead of real tools")
                print(f"   Expected {expected_steps} steps, got fallback")
                failed += 1
            continue
        
        # Check step count
        if len(steps) != expected_steps:
            print(f"❌ FAILED: Expected {expected_steps} steps, got {len(steps)}")
            for j, step in enumerate(steps, 1):
                print(f"   Step {j}: {step['tool']}")
            failed += 1
            continue
        
        # Display generated tools
        print(f"✅ PASSED: Generated {len(steps)} step(s)")
        for j, step in enumerate(steps, 1):
            tool = step.get("tool", "unknown")
            params = step.get("params", {})
            param_str = ", ".join(f"{k}={v}" for k, v in params.items()) if params else "no params"
            print(f"   Step {j}: {tool} ({param_str})")
        
        passed += 1
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        failed += 1

# Summary
print("\n" + "=" * 70)
print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_cases)} tests")
print("=" * 70)

if failed == 0:
    print("✅ ALL TESTS PASSED - plan_tasks() is generating real multi-step actions!")
    sys.exit(0)
else:
    print(f"❌ {failed} test(s) failed")
    sys.exit(1)
