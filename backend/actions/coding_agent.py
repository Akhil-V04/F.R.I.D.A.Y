"""
FRIDAY Autonomous Coding Agent
Generates complete projects using Qwen-based local processing.
"""

import subprocess
import time
import pyautogui
import pyperclip
import os
import webbrowser
import json
import urllib.parse
from pathlib import Path
from datetime import datetime

from voice.tts import speak
from voice.stt import listen
from memory.state import start_new_project, set_vscode_open, get_state, is_vscode_running
from actions.screen import get_screen_text

# Constants
VSCODE_PATH = "C:\\Users\\akhil\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"
CHATGPT_URL = "https://chatgpt.com"
CHROME_PATH = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"


# ============================================================================
# MAIN FLOW: ChatGPT Research → VS Code → Copilot (Fully Automated)
# ============================================================================


def run_coding_agent(project_description: str) -> str:
    """
    Autonomous coding agent: ChatGPT research → VS Code → Copilot.
    
    STEP 1: Open ChatGPT in Chrome (personal profile)
    STEP 2: Copy ChatGPT response from screen
    STEP 3: Open VS Code (check state if already open)
    STEP 4: Open Copilot chat in VS Code
    STEP 5: Paste research into Copilot
    STEP 6: Return confirmation
    
    Args:
        project_description (str): Description of the project to build
    
    Returns:
        str: Status message
    """
    try:
        # ===== STEP 1: Open ChatGPT in Chrome =====
        print("[STEP 1] Opening ChatGPT in Chrome (personal profile)...")
        speak("Researching your project with ChatGPT boss.")
        
        try:
            # Build ChatGPT URL with prompt
            chatgpt_prompt = f"{project_description} give me a step by step implementation plan"
            url = f"https://chatgpt.com/?q={urllib.parse.quote(chatgpt_prompt)}"
            
            # Open Chrome with default personal profile
            subprocess.Popen([CHROME_PATH, "--profile-directory=Default", url])
            time.sleep(8)  # Wait for ChatGPT page to load
        except Exception as e:
            return f"[FAILED - STEP 1] Could not open ChatGPT: {str(e)}"
        
        # ===== STEP 2: Copy ChatGPT response from screen =====
        print("[STEP 2] Reading ChatGPT response from screen...")
        speak("Reading the research from ChatGPT.")
        
        try:
            # Poll screen text until we get substantial response (> 200 chars)
            research_result = ""
            max_wait_time = 30  # Max 30 seconds
            poll_interval = 2   # Check every 2 seconds
            elapsed = 0
            
            while elapsed < max_wait_time:
                current_text = get_screen_text()
                
                # Check if we have meaningful response
                if current_text and len(current_text) > 200:
                    research_result = current_text
                    print(f"[OK] Got response ({len(research_result)} chars)")
                    speak("Got the research results boss.")
                    break
                
                # Wait before retrying
                time.sleep(poll_interval)
                elapsed += poll_interval
            
            if not research_result:
                # Timeout - use whatever we have or default message
                research_result = "Unable to fetch ChatGPT response. Using project description as fallback."
                print(f"[WARNING] Screen text poll timed out. Using fallback.")
        except Exception as e:
            return f"[FAILED - STEP 2] Could not read screen: {str(e)}"
        
        # ===== STEP 3: Open VS Code =====
        print("[STEP 3] Opening VS Code...")
        speak("Opening VS Code now.")
        
        try:
            # Check if VS Code is already open
            state = get_state()
            
            if not state.get("vscode_open") and not is_vscode_running():
                # VS Code not open - launch it
                subprocess.Popen([VSCODE_PATH, "--new-window"])
                time.sleep(4)  # Wait for VS Code to start
                set_vscode_open(True)
                print("[OK] VS Code opened")
            else:
                print("[OK] VS Code already running")
                set_vscode_open(True)
        except Exception as e:
            return f"[FAILED - STEP 3] Could not open VS Code: {str(e)}"
        
        # ===== STEP 4: Open Copilot chat in VS Code =====
        print("[STEP 4] Opening Copilot chat...")
        speak("Opening Copilot chat in VS Code.")
        
        try:
            # Open Copilot chat with Ctrl+Shift+I
            pyautogui.hotkey('ctrl', 'shift', 'i')
            time.sleep(2)  # Wait for Copilot panel to open
            print("[OK] Copilot chat opened")
        except Exception as e:
            return f"[FAILED - STEP 4] Could not open Copilot chat: {str(e)}"
        
        # ===== STEP 5: Paste research into Copilot =====
        print("[STEP 5] Pasting research into Copilot...")
        speak("Pasting the plan to Copilot.")
        
        try:
            # Build the prompt for Copilot
            prompt_text = f"Build this for me:\n{project_description}\n\nResearch:\n{research_result[:800]}"
            
            # Copy to clipboard and paste
            pyperclip.copy(prompt_text)
            time.sleep(0.3)
            
            pyautogui.hotkey('ctrl', 'v')  # Paste
            time.sleep(0.5)
            
            pyautogui.press('enter')  # Send prompt
            print("[OK] Prompt sent to Copilot")
            speak("Plan sent to Copilot. Start building boss.")
        except Exception as e:
            return f"[FAILED - STEP 5] Could not paste to Copilot: {str(e)}"
        
        # ===== STEP 6: Return confirmation =====
        print("[SUCCESS] All steps completed!")
        return "Boss, I've sent the project plan to Copilot. ChatGPT research included. You're good to go."
    
    except Exception as e:
        # Unexpected error
        error_msg = f"[FAILED] Unexpected error: {str(e)}"
        print(error_msg)
        speak(f"Sorry boss, something went wrong: {str(e)}")
        return error_msg


