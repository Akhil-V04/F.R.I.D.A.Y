"""
Test execute_smart routing with debug output
"""

from brain.qwen_executor import execute_smart

print("=" * 80)
print("EXECUTE_SMART ROUTING TEST WITH DEBUG OUTPUT")
print("=" * 80)

test_commands = [
    # Fast path cases (simple, direct)
    ("open chrome", "FAST PATH"),
    ("get the time", "FAST PATH"),
    ("take a screenshot", "FAST PATH"),
    
    # Multi-step path cases
    ("open chrome and take a screenshot", "MULTI-STEP PATH"),
    ("open notepad and write hello", "MULTI-STEP PATH"),
    ("send message and open chrome", "MULTI-STEP PATH"),
    
    # Qwen path cases (complex/ambiguous)
    ("what is the capital of france", "QWEN PATH"),
    ("tell me something interesting", "QWEN PATH"),
]

print("\nTesting routing decisions (watching debug output):")
print("-" * 80)

for cmd, expected_path in test_commands:
    print(f"\n📝 Command: '{cmd}'")
    print(f"   Expected: {expected_path}")
    print("   Debug output:")
    print("   " + "-" * 76)
    
    # This will print debug logs showing which path is taken
    try:
        result = execute_smart(cmd)
        # We're not checking the actual result, just the debug path chosen
    except Exception as e:
        print(f"   (Error occurred, but routing was determined)")
    
    print("   " + "-" * 76)

print("\n" + "=" * 80)
print("✅ Routing test complete - check debug output above for path selection")
print("=" * 80)
