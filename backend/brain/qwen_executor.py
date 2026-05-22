"""
Qwen Tool Executor - Unified AI-driven tool selection and execution.

This module uses Qwen (via Ollama) as a decision engine to:
1. Understand user intent
2. Select the best tool (single-step) or plan tasks (multi-step)
3. Extract parameters
4. Execute the tool(s)

Returns ONLY tool execution results (no normal text).
"""

import time
from brain.ollama import decide_tool, plan_tasks
from tools.executor import ToolExecutor
from memory.smart_cache import SmartCache

# Singleton cache instance
_cache = SmartCache()

# Tools that should NOT be cached (real-time data or variable results)
NO_CACHE_TOOLS = {"ask_brain", "get_world_briefing", "set_timer", "read_screen"}


def execute_with_qwen(user_input, original_text=""):
    """
    Execute a user command using Qwen as decision engine.
    With SmartCache integration for instant repeat command execution.
    
    This replaces the old parse_command() + execute_command() flow.
    
    Args:
        user_input (str): User's spoken/typed command
        original_text (str): Original text for logging
    
    Returns:
        str or dict: Tool execution result
    """
    try:
        # ===== CACHE CHECK: Before Qwen processing =====
        cached = _cache.get(user_input)
        if cached:
            print(f"[CACHE HIT] Serving instantly: {user_input}")
            _cache.increment_usage(cached.get("normalized_key", _cache.normalize(user_input)))
            return cached.get("result")
        
        # Record start time for response time tracking
        start_time = time.time()
        
        # Step 1: Use Qwen to decide tool and params
        tool_request = decide_tool(user_input)
        print(f"[Qwen Decision] Tool: {tool_request.get('tool')}, Params: {tool_request.get('params')}")
        
        # Step 2: Handle send_email parameter extraction (fill missing subject/body)
        if tool_request.get("tool") == "send_email":
            tool_request = _enrich_email_params(tool_request, user_input)
        
        # Step 3: Execute the tool
        result = ToolExecutor.execute(tool_request)
        
        # Step 4: Extract result and calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)
        
        if result["success"]:
            tool_name = tool_request.get("tool")
            final_result = result["result"]
            
            # ===== CACHE STORE: After successful execution =====
            # Skip caching for real-time/variable tools
            if tool_name not in NO_CACHE_TOOLS:
                _cache.set(user_input, final_result, tool_name, response_ms=response_time_ms)
                print(f"[CACHE MISS] Response time: {response_time_ms}ms - cached for next time")
            else:
                print(f"[NO CACHE] Tool '{tool_name}' skipped (real-time data)")
            
            return final_result
        else:
            # Don't cache errors
            return f"Tool error: {result.get('error', 'Unknown error')}"
    
    except Exception as e:
        print(f"Error in execute_with_qwen: {e}")
        return f"Execution failed: {str(e)}"


