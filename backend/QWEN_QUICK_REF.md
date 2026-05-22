# Qwen Decision Engine - Quick Reference

## Setup (One Time)
```bash
# 1. Install Ollama from https://ollama.ai

# 2. Run Ollama server
ollama serve

# 3. In another terminal, pull Qwen
ollama pull qwen2.5:3b

# 4. Verify
python test_qwen_decisions.py
```

## Running F.R.I.D.A.Y
```bash
# With decision engine active
python main.py

# Just test decisions
python test_qwen_decisions.py
```

## How It Works
```
User: "open chrome"
         ↓
    [Qwen analyzes]
         ↓
    {"tool": "open_app", "params": {"app_name": "chrome"}}
         ↓
    [Execute tool]
         ↓
    Chrome opens
```

## Supported Commands

### Time & Date
- "what time is it" → `get_time`
- "what's the date" → `get_date`

### System
- "check battery" → `get_battery`
- "system info" → `get_system_info`

### Apps
- "open chrome" → `open_app`
- "close notepad" → `close_app`

### News
- "what's the news" → `get_news`
- "tech news" → `get_news` (with category)

### Web
- "google python tutorial" → `search_google`
- "youtube cat videos" → `search_youtube`

### Messaging
- "message mom on whatsapp" → `send_whatsapp`

### Screen Control
- "click submit" → `click_text`
- "scroll down" → `scroll_down`
- "type hello" → `type_text`

## Key Files

| File | Purpose |
|------|---------|
| `brain/qwen_executor.py` | Decision engine |
| `brain/intent_mapper.py` | Tool definitions |
| `brain/command_parser.py` | Full pipeline |
| `test_qwen_decisions.py` | Testing |
| `QWEN_SETUP.md` | Full documentation |

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Connection refused | Run `ollama serve` |
| Model not found | Run `ollama pull qwen2.5:3b` |
| Slow first response | Normal - model loads once |
| Invalid JSON | Check logs, restart Ollama |

## Add New Tool

In `brain/intent_mapper.py`:

```python
TOOL_DEFINITIONS = {
    "my_tool": {
        "description": "What it does",
        "required_params": {"name": "type"},
        "examples": [("example input", {"name": "value"})]
    }
}
```

That's it! Qwen learns automatically.

## Architecture

```
main.py (entry point)
  ↓
brain/command_parser.py (parse_and_execute)
  ↓
brain/qwen_executor.py (qwen_decision_only)
  ↓
Ollama/Qwen 2.5 3B
  ↓
actions/ (tool execution)
```

---

**Status**: ✅ Ready to use
**Model**: Qwen 2.5 3B (via Ollama)
**Latency**: ~200-500ms per decision
