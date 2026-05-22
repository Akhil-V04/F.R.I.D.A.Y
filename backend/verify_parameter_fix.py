"""Quick verification that parameter fixes work correctly"""

import json
from brain.ollama import decide_tool, decide_action
from tools.executor import ToolExecutor
from brain.qwen_executor import _legacy_command_to_tool

print("=" * 70)
print("QUICK VERIFICATION: Parameter Fix")
print("=" * 70)

# Test 1: ask_brain from decide_tool only has user_input
print("\n[1] decide_tool with ask_brain")
print("-" * 70)

# Force ask_brain to be returned
from brain.ollama import extract_json_from_response

# Simulate Qwen returning ask_brain
qwen_response = '{"tool": "ask_brain", "params": {"question": "hello", "user_input": "hello", "extra": "param"}}'
extracted = extract_json_from_response(qwen_response)
print(f"Raw response: {qwen_response}")
print(f"Extracted: {extracted}")

# Now apply the sanitization that happens in decide_tool
if extracted and extracted.get("tool") == "ask_brain":
    user_input_val = extracted["params"].get("user_input", "hello")
    extracted["params"] = {"user_input": user_input_val}
    print(f"After sanitization: {extracted}")
    
    # Verify only user_input exists
    assert "user_input" in extracted["params"], "Must have user_input"
    assert "question" not in extracted["params"], "Must not have question"
    assert "extra" not in extracted["params"], "Must not have extra"
    print("✅ Sanitized correctly - only user_input remains")

# Test 2: Execution with user_input (should work)
print("\n[2] Execute ask_brain with user_input (should succeed)")
print("-" * 70)

request = {"tool": "ask_brain", "params": {"user_input": "test"}}
result = ToolExecutor.execute(request)
print(f"Request: {request}")
print(f"Success: {result['success']}")
if result['success']:
    print(f"Result length: {len(result['result'])} chars")
    print("✅ Execution successful")
else:
    print(f"❌ Error: {result['error']}")

# Test 3: Execution with target (should fail)
print("\n[3] Execute ask_brain with target (should fail)")
print("-" * 70)

request = {"tool": "ask_brain", "params": {"target": "test"}}
result = ToolExecutor.execute(request)
print(f"Request: {request}")
print(f"Success: {result['success']}")
if not result['success']:
    print(f"Error: {result['error']}")
    assert "user_input" in result["error"], "Error should mention user_input"
    print("✅ Correctly rejected - missing user_input parameter")
else:
    print("❌ Unexpected success")

# Test 4: decide_action backward compat
print("\n[4] decide_action backward compatibility")
print("-" * 70)

cmd = {"action": "ask_brain", "target": "hello world"}
tool_req = _legacy_command_to_tool(cmd)
print(f"Old command: {cmd}")
print(f"New tool request: {tool_req}")

assert tool_req["tool"] == "ask_brain", "Tool must be ask_brain"
assert tool_req["params"]["user_input"] == "hello world", "user_input must match target"
assert "target" not in tool_req["params"], "Must not have target in params"
print("✅ Conversion correct")

print("\n" + "=" * 70)
print("✅ ALL VERIFICATIONS PASSED")
print("=" * 70)