def _enrich_email_params(tool_request, user_input):
    """
    Enrich send_email parameters with contact, subject, and body extracted from user input.
    Fills in missing required parameters - contact from available contacts or defaults.
    
    Args:
        tool_request: {"tool": "send_email", "params": {...}}
        user_input: Original user command
    
    Returns:
        tool_request with enriched params
    """
    from actions.email_sender import CONTACTS
    
    params = tool_request.get("params", {})
    user_lower = user_input.lower()
    
    # ===== EXTRACT CONTACT =====
    if "contact" not in params or not params.get("contact"):
        contact = None
        
        # Try to find known contacts in user input
        for contact_name in CONTACTS.keys():
            if contact_name in user_lower:
                contact = contact_name
                break
        
        # If not found, try patterns like "to [name]", "email to [name]"
        if not contact:
            for pattern in ["to ", "email to ", "send to "]:
                if pattern in user_lower:
                    try:
                        contact_part = user_lower.split(pattern)[1].strip()
                        # Extract first word as contact name
                        contact_candidate = contact_part.split()[0] if contact_part.split() else None
                        if contact_candidate and contact_candidate in CONTACTS:
                            contact = contact_candidate
                            break
                    except:
                        pass
        
        # Fallback: use "mom" as default contact
        if not contact:
            contact = "mom"
        
        params["contact"] = contact
    
    # ===== EXTRACT SUBJECT =====
    if "subject" not in params or not params.get("subject"):
        subject = None
        
        # Try to find subject after common patterns: "subject:", "with subject", "titled", "about"
        for pattern in ["subject:", "with subject", "titled", "about "]:
            if pattern in user_lower:
                try:
                    subject_part = user_lower.split(pattern)[1].strip()
                    # Take content before stop words
                    for stop_word in [" and ", ".", "\n", " say ", " tell ", " with"]:
                        if stop_word in subject_part:
                            subject_part = subject_part.split(stop_word)[0]
                    subject = subject_part.strip()
                    if subject and len(subject) > 2:  # Ensure it's meaningful
                        break
                except:
                    pass
        
        # Fallback to default subject
        if not subject:
            subject = "Message from FRIDAY"
        
        params["subject"] = subject[:100]  # Limit to 100 chars
    
    # ===== EXTRACT BODY =====
    if "body" not in params or not params.get("body"):
        body = None
        
        # Try to find body after common keywords: "message:", "body:", "say", "tell"
        for keyword in ["message:", "body:", "say ", "tell ", "write "]:
            if keyword in user_lower:
                try:
                    body_part = user_lower.split(keyword)[1].strip()
                    # Extract the content (avoid "subject", "to", etc.)
                    for stop_word in ["subject", " with ", "\n\n"]:
                        if stop_word in body_part:
                            body_part = body_part.split(stop_word)[0]
                    body = body_part.strip()
                    if body and len(body) > 2:  # Ensure it's meaningful
                        break
                except:
                    pass
        
        # Fallback to default body
        if not body:
            body = "Sent via FRIDAY assistant"
        
        params["body"] = body
    
    tool_request["params"] = params
    return tool_request


def qwen_decision_only(user_input):
    """
    Get Qwen's tool decision WITHOUT executing.
    Useful for seeing what Qwen decides before executing.
    
    Args:
        user_input (str): User command
    
    Returns:
        dict: {"tool": "name", "params": {...}}
    """
    return decide_tool(user_input)


def execute_plan(plan, user_input=""):
    """
    Execute a multi-step task plan sequentially.
    Stops on first failure and returns partial results.
    
    Args:
        plan (dict): {"steps": [{"tool": "...", "params": {...}}, ...]}
        user_input (str): Original user input for logging
    
    Returns:
        dict: {
            "success": bool,
            "completed_steps": int,
            "total_steps": int,
            "results": [step_results],
            "error": str (if any step failed)
        }
    """
    try:
        steps = plan.get("steps", [])
        if not steps:
            return {
                "success": False,
                "completed_steps": 0,
                "total_steps": 0,
                "results": [],
                "error": "No steps in plan"
            }
        
        results = []
        print(f"\n[TASK PLAN] Executing {len(steps)} steps for: {user_input}")
        
        for i, step in enumerate(steps, 1):
            tool_name = step.get("tool")
            params = step.get("params", {})
            
            print(f"  Step {i}/{len(steps)}: {tool_name}")
            
            # Execute the step
            tool_request = {"tool": tool_name, "params": params}
            result = ToolExecutor.execute(tool_request)
            
            # Store result
            step_result = {
                "step": i,
                "tool": tool_name,
                "success": result.get("success", False),
                "result": result.get("result"),
                "error": result.get("error")
            }
            results.append(step_result)
            
            # Stop if any step fails
            if not result.get("success"):
                print(f"  ✗ Step {i} failed: {result.get('error')}")
                return {
                    "success": False,
                    "completed_steps": i - 1,
                    "total_steps": len(steps),
                    "results": results,
                    "error": f"Step {i} ({tool_name}) failed: {result.get('error')}"
                }
            
            print(f"  ✓ Step {i} complete")
        
        print(f"[TASK PLAN] All {len(steps)} steps completed successfully!")
        
        # Return success with all results
        return {
            "success": True,
            "completed_steps": len(steps),
            "total_steps": len(steps),
            "results": results,
            "error": None
        }
    
    except Exception as e:
        print(f"Error in execute_plan: {e}")
        return {
            "success": False,
            "completed_steps": 0,
            "total_steps": len(plan.get("steps", [])),
            "results": [],
            "error": f"Plan execution failed: {str(e)}"
        }


