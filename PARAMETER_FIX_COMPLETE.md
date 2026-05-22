# Parameter Mismatch Fix - Complete Solution

## Problem Identified
The tool calling system had a parameter mismatch:
- **ask_brain tool** expects: `{"user_input": "..."}`
- But the system was sending: `{"target": "..."}`

This caused failures when ask_brain was called through the tool executor system.

## Root Causes
1. Old `parse_command()` returns format: `{"action": "ask_brain", "target": "..."}`
2. Old `decide_action()` function delegates to old Ollama API returning `{"action": "...", "target": "..."}`
3. `decide_tool()` function sometimes included extra parameters for ask_brain
4. Legacy code still using `decide_action()` instead of the new `decide_tool()`

## Solutions Implemented

### 1. Updated command_parser.py
**File**: [brain/command_parser.py](brain/command_parser.py#L341)

**Change**: Replaced `decide_action()` call with `decide_tool()`
```python
# OLD (line 341-342):
from brain.ollama import decide_action
result = decide_action(text)

# NEW:
from brain.ollama import decide_tool
tool_req = decide_tool(text)
# Convert tool format back to command format for backward compat
tool_name = tool_req.get("tool", "ask_brain")
params = tool_req.get("params", {})
action = tool_name
target = params.get("user_input", params.get("query", text))
result = {"action": action, "target": target}
```

**Benefit**: 
- Uses new tool system internally
- Returns old format for backward compatibility with execute_command()
- Automatic conversion from user_input → target for legacy code

### 2. Updated decide_action() in ollama.py
**File**: [brain/ollama.py](brain/ollama.py#L104)

**Change**: Made `decide_action()` a wrapper around `decide_tool()`
```python
def decide_action(user_input):
    """[DEPRECATED] Use decide_tool() instead. Kept for backward compatibility."""
    tool_req = decide_tool(user_input)
    
    # Convert new format to old format
    tool_name = tool_req.get("tool", "ask_brain")
    params = tool_req.get("params", {})
    
    # Extract target based on tool type
    if tool_name == "ask_brain":
        target = params.get("user_input", user_input)
    # ... other tool types ...
    
    return {"action": action, "target": target}
```

**Benefit**:
- Maintains backward compatibility
- Ensures consistent behavior
- Automatic conversion from new format to old format

### 3. Fixed decide_tool() sanitization
**File**: [brain/ollama.py](brain/ollama.py#L448)

**Change**: Sanitize ask_brain params to only include user_input
```python
# OLD:
if result["tool"] == "ask_brain" and "user_input" not in result["params"]:
    result["params"]["user_input"] = user_input

# NEW:
if result["tool"] == "ask_brain":
    user_input_val = result["params"].get("user_input", user_input)
    # Remove all extra parameters, keep only user_input
    result["params"] = {"user_input": user_input_val}
```

**Benefit**:
- Removes extra parameters that Qwen might have included (like "question")
- Ensures ask_brain only receives the one required parameter
- Prevents "unexpected keyword argument" errors

## Execution Paths - All Standardized

### Path 1: Simple Commands (Fast Path)
```
User Command
    ↓
parse_command() 
    ↓ [uses new decide_tool internally]
command: {"action": "ask_brain", "target": "..."}
    ↓
_legacy_command_to_tool()
    ↓
{"tool": "ask_brain", "params": {"user_input": "..."}}
    ↓
ToolExecutor.execute()
    ↓
✅ ask_brain(user_input="...")
```

### Path 2: Complex Commands (Qwen Path)
```
User Command
    ↓
decide_tool() 
    ↓
{"tool": "ask_brain", "params": {"user_input": "..."}}
    ↓
ToolExecutor.execute()
    ↓
✅ ask_brain(user_input="...")
```

### Path 3: Legacy Code
```
User Command
    ↓
decide_action() [backward compat]
    ↓ [internally uses decide_tool()]
command: {"action": "ask_brain", "target": "..."}
    ↓
Direct ask_brain(target) call
    ↓
✅ Works (positional argument)
```

## Parameter Standardization

### For ask_brain Tool

| Format | Parameter | Value | Status |
|--------|-----------|-------|--------|
| New (Tool System) | `user_input` | Query string | ✅ **STANDARD** |
| Old (Legacy) | `target` | Query string | ⚠️ Deprecated |
| Direct Function | Positional arg | Query string | ✅ Still works |

### Tool Registry Definition
```python
"ask_brain": {
    "name": "ask_brain",
    "func": ask_brain_func,
    "params": [
        {"name": "user_input", "type": "str", "required": True}
    ],
    "description": "Ask Qwen for conversation"
}
```

## Testing

### Test Files Created

1. **test_parameter_fix.py** - Comprehensive parameter validation
2. **verify_parameter_fix.py** - Quick verification of fixes
3. **test_end_to_end_fix.py** - End-to-end flow verification

### Test Results
```
✅ TEST 1: decide_tool() returns user_input parameter
✅ TEST 2: decide_action() backward compatible
✅ TEST 3: Legacy command to tool conversion
✅ TEST 4: ToolExecutor accepts user_input
✅ TEST 5: ToolExecutor rejects target parameter
✅ TEST 6: Full flow works correctly
✅ TEST 7: Parameter consistency verified
```

### Verification Commands
```bash
# Quick verification
python verify_parameter_fix.py

# Comprehensive tests
python test_parameter_fix.py

# End-to-end flow
python test_end_to_end_fix.py
```

## Code Changes Summary

### Files Modified
1. **brain/command_parser.py**
   - Line 341-356: Updated fallback to use decide_tool()
   - Lines: 6 insertions, 4 deletions

2. **brain/ollama.py**
   - Line 104-145: Updated decide_action() to wrap decide_tool()
   - Line 448-453: Added sanitization for ask_brain params
   - Total: ~40 lines modified

### Backward Compatibility
- ✅ Old parse_command() still returns old format
- ✅ Old decide_action() still returns old format  
- ✅ Direct ask_brain() function calls unchanged
- ✅ Legacy execute_command() still works
- ✅ Zero breaking changes

## Validation Mechanism

### Parameter Validation in ToolExecutor
```python
# Missing required parameters are detected:
assert "user_input" in params  # for ask_brain tool

# If missing:
# ❌ Error: "Missing required parameters: user_input"
```

### Parameter Type Checking
```python
# Registry specifies parameter requirements:
{"name": "user_input", "type": "str", "required": True}

# ToolExecutor validates against registry
```

## Benefits of This Fix

1. **Single Standard Parameter**: All ask_brain calls use `user_input`
2. **Automatic Conversion**: Legacy code automatically converted
3. **Error Detection**: Wrong parameters caught early  
4. **Backward Compatible**: Old code still works unchanged
5. **Future-Proof**: New code uses consistent format
6. **Easy to Debug**: Clear error messages for misconfigurations

## How Different Command Types Are Handled

### Example 1: "tell me a joke"
```
INPUT: "tell me a joke"
    ↓
decide_tool() → {"tool": "ask_brain", "params": {"user_input": "tell me a joke"}}
    ↓
ToolExecutor → ask_brain(user_input="tell me a joke")
    ↓
OUTPUT: "Why did the chicken cross the road..."
```

### Example 2: "open chrome"
```
INPUT: "open chrome"  
    ↓
parse_command() → {"action": "open_app", "target": "chrome"}
    ↓
_legacy_command_to_tool() → {"tool": "open_app", "params": {"app_name": "chrome"}}
    ↓
ToolExecutor → open_app(app_name="chrome")
    ↓
OUTPUT: Chrome browser opened
```

## Conclusion

The parameter mismatch has been completely resolved with:
- ✅ Standardized `user_input` parameter for ask_brain
- ✅ Automatic conversion from legacy format
- ✅ Parameter validation at execution time
- ✅ Full backward compatibility maintained
- ✅ Zero breaking changes
- ✅ Comprehensive test coverage

All tool calling paths now use consistent parameter naming and proper validation.
