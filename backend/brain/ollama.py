import requests
import json
from memory.memory import get_cached_command, cache_command
from brain.command_parser import fast_path_check

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:3b"

conversation_history = []

SYSTEM_PROMPT = "You are FRIDAY, a highly intelligent AI assistant built for your boss. You talk like a real person - natural, warm, slightly witty. You are loyal, sharp, and occasionally sarcastic like the FRIDAY from Iron Man/Avengers. Rules: Reply in 1-2 sentences max. Never sound robotic. No bullet points. No lists. Talk conversationally like a human assistant would. Call the user 'boss' naturally but not every sentence. If asked something personal or funny, play along. If asked to do something, confirm it confidently. You are aware you are running locally on boss's machine."


def ask_brain(user_input):
    """Send a prompt to Ollama and get a response with conversation history"""
    try:
        # Check cache first
        cached = get_cached_command(user_input)
        if cached and cached.get("count", 0) > 2:
            print("Using cached response")
            return cached["response"]
        
        global conversation_history
        
        # Add user message to history
        conversation_history.append({"role": "user", "content": user_input})
        
        # Build full prompt from last 6 messages
        recent_messages = conversation_history[-6:]
        full_prompt = ""
        for msg in recent_messages:
            if msg["role"] == "user":
                full_prompt += f"User: {msg['content']}\n"
            else:
                full_prompt += f"FRIDAY: {msg['content']}\n"
        
        # Add prompt for assistant to continue
        final_prompt = full_prompt + "FRIDAY:"
        
        # Create payload with options
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": final_prompt,
            "system": SYSTEM_PROMPT,
            "stream": False,
            "options": {
                "num_predict": 120,
                "temperature": 0.8,
                "top_p": 0.9,
                "stop": ["\nUser:", "\nBoss:"]
            }
        }
        
        # Make request to Ollama
        response = requests.post(OLLAMA_URL, json=payload, timeout=20)
        response.raise_for_status()
        
        # Extract and clean response
        response_text = response.json()["response"].strip()
        
        # Cache the response
        cache_command(user_input, "ask_brain", response_text)
        
        # Add assistant message to history
        conversation_history.append({"role": "assistant", "content": response_text})
        
        # Keep only last 10 messages
        if len(conversation_history) > 10:
            conversation_history = conversation_history[-10:]
        
        return response_text
    
    except Exception as e:
        print(f"Error asking brain: {e}")
        return "Sorry boss, I had an error."


def correct_command(text):
    """Correct speech recognition errors in voice commands using Ollama"""
    try:
        prompt = f"""You are a speech correction AI. The user spoke a voice command but speech recognition made errors.
Fix ONLY spelling/recognition mistakes. Keep the meaning exactly same.
Common mistakes: "melt"→"mail", "cloud"→"claude", "good"→"google", "sent"→"send"
Return ONLY the corrected command, nothing else, no explanation.
Original command: "{text}"
Corrected command:"""
        
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"num_predict": 20, "temperature": 0.1}
        }
        
        response = requests.post(OLLAMA_URL, json=payload, timeout=10)
        response.raise_for_status()
        
        return response.json()["response"].strip()
    
    except Exception as e:
        print(f"Error correcting command: {e}")
        return text


def decide_action(user_input):
    """
    [DEPRECATED] Use decide_tool() instead. This is kept for backward compatibility.
    
    Use AI to intelligently decide which action to take for ambiguous commands.
    Now delegates to decide_tool() and converts format.
    
    Args:
        user_input (str): User's voice command
    
    Returns:
        dict: {"action": action_name, "target": target_value} (old format, for backward compat)
    """
    try:
        # Use new tool system
        tool_req = decide_tool(user_input)
        
        # Convert new format {"tool": "...", "params": {...}} 
        # to old format {"action": "...", "target": "..."}
        tool_name = tool_req.get("tool", "ask_brain")
        params = tool_req.get("params", {})
        
        # Map tool to action
        action = tool_name
        
        # Extract target from params based on tool type
        if tool_name == "ask_brain":
            target = params.get("user_input", user_input)
        elif tool_name in ["search_google", "search_youtube"]:
            target = params.get("query", user_input)
        elif tool_name == "open_app":
            target = params.get("app_name", user_input)
        elif tool_name == "open_url":
            target = params.get("url", user_input)
        elif tool_name in ["send_email", "send_whatsapp", "send_whatsapp_flow"]:
            target = params.get("contact", params.get("initial_contact", user_input))
        else:
            target = user_input
        
        return {"action": action, "target": target}
    
    except Exception as e:
        print(f"Error in decide_action: {e}")
        # Fallback to ask_brain with proper format
        return {"action": "ask_brain", "target": user_input}



def is_ollama_running():
    """Check if Ollama service is running"""
    try:
        response = requests.get("http://localhost:11434")
        return response.status_code == 200
    except Exception:
        return False


def clear_history():
    """Clear conversation history"""
    global conversation_history
    conversation_history.clear()


