#!/usr/bin/env python3
"""
🚀 START HERE - F.R.I.D.A.Y Tool System Quick Start

Run this file to see everything working, then read the guides.
"""

import subprocess
import sys
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def main():
    print_header("F.R.I.D.A.Y Tool System - Quick Start")
    
    # Check if tool system exists
    tools_dir = Path("tools")
    if not tools_dir.exists():
        print("❌ Error: tools/ directory not found")
        print("Make sure you're in the F.R.I.D.A.Y directory")
        return
    
    print("✅ Tool system found!\n")
    
    # Menu
    while True:
        print("\nWhat would you like to do?")
        print("1. Run tests (8 quick tests)")
        print("2. Run examples (8 complete workflows)")
        print("3. Show quick reference (cheat sheet)")
        print("4. Show documentation (full guides)")
        print("5. Exit")
        
        choice = input("\nEnter 1-5: ").strip()
        
        if choice == "1":
            run_tests()
        elif choice == "2":
            run_examples()
        elif choice == "3":
            show_reference()
        elif choice == "4":
            show_docs()
        elif choice == "5":
            print("\n👋 Goodbye!\n")
            break
        else:
            print("❓ Invalid choice, try again")

def run_tests():
    """Run test suite"""
    print_header("Running Test Suite (8/8 tests)")
    
    result = subprocess.run(
        [sys.executable, "-m", "tools.test_tools"],
        capture_output=False
    )
    
    if result.returncode == 0:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed")

def run_examples():
    """Run example workflows"""
    print_header("Running Example Workflows (8/8 examples)")
    
    result = subprocess.run(
        [sys.executable, "examples_tool_usage.py"],
        capture_output=False
    )
    
    if result.returncode == 0:
        print("\n✅ All examples completed!")
    else:
        print("\n❌ Some examples failed")

def show_reference():
    """Show quick reference"""
    print_header("Quick Reference - Common Commands")
    
    guide = """
BASIC TOOL USAGE
================

From convenience function:
    from tools.executor import execute_tool
    execute_tool("get_time")

From JSON:
    from tools.executor import ToolExecutor
    result = ToolExecutor.execute({"tool": "get_time", "params": {}})

From legacy (unchanged):
    from actions.system import get_time
    get_time()

COMMON EXAMPLES
===============

Get system info:
    execute_tool("get_time")
    execute_tool("get_date")
    execute_tool("get_battery")

Send message:
    execute_tool("send_whatsapp", contact="mom", message="Hello")
    execute_tool("send_email", contact="email@test.com", 
                 subject="Hi", body="Hello")

App control:
    execute_tool("open_app", app_name="chrome")
    execute_tool("close_app", app_name="chrome")

News:
    execute_tool("get_news", category="tech")
    execute_tool("get_world_briefing")

Web:
    execute_tool("search_google", query="python")
    execute_tool("open_url", url="https://google.com")

Screen:
    execute_tool("click_text", text="Submit")
    execute_tool("type_text", text="Hello")
    execute_tool("press_key", key="enter")

ALL 34 TOOLS
============

Messaging: send_whatsapp, send_whatsapp_flow, send_email
Apps: open_app, close_app, close_all_apps
News: get_news, get_world_briefing, get_india_briefing, get_news_by_topic
Screen: click_text, find_text, get_screen_text, scroll_down, scroll_up, 
        type_text, press_key
System: get_time, get_date, get_battery, take_screenshot, shutdown_pc, restart_pc
Web: open_url, search_google, search_youtube, open_world_monitor, 
     open_claude, open_chatgpt, open_and_search
Clock: open_clock, set_timer, set_alarm, close_clock

FOR MORE
========
- Read QUICK_REFERENCE.md for detailed cheat sheet
- Read TOOL_SYSTEM.md for full documentation
- See examples_tool_usage.py for complete workflows
"""
    
    print(guide)

def show_docs():
    """Show documentation guide"""
    print_header("Available Documentation")
    
    docs = """
📚 DOCUMENTATION FILES
=======================

1. QUICK_REFERENCE.md
   - Best for: Quick lookup
   - Length: ~5 min read
   - Contains: Cheat sheet, common operations
   
2. TOOL_SYSTEM.md
   - Best for: Complete understanding
   - Length: ~15 min read
   - Contains: Full guide, architecture, all tools
   
3. TOOL_SYSTEM_SUMMARY.md
   - Best for: Executive overview
   - Length: ~10 min read
   - Contains: Summary, architecture, testing results
   
4. INTEGRATION_GUIDE.md
   - Best for: Advanced integration
   - Length: ~15 min read
   - Contains: Optional refactoring patterns
   
5. DELIVERABLES.md
   - Best for: Project overview
   - Length: ~10 min read
   - Contains: What was delivered, features, results

QUICK START ORDER
=================
1. Read QUICK_REFERENCE.md (5 min)
2. Run examples_tool_usage.py (see it work)
3. Read TOOL_SYSTEM.md (learn fully)
4. Read INTEGRATION_GUIDE.md (if refactoring)

Or just start using tools in your code!

GETTING HELP
============
- All tools have descriptions: get_tool_info("tool_name")
- See parameters: from tools.registry import get_tool_info
- Run tests: python -m tools.test_tools
- Run examples: python examples_tool_usage.py
"""
    
    print(docs)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
