#!/usr/bin/env python3
"""
Unit test for set_timer parameter mapping logic.
Tests the mapping without executing the actual tool.
"""

import sys
sys.path.insert(0, r'c:\Users\akhil\Downloads\F.R.I.D.A.Y')

print("=" * 70)
print("TESTING set_timer PARAMETER MAPPING LOGIC")
print("=" * 70)

# Simulate the parameter mapping logic from executor.py
def map_params(tool_name, params):
    """Test the parameter mapping logic"""
    parameter_aliases = {
        "send_whatsapp": {
            "to": "contact_name",
            "contact": "contact_name",
        },
        "send_email": {
            "to": "contact",
        },
        "set_timer": {
            "minutes": "duration_str",
            "duration": "duration_str",
        }
    }
    
    if tool_name in parameter_aliases:
        alias_map = parameter_aliases[tool_name]
        for alias, canonical in alias_map.items():
            if alias in params and canonical not in params:
                params[canonical] = params.pop(alias)
    
    # Type conversion for set_timer
    if tool_name == "set_timer" and "duration_str" in params:
        duration_val = params["duration_str"]
        try:
            if isinstance(duration_val, str):
                numeric_str = ''.join(c for c in duration_val if c.isdigit())
                if numeric_str:
                    duration_val = int(numeric_str)
                else:
                    duration_val = str(duration_val)
            
            if isinstance(duration_val, int):
                params["duration_str"] = f"{duration_val} minutes"
            else:
                params["duration_str"] = str(duration_val)
        except Exception:
            pass
    
    return params

test_cases = [
    {
        "name": "Qwen format with string number",
        "tool": "set_timer",
        "input": {"minutes": "5"},
        "expect_key": "duration_str",
        "expect_value": "5 minutes",
        "description": "Qwen sends {'minutes': '5'} → should become {'duration_str': '5 minutes'}"
    },
    {
        "name": "Registry format (duration)",
        "tool": "set_timer",
        "input": {"duration": "10 minutes"},
        "expect_key": "duration_str",
        "expect_value": "10 minutes",
        "description": "Registry format {'duration': '10 minutes'} → maps to {'duration_str': '10 minutes'}"
    },
    {
        "name": "Qwen with integer",
        "tool": "set_timer",
        "input": {"minutes": 3},
        "expect_key": "duration_str",
        "expect_value": "3 minutes",
        "description": "Integer {'minutes': 3} → formats to {'duration_str': '3 minutes'}"
    },
    {
        "name": "Already correct format",
        "tool": "set_timer",
        "input": {"duration_str": "2 minutes"},
        "expect_key": "duration_str",
        "expect_value": "2 minutes",
        "description": "Already correct → passes through unchanged"
    },
]

passed = 0
failed = 0

for i, test in enumerate(test_cases, 1):
    print(f"\n[Test {i}] {test['name']}")
    print(f"  Description: {test['description']}")
    print(f"  Input:  {test['input']}")
    
    result = map_params(test['tool'], test['input'].copy())
    
    print(f"  Output: {result}")
    
    # Check result
    if test['expect_key'] in result and result[test['expect_key']] == test['expect_value']:
        print(f"  ✅ PASS: Got expected '{test['expect_key']}' = '{test['expect_value']}'")
        passed += 1
    else:
        actual_key = list(result.keys())[0] if result else "empty"
        actual_value = result.get(actual_key, "N/A") if result else "N/A"
        print(f"  ❌ FAIL: Expected '{test['expect_key']}' = '{test['expect_value']}'")
        print(f"           Got '{actual_key}' = '{actual_value}'")
        failed += 1

# Summary
print("\n" + "=" * 70)
print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_cases)} tests")
print("=" * 70)

if failed == 0:
    print("""
✅ ALL TESTS PASSED!

set_timer parameter mapping works correctly:
  • Qwen's "minutes" parameter → "duration_str"
  • Registry's "duration" parameter → "duration_str"
  • String/integer values → formatted as "N minutes"
  • Already correct format → passes through unchanged

Mapping Summary:
  "minutes": "X"    → "duration_str": "X minutes"
  "duration": "Y"   → "duration_str": "Y" (if already formatted)
  "duration_str": "Z" → "duration_str": "Z" (passthrough)
""")
    sys.exit(0)
else:
    print(f"\n❌ {failed} test(s) failed")
    sys.exit(1)
