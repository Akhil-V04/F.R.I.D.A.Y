"""
Tool Executor - Executes tools based on JSON input
"""

import json
import re
from tools.registry import get_tool, TOOLS


# ===== HELPER FUNCTIONS FOR BUG 2 & BUG 5 =====

def extract_contact_from_input(text):
    """
    Extract contact name from user input.
    Looks for patterns like "to [name]" or "email to [name]"
    
    Args:
        text (str): User input text
    
    Returns:
        str: Contact name or empty string
    """
    if not text:
        return ""
    
    text_lower = text.lower()
    
    # Look for "to [name]" pattern
    patterns = [
        r'to\s+([a-z]+)',           # "to john"
        r'email\s+to\s+([a-z]+)',   # "email to john"
        r'send\s+to\s+([a-z]+)',    # "send to john"
        r'message\s+to\s+([a-z]+)', # "message to john"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            return match.group(1).capitalize()
    
    return ""


def extract_body_from_input(text):
    """
    Extract message body from user input.
    Looks for content after keywords like "say", "message", "that", "saying", "tell"
    
    Args:
        text (str): User input text
    
    Returns:
        str: Message body or empty string
    """
    if not text:
        return ""
    
    text_lower = text.lower()
    
    # Look for content after keywords
    keywords = ["say ", "saying ", "message ", "that ", "with ", "tell "]
    
    for keyword in keywords:
        if keyword in text_lower:
            # Get content after the keyword
            parts = text_lower.split(keyword, 1)
            if len(parts) > 1:
                body = parts[1].strip()
                # Stop at subject/other markers
                for stop_word in [" subject ", " titled "]:
                    if stop_word in body:
                        body = body.split(stop_word)[0].strip()
                if body:
                    return body
    
    return ""


def convert_boolean_to_text(value):
    """
    Convert boolean, None, and string representations to human-readable text.
    BUG 5 fix: Convert True/False/None to natural language responses.
    
    Args:
        value: Result value (bool, None, str, etc.)
    
    Returns:
        str: Human-readable text
    """
    if value is True or value == "True" or value == "true":
        return "Done boss"
    elif value is False or value == "False" or value == "false":
        return "That didn't work boss"
    elif value is None or value == "None" or value == "none":
        return "No result boss"
    elif isinstance(value, str):
        return value
    else:
        return str(value)


class ToolExecutor:
    """Executes tools based on JSON input"""
    
    @staticmethod
    def execute(tool_request):
        """
        Execute a tool based on request.
        
        Args:
            tool_request: dict or JSON string with:
                - tool: tool name
                - params: dict of parameters (optional)
        
        Returns:
            dict: {success: bool, result: any, error: str}
        """
        try:
            # Parse if JSON string
            if isinstance(tool_request, str):
                tool_request = json.loads(tool_request)
            
            # Get tool name
            tool_name = tool_request.get("tool")
            if not tool_name:
                return {"success": False, "error": "No tool specified"}
            
            # Get tool definition
            tool_def = get_tool(tool_name)
            if not tool_def:
                return {"success": False, "error": f"Tool '{tool_name}' not found"}
            
            # Get function and parameters
            func = tool_def["func"]
            params = tool_request.get("params", {})
            original_user_input = tool_request.get("user_input", "")  # For extraction helpers
            
            # ===== PARAMETER MAPPING: Handle common aliases =====
            # Map alternative parameter names to canonical function parameter names
            parameter_aliases = {
                "send_whatsapp": {
                    "to": "contact_name",              # Qwen uses "to"
                    "contact": "contact_name",         # Registry uses "contact"
                },
                "send_email": {
                    "to": "contact",                   # Email uses "contact" directly
                },
                "set_timer": {
                    "minutes": "duration_str",         # Qwen uses "minutes"
                    "duration": "duration_str",        # Registry/tool uses "duration" → function uses "duration_str"
                }
            }
            
            if tool_name in parameter_aliases:
                alias_map = parameter_aliases[tool_name]
                for alias, canonical in alias_map.items():
                    if alias in params and canonical not in params:
                        params[canonical] = params.pop(alias)
            
            # ===== BUG 1: TIMER PARAM NORMALIZATION =====
            # Handle various timer parameter formats and provide defaults
            if tool_name == "set_timer":
                # Check for "minutes" or "seconds" keys and normalize
                if "minutes" in params and "duration_str" not in params:
                    params["duration_str"] = f"{params['minutes']} minutes"
                elif "seconds" in params and "duration_str" not in params:
                    params["duration_str"] = f"{params['seconds']} seconds"
                
                # If still no duration, default to 5 minutes
                if "duration_str" not in params:
                    params["duration_str"] = "5 minutes"
            
            # ===== PARAMETER TYPE CONVERSION: Fix type mismatches =====
            # Handle cases where parameter values need type conversion
            if tool_name == "set_timer" and "duration_str" in params:
                # Ensure duration is formatted as "N minutes" string
                duration_val = params["duration_str"]
                # Convert to int if it's a string
                try:
                    if isinstance(duration_val, str):
                        # Extract numeric part if it's a string like "5" or "5 minutes"
                        numeric_str = ''.join(c for c in duration_val if c.isdigit())
                        if numeric_str:
                            duration_val = int(numeric_str)
                        else:
                            duration_val = str(duration_val)
                    
                    # Format as "N minutes" for the set_timer function
                    if isinstance(duration_val, int):
                        params["duration_str"] = f"{duration_val} minutes"
                    else:
                        # Keep as-is if already formatted
                        params["duration_str"] = str(duration_val)
                except Exception:
                    # Keep original value if conversion fails
                    pass
            
            # ===== BUG 2: EMAIL MISSING PARAMS HANDLING =====
            # Fill in missing email parameters from user input or defaults
            if tool_name in ["send_email", "compose_email"]:
                if "contact" not in params or not params.get("contact"):
                    params["contact"] = extract_contact_from_input(original_user_input)
                
                if "subject" not in params or not params.get("subject"):
                    params["subject"] = "Message from FRIDAY"
                
                if "body" not in params or not params.get("body"):
                    extracted_body = extract_body_from_input(original_user_input)
                    params["body"] = extracted_body if extracted_body else "Sent via FRIDAY assistant"
            
            # Validate required parameters
            missing_params = []
            for param in tool_def["params"]:
                if param.get("required", False) and param["name"] not in params:
                    missing_params.append(param["name"])
            
            if missing_params:
                return {
                    "success": False,
                    "error": f"Missing required parameters: {', '.join(missing_params)}"
                }
            
            # Apply default values for missing optional parameters
            for param in tool_def["params"]:
                if param["name"] not in params and "default" in param:
                    params[param["name"]] = param["default"]
            
            # Execute function with parameters
            result = func(**params)
            
            # ===== BUG 3: SCREEN OUTPUT TRUNCATION =====
            # Truncate read_screen results to prevent overwhelming output
            if tool_name == "read_screen":
                result = str(result)
                result = ' '.join(result.split())  # Collapse whitespace
                result = result[:400] + "..." if len(result) > 400 else result
            
            # ===== BUG 5: BOOLEAN OUTPUT CONVERSION (WRAPPER) =====
            # Convert all results to human-readable strings
            # Apply to EVERY tool execution without exception
            result = convert_boolean_to_text(result)
            
            return {
                "success": True,
                "result": result,
                "tool": tool_name
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "tool": tool_request.get("tool") if isinstance(tool_request, dict) else "unknown"
            }
    
    @staticmethod
    def execute_batch(requests):
        """
        Execute multiple tool requests.
        
        Args:
            requests: list of tool requests
        
        Returns:
            list of results
        """
        results = []
        for request in requests:
            results.append(ToolExecutor.execute(request))
        return results
    
    @staticmethod
    def list_all_tools():
        """Get all available tools with info"""
        return TOOLS
    
    @staticmethod
    def get_tool_schema(tool_name):
        """Get JSON schema for a specific tool"""
        tool = get_tool(tool_name)
        if not tool:
            return None
        
        return {
            "name": tool["name"],
            "description": tool["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    param["name"]: {
                        "type": param["type"],
                        "description": param["description"]
                    }
                    for param in tool["params"]
                },
                "required": [
                    param["name"]
                    for param in tool["params"]
                    if param.get("required", False)
                ]
            }
        }


def execute_tool(tool_name, **kwargs):
    """
    Convenience function to execute a tool.
    
    Args:
        tool_name: name of tool
        **kwargs: parameters for the tool
    
    Returns:
        result or raises exception
    """
    request = {"tool": tool_name, "params": kwargs}
    result = ToolExecutor.execute(request)
    
    if not result["success"]:
        raise Exception(result["error"])
    
    return result["result"]