# ============================================================================
# NEW STABLE APPROACH - Qwen-based generation + filesystem operations
# ============================================================================


def refine_app_idea(idea: str) -> str:
    """
    Use Qwen to validate and refine the app idea.
    
    Args:
        idea: Raw app idea from user
        
    Returns:
        Refined, validated idea
    """
    try:
        from brain.ollama import ask_brain
        
        prompt = f"""User wants to build: {idea}

Validate and refine this idea. Make it:
1. Specific and achievable
2. Scope-appropriate (can build in minutes)
3. Interesting and useful

Return ONLY the refined idea (1-2 sentences), nothing else."""
        
        refined = ask_brain(prompt)
        print(f"[STEP 1] Idea refined: {refined}")
        return refined.strip()
    except Exception as e:
        print(f"[ERROR] Idea refinement failed: {e}")
        return idea  # Fallback to original


def generate_app_plan(idea: str) -> str:
    """
    Use Qwen to generate a structured plan for building the app.
    
    Args:
        idea: Refined app idea
        
    Returns:
        Structured plan (steps)
    """
    try:
        from brain.ollama import ask_brain
        
        prompt = f"""Build plan for: {idea}

Create a clear, numbered plan with 3-5 HIGH-LEVEL steps.
Focus on architecture, not implementation details.

Format:
1. [Step name] - [brief description]
2. [Step name] - [brief description]
...

Return ONLY the plan, nothing else."""
        
        plan = ask_brain(prompt)
        print(f"[STEP 2] Plan generated:\n{plan}")
        return plan.strip()
    except Exception as e:
        print(f"[ERROR] Plan generation failed: {e}")
        return "No plan available"


def generate_file_structure(idea: str, plan: str) -> dict:
    """
    Use Qwen to determine needed files and folder structure.
    
    Args:
        idea: App idea
        plan: High-level plan
        
    Returns:
        Dict with file paths and descriptions
    """
    try:
        from brain.ollama import ask_brain
        
        prompt = f"""For building: {idea}

With this plan:
{plan}

What files and folders do we need?

Return JSON ONLY:
{{
  "files": {{
    "main.py": "Main file description",
    "utils.py": "Utilities description",
    "config.json": "Config file"
  }},
  "folders": ["src", "tests", "data"]
}}

No other text, just JSON."""
        
        response = ask_brain(prompt)
        
        # Try to parse JSON
        json_str = response[response.find('{'):response.rfind('}')+1]
        structure = json.loads(json_str)
        print(f"[STEP 3] File structure generated: {len(structure['files'])} files")
        return structure
    except Exception as e:
        print(f"[ERROR] File structure generation failed: {e}")
        # Return minimal structure
        return {
            "files": {"main.py": "Main file"},
            "folders": []
        }


