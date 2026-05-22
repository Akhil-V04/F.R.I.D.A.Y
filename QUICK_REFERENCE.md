# Tool System - Quick Reference

## Installation

Copy the `tools/` directory to your project. No dependencies beyond what F.R.I.D.A.Y already uses.

```bash
# Files already present
tools/
├── __init__.py
├── registry.py
├── executor.py
├── integration.py
└── test_tools.py
```

## Three Ways to Call Tools

### Method 1: Legacy (Existing Code - No Changes)
```python
from actions.whatsapp import send_message_to_contact
from actions.system import get_time

send_message_to_contact("mom", "Hello")
time = get_time()
```

### Method 2: Convenience Functions (Simple)
```python
from tools.executor import execute_tool

execute_tool("send_whatsapp", contact="mom", message="Hello")
time = execute_tool("get_time")
battery = execute_tool("get_battery")
```

### Method 3: JSON (AI-Ready)
```python
from tools.executor import ToolExecutor

result = ToolExecutor.execute({
    "tool": "send_whatsapp",
    "params": {"contact": "mom", "message": "Hello"}
})
```

## Common Operations

### System Info
```python
# Method 1: Legacy
from actions.system import get_time, get_date, get_battery

# Method 2: Tool
execute_tool("get_time")
execute_tool("get_date")
execute_tool("get_battery")
```

### App Control
```python
# Open app
execute_tool("open_app", app_name="chrome")

# Close app
execute_tool("close_app", app_name="chrome")

# Close all
execute_tool("close_all_apps")
```

### Messaging
```python
# Send WhatsApp
execute_tool("send_whatsapp", contact="mom", message="Hello")

# Send Email
execute_tool("send_email", 
    contact="mom@email.com",
    subject="Hello",
    body="Just checking in"
)
```

### News
```python
# Get specific category
execute_tool("get_news", category="technology", limit=5)

# Get world briefing
execute_tool("get_world_briefing")

# Get India briefing
execute_tool("get_india_briefing")

# Get by topic
execute_tool("get_news_by_topic", topic="AI")
```

### Web
```python
execute_tool("search_google", query="python programming")
execute_tool("search_youtube", query="tutorial")
execute_tool("open_url", url="https://google.com")
execute_tool("open_chatgpt")
execute_tool("open_claude")
```

### Screen Control
```python
# Click text
execute_tool("click_text", text="Submit")

# Type text
execute_tool("type_text", text="Hello world")

# Press key
execute_tool("press_key", key="enter")

# Scroll
execute_tool("scroll_down", amount=5)
execute_tool("scroll_up", amount=3)

# Read screen
execute_tool("get_screen_text")

# Find text
execute_tool("find_text", search_text="Login")
```

## Error Handling

```python
from tools.executor import ToolExecutor

result = ToolExecutor.execute({
    "tool": "send_whatsapp",
    "params": {}  # Missing contact, message
})

if not result["success"]:
    print(f"Error: {result['error']}")
    # Error: Missing required parameters: contact, message

# Or use convenience function with exception
try:
    result = execute_tool("send_whatsapp")  # Missing params
except Exception as e:
    print(f"Error: {e}")
```

## List Available Tools

```python
from tools.registry import list_tools, get_tool_info

# Get all tool names
tools = list_tools()
print(tools)  # ['send_whatsapp', 'send_email', 'open_app', ...]

# Get full info about a tool
info = get_tool_info("send_whatsapp")
print(info["description"])
print(info["params"])
```

## For AI/Ollama Integration

```python
from tools.integration import (
    get_ai_tool_description,
    get_ai_tool_json_schema,
    command_to_tool_request
)

# Get tool descriptions for AI prompts
desc = get_ai_tool_description()
# Use in: prompt = f"Available tools:\n{desc}\n\nRespond with tool calls..."

# Get JSON schemas for function calling
schemas = get_ai_tool_json_schema()
# Use in: AI function calling / tool use

# Convert old commands to new format
tool_req = command_to_tool_request("send_whatsapp", "mom|Hello")
result = ToolExecutor.execute(tool_req)
```

## Batch Operations

```python
requests = [
    {"tool": "get_time", "params": {}},
    {"tool": "get_battery", "params": {}},
    {"tool": "get_news", "params": {"category": "tech"}},
]

results = ToolExecutor.execute_batch(requests)
# [time_result, battery_result, news_result]
```

## Running Tests/Examples

```bash
# Run test suite
python -m tools.test_tools

# Run examples
python examples_tool_usage.py
```

## Integration with Existing Code

The tool system **doesn't require** any changes to existing code:

```python
# main.py - NO CHANGES NEEDED
from actions.whatsapp import send_message_to_contact

# Still works exactly the same
send_message_to_contact("mom", "Hello")

# And you can also use tools if you want
from tools.executor import execute_tool
execute_tool("send_whatsapp", contact="mom", message="Hello")

# Both approaches work side-by-side
```

## Key Points

✓ **Backward Compatible** - Old code works unchanged
✓ **No Dependencies** - Uses existing imports
✓ **Well Documented** - Full guides + examples
✓ **Production Ready** - All tests passing
✓ **Easy to Use** - 3 usage patterns, pick what you like

## Pro Tips

1. Use **convenience functions** for simple scripts
2. Use **JSON** when integrating with AI/APIs
3. Use **legacy** when working in existing code
4. All approaches are 100% compatible

## Documentation

- Full guide: `TOOL_SYSTEM.md`
- Summary: `TOOL_SYSTEM_SUMMARY.md`
- Examples: `examples_tool_usage.py`
- Tests: `tools/test_tools.py`

---

**Happy coding! The tool system is ready to use.** 🚀
