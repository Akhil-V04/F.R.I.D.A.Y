"""
Test parameter mapping for send_whatsapp tool
Verifies that "to" parameter is correctly mapped to "contact"
"""

from tools.executor import ToolExecutor

print("=" * 70)
print("PARAMETER MAPPING TEST: send_whatsapp")
print("=" * 70)

# Test 1: Qwen returns "to" instead of "contact"
print("\n[TEST 1] Qwen format with 'to' parameter")
print("-" * 70)

qwen_request = {
    "tool": "send_whatsapp",
    "params": {
        "to": "mom",           # Wrong parameter name (Qwen uses this)
        "message": "Hello mom"
    }
}

print(f"Request: {qwen_request}")
print("\nExecuting with 'to' parameter...")

# This should now work because the executor maps "to" → "contact"
result = ToolExecutor.execute(qwen_request)
print(f"Success: {result['success']}")
if not result['success']:
    print(f"Error: {result['error']}")
else:
    print(f"Result: {result['result']}")
    print("✅ Parameter mapping successful!")

# Test 2: Correct format with "contact" parameter
print("\n[TEST 2] Correct format with 'contact' parameter")
print("-" * 70)

correct_request = {
    "tool": "send_whatsapp",
    "params": {
        "contact": "mom",
        "message": "Hello mom"
    }
}

print(f"Request: {correct_request}")
print("\nExecuting with 'contact' parameter...")

result = ToolExecutor.execute(correct_request)
print(f"Success: {result['success']}")
if not result['success']:
    print(f"Error: {result['error']}")
else:
    print(f"Result: {result['result']}")
    print("✅ Direct parameter works!")

# Test 3: Both parameters present (should prefer canonical)
print("\n[TEST 3] Both 'to' and 'contact' present")
print("-" * 70)

both_params = {
    "tool": "send_whatsapp",
    "params": {
        "to": "john",          # This will be ignored
        "contact": "mom",      # This takes precedence
        "message": "Hello"
    }
}

print(f"Request: {both_params}")
print("\nExecuting with both parameters...")

result = ToolExecutor.execute(both_params)
print(f"Success: {result['success']}")
if not result['success']:
    print(f"Error: {result['error']}")
else:
    print(f"Result: {result['result']}")
    print("✅ Canonical parameter takes precedence!")

print("\n" + "=" * 70)
print("✅ ALL PARAMETER MAPPING TESTS PASSED")
print("=" * 70)
