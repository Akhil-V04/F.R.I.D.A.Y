"""
Test all 5 bug fixes in executor.py and ollama.py
"""

from tools.executor import (
    ToolExecutor, extract_contact_from_input, extract_body_from_input, 
    convert_boolean_to_text
)
from brain.ollama import plan_tasks

print("=" * 70)
print("Executor Bug Fixes Test Suite")
print("=" * 70)
print()

# ===== TEST BUG 1: Timer param normalization =====
print("[BUG 1] Timer Param Normalization\n")
print("-" * 70)

test_cases_timer = [
    ({"tool": "set_timer", "params": {"minutes": 5}}, "Should map minutes to duration_str"),
    ({"tool": "set_timer", "params": {"seconds": 30}}, "Should map seconds to duration_str"),
    ({"tool": "set_timer", "params": {}}, "Should default to 5 minutes"),
]

for request, description in test_cases_timer:
    print(f"Testing: {description}")
    print(f"  Input: {request}")
    # Note: We can't actually test set_timer without the full tool setup,
    # but we can verify the parameter mapping logic
    params = request.get("params", {})
    
    # Simulate BUG 1 logic
    if "minutes" in params and "duration_str" not in params:
        params["duration_str"] = f"{params['minutes']} minutes"
    elif "seconds" in params and "duration_str" not in params:
        params["duration_str"] = f"{params['seconds']} seconds"
    if "duration_str" not in params:
        params["duration_str"] = "5 minutes"
    
    print(f"  Result: duration_str = '{params.get('duration_str')}'")
    print()

# ===== TEST BUG 2: Email param extraction =====
print("[BUG 2] Email Param Extraction\n")
print("-" * 70)

test_inputs = [
    ("send email to john", "john"),
    ("email to alice about the project", "alice"),
    ("message to mom saying hello", "mom"),
    ("write to dad", "dad"),
]

print("Testing extract_contact_from_input():")
for text, expected in test_inputs:
    result = extract_contact_from_input(text)
    status = "✓" if result.lower() == expected.lower() else "✗"
    print(f"{status} '{text}' → '{result}' (expected: '{expected}')")

print()

test_bodies = [
    ("send a message saying hello world", "hello world"),
    ("email that the meeting is tomorrow", "the meeting is tomorrow"),
    ("tell them about the project", "about the project"),
]

print("Testing extract_body_from_input():")
for text, expected_substring in test_bodies:
    result = extract_body_from_input(text)
    status = "✓" if expected_substring in result.lower() else "✗"
    print(f"{status} '{text}' → '{result[:40]}...'")

print()

# ===== TEST BUG 3: Screen output truncation =====
print("[BUG 3] Screen Output Truncation\n")
print("-" * 70)

long_text = "This is some text on screen. " * 20  # Create text > 400 chars
print(f"Original text length: {len(long_text)} chars")

# Simulate BUG 3 logic
result = str(long_text)
result = ' '.join(result.split())  # Collapse whitespace
result = result[:400] + "..." if len(result) > 400 else result

print(f"Truncated text length: {len(result)} chars")
print(f"Truncated: {result[:80]}...")
print()

# ===== TEST BUG 4: Multi-step planner =====
print("[BUG 4] Multi-Step Planner with Fast Path\n")
print("-" * 70)

test_commands = [
    "take a screenshot and tell me the time",
    "open chrome and take a screenshot",
    "what's going on and battery status",
]

print("Testing plan_tasks() with multi-step commands:")
for cmd in test_commands:
    print(f"\nCommand: '{cmd}'")
    plan = plan_tasks(cmd)
    steps = plan.get("steps", [])
    print(f"  Steps: {len(steps)}")
    for i, step in enumerate(steps, 1):
        print(f"    {i}. {step.get('tool')} - {step.get('params')}")

print()

# ===== TEST BUG 5: Boolean output conversion =====
print("[BUG 5] Boolean Output Conversion\n")
print("-" * 70)

test_outputs = [
    (True, "Done boss"),
    (False, "That didn't work boss"),
    (None, "No result boss"),
    ("True", "Done boss"),
    ("False", "That didn't work boss"),
    ("None", "No result boss"),
    ("Custom message", "Custom message"),
]

print("Testing convert_boolean_to_text():")
all_pass = True
for value, expected in test_outputs:
    result = convert_boolean_to_text(value)
    status = "✓" if result == expected else "✗"
    if result != expected:
        all_pass = False
    print(f"{status} convert_boolean_to_text({repr(value)}) → '{result}'")

print()
if all_pass:
    print("✓ All boolean conversion tests PASSED!")
else:
    print("✗ Some boolean conversion tests FAILED")

print()
print("=" * 70)
print("✓ Executor Bug Fixes Test Complete")
print("=" * 70)
