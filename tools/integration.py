"""
Tool Integration Bridge - Bridges command-based system with tool-based system
Allows Ollama/AI to use tools via structured JSON input
"""

import json
from tools.executor import ToolExecutor, execute_tool
from tools.registry import list_tools as get_all_tools, get_tool_info


def command_to_tool_request(action, target):
    """
    Convert legacy command format to tool request.
    
    Args:
        action: action type (from parse_command)
        target: target value (from parse_command)
    
    Returns:
        dict: tool request with tool name and params
    """
    
    # Mapping from legacy actions to tools
    action_to_tool = {
        "send_whatsapp": ("send_whatsapp", lambda t: {"contact": t.split("|")[0].strip(), "message": t.split("|")[1].strip() if "|" in t else "Hello"}),
        "send_email": ("send_email", lambda t: {"contact": t.split("|")[0].strip(), "subject": t.split("|")[1].strip() if "|" in t else "Message", "body": t.split("|")[2].strip() if len(t.split("|")) > 2 else ""}),
        "open_app": ("open_app", lambda t: {"app_name": t}),
        "close_app": ("close_app", lambda t: {"app_name": t}),
        "search_google": ("search_google", lambda t: {"query": t}),
        "search_youtube": ("search_youtube", lambda t: {"query": t}),
        "open_url": ("open_url", lambda t: {"url": t}),
        "click_text": ("click_text", lambda t: {"text": t}),
        "type_text": ("type_text", lambda t: {"text": t}),
        "press_key": ("press_key", lambda t: {"key": t}),
        "scroll_down": ("scroll_down", lambda t: {}),
        "scroll_up": ("scroll_up", lambda t: {}),
        "get_news": ("get_news", lambda t: {"category": t if t else "world"}),
        "set_timer": ("set_timer", lambda t: {"duration": t}),
        "set_alarm": ("set_alarm", lambda t: {"time": t}),
    }
    
    # Get tool mapping
    if action in action_to_tool:
        tool_name, param_builder = action_to_tool[action]
        params = param_builder(target) if target else {}
    else:
        # Try direct action-to-tool mapping
        tool_name = action
        params = {"target": target} if target else {}
    
    return {
        "tool": tool_name,
        "params": params
    }


def execute_command_as_tool(action, target):
    """
    Execute a legacy command using the new tool system.
    
    Args:
        action: action type
        target: target value
    
    Returns:
        result from tool execution
    """
    try:
        tool_request = command_to_tool_request(action, target)
        result = ToolExecutor.execute(tool_request)
        
        if result["success"]:
            return result["result"]
        else:
            return f"Tool error: {result['error']}"
    
    except Exception as e:
        return f"Error executing tool: {str(e)}"


def get_ai_tool_description():
    """
    Get tool descriptions formatted for AI (Ollama) to understand.
    Perfect for prompts and function calling.
    
    Returns:
        str: Formatted tool descriptions
    """
    from tools.registry import TOOLS
    tools = TOOLS
    descriptions = []
    
    for tool_name in sorted(tools.keys()):
        tool_info = get_tool_info(tool_name)
        params_desc = ""
        
        if tool_info["params"]:
            params_desc = "\n    Parameters:\n"
            for param in tool_info["params"]:
                required = "required" if param.get("required", False) else "optional"
                params_desc += f"      - {param['name']} ({param['type']}, {required}): {param['description']}\n"
        
        desc = f"  • {tool_name}: {tool_info['description']}{params_desc}"
        descriptions.append(desc)
    
    return "Available Tools:\n" + "\n".join(descriptions)


def get_ai_tool_json_schema():
    """
    Get tools in JSON Schema format for AI function calling.
    
    Returns:
        list: Tool schemas in JSON Schema format
    """
    from tools.registry import TOOLS
    tools = TOOLS
    schemas = []
    
    for tool_name in sorted(tools.keys()):
        tool_info = get_tool_info(tool_name)
        
        schema = {
            "name": tool_name,
            "description": tool_info["description"],
            "input_schema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
        
        for param in tool_info["params"]:
            schema["input_schema"]["properties"][param["name"]] = {
                "type": param["type"],
                "description": param["description"]
            }
            if param.get("required", False):
                schema["input_schema"]["required"].append(param["name"])
        
        schemas.append(schema)
    
    return schemas
