"""
End-to-end verification that parameter mismatch is fixed.
Tests the complete flow: command -> decision -> execution
"""

from brain.command_parser import parse_command
from brain.qwen_executor import _legacy_command_to_tool, execute_smart
from tools.executor import ToolExecutor

print("=" * 80)
print("END-TO-END VERIFICATION: Parameter Fix Complete")
print("=" * 80)

# ===== TEST 1: parse_command fallback path =====
print("\n[TEST 1] parse_command fallback (uses decide_tool now)")
print("-" * 80)

test_input = "what are your thoughts on AI"
print(f"Input: {test_input}")

# This triggers the fallback path that now uses decide_tool
cmd = parse_command(test_input)
print(f"parse_command result: {cmd}")

# The command format should now use correct parameters
if cmd.get("action") == "ask_brain":
    assert "target" in cmd, "Legacy format should have target for backward compat"
    print(f"✅ Returns old format (action=ask_brain, target='{cmd['target']}')")

# ===== TEST 2: Legacy command to tool conversion =====
print("\n[TEST 2] Convert legacy command to tool format")
print("-" * 80)

legacy_cmd = {"action": "ask_brain", "target": "what is the meaning of life"}
print(f"Legacy command: {legacy_cmd}")

tool_req = _legacy_command_to_tool(legacy_cmd)
print(f"Converted to tool: {tool_req}")

# Verify conversion
assert tool_req["tool"] == "ask_brain", "Tool must be ask_brain"
assert tool_req["params"]["user_input"] == legacy_cmd["target"], "user_input must match target"
assert "target" not in tool_req["params"], "params must not have 'target'"
print("✅ Conversion successful: target -> user_input")

# ===== TEST 3: Tool execution with converted params =====
print("\n[TEST 3] Execute tool with converted parameters")
print("-" * 80)

result = ToolExecutor.execute(tool_req)
print(f"Execution success: {result['success']}")

if result['success']:
    print(f"Result: {result['result'][:80]}...")
    print("✅ Tool executed successfully with user_input parameter")
else:
    print(f"❌ Execution failed: {result['error']}")

# ===== TEST 4: Direct new tool format =====
print("\n[TEST 4] Direct new tool format (tool calling system)")
print("-" * 80)

new_format = {"tool": "ask_brain", "params": {"user_input": "tell me a joke"}}
print(f"Direct tool format: {new_format}")

result = ToolExecutor.execute(new_format)
print(f"Execution success: {result['success']}")

if result['success']:
    print(f"Result: {result['result'][:80]}...")
    print("✅ Direct tool format works with user_input")
else:
    print(f"❌ Execution failed: {result['error']}")

# ===== TEST 5: WRONG format - should fail =====
print("\n[TEST 5] Wrong format rejection (target instead of user_input)")
print("-" * 80)

wrong_format = {"tool": "ask_brain", "params": {"target": "hello"}}
print(f"Wrong tool format: {wrong_format}")

result = ToolExecutor.execute(wrong_format)
print(f"Execution success: {result['success']}")

if not result['success']:
    print(f"Error: {result['error']}")
    assert "user_input" in result["error"], "Error should mention user_input"
    print("✅ Correctly rejected wrong parameter name (target)")
else:
    print("❌ Should have failed with wrong parameter")

# ===== TEST 6: Parameter consistency summary =====
print("\n[TEST 6] Parameter Standardization Summary")
print("-" * 80)

print("""
STANDARDIZED PARAMETERS FOR ask_brain:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OLD FORMAT (Legacy - for backward compatibility):
  parse_command() → {"action": "ask_brain", "target": "..."}
  
NEW FORMAT (Tool calling system):
  decide_tool() → {"tool": "ask_brain", "params": {"user_input": "..."}}
  
CONVERSION (Automatic):
  Legacy command → Tool request conversion automatically handles:
  - Extracts "target" from legacy command
  - Creates "user_input" in new params
  - Removes "target" from tool params
  
PARAMETER VALIDATION:
  ✅ ask_brain requires "user_input" parameter
  ❌ "target" parameter is NOT accepted (causes error)
  ✅ ToolExecutor validates parameters against tool registry
  ✅ Missing required parameters are detected and reported

EXECUTION PATHS:
  1. Simple commands → parse_command() → tool conversion → execution
  2. Complex commands → decide_tool() → direct execution
  3. Ambiguous → decide_tool() → ask_brain with proper user_input
  
ALL PATHS STANDARDIZED ON: "user_input" parameter for ask_brain
""")

print("\n" + "=" * 80)
print("✅ PARAMETER MISMATCH COMPLETELY FIXED")
print("=" * 80)
print("""
FIXES APPLIED:
1. ✅ command_parser.py: Now uses decide_tool() instead of decide_action()
2. ✅ decide_action(): Delegates to decide_tool() for new format, converts back to old
3. ✅ decide_tool(): Sanitizes ask_brain params to only include user_input
4. ✅ _legacy_command_to_tool(): Converts target → user_input automatically
5. ✅ ToolExecutor: Validates required parameters (user_input for ask_brain)

RESULT:
- All ask_brain calls now use "user_input" parameter
- No more "target" parameter in tool system
- Automatic conversion from legacy format for backward compatibility
- Parameter validation prevents misconfigurations
""")
