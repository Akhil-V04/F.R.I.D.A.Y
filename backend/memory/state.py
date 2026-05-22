"""
State Management for F.R.I.D.A.Y
Tracks VS Code status, project context, and session mode.

Minimal implementation using JSON file for persistence.
"""

import json
import os
import subprocess
from pathlib import Path


# State file location
STATE_FILE = os.path.join(os.path.dirname(__file__), "state.json")

# Default state
DEFAULT_STATE = {
    "vscode_open": False,
    "current_project": None,
    "new_project_mode": False
}


def _load_state():
    """Load state from JSON file"""
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading state: {e}")
    
    return DEFAULT_STATE.copy()


def _save_state(state):
    """Save state to JSON file"""
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        print(f"Error saving state: {e}")


def is_vscode_running():
    """
    Check if VS Code process is currently running.
    
    Returns:
        bool: True if Code.exe is running, False otherwise
    """
    try:
        result = subprocess.run(["tasklist"], capture_output=True, text=True, timeout=5)
        return "code.exe" in result.stdout.lower()
    except Exception as e:
        print(f"Error checking VS Code process: {e}")
        return False


def sync_vscode_state():
    """
    Sync stored state with actual VS Code process status.
    If VS Code was closed, update state accordingly.
    """
    state = _load_state()
    
    # Check if VS Code is actually running
    running = is_vscode_running()
    
    if state["vscode_open"] and not running:
        # VS Code was open but now closed - update state
        print("[STATE] VS Code closed, updating state...")
        state["vscode_open"] = False
        state["new_project_mode"] = False
        _save_state(state)
    
    return state


def get_state():
    """Get current assistant state (synced with actual process)"""
    return sync_vscode_state()


def set_vscode_open(is_open):
    """Mark VS Code as open/closed"""
    state = _load_state()
    state["vscode_open"] = is_open
    _save_state(state)


def set_project(project_name):
    """Set current project context"""
    state = _load_state()
    state["current_project"] = project_name
    _save_state(state)


def set_new_project_mode(is_new):
    """Set session mode (new project vs existing)"""
    state = _load_state()
    state["new_project_mode"] = is_new
    _save_state(state)


def start_new_project(project_name):
    """
    Initialize new project mode.
    Sets: vscode_open=True, current_project=project_name, new_project_mode=True
    """
    state = {
        "vscode_open": True,
        "current_project": project_name,
        "new_project_mode": True
    }
    _save_state(state)
    return state


def switch_to_existing_project(project_name):
    """
    Switch to existing project.
    Sets: new_project_mode=False, current_project=project_name
    """
    state = _load_state()
    state["current_project"] = project_name
    state["new_project_mode"] = False
    _save_state(state)
    return state


def reset_state():
    """Reset state to default (e.g., when closing all projects)"""
    _save_state(DEFAULT_STATE.copy())


def should_open_new_vscode():
    """
    Determine if we should open a NEW VS Code window.
    
    Returns:
        True if should open new window (either VSCode closed or new project mode)
        False if VSCode already open and not in new project mode
    """
    state = _load_state()
    
    # If VS Code not open, open new one
    if not state["vscode_open"]:
        return True
    
    # If already open but creating new project, open new window
    # (don't disturb existing work)
    
    return False


def print_state():
    """Pretty print current state"""
    state = _load_state()
    print("\n" + "="*50)
    print("ASSISTANT STATE")
    print("="*50)
    print(f"VS Code Open:      {state['vscode_open']}")
    print(f"Current Project:   {state['current_project'] or 'None'}")
    print(f"New Project Mode:  {state['new_project_mode']}")
    print("="*50 + "\n")