def generate_code_for_file(filename: str, filetype: str, idea: str, context: str) -> str:
    """
    Use Qwen to generate code for a specific file.
    
    Args:
        filename: Name of file to generate
        filetype: Type of file (.py, .json, .txt)
        idea: App idea
        context: Context about the app
        
    Returns:
        Complete code for the file
    """
    try:
        from brain.ollama import ask_brain
        
        filetype_hint = {
            ".py": "Python",
            ".js": "JavaScript",
            ".json": "JSON config",
            ".txt": "Plain text",
            ".md": "Markdown"
        }.get(filetype, "Text")
        
        prompt = f"""Generate complete code for file: {filename}

App: {idea}
Context: {context}

Requirements:
1. Production-quality code
2. Complete and working
3. Well-commented
4. Proper error handling
5. {filetype_hint} format

Return ONLY code, no explanations."""
        
        code = ask_brain(prompt)
        print(f"[STEP 4] Generated {filename} ({len(code)} chars)")
        return code.strip()
    except Exception as e:
        print(f"[ERROR] Code generation for {filename} failed: {e}")
        return f"# Error generating {filename}\n# {str(e)}"


def create_project_folder(project_name: str) -> str:
    """
    Create project folder in user's Downloads.
    
    Args:
        project_name: Name of project
        
    Returns:
        Full path to project folder
    """
    try:
        # Use user's Downloads folder
        downloads = Path.home() / "Downloads"
        project_path = downloads / project_name.replace(" ", "_").lower()
        
        # Create folder
        project_path.mkdir(parents=True, exist_ok=True)
        print(f"[STEP 5a] Project folder created: {project_path}")
        return str(project_path)
    except Exception as e:
        print(f"[ERROR] Folder creation failed: {e}")
        raise


def write_project_files(project_path: str, file_structure: dict, code_map: dict) -> bool:
    """
    Write generated code files to project folder.
    
    Args:
        project_path: Path to project folder
        file_structure: Structure from generate_file_structure()
        code_map: Dict of {filename: code}
        
    Returns:
        True if successful
    """
    try:
        project = Path(project_path)
        
        # Create folders
        for folder in file_structure.get("folders", []):
            (project / folder).mkdir(exist_ok=True)
        
        # Write files
        written = 0
        for filename, code in code_map.items():
            filepath = project / filename
            filepath.parent.mkdir(parents=True, exist_ok=True)
            filepath.write_text(code)
            written += 1
            print(f"  [OK] {filename}")
        
        print(f"[STEP 5b] Files written: {written} files")
        return True
    except Exception as e:
        print(f"[ERROR] File writing failed: {e}")
        return False


def open_project_in_vscode(project_path: str) -> bool:
    """
    Open project folder in VS Code (CLI-based, no UI automation).
    
    Args:
        project_path: Path to project folder
        
    Returns:
        True if opened successfully
    """
    try:
        # Mark as new project in state
        project_name = Path(project_path).name
        start_new_project(project_name)
        
        # Open with VS Code CLI (no UI automation)
        subprocess.Popen([VSCODE_PATH, project_path])
        print(f"[STEP 6] VS Code opened: {project_path}")
        time.sleep(2)  # Give VS Code time to open
        return True
    except Exception as e:
        print(f"[ERROR] VS Code open failed: {e}")
        return False


