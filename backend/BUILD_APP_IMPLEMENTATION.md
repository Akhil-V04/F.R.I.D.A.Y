# Build App Command - Implementation Code

## COPY THESE IMPLEMENTATIONS INTO `actions/coding_agent.py`

### ADD AT TOP (After existing imports):

```python
import requests
import json
from pathlib import Path
from datetime import datetime
```

---

## NEW HELPER FUNCTIONS (Add to coding_agent.py):

### 1. Qwen-Based Idea Refinement

```python
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
```

### 2. Generate Structured Plan

```python
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
```

### 3. Generate File Structure

```python
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
```

### 4. Generate Code for a File

```python
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
```

### 5. Create Project Folder

```python
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
```

### 6. Write Project Files

```python
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
            print(f"  ✓ {filename}")
        
        print(f"[STEP 5b] Files written: {written} files")
        return True
    except Exception as e:
        print(f"[ERROR] File writing failed: {e}")
        return False
```

### 7. Open Project in VS Code

```python
def open_project_in_vscode(project_path: str) -> bool:
    """
    Open project folder in VS Code (CLI-based, no UI automation).
    
    Args:
        project_path: Path to project folder
        
    Returns:
        True if opened successfully
    """
    try:
        from memory.state import start_new_project
        import subprocess
        
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
```

### 8. Step Logger

```python
def log_step(step_num: int, description: str, duration_ms: float = 0):
    """Log a step in the build process."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    timing = f" ({duration_ms}ms)" if duration_ms > 0 else ""
    print(f"\n[{timestamp}] Step {step_num}: {description}{timing}")
```

### 9. Main New Function (run_coding_agent_v2)

```python
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
        print("\n" + "="*50)
        print("BUILD APP - STABLE VERSION")
        print("="*50)
        
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
        
        for filename, description in file_structure.get("files", {}).items():
            step_start = time.time()
            code = generate_code_for_file(
                filename,
                Path(filename).suffix,
                refined_idea,
                description
            )
            code_map[filename] = code
            step_duration = (time.time() - step_start) * 1000
            
            # Speak progress
            progress = len(code_map)
            if progress % 3 == 0:  # Every 3 files
                speak(f"Generated {progress} of {total_files} files.")
        
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
        
        print("\n" + "="*50)
        print(f"✅ PROJECT CREATED SUCCESSFULLY")
        print("="*50)
        print(f"Project: {project_name}")
        print(f"Location: {project_path}")
        print(f"Files: {len(code_map)}")
        print(f"Time: {total_duration:.1f}s")
        print("="*50 + "\n")
        
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
        print(f"\n❌ BUILD FAILED: {str(e)}")
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
```

---

## MODIFY EXISTING FUNCTIONS:

### Update `coding_agent_flow()` to use new v2:

**REPLACE this:**
```python
def coding_agent_flow(initial_command=""):
    # ... old code that calls run_coding_agent()
    result = run_coding_agent(idea)
    return result
```

**WITH this:**
```python
def coding_agent_flow(initial_command=""):
    """
    Main voice-triggered flow for the coding agent.
    Uses new stable v2 approach (Qwen-based, no browser).
    
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
    
    speak(f"Building {idea} for you boss. This will be fast, stable version.")
    
    # Use NEW v2 approach
    result = run_coding_agent_v2(idea)
    
    if result["success"]:
        return f"✅ {result['project_name']} created in {result['duration_seconds']:.1f}s"
    else:
        return f"❌ Build failed: {result['error']}"
```

---

## KEEP OLD FUNCTIONS (For backward compatibility):

Don't delete these, just add [DEPRECATED] comment:

```python
# [DEPRECATED] Old browser-based approach - kept for fallback
def open_chatgpt_and_ask(prompt_text):
    """DEPRECATED: Use Qwen instead."""
    # ... existing code unchanged

# [DEPRECATED] Old browser-based approach - kept for fallback
def paste_to_copilot(prompt_text):
    """DEPRECATED: Use Qwen instead."""
    # ... existing code unchanged

# [DEPRECATED] Old approach - kept for fallback
def run_coding_agent(idea):
    """DEPRECATED: Use run_coding_agent_v2() instead."""
    # ... existing code unchanged
```

---

## SUMMARY OF CHANGES

### Remove (Complete):
- ❌ `open_chatgpt_and_ask()` functionality (keep function, mark deprecated)
- ❌ `paste_to_copilot()` functionality (keep function, mark deprecated)
- ❌ `run_coding_agent()` internal logic (keep function, mark deprecated)

### Add (New Functions):
- ✅ `refine_app_idea()` - Qwen idea validation
- ✅ `generate_app_plan()` - Qwen plan generation
- ✅ `generate_file_structure()` - Qwen structure generation
- ✅ `generate_code_for_file()` - Qwen code generation
- ✅ `create_project_folder()` - Filesystem operations
- ✅ `write_project_files()` - Filesystem operations
- ✅ `open_project_in_vscode()` - VS Code CLI
- ✅ `log_step()` - Logging utility
- ✅ `run_coding_agent_v2()` - Main new function

### Update:
- ✅ `coding_agent_flow()` - Call v2 instead of old approach
- ✅ `open_vscode_new_window()` - Already uses state management

### Total Lines:
- **Added:** ~450 lines (all helper functions + v2)
- **Deleted:** ~100 lines (old approaches marked deprecated)
- **Net:** +350 lines (all in one file)

---

## INTEGRATION CHECKLIST

- [ ] Copy all new functions into `coding_agent.py`
- [ ] Update `coding_agent_flow()` to call `run_coding_agent_v2()`
- [ ] Mark old functions as `[DEPRECATED]`
- [ ] Add imports: `requests`, `json`, `Path`, `datetime`
- [ ] Test with: "build me a calculator"
- [ ] Verify files created
- [ ] Verify VS Code opens
- [ ] Check state tracking

---

## TESTING

```bash
# Quick test
python -c "
from actions.coding_agent import run_coding_agent_v2
result = run_coding_agent_v2('simple counter app')
print(f'Success: {result[\"success\"]}')
print(f'Files: {result[\"files_created\"]}')
print(f'Time: {result[\"duration_seconds\"]:.1f}s')
"
```

---

**Status:** Ready for implementation
