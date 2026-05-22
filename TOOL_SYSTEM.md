# Tool-Based System Architecture for F.R.I.D.A.Y

## Overview

The tool-based system provides a **centralized, JSON-driven interface** for all F.R.I.D.A.Y functions while maintaining 100% backward compatibility with existing code. No breaking changes.

## Installation & Structure

```
tools/
├── __init__.py          # Export main classes
├── registry.py          # Tool definitions (34 tools registered)
├── executor.py          # JSON executor & convenience functions
├── integration.py       # Bridge between old and new system
└── test_tools.py        # Test suite (all passing ✓)
```

## Quick Start

### Method 1: JSON-Based Execution (New - Recommended for AI)

```python
from tools.executor import ToolExecutor

# Execute tool via JSON
request = {
    "tool": "send_whatsapp",
    "params": {
        "contact": "mom",
        "message": "Hello mom!"
    }
}

result = ToolExecutor.execute(request)
print(result)  # {'success': True, 'result': <response>, 'tool': 'send_whatsapp'}
```

### Method 2: Convenience Function (Pythonic)

```python
from tools.executor import execute_tool

# Execute tool directly
result = execute_tool("get_time")
print(result)  # "It's 2:17 PM"

# With parameters
result = execute_tool("send_whatsapp", contact="mom", message="Hello")
print(result)  # <response from whatsapp>
```

### Method 3: Legacy System (Still Works - No Changes Needed)

```python
from actions.system import get_time
from actions.whatsapp import send_message_to_contact

# Old code continues to work exactly as before
time = get_time()
send_message_to_contact("mom", "Hello")
```

## Available Tools (34 Total)

### Messaging
- `send_whatsapp` - Send WhatsApp message
- `send_whatsapp_flow` - Interactive WhatsApp flow
- `send_email` - Send email

### App Control
- `open_app` - Open application
- `close_app` - Close application
- `close_all_apps` - Close all apps

### News
- `get_news` - Fetch news by category
- `get_world_briefing` - Global + India news
- `get_india_briefing` - India news only
- `get_news_by_topic` - News by topic

### Screen Interaction
- `click_text` - Find and click text
- `find_text` - Find text position
- `get_screen_text` - Read screen text
- `scroll_down` / `scroll_up` - Scroll
- `type_text` - Type text
- `press_key` - Press keyboard key

### System Info
- `get_time` - Current time
- `get_date` - Current date
- `get_battery` - Battery status
- `take_screenshot` - Take screenshot
- `shutdown_pc` / `restart_pc` - System control

### Web
- `open_url` - Open URL
- `search_google` - Search Google
- `search_youtube` - Search YouTube
- `open_world_monitor` - Open news monitor
- `open_claude` - Open Claude AI
- `open_chatgpt` - Open ChatGPT
- `open_and_search` - Open & search

### Clock
- `open_clock` - Open clock app
- `set_timer` - Create timer
- `set_alarm` - Set alarm
- `close_clock` - Close clock

## Integration with Ollama/AI

### Get Tool Descriptions for Prompting

```python
from tools.integration import get_ai_tool_description

# Get formatted description for AI
descriptions = get_ai_tool_description()
print(descriptions)

# Use in Ollama prompt
prompt = f"""
You are F.R.I.D.A.Y, an AI assistant.

{descriptions}

When user asks you to do something, respond with a tool call in JSON:
{{"tool": "<tool_name>", "params": {{...}}}}
"""
```

### Get JSON Schema for Function Calling

```python
from tools.integration import get_ai_tool_json_schema

# Get OpenAI-style schemas
schemas = get_ai_tool_json_schema()

# schemas[0] looks like:
# {
#   "name": "send_whatsapp",
#   "description": "Send WhatsApp message to a contact",
#   "input_schema": {
#     "type": "object",
#     "properties": {
#       "contact": {"type": "str", "description": "Contact name..."},
#       "message": {"type": "str", "description": "Message text..."}
#     },
#     "required": ["contact", "message"]
#   }
# }
```

### Convert Legacy Commands to Tools

```python
from tools.integration import command_to_tool_request, execute_command_as_tool

# Old command format
action = "send_whatsapp"
target = "mom|Hello"

# Convert to tool request
tool_request = command_to_tool_request(action, target)
# {'tool': 'send_whatsapp', 'params': {'contact': 'mom', 'message': 'Hello'}}

# Execute
result = execute_command_as_tool(action, target)
```

## Integration with Existing Brain/Ollama

No changes needed to `brain/ollama.py` or `main.py`. The tool system works alongside existing code.

However, you **can** optionally enhance Ollama to use tools:

```python
# Optional: In brain/ollama.py, you could add:
from tools.integration import get_ai_tool_description

def ask_brain_with_tools(question):
    """Ask Ollama with access to tools"""
    tools_desc = get_ai_tool_description()
    
    prompt = f"""
    You are F.R.I.D.A.Y.
    
    Available tools:
    {tools_desc}
    
    When user asks: {question}
    
    Respond with either:
    1. Plain text answer, OR
    2. JSON tool call: {{"tool": "tool_name", "params": {{...}}}}
    """
    
    return ask_brain(prompt)
```

## Error Handling

```python
from tools.executor import ToolExecutor

result = ToolExecutor.execute({
    "tool": "send_whatsapp",
    "params": {}  # Missing required params
})

if not result["success"]:
    print(f"Error: {result['error']}")
    # Error: Missing required parameters: contact, message
```

## Why This System?

### Benefits

1. **No Breaking Changes** - Existing code continues to work
2. **AI-Ready** - Tools designed for LLM function calling
3. **Structured I/O** - JSON input/output for APIs
4. **Centralized** - All tools in one place
5. **Extensible** - Easy to add new tools
6. **Documented** - Each tool has metadata
7. **Type-Safe** - Parameter validation

### When to Use Each Method

| Method | When | Example |
|--------|------|---------|
| Legacy | Existing code, direct calls | `from actions.whatsapp import send_message_to_contact` |
| Convenience | Python code, simple usage | `execute_tool("get_time")` |
| JSON | AI/LLM integration, APIs | `ToolExecutor.execute({"tool": "...", "params": ...})` |

## Testing

Run the test suite:

```bash
cd c:\Users\akhil\Downloads\F.R.I.D.A.Y
python -m tools.test_tools
```

All 8 tests pass ✓:
- Basic tool execution
- Convenience functions
- Tool listing
- Legacy command conversion
- Tool information retrieval
- AI descriptions
- Error handling
- JSON input

## Adding New Tools

1. Add function to appropriate module (e.g., `actions/new_module.py`)
2. Register in `tools/registry.py`:

```python
"my_new_tool": {
    "name": "my_new_tool",
    "func": my_function,
    "params": [
        {"name": "param1", "type": "str", "description": "...", "required": True},
    ],
    "description": "What this tool does"
}
```

3. Tool is immediately available via all three methods!

## Files Modified

- Created: `tools/__init__.py`
- Created: `tools/registry.py` (34 tools registered)
- Created: `tools/executor.py` (JSON executor)
- Created: `tools/integration.py` (Bridge to legacy)
- Created: `tools/test_tools.py` (Test suite)
- **No existing files modified** ✓

## Summary

You now have a **dual-mode system** that supports:

1. **Legacy code** - Works exactly as before
2. **New tool-based code** - JSON-driven execution
3. **AI integration** - Built-in Ollama/LLM support

Switch methods as needed. No refactoring of existing code required.