def plan_next_action(context, current_screen, last_action, last_result):
    """
    Use AI to plan the next action based on current state.
    
    Args:
        context (str): User's original goal
        current_screen (str): What is visible on screen
        last_action (str): The action that was just taken
        last_result (str): The result of the last action
    
    Returns:
        dict: {"next_action": action_name, "target": target, "reason": reason}
    """
    try:
        prompt = f"""You are FRIDAY, an autonomous AI assistant with access to:
- Screen reading and OCR
- Mouse and keyboard control
- Browser automation
- File system access
- App launching

Current situation:
- Last action taken: {last_action}
- Result of last action: {last_result}
- What is currently visible on screen: {current_screen[:300]}
- User's original goal: {context}

Based on this, what should be the NEXT action to take to achieve the goal?

Respond with JSON only:
{{"next_action": "action_name", "target": "what to act on", "reason": "why"}}

Available actions: click_text, type_text, scroll_down, scroll_up, open_app, 
open_url, press_key, wait, take_screenshot, read_screen, done

If goal is achieved respond: {{"next_action": "done", "target": "", "reason": "goal achieved"}}"""
        
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"num_predict": 60, "temperature": 0.1}
        }
        
        response = requests.post(OLLAMA_URL, json=payload, timeout=15)
        response.raise_for_status()
        
        # Extract response text
        text = response.json()["response"].strip()
        
        # Clean markdown code blocks if present
        text = text.replace("```json", "").replace("```", "").strip()
        
        # Parse JSON
        result = json.loads(text)
        return result
    
    except Exception as e:
        print(f"Error in plan_next_action: {e}")
        return {"next_action": "done", "target": "", "reason": "error"}


def autonomous_execute(goal, max_steps=10):
    """
    Execute a goal autonomously using AI planning and screen automation.
    
    Args:
        goal (str): The goal to achieve
        max_steps (int): Maximum steps to take before stopping
    
    Returns:
        str: Completion message
    """
    try:
        # Import required modules
        import time
        import pyautogui
        from actions.screen import click_text, type_text, scroll_down, scroll_up, take_screenshot
        from actions.screen_monitor import get_current_screen
        
        last_action = "none"
        last_result = "starting"
        step = 0
        
        while step < max_steps:
            # Get current screen state
            screen = get_current_screen()
            
            # Get AI plan for next action
            plan = plan_next_action(goal, screen, last_action, last_result)
            next_action = plan.get("next_action", "done")
            target = plan.get("target", "")
            
            # Log what AI decided
            print(f"AI Planning: {next_action} → {target}")
            
            # Check if goal is achieved
            if next_action == "done":
                break
            
            # Execute the planned action
            if next_action == "click_text":
                success, msg = click_text(target)
                last_result = msg
            
            elif next_action == "type_text":
                type_text(target)
                last_result = f"typed {target}"
            
            elif next_action == "scroll_down":
                scroll_down()
                last_result = "scrolled down"
            
            elif next_action == "scroll_up":
                scroll_up()
                last_result = "scrolled up"
            
            elif next_action == "press_key":
                pyautogui.press(target)
                last_result = f"pressed {target}"
            
            elif next_action == "wait":
                time.sleep(2)
                last_result = "waited"
            
            elif next_action == "read_screen":
                last_result = screen[:200]
            
            elif next_action == "take_screenshot":
                take_screenshot()
                last_result = "screenshot taken"
            
            elif next_action == "open_app":
                from actions.apps import open_app
                open_app(target)
                last_result = f"opened {target}"
            
            elif next_action == "open_url":
                from actions.web import open_url
                open_url(target)
                last_result = f"opened {target}"
            
            # Update action tracking
            last_action = next_action
            step += 1
            
            # Brief pause between actions
            time.sleep(0.5)
        
        return f"Task completed in {step} steps boss."
    
    except Exception as e:
        print(f"Error in autonomous_execute: {e}")
        return f"Task failed after {step} steps boss."


def extract_json_from_response(text):
    """
    Extract valid JSON from Qwen response, even if surrounded by text.
    Tries multiple extraction strategies.
    
    Args:
        text (str): Raw response from Qwen
    
    Returns:
        dict: Parsed JSON or None if extraction fails
    """
    import re
    
    text = text.strip()
    
    # Strategy 1: Try parsing the whole response as JSON
    try:
        return json.loads(text)
    except:
        pass
    
    # Strategy 2: Extract JSON object using regex (most robust)
    # Finds content between outer { and last }
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        json_str = match.group(0)
        try:
            return json.loads(json_str)
        except:
            pass
    
    # Strategy 3: Extract JSON array using regex
    # Finds content between [ and ]
    match = re.search(r'\[.*\]', text, re.DOTALL)
    if match:
        json_str = match.group(0)
        try:
            return json.loads(json_str)
        except:
            pass
    
    # Strategy 4: Fix common issues and retry
    try:
        # Add missing closing brace
        if text.count('{') > text.count('}'):
            text = text + '}' * (text.count('{') - text.count('}'))
        # Add missing closing bracket
        if text.count('[') > text.count(']'):
            text = text + ']' * (text.count('[') - text.count(']'))
        return json.loads(text)
    except:
        pass
    
    return None


