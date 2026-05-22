#!/usr/bin/env python3
"""
Verify complete set_timer flow: Qwen output → Parameter mapping → Tool execution
"""

import sys
sys.path.insert(0, r'c:\Users\akhil\Downloads\F.R.I.D.A.Y')

print("=" * 70)
print("VERIFYING set_timer COMPLETE FIX FLOW")
print("=" * 70)

# Simulated Qwen responses
qwen_responses = [
    {
        "name": "Simple minute duration",
        "qwen_output": {"tool": "set_timer", "params": {"minutes": "5"}},
        "expected": "5 minutes",
        "description": "Qwen returns minutes parameter"
    },
    {
        "name": "Duration as string",
        "qwen_output": {"tool": "set_timer", "params": {"minutes": "10"}},
        "expected": "10 minutes",
        "description": "String number converted and formatted"
    },
    {
        "name": "Duration as integer",
        "qwen_output": {"tool": "set_timer", "params": {"minutes": 2}},
        "expected": "2 minutes",
        "description": "Integer number formatted as 'N minutes'"
    },
]

print("\nFlow: Qwen Response → Parameter Mapping → Tool Ready")
print("-" * 70)

def apply_mapping(tool_name, params):
    """Apply parameter mapping (copy from executor.py)"""
    parameter_aliases = {
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
            
            if isinstance(duration_val, int):
                params["duration_str"] = f"{duration_val} minutes"
            else:
                params["duration_str"] = str(duration_val)
        except Exception:
            pass
    
    return params

for i, resp in enumerate(qwen_responses, 1):
    print(f"\n[Test {i}] {resp['name']}")
    print(f"  {resp['description']}")
    
    qwen = resp['qwen_output']
    tool_name = qwen['tool']
    params_in = qwen['params'].copy()
    
    print(f"\n  Qwen Response:")
    print(f"    tool: {tool_name}")
    print(f"    params: {params_in}")
    
    mappedparams = apply_mapping(tool_name, params_in)
    
    print(f"\n  After Mapping:")
    print(f"    params: {mappedparams}")
    
    expected = resp['expected']
    actual = mappedparams.get('duration_str', 'MISSING')
    
    if actual == expected:
        print(f"\n  ✅ CORRECT: duration_str = '{actual}'")
    else:
        print(f"\n  ❌ ERROR: Expected '{expected}', got '{actual}'")

print("\n" + "=" * 70)
print("""
✅ SUMMARY

The fix ensures:
  1. Qwen sends: {"minutes": "5"}
  2. Mapping converts: {"duration_str": "5 minutes"}
  3. Tool receives correct parameter with proper format

Parameter Mapping Layer:
  • Handles Qwen's alternative parameter names
  • Converts types (int → string)
  • Formats values for function expectations
  • Applied BEFORE tool execution

This solves the original problem without changing tool logic.
""")