def run_coding_agent_v2(initial_idea: str) -> dict:
    """
    NEW STABLE APPROACH: Qwen-based generation + filesystem operations.
    
    No browser automation, no long waits, all local processing.
    
    Args:
        initial_idea: User's app idea
        
    Returns:
        dict with:
        {
            "success": bool,
            "project_name": str,
            "project_path": str,
            "plan": str,
            "files_created": int,
            "duration_seconds": float,
            "error": str or None
        }
    """
    start_time = time.time()
    
    try:
        print("\n" + "="*60)
        print("BUILD APP - STABLE VERSION (Qwen-based)")
        print("="*60)
        
        speak("Refining your app idea with Qwen boss.")
        
        # STEP 1: Refine idea
        step_start = time.time()
        refined_idea = refine_app_idea(initial_idea)
        step_duration = (time.time() - step_start) * 1000
        
        # STEP 2: Generate plan
        step_start = time.time()
        speak("Creating project plan.")
        plan = generate_app_plan(refined_idea)
        step_duration = (time.time() - step_start) * 1000
        
        # STEP 3: Generate file structure
        step_start = time.time()
        speak("Defining file structure.")
        file_structure = generate_file_structure(refined_idea, plan)
        step_duration = (time.time() - step_start) * 1000
        
        # STEP 4: Create project folder
        step_start = time.time()
        speak("Creating project folder.")
        project_path = create_project_folder(refined_idea)
        step_duration = (time.time() - step_start) * 1000
        
        # STEP 5: Generate code for each file
        speak("Generating code files.")
        code_map = {}
        total_files = len(file_structure.get("files", {}))
        
        for i, (filename, description) in enumerate(file_structure.get("files", {}).items(), 1):
            step_start = time.time()
            code = generate_code_for_file(
                filename,
                Path(filename).suffix,
                refined_idea,
                description
            )
            code_map[filename] = code
            step_duration = (time.time() - step_start) * 1000
            
            # Speak progress every 3 files
            if i % 3 == 0:
                speak(f"Generated {i} of {total_files} files.")
        
        # STEP 6: Write files to disk
        step_start = time.time()
        speak("Writing files to project.")
        
        if not write_project_files(project_path, file_structure, code_map):
            raise Exception("Failed to write files")
        
        step_duration = (time.time() - step_start) * 1000
        
        # STEP 7: Open in VS Code
        step_start = time.time()
        speak("Opening VS Code with your project boss.")
        
        if not open_project_in_vscode(project_path):
            print("[WARNING] VS Code open may have failed, but files exist")
        
        step_duration = (time.time() - step_start) * 1000
        
        # SUCCESS
        total_duration = time.time() - start_time
        project_name = Path(project_path).name
        
        print("\n" + "="*60)
        print(f"[SUCCESS] PROJECT CREATED SUCCESSFULLY")
        print("="*60)
        print(f"Project: {project_name}")
        print(f"Location: {project_path}")
        print(f"Files: {len(code_map)}")
        print(f"Time: {total_duration:.1f}s")
        print("="*60 + "\n")
        
        speak(f"Done boss! Your {project_name} project is ready at {project_path}")
        
        return {
            "success": True,
            "project_name": project_name,
            "project_path": project_path,
            "plan": plan,
            "files_created": len(code_map),
            "duration_seconds": total_duration,
            "error": None
        }
    
    except Exception as e:
        print(f"\n[FAILED] BUILD FAILED: {str(e)}")
        speak(f"Sorry boss, I ran into an issue: {str(e)}")
        
        return {
            "success": False,
            "project_name": None,
            "project_path": None,
            "plan": None,
            "files_created": 0,
            "duration_seconds": time.time() - start_time,
            "error": str(e)
        }


# ============================================================================
# DEPRECATED: Old browser-based approach - kept for backward compatibility
# ============================================================================


def open_chatgpt_and_ask(prompt_text):
    """
    Open ChatGPT in Chrome, send prompt, and retrieve response.
    
    Args:
        prompt_text (str): The prompt to send to ChatGPT
        
    Returns:
        str: The response text from ChatGPT
    """
    # Open ChatGPT in Chrome with default profile
    subprocess.Popen([CHROME_PATH, "--profile-directory=Default", CHATGPT_URL])
    time.sleep(6)
    
    # Click on message input area (bottom center of ChatGPT)
    pyautogui.click(756, 650)
    time.sleep(1)
    
    # Type prompt using clipboard
    pyperclip.copy(prompt_text)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)
    
    # Send prompt
    pyautogui.press('enter')
    time.sleep(20)  # Wait for ChatGPT response
    
    # Copy response text
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.3)
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(0.3)
    
    # Paste from clipboard
    response = pyperclip.paste()
    
    return response


