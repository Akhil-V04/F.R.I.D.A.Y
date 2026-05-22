"""
Test multi-step command detection fixes
"""

from brain.qwen_executor import detect_multi_step_command

print("=" * 70)
print("MULTI-STEP DETECTION TEST")
print("=" * 70)

# Test cases - these should be detected as multi-step
multi_step_cases = [
    "open chrome and take a screenshot",
    "open notepad and write hello",
    "send message and open chrome",
    "take screenshot and send it",
    "open chrome then search google",
    "open chrome and then take screenshot",
    "send message after opening chrome",
    "create a file, then open it",
]

# Test cases - these should NOT be detected as multi-step
single_step_cases = [
    "open chrome",
    "take a screenshot",
    "send message to john",
    "get the time",
    "close all apps",
    "what is the weather",
    "tell me a joke",
]

print("\n✓ MULTI-STEP COMMANDS (should be True):")
print("-" * 70)
all_correct = True
for cmd in multi_step_cases:
    result = detect_multi_step_command(cmd)
    status = "✅" if result else "❌"
    print(f"{status} '{cmd}' → {result}")
    if not result:
        all_correct = False

print("\n✓ SINGLE-STEP COMMANDS (should be False):")
print("-" * 70)
for cmd in single_step_cases:
    result = detect_multi_step_command(cmd)
    status = "✅" if not result else "❌"
    print(f"{status} '{cmd}' → {result}")
    if result:
        all_correct = False

print("\n" + "=" * 70)
if all_correct:
    print("✅ ALL TESTS PASSED - Detection working correctly!")
else:
    print("⚠️  SOME TESTS FAILED - See above")
print("=" * 70)
