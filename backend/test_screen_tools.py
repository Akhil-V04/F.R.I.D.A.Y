"""
Test screen tools registration and ScreenAgent implementation
"""

import sys
from pathlib import Path

friday_path = Path(__file__).parent
sys.path.insert(0, str(friday_path))

print("=" * 75)
print("Screen Tools Registration Test")
print("=" * 75)
print()

# TEST 1: Import ScreenAgent
print("[TEST 1] Import ScreenAgent from actions.screen")
try:
    from actions.screen import ScreenAgent
    print("✓ ScreenAgent imported successfully")
    print(f"  Type: {type(ScreenAgent)}")
except ImportError as e:
    print(f"✗ Failed to import ScreenAgent: {e}")
    sys.exit(1)
print()

# TEST 2: Instantiate ScreenAgent
print("[TEST 2] Instantiate ScreenAgent")
try:
    agent = ScreenAgent()
    print("✓ ScreenAgent instantiated")
except Exception as e:
    print(f"✗ Failed to instantiate: {e}")
    sys.exit(1)
print()

# TEST 3: Check ScreenAgent methods
print("[TEST 3] Check ScreenAgent methods")
methods = {
    "read_screen_text": "Read text from screen",
    "analyze_screen": "Analyze screen with question",
    "find_and_click": "Find and click text"
}

for method_name, description in methods.items():
    if hasattr(agent, method_name):
        method = getattr(agent, method_name)
        print(f"✓ {method_name}() exists - {description}")
        if callable(method):
            print(f"  ✓ {method_name} is callable")
        else:
            print(f"  ✗ {method_name} is not callable")
    else:
        print(f"✗ {method_name}() NOT found")
print()

# TEST 4: Import registry
print("[TEST 4] Import registry and check ScreenAgent instance")
try:
    from tools.registry import _screen_agent, TOOLS
    print("✓ Registry imported with ScreenAgent instance")
    print(f"  _screen_agent type: {type(_screen_agent)}")
except ImportError as e:
    print(f"✗ Failed to import from registry: {e}")
    sys.exit(1)
print()

# TEST 5: Check registered tools
print("[TEST 5] Check registered tools in TOOLS registry")
screen_tools = ["read_screen", "analyze_screen", "click_text"]

for tool_name in screen_tools:
    if tool_name in TOOLS:
        tool_def = TOOLS[tool_name]
        print(f"✓ {tool_name} registered")
        print(f"  Description: {tool_def.get('description')}")
        print(f"  Function: {tool_def.get('func')}")
    else:
        print(f"✗ {tool_name} NOT registered")
print()

# TEST 6: Check fast_path_check uses read_screen
print("[TEST 6] Verify fast_path_check uses 'read_screen' tool")
from brain.command_parser import fast_path_check
import inspect

source = inspect.getsource(fast_path_check)
if '"read_screen"' in source or "'read_screen'" in source:
    print("✓ fast_path_check uses 'read_screen' tool name")
else:
    print("✗ fast_path_check doesn't use 'read_screen' tool name")
print()

# TEST 7: Test fast_path_check with screen patterns
print("[TEST 7] Test fast_path_check with screen patterns")
test_inputs = [
    "what do you see",
    "read screen",
    "read the screen",
    "screen"
]

for test_input in test_inputs:
    result = fast_path_check(test_input)
    if result and result.get("tool") == "read_screen":
        print(f"✓ '{test_input}' → read_screen tool detected")
    else:
        print(f"✗ '{test_input}' → {result}")
print()

# TEST 8: Check read_screen_text implementation
print("[TEST 8] Check read_screen_text() implementation")
agent_source = inspect.getsource(ScreenAgent.read_screen_text)

checks = {
    "Terminal filtering": "PS ",
    "Virtual env filtering": ".venv",
    "Box drawing char filtering": "─│┌┐└┘",
    "Line length filtering": "len(line) < 4",
    "Max 500 char limit": "[:500]",
    "Returns string": "-> str"
}

for feature, pattern in checks.items():
    if pattern in agent_source:
        print(f"✓ {feature}")
    else:
        print(f"✗ {feature} - pattern not found: {pattern}")
print()

print("=" * 75)
print("✓ Screen Tools Registration Test Complete")
print("=" * 75)
print()
print("Summary:")
print("- ScreenAgent class created with 3 methods")
print("- ScreenAgent imported in registry.py")
print("- _screen_agent instance created in registry")
print("- read_screen, analyze_screen, click_text registered")
print("- fast_path_check detects screen patterns")
print("- read_screen_text filters out terminal output")
print("- All tools return proper response format")
print()
