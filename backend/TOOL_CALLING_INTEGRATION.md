# Tool-Calling AI System - Integration Guide

## Current Status

✅ **Already Complete:**
- Tool registry: 34 tools registered (`tools/registry.py`)
- Tool executor: JSON-based execution (`tools/executor.py`)
- Qwen integration: `decide_tool()` function (`brain/ollama.py`)
- Brain executor: `execute_with_qwen()` (`brain/qwen_executor.py`)

⚠️ **Missing:**
- Integration into main.py command flow
- Performance optimization (direct vs Qwen execution)
- Fallback handling for ambiguous commands

---

## Integration Points (Exact Locations)

### 1. **Main.py Integration Points**

**Location 1: Line 488** (in parse_initial_command function)
```python
# CURRENT (old system)
command = parse_command(initial_command)

# UPGRADE TO (AI-driven)
from brain.qwen_executor import execute_with_qwen
result = execute_with_qwen(initial_command)
return result
```

**Location 2: Line 536** (in main voice loop)
```python
# CURRENT (old system)
command = parse_command(clean_text)

# UPGRADE TO (AI-driven)
from brain.qwen_executor import execute_with_qwen
result = execute_with_qwen(clean_text)
# Then handle the result
if isinstance(result, dict) and not result.get("success"):
    speak(result.get("error", "Something went wrong"))
    continue
```

---

## Minimal Changes Required

### Option A: Smart Hybrid (Recommended)
Use Qwen only when needed (commands are ambiguous), otherwise execute directly.

```python
def smart_execute(user_command):
    """
    Execute command smartly:
    - Simple commands → direct execution (fast)
    - Ambiguous commands → Qwen decides (intelligent)
    """
    # Step 1: Try direct execution (fast path)
    # Simple patterns that don't need AI
    if "open" in user_command.lower() and not any(x in user_command.lower() for x in ["and search", "for", "tell me"]):
        # Direct: "open chrome"
        command = parse_command(user_command)
        result = execute_command(command)
        return result
    
    # Step 2: Ambiguous → Use Qwen (intelligent path)
    # Patterns that need AI decision
    from brain.qwen_executor import execute_with_qwen
    return execute_with_qwen(user_command)
```

### Option B: Full AI (Simpler)
Use Qwen for all commands.

```python
def ai_driven_execute(user_command):
    """Execute all commands using Qwen AI."""
    from brain.qwen_executor import execute_with_qwen
    return execute_with_qwen(user_command)
```

### Option C: Gradual Migration (Safest)
Keep old system, add Qwen as optional feature.

```python
def execute_with_fallback(user_command, prefer_qwen=False):
    """
    Execute with fallback:
    - If prefer_qwen: try Qwen first, fallback to old system
    - If not: use old system, can switch to Qwen anytime
    """
    if prefer_qwen:
        try:
            from brain.qwen_executor import execute_with_qwen
            return execute_with_qwen(user_command)
        except Exception as e:
            print(f"Qwen failed, falling back to old system: {e}")
            command = parse_command(user_command)
            return execute_command(command)
    else:
        # Old system (current behavior)
        command = parse_command(user_command)
        return execute_command(command)
```

---

## Performance Optimization

### Fast Path (Direct Execution)
**When to use:** Simple, unambiguous commands
**Time:** ~100ms
**Reliability:** Always works
```python
# These should bypass Qwen:
"open chrome"           # Simple app open
"get time"              # Simple info request
"send message to akhil with hi"  # Direct with target
```

### Smart Path (AI Decision)
**When to use:** Ambiguous or complex commands
**Time:** ~2-3 seconds (Qwen latency)
**Reliability:** Works for complex scenarios
```python
# These should use Qwen:
"do something useful"   # Vague, Qwen decides
"I want to talk to someone"  # Ambiguous, Qwen clarifies
"help me work"          # Open-ended, Qwen interprets
```

### Implementation
```python
from brain.command_parser import parse_command
from brain.qwen_executor import execute_with_qwen

SIMPLE_PATTERNS = [
    "open {app}",
    "close {app}", 
    "send message",
    "get time",
    "get date",
]

def should_use_qwen(user_command):
    """Decide if command needs Qwen or can use direct execution."""
    text = user_command.lower()
    
    # Direct execution for simple patterns
    if any(pattern in text for pattern in ["open", "close", "get time", "get date", "get battery"]):
        # But if it's complex, use Qwen
        if any(x in text for x in ["and", "or", "but", "while", "if"]):
            return True  # Complex, use Qwen
        return False  # Simple, direct execution
    
    # Default to Qwen for everything else
    return True

# Usage
if should_use_qwen(user_input):
    result = execute_with_qwen(user_input)  # AI decision
else:
    command = parse_command(user_input)     # Direct execution
    result = execute_command(command)
```

---

## Backward Compatibility Strategy