def open_vscode_new_window(project_name=""):
    """
    Open a new VS Code window and mark project as new.
    
    Args:
        project_name (str): Name of the new project
    
    Returns:
        bool: True if opened successfully
    """
    try:
        # Mark as new project in state
        if project_name:
            start_new_project(project_name)
        
        subprocess.Popen([VSCODE_PATH, "--new-window"])
        time.sleep(4)
        return True
    except Exception as e:
        print(f"Error opening VS Code: {e}")
        return False


def paste_to_copilot(prompt_text):
    """
    Open VS Code Copilot chat and paste prompt.
    
    Args:
        prompt_text (str): The prompt to send to Copilot
        
    Returns:
        bool: True if pasted successfully
    """
    try:
        # Try to open Copilot chat with Ctrl+Shift+I
        pyautogui.hotkey('ctrl', 'shift', 'i')
        time.sleep(2)
        
        # If that doesn't work, try Ctrl+I
        if not pyautogui.locateOnScreen:  # Simple fallback
            pyautogui.hotkey('ctrl', 'i')
            time.sleep(2)
        
        # Click on Copilot input area
        pyautogui.click(756, 650)
        time.sleep(1)
        
        # Type prompt
        pyperclip.copy(prompt_text)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.5)
        
        # Send prompt
        pyautogui.press('enter')
        
        return True
    except Exception as e:
        print(f"Error pasting to Copilot: {e}")
        return False


def run_coding_agent_deprecated(idea):
    """
    DEPRECATED: Old browser-based coding agent (kept for backward compatibility).
    Use run_coding_agent() instead.
    
    Args:
        idea (str): The project idea to implement
        
    Returns:
        str: Completion message
    """
    speak("Interesting idea boss. Let me research this for you.")
    time.sleep(0.5)
    
    # Build research prompt for ChatGPT
    research_prompt = f"""I want to build: {idea}
    
Please provide:
1. Best approach and tech stack
2. Complete file structure
3. Full working code for each file
4. Step by step implementation

Make it production quality and complete."""
    
    speak("Opening ChatGPT to research your project boss.")
    response = open_chatgpt_and_ask(research_prompt)
    
    speak("Got the solution boss. Opening VS Code now.")
    # Pass project idea to open_vscode_new_window (marks as new project in state)
    open_vscode_new_window(project_name=idea)
    
    speak("Pasting to Copilot to build your project boss.")
    
    # Build Copilot prompt with research findings
    copilot_prompt = f"""Build this complete project for me:

Project: {idea}

Research and solution:
{response[:2000] if response else 'Build a complete working ' + idea}

Create all necessary files with complete working code."""
    
    paste_to_copilot(copilot_prompt)
    
    return f"Project {idea} is being built in VS Code boss."


def coding_agent_flow(initial_command=""):
    """
    Main voice-triggered flow for the coding agent.
    Uses new stable v2 approach (Qwen-based, no browser automation).
    
    Args:
        initial_command (str): The initial command from voice input
        
    Returns:
        str: Status message
    """
    # Extract project idea from command
    idea = initial_command
    
    # Remove common trigger words
    for word in ["build me", "create", "make", "develop", "build a", "build an"]:
        idea = idea.replace(word, "").strip()
    
    # If no idea extracted, ask for it
    if len(idea) < 3:
        speak("What do you want to build boss?")
        idea = listen()
        
        if not idea:
            return "Couldn't hear your idea boss."
    
    speak(f"Building {idea} for you boss. Fast and stable.")
    
    # Use NEW v2 approach (Qwen-based, no browser)
    result = run_coding_agent_v2(idea)
    
    if result["success"]:
        return f"[SUCCESS] {result['project_name']} created in {result['duration_seconds']:.1f}s"
    else:
        return f"[FAILED] Build failed: {result['error']}"
