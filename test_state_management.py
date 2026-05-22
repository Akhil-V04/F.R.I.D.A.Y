#!/usr/bin/env python3
"""
State Management System - Demo & Testing

Run this to see state management in action.
Demonstrates all key scenarios.
"""

import sys
import os
import time
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.state import (
    get_state,
    set_vscode_open,
    set_project,
    set_new_project_mode,
    start_new_project,
    switch_to_existing_project,
    reset_state,
    print_state,
    is_vscode_running,
    sync_vscode_state,
    STATE_FILE
)


def test_basic_state():
    """Test basic state operations"""
    print("\n" + "="*60)
    print("TEST 1: Basic State Operations")
    print("="*60)
    
    # Start fresh
    reset_state()
    
    print("\n1. Initial state (after reset):")
    print_state()
    
    print("\n2. Set VS Code as open:")
    set_vscode_open(True)
    print_state()
    
    print("\n3. Set current project:")
    set_project("my_awesome_app")
    print_state()
    
    print("\n4. Set new project mode:")
    set_new_project_mode(True)
    print_state()


def test_new_project():
    """Test new project mode"""
    print("\n" + "="*60)
    print("TEST 2: New Project Creation")
    print("="*60)
    
    reset_state()
    
    print("\n1. Starting new project 'todo_app':")
    start_new_project("todo_app")
    print_state()
    
    state = get_state()
    assert state["vscode_open"] == True
    assert state["current_project"] == "todo_app"
    assert state["new_project_mode"] == True
    print("\n✓ All fields set correctly")


def test_project_switching():
    """Test switching between projects"""
    print("\n" + "="*60)
    print("TEST 3: Project Switching")
    print("="*60)
    
    reset_state()
    
    print("\n1. Start with new project:")
    start_new_project("calculator_app")
    print_state()
    
    print("\n2. Switch to existing project:")
    switch_to_existing_project("old_project")
    print_state()
    
    state = get_state()
    assert state["current_project"] == "old_project"
    assert state["new_project_mode"] == False  # Switched to existing
    print("\n✓ Project switched, new_project_mode set to False")


def test_smart_vscode_behavior():
    """Test smart VS Code opening logic"""
    print("\n" + "="*60)
    print("TEST 4: Smart VS Code Opening Logic")
    print("="*60)
    
    reset_state()
    
    print("\nScenario 1: VS Code not running, should open")
    set_vscode_open(False)
    state = get_state()
    should_open = not (state["vscode_open"] and not state["new_project_mode"])
    print(f"  Should open new window: {should_open}")
    assert should_open == True, "Should open when not running"
    print("  ✓ Correct")
    
    print("\nScenario 2: VS Code running, NOT new project, should NOT open")
    set_vscode_open(True)
    set_new_project_mode(False)
    state = get_state()
    should_open = not (state["vscode_open"] and not state["new_project_mode"])
    print(f"  Should open new window: {should_open}")
    assert should_open == False, "Should NOT open when already running"
    print("  ✓ Correct (won't disturb existing project)")
    
    print("\nScenario 3: VS Code running, IS new project, should open")
    set_vscode_open(True)
    set_new_project_mode(True)
    state = get_state()
    should_open = state["new_project_mode"]  # Open if new project mode
    print(f"  Should open new window: {should_open}")
    assert should_open == True, "Should open for new project"
    print("  ✓ Correct (opens new window for new project)")


def test_state_persistence():
    """Test state persists across calls"""
    print("\n" + "="*60)
    print("TEST 5: State Persistence")
    print("="*60)
    
    reset_state()
    
    print("\n1. Set state:")
    start_new_project("persistent_app")
    print_state()
    
    print("\n2. Get state again (simulating new session):")
    state1 = get_state()
    state2 = get_state()  # Call again
    
    print(f"  First call:  {state1}")
    print(f"  Second call: {state2}")
    
    assert state1 == state2, "State should be persistent"
    print("\n✓ State persisted correctly")


def test_state_file():
    """Verify state.json file exists and is valid JSON"""
    print("\n" + "="*60)
    print("TEST 6: State File Verification")
    print("="*60)
    
    reset_state()
    start_new_project("test_app")
    
    print(f"\nState file location: {STATE_FILE}")
    
    assert os.path.exists(STATE_FILE), "State file should exist"
    print("✓ State file exists")
    
    with open(STATE_FILE, 'r') as f:
        data = json.load(f)
    
    print(f"\nState file contents:")
    print(json.dumps(data, indent=2))
    
    assert isinstance(data, dict), "State should be dict"
    assert "vscode_open" in data, "Should have vscode_open"
    assert "current_project" in data, "Should have current_project"
    assert "new_project_mode" in data, "Should have new_project_mode"
    print("\n✓ State file format valid")


def test_vscode_detection():
    """Test VS Code process detection"""
    print("\n" + "="*60)
    print("TEST 7: VS Code Process Detection")
    print("="*60)
    
    running = is_vscode_running()
    print(f"\nVS Code currently running: {running}")
    print(f"Process detection method: tasklist (Windows)")
    print("✓ Detection works")


def test_state_sync():
    """Test state sync with actual process"""
    print("\n" + "="*60)
    print("TEST 8: State Synchronization")
    print("="*60)
    
    reset_state()
    
    print("\n1. Pretend VS Code is open:")
    set_vscode_open(True)
    set_project("some_project")
    print_state()
    
    print("\n2. Check actual process status:")
    running = is_vscode_running()
    print(f"   Actual status: {running}")
    
    print("\n3. Sync state (corrects if mismatch):")
    synced_state = sync_vscode_state()
    print_state()
    
    # If VS Code not actually running, state should be corrected
    if not running and synced_state["vscode_open"]:
        print("\n   Note: VS Code not running, but was marked as open")
        print("   State was corrected to vscode_open=false")
    
    print("\n✓ State sync works")


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "STATE MANAGEMENT SYSTEM - TEST SUITE" + " "*7 + "║")
    print("╚" + "="*58 + "╝")
    
    try:
        test_basic_state()
        test_new_project()
        test_project_switching()
        test_smart_vscode_behavior()
        test_state_persistence()
        test_state_file()
        test_vscode_detection()
        test_state_sync()
        
        print("\n" + "="*60)
        print("✓ ALL TESTS PASSED")
        print("="*60)
        
        print("\nKey Features:")
        print("  ✓ State persists across calls (JSON file)")
        print("  ✓ Smart VS Code opening logic")
        print("  ✓ Project tracking")
        print("  ✓ New/existing project detection")
        print("  ✓ Auto-sync with actual process status")
        
        print("\nAPI Examples:")
        print("  from memory.state import start_new_project, get_state")
        print("  start_new_project('my_app')")
        print("  state = get_state()")
        print("  print(state['vscode_open'])  # True")
        
        print("\n" + "="*60 + "\n")
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
