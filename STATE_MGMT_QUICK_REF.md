# State Management - Quick Reference

## Files Added/Modified

### NEW
- **`memory/state.py`** - State management module (81 lines)

### MODIFIED
- **`actions/apps.py`** - Added VS Code state check (~20 lines)
- **`actions/coding_agent.py`** - Added project tracking (~10 lines)

---

## API Cheat Sheet

```python
from memory.state import *

# READ
get_state()                 # Get full {vscode_open, current_project, new_project_mode}
is_vscode_running()         # Check if VS Code.exe is running

# WRITE
set_vscode_open(True/False)            # Mark VS Code as open/closed
set_project("project_name")             # Set current project
set_new_project_mode(True/False)        # Toggle new project mode
start_new_project("name")               # Start new project (sets all 3)
switch_to_existing_project("name")      # Switch to existing project

# SYNC
sync_vscode_state()         # Sync stored state with actual process
reset_state()               # Reset to default

# DEBUG
print_state()               # Pretty print current state
```

---

## Behavior Rules

### Rule 1: Don't Open If Already Open
```
IF VS Code running AND not new_project_mode
THEN don't open new window
```

### Rule 2: Always Open For New Projects
```
IF building new_project
THEN open new window regardless (new_project_mode=true)
```

### Rule 3: Auto-Detect Closure
```
IF state says open BUT process not running
THEN update state to closed
```

---

## State File

Location: `memory/state.json`

```json
{
  "vscode_open": boolean,
  "current_project": "string or null",
  "new_project_mode": boolean
}
```

---

## Integration Points

### 1. In `actions/apps.py` (ALREADY DONE)

When user says "open VS Code":

```python
# Line ~120 in open_app()
if app_lower in ["vs code", "vscode"]:
    state = get_state()
    vscode_running = is_vscode_running()
    
    if vscode_running and not state["new_project_mode"]:
        return True  # Don't open new window
    else:
        set_vscode_open(True)  # Mark as open, then proceed to open
```

### 2. In `actions/coding_agent.py` (ALREADY DONE)

When creating new project:

```python
# In run_coding_agent()
open_vscode_new_window(project_name=idea)

# In open_vscode_new_window()
if project_name:
    start_new_project(project_name)  # Sets state
```

### 3. In `main.py` (OPTIONAL)

Optionally use state in main loop:

```python
from memory.state import get_state

def startup():
    state = get_state()
    if state["current_project"]:
        speak(f"Working on {state['current_project']}")
```

---

## Example Scenarios

### Scenario A: User tries to open VS Code twice

```
User: "open VS Code"
→ Checks state: vscode_open=true, new_project_mode=false
→ Checks process: Code.exe running
→ Returns True without opening new window ✓

User doesn't notice, existing window keeps focus
```

### Scenario B: User builds new project while one is open

```
User: "build me a calculator"
→ run_coding_agent() called
→ open_vscode_new_window(project_name="calculator")
→ start_new_project("calculator") sets: new_project_mode=true
→ Opens new VS Code window ✓

Now two VS Code windows: original + new project
```

### Scenario C: User closes VS Code manually

```
User closes VS Code window
→ Later: User says "open VS Code"
→ get_state() called: vscode_open=true (outdated)
→ is_vscode_running() → false (actual status)
→ sync_vscode_state() updates state to vscode_open=false ✓
→ Opens new window ✓
```

---

## Testing

Quick sanity check:

```bash
# Run this to verify state operations work
python -c "
from memory.state import *
print('Testing state management...')
start_new_project('test')
print_state()
reset_state()
print('✓ State management working')
"
```

---

## Minimal Changes Summary

| File | Changes | Lines |
|------|---------|-------|
| state.py (NEW) | Full module | 81 |
| apps.py | VS Code check | +20 |
| coding_agent.py | Project tracking | +10 |
| **Total** | **Minimal** | **+30** |

---

## Key Points

✅ **Non-intrusive** - Doesn't modify existing logic
✅ **Self-contained** - All state logic in one module
✅ **Persistent** - State survives restarts
✅ **Smart** - Auto-detects if VS Code closed
✅ **Flexible** - Can extend with more fields if needed

---

## State Transitions

```
Start
  ↓
[Open VS Code]
  → vscode_open=true
  ↓
[Build new project]
  → vscode_open=true, new_project_mode=true, current_project="name"
  ↓
[Open VS Code again - opens NEW window]
  (because new_project_mode=true)
  ↓
[Close new VS Code window]
  → state syncs, updates new_project_mode=false
  ↓
[Open VS Code - reuses existing]
  (because new_project_mode=false)
```

---

## Common Questions

**Q: Does this affect user experience?**
A: No, it prevents annoying behavior (multiple VS Code windows).

**Q: What if state.json gets corrupted?**
A: System generates default state automatically.

**Q: How do I reset state?**
A: Call `reset_state()` or delete `memory/state.json`.

**Q: Does this work with VS Code already running?**
A: Yes, `is_vscode_running()` checks actual process.

**Q: Can I extend this?**
A: Yes, just add fields to state dict and create get/set functions.

---

**Status:** ✅ Ready to use