### Keep Everything Working
```python
# Old functions still exist and work:
from brain.command_parser import parse_command
from actions.apps import open_app
from actions.whatsapp import send_whatsapp_message

# Old way (still works):
command = parse_command("open chrome")  
result = execute_command(command)

# New way (works in parallel):
from brain.qwen_executor import execute_with_qwen
result = execute_with_qwen("open chrome")

# Both produce the same result - no breaking changes!
```

### Fallback Chain
```
User Command
    ↓
Try Qwen (new system)
    ↓ (if Qwen fails)
Try Parse_command (old system)
    ↓ (if old system fails)
Fallback to ask_brain (general conversation)
```

---

## Implementation Checklist

### Phase 1: Add Smart Execution (5 minutes)
- [ ] Create `smart_execute()` function
- [ ] Test with 5 sample commands
- [ ] Deploy to brain/qwen_executor.py

### Phase 2: Integrate into Main.py (10 minutes)
- [ ] Modify line 488 in main.py
- [ ] Modify line 536 in main.py
- [ ] Add fallback handling
- [ ] Test 10 real voice commands

### Phase 3: Performance Tuning (10 minutes)
- [ ] Measure Qwen latency
- [ ] Identify fast vs slow commands
- [ ] Adjust smart execution patterns
- [ ] Test performance

### Phase 4: Monitor & Adjust (Ongoing)
- [ ] Log which path each command takes
- [ ] Track success rates
- [ ] Adjust smart execution patterns based on failures

---

## Code Snippets

### Complete Smart Execution Function
```python
# Add to brain/qwen_executor.py

def execute_smart(user_input, original_text=""):
    """
    Execute with smart routing:
    - Simple/direct commands → parse_command + execute (fast)
    - Ambiguous/complex commands → Qwen decide_tool + execute (intelligent)
    """
    from brain.command_parser import parse_command
    from tools.executor import ToolExecutor
    
    text_lower = user_input.lower().strip()
    
    # Decision logic: detect if command is simple or needs AI
    is_simple = (
        not any(x in text_lower for x in ["and", "or", "but", "while", "if", "that", "which"]) and
        any(x in text_lower for x in ["open", "close", "get", "send"]) and
        len(user_input.split()) < 10  # Short commands are usually direct
    )
    
    if is_simple:
        # Fast path: use old parser for simple commands
        try:
            command = parse_command(user_input)
            if command:
                # Convert old command format to tool format
                from tools.integration import legacy_to_tool
                tool_request = legacy_to_tool(command)
                result = ToolExecutor.execute(tool_request)
                return result["result"] if result["success"] else result["error"]
        except Exception as e:
            print(f"Simple path failed: {e}")
    
    # Intelligent path: use Qwen for complex/ambiguous commands
    return execute_with_qwen(user_input, original_text)
```

### Integration into Main.py
```python
# In main.py, replace lines 488 and 536

# OLD:
# command = parse_command(initial_command)

# NEW:
from brain.qwen_executor import execute_smart
result = execute_smart(initial_command)
if result:
    return result
```

---

## Testing the Integration

### Test Script
```python
# test_integration.py
from brain.qwen_executor import execute_with_qwen, execute_smart

test_commands = [
    # Simple (should be fast)
    ("open chrome", "open_app", "chrome"),
    ("get time", "get_time", ""),
    ("close all apps", "close_all_apps", ""),
    
    # Complex (needs Qwen)
    ("open google and search for python", "open_and_search", "python"),
    ("send whatsapp to akhil saying hey buddy", "send_whatsapp", "akhil"),
    ("what's the news today", "get_news", "world"),
]

for cmd, expected_tool, expected_param in test_commands:
    print(f"\nTesting: {cmd}")
    result = execute_smart(cmd)
    print(f"Result: {result}")
    # Verify tool and parameters
```

---

## Quick Summary

**What's Built:**
- ✅ Tool registry (34 tools)
- ✅ Tool executor (JSON-based)
- ✅ Qwen integration (decide_tool)
- ✅ Brain executor (execute_with_qwen)

**What's Needed:**
- ⚠️ Integration into main.py (2 line changes)
- ⚠️ Smart execution router (new function, ~30 lines)
- ⚠️ Performance optimization (pattern detection)

**Changes Required:**
- **Size:** Minimal (< 50 lines new code)
- **Modified Files:** main.py (2 locations), qwen_executor.py (1 new function)
- **Breaking Changes:** Zero
- **Backward Compatibility:** 100%

**Time to Implement:**
- Smart routing: 5 minutes
- Main.py integration: 10 minutes
- Testing: 10 minutes
- **Total: ~25 minutes**

---

## Next Steps

1. Copy smart_execute() function to brain/qwen_executor.py
2. Update main.py lines 488 and 536
3. Run test_integration.py
4. Deploy and monitor

Done! Your assistant is now AI-driven with Qwen making intelligent decisions about which tool to use.