def detect_multi_step_command(user_input):
    """
    Detect if a command requires multiple steps.
    Uses simple pattern-based heuristics for speed and accuracy.
    
    Args:
        user_input (str): User's command
    
    Returns:
        bool: True if command likely needs multiple steps
    """
    text_lower = user_input.lower().strip()
    
    # ===== PRIMARY DETECTION: Explicit connectors (HIGH CONFIDENCE) =====
    # If command contains "and" or "then" between clauses, it's multi-step
    conjunction_patterns = [
        " and ",      # "open chrome and screenshot"
        " then ",     # "open chrome then screenshot"
        "and then",   # "open chrome and then screenshot"
        " after ",    # "open chrome after you open notepad"
        ", then ",    # "open chrome, then screenshot"
    ]
    
    has_conjunction = any(pattern in text_lower for pattern in conjunction_patterns)
    
    if has_conjunction:
        return True
    
    # ===== SECONDARY DETECTION: Complex planned actions =====
    # Keywords that indicate multi-step tasks
    complex_keywords = [
        "plan", "schedule", "prepare", "setup", "build", "develop",
        "steps", "process", "workflow", "sequence", "organize",
        "first", "second", "third", "next", "meanwhile"
    ]
    
    has_complex = any(kw in text_lower for kw in complex_keywords)
    is_long = len(user_input.split()) > 15
    
    return has_complex or is_long





def execute_smart(user_input, original_text=""):
    """
    Smart execution router - optimal performance for all command types.
    
    Strategy:
    - SIMPLE commands → parse_command() + direct tool execution (FAST, ~100ms)
    - MULTI-STEP commands → Qwen plans + sequential execution (~3-5s)
    - COMPLEX SINGLE commands → Qwen decides (INTELLIGENT, ~2-3s)
    - FALLBACK → ask_brain for general conversation
    
    Benefits:
    - Simple "open chrome" takes ~100ms (vs 2-3s with Qwen)
    - Complex "open chrome and take screenshot" uses task planner
    - Seamless fallback for conversations
    
    Args:
        user_input (str): User's command
        original_text (str): Original text for logging
    
    Returns:
        str or dict: Tool execution result
    """
    try:
        text_lower = user_input.lower().strip()
        
        # ===== CACHE CHECK: Before everything (even fast path) =====
        # Instant return for repeated commands (cached from previous execution)
        cached = _cache.get(user_input)
        if cached:
            print(f"[CACHE HIT] Serving instantly: {user_input}")
            return cached.get("result")
        
        # ===== ULTRA-FAST PATH: Pattern-based direct routing =====
        # Check for high-frequency simple commands before any processing
        from brain.command_parser import fast_path_check
        
        fast_match = fast_path_check(user_input)
        if fast_match:
            # Check if this is a fully-handled command (like email)
            if fast_match.get("handled"):
                print(f"[FAST PATH] Command fully handled: {fast_match.get('result')}")
                # Cache the handled result for next time
                result_value = fast_match.get("result")
                tool_name = fast_match.get("tool", "handled_command")
                _cache.set(user_input, result_value, tool_name, response_ms=0)
                return result_value
            
            # Otherwise, it's a tool that needs execution
            print(f"[FAST PATH] Matched: {fast_match.get('tool')}")
            tool_name = fast_match.get("tool")
            params = fast_match.get("params", {})
            
            # Execute the tool directly without going through Qwen
            result = ToolExecutor.execute({"tool": tool_name, "params": params})
            
            if result["success"]:
                final_result = result["result"]
                # Cache the result for future use
                response_time_ms = 0  # Fast path is always fast
                if tool_name not in NO_CACHE_TOOLS:
                    _cache.set(user_input, final_result, tool_name, response_ms=response_time_ms)
                return final_result
            else:
                print(f"[FAST PATH FAILED] Tool execution error: {result.get('error')}")
        
        # ===== FAST PATH: Simple Direct Execution =====
        # Use when command is unambiguous and pattern-based
        # Patterns: "open X", "close X", "get time", "send message to X with Y"
        
        has_complexity = any(phrase in text_lower for phrase in [
            " and ", " or ", " but ", "while ", "if ", "which ", "that ",
            "something", "anything", "whatever", "tell me", "what ", "how ",
            "do you think", "help me", "figure out"
        ])
        
        is_direct = any(keyword in text_lower for keyword in [
            "open ", "close ", "get time", "get date", "get battery",
            "screenshot", "send message", "send email"
        ])
        
        is_short = len(user_input.split()) <= 10
        
        if is_direct and not has_complexity and is_short:
            # Try direct execution (fast path)
            print(f"[FAST PATH] Simple command: {user_input}")
            from brain.command_parser import parse_command
            
            command = parse_command(user_input)
            if command and command.get("action"):
                # Convert old command format to new tool format
                tool_request = _legacy_command_to_tool(command)
                result = ToolExecutor.execute(tool_request)
                
                if result["success"]:
                    print(f"[FAST PATH OK] Result: {result['result']}")
                    return result["result"]
                else:
                    # Fast path failed, try Qwen
                    print(f"[FAST PATH FAILED] Falling back to Qwen: {result['error']}")
        
        # ===== MULTI-STEP PATH: Task Planning =====
        # Use for commands that require multiple sequential steps
        if detect_multi_step_command(user_input):
            print(f"[MULTI-STEP PATH] Detected multi-step command: {user_input}")
            plan = plan_tasks(user_input)
            
            # FALLBACK: If planner returns only ask_brain, it failed to parse
            # Route to Qwen instead of executing useless single-step plan
            steps = plan.get("steps", [])
            if len(steps) == 1 and steps[0].get("tool") == "ask_brain":
                print(f"[MULTI-STEP FALLBACK] Planner returned only ask_brain, routing to Qwen instead")
                return execute_with_qwen(user_input, original_text)
            
            result = execute_plan(plan, user_input)
            
            # Format the result for voice output
            if result.get("success"):
                # Return summary of completed steps
                return f"Task completed: Executed {result.get('completed_steps')} steps successfully."
            else:
                # Return error with partial progress
                return f"Task partially completed ({result.get('completed_steps')}/{result.get('total_steps')} steps). " \
                       f"Error at step {result.get('completed_steps', 0) + 1}: {result.get('error')}"
        
        # ===== INTELLIGENT PATH: Qwen Decision (Single-Step) =====
        # Use for complex, ambiguous, or conversational commands
        print(f"[QWEN PATH] Routing to Qwen: {user_input}")
        return execute_with_qwen(user_input, original_text)
    
    except Exception as e:
        print(f"Error in execute_smart: {e}")
        # Emergency fallback: use ask_brain for general conversation
        from brain.ollama import ask_brain
        return ask_brain(user_input)


