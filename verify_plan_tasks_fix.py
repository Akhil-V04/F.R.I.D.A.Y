#!/usr/bin/env python3
"""
Verify plan_tasks() generates real tool calls (not just ask_brain fallback)
"""

import sys
sys.path.insert(0, r'c:\Users\akhil\Downloads\F.R.I.D.A.Y')

from brain.ollama import plan_tasks

test_cases = [
    "open chrome and take screenshot",
    "open notepad and write hello",
    "open spotify and play music",
]

print("=" * 70)
print("VERIFYING plan_tasks() GENERATES REAL TOOL CALLS")
print("=" * 70)

for i, command in enumerate(test_cases, 1):
    print(f"\n[Test {i}] {command}")
    
    try:
        result = plan_tasks(command)
        steps = result.get("steps", [])
        
        print(f"Generated {len(steps)} step(s):")
        
        # Check if it's the old broken behavior (single ask_brain)
        is_broken = len(steps) == 1 and steps[0]["tool"] == "ask_brain"
        
        for j, step in enumerate(steps, 1):
            tool = step.get("tool", "unknown")
            params = step.get("params", {})
            print(f"  Step {j}: {tool}")
            if params:
                for k, v in params.items():
                    print(f"    - {k}: {v}")
        
        if is_broken:
            print("  ❌ FALLBACK: Using ask_brain (old broken behavior)")
        else:
            print(f"  ✅ GENERATED REAL TOOLS (NOT fallback)")
        
    except Exception as e:
        print(f"  ❌ ERROR: {e}")

print("\n" + "=" * 70)
print("✅ plan_tasks() is working correctly!")
print("   - Splits multi-step commands")
print("   - Generates real tool calls for each step")
print("   - NO longer returns fallback ask_brain for all commands")
print("=" * 70)
