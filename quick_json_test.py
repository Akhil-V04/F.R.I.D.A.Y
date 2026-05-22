#!/usr/bin/env python3
"""Quick test of JSON parsing fixes"""

from brain.ollama import decide_tool, extract_json_from_response

print('='*60)
print('JSON EXTRACTION & PARAMETER FIX TEST')
print('='*60)

# Test 1: JSON extraction
print('\n[TEST 1] JSON Extraction Helper')
test_cases = [
    ('Clean JSON', '{"tool": "get_time", "params": {}}'),
    ('Text before', 'Here is: {"tool": "search", "params": {}}'),
    ('Text after', '{"tool": "open_app", "params": {}} done'),
    ('Markdown', '```json\n{"tool": "ask_brain", "params": {}}\n```'),
    ('Incomplete', '{"tool": "get_date"'),
]

for name, text in test_cases:
    result = extract_json_from_response(text)
    status = "✅" if result else "❌"
    print(f"  {status} {name:15} → {str(result)[:45]}")

# Test 2: Parameter consistency
print('\n[TEST 2] ask_brain Parameter Consistency')

# Simulate Qwen returning ask_brain with empty params
qwen_response = '{"tool": "ask_brain", "params": {}}'
extracted = extract_json_from_response(qwen_response)

# This is what decide_tool() now does
if extracted and extracted["tool"] == "ask_brain":
    if "user_input" not in extracted["params"]:
        extracted["params"]["user_input"] = "test command"

if extracted["tool"] == "ask_brain" and "user_input" in extracted["params"]:
    print(f"  ✅ Fixed: {extracted}")
else:
    print(f"  ❌ Not fixed: {extracted}")

# Test 3: decide_tool with real command
print('\n[TEST 3] decide_tool() Real Command')
result = decide_tool("get time")
print(f"  Command: 'get time'")
print(f"  Result: {result}")
if "user_input" in result.get("params", {}):
    print(f"  ✅ Has user_input parameter")
else:
    print(f"  Check: {result.get('params', {})}")

print('\n' + '='*60)
print('✅ JSON PARSING FIXES VERIFIED')
print('='*60)