def _legacy_command_to_tool(command):
    """
    Convert old parse_command() format to new tool format.
    
    Args:
        command (dict): {"action": "...", "target": "..."}
    
    Returns:
        dict: {"tool": "...", "params": {...}}
    """
    action = command.get("action", "ask_brain")
    target = command.get("target", "")
    
    # Mapping from old actions to new tools
    action_to_tool = {
        "open_app": "open_app",
        "close_app": "close_app",
        "close_all_apps": "close_all_apps",
        "open_url": "open_url",
        "search_google": "search_google",
        "search_youtube": "search_youtube",
        "get_time": "get_time",
        "get_date": "get_date",
        "get_battery": "get_battery",
        "take_screenshot": "take_screenshot",
        "whatsapp_flow": "send_whatsapp_flow",
        "email_flow": "send_email",
        "world_briefing": "get_world_briefing",
        "india_briefing": "get_india_briefing",
        "ask_brain": "ask_brain",
    }
    
    tool_name = action_to_tool.get(action, "ask_brain")
    
    # Parameter mapping based on tool
    params = {}
    
    if tool_name == "open_app":
        params = {"app_name": target}
    elif tool_name == "close_app":
        params = {"app_name": target}
    elif tool_name == "open_url":
        params = {"url": target}
    elif tool_name in ["search_google", "search_youtube"]:
        params = {"query": target}
    elif tool_name == "send_whatsapp_flow":
        params = {"initial_contact": target}
    elif tool_name == "send_email":
        params = {"contact": target}
    elif tool_name == "ask_brain":
        params = {"user_input": target or ""}
    
    return {"tool": tool_name, "params": params}