def decide_tool(user_input):
    """
    Use Qwen to decide which TOOL to use and extract parameters (TOOL SYSTEM).
    Returns ONLY JSON format with tool name and params - NO normal text responses.
    
    Args:
        user_input (str): User's command
    
    Returns:
        dict: {"tool": "tool_name", "params": {"param": "value"}}
    """
    try:
        # Import tools list
        from tools.registry import TOOLS
        
        # Build tool descriptions
        tools_desc = "\n".join([
            f"  • {name}: {tool['description']}"
            for name, tool in TOOLS.items()
        ])
        
        # STRICT JSON PROMPT - emphasizes JSON-only output
        prompt = f"""TOOL SELECTOR - RESPOND WITH ONLY VALID JSON

Available Tools:
{tools_desc}

User Command: "{user_input}"

**CRITICAL: Respond with ONLY valid JSON. No explanation, no text before or after.**

Select the best tool and extract parameters.

MANDATORY JSON FORMAT (exactly this structure):
{{
"tool": "tool_name",
"params": {{"param1": "value1"}}
}}

Rules:
- tool: must be from the available tools list
- params: object with extracted parameters
- If no parameters, use empty: {{"params": {{}}}}
- If command unclear, tool must be "ask_brain"

RESPOND WITH ONLY THE JSON OBJECT. NOTHING ELSE."""
        
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": 100,
                "temperature": 0.05,  # Very low for strict JSON
                "top_p": 0.8,
                "top_k": 40,
                "stop": ["}", "\n\n"]  # Stop after JSON close
            }
        }
        
        response = requests.post(OLLAMA_URL, json=payload, timeout=15)
        response.raise_for_status()
        
        text = response.json()["response"].strip()
        
        # Try to extract valid JSON
        result = extract_json_from_response(text)
        
        if result and isinstance(result, dict):
            # Validate structure
            if "tool" in result and "params" in result:
                # Sanitize params for ask_brain - only keep user_input
                if result["tool"] == "ask_brain":
                    user_input_val = result["params"].get("user_input", user_input)
                    # Remove all extra parameters, keep only user_input
                    result["params"] = {"user_input": user_input_val}
                return result
        
        # Fallback: return safe default
        return {"tool": "ask_brain", "params": {"user_input": user_input}}
    
    except Exception as e:
        print(f"Error in decide_tool: {e}")
        # Safe fallback
        return {"tool": "ask_brain", "params": {"user_input": user_input}}


def plan_tasks(user_input):
    """
    Split a multi-step command and generate tool calls for each step.
    Uses rule-based splitting on common connectors: "and", "then", " after ".
    For each step, tries fast_path_check first (instant matching), then decide_tool.
    Handles nested multi-step commands (multiple connectors).
    
    Args:
        user_input (str): User's complex command
    
    Returns:
        dict: {"steps": [{"tool": "tool_name", "params": {...}}, ...]}
    """
    def split_on_connectors(text):
        """Recursively split text on connectors, handling nested multi-step."""
        connectors = [" and then ", " after ", " and ", " then ", ", then "]
        
        for connector in connectors:
            if connector.lower() in text.lower():
                # Split preserving case-insensitive matching
                parts = text.split(connector)
                all_steps = []
                for part in parts:
                    part = part.strip()
                    if not part:
                        continue
                    # Recursively check if this part also has connectors
                    nested_steps = split_on_connectors(part)
                    all_steps.extend(nested_steps)
                return all_steps if all_steps else [text]
        
        return [text]
    
    try:
        # Split on connectors (handles nested)
        steps = split_on_connectors(user_input)
        
        # Process each step through fast_path_check first, then decide_tool
        plan_steps = []
        for step in steps:
            step = step.strip()
            if not step:  # Skip empty steps
                continue
            
            # ===== BUG 4: Use fast_path_check first for instant matching =====
            # Fast path check for high-frequency patterns
            fast_result = fast_path_check(step)
            
            if fast_result:
                # Fast path matched
                plan_steps.append({
                    "tool": fast_result.get("tool", "ask_brain"),
                    "params": fast_result.get("params", {})
                })
            else:
                # Fall back to decide_tool for complex commands
                result = decide_tool(step)
                
                if result and "tool" in result:
                    plan_steps.append({
                        "tool": result.get("tool", "ask_brain"),
                        "params": result.get("params", {})
                    })
        
        # Return plan or fallback if nothing parsed
        if plan_steps:
            return {"steps": plan_steps}
        else:
            return {
                "steps": [
                    {"tool": "ask_brain", "params": {"user_input": user_input}}
                ]
            }
    
    except Exception as e:
        print(f"Error in plan_tasks: {e}")
        # Safe fallback
        return {
            "steps": [
                {"tool": "ask_brain", "params": {"user_input": user_input}}
            ]
        }
