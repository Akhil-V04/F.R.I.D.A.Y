#!/usr/bin/env python3
"""
Test script for Smart Execution Router integration.

Tests both fast path (simple commands) and intelligent path (Qwen commands).
"""

import time
from brain.qwen_executor import execute_smart, execute_with_qwen, qwen_decision_only
from brain.command_parser import parse_command

# Suppress dashboard updates during testing
import os
os.environ['FRIDAY_TEST_MODE'] = '1'


def test_fast_path():
    """Test commands that should use fast path (direct execution)"""
    print("\n" + "="*60)
    print("TESTING FAST PATH (Simple Commands)")
    print("="*60)
    
    fast_commands = [
        "get time",
        "get date",
        "get battery",
        "take screenshot",
        "open chrome",
        "close chrome",
    ]
    
    for cmd in fast_commands:
        print(f"\n[FAST] Testing: {cmd}")
        start = time.time()
        try:
            result = execute_smart(cmd)
            elapsed = time.time() - start
            print(f"  Result: {result}")
            print(f"  Time: {elapsed:.2f}s")
            if elapsed > 0.5:
                print(f"  ⚠️  WARNING: Fast path took too long!")
        except Exception as e:
            print(f"  ❌ Error: {e}")


def test_qwen_path():
    """Test commands that should use Qwen path (intelligent execution)"""
    print("\n" + "="*60)
    print("TESTING QWEN PATH (Complex Commands)")
    print("="*60)
    
    qwen_commands = [
        "tell me something useful",
        "what should I do",
        "help me with my day",
        "do something interesting",
    ]
    
    for cmd in qwen_commands:
        print(f"\n[QWEN] Testing: {cmd}")
        start = time.time()
        try:
            decision = qwen_decision_only(cmd)
            print(f"  Decision: {decision}")
            
            # Full execution
            result = execute_smart(cmd)
            elapsed = time.time() - start
            print(f"  Result: {result}")
            print(f"  Time: {elapsed:.2f}s")
        except Exception as e:
            print(f"  ❌ Error: {e}")


def test_decision_consistency():
    """Test that Qwen makes consistent decisions"""
    print("\n" + "="*60)
    print("TESTING DECISION CONSISTENCY")
    print("="*60)
    
    test_commands = [
        ("get the time", "get_time"),
        ("open google chrome", "open_app"),
        ("search for python tutorials", "search_google"),
    ]
    
    for cmd, expected_tool in test_commands:
        print(f"\n[DECIDE] Testing: {cmd}")
        try:
            decision = qwen_decision_only(cmd)
            tool = decision.get("tool")
            print(f"  Expected: {expected_tool}")
            print(f"  Got: {tool}")
            if tool == expected_tool or tool.startswith(expected_tool.split("_")[0]):
                print(f"  ✅ Match!")
            else:
                print(f"  ⚠️  Different tool selected (may still be valid)")
        except Exception as e:
            print(f"  ❌ Error: {e}")


def test_backward_compatibility():
    """Test that parse_command still works for old code"""
    print("\n" + "="*60)
    print("TESTING BACKWARD COMPATIBILITY")
    print("="*60)
    
    test_commands = [
        "open chrome",
        "get time",
        "search python",
    ]
    
    for cmd in test_commands:
        print(f"\n[COMPAT] Testing: {cmd}")
        try:
            command = parse_command(cmd)
            print(f"  Parsed: {command}")
            print(f"  ✅ parse_command still works")
        except Exception as e:
            print(f"  ❌ Error: {e}")


def test_performance_summary():
    """Test overall performance"""
    print("\n" + "="*60)
    print("PERFORMANCE SUMMARY")
    print("="*60)
    
    # Fast path test
    print("\nFast Path Benchmark (10 iterations):")
    start = time.time()
    for i in range(10):
        try:
            execute_smart("get time")
        except:
            pass
    elapsed = time.time() - start
    avg_time = elapsed / 10
    print(f"  Average time: {avg_time*1000:.1f}ms per command")
    print(f"  Total: {elapsed:.2f}s for 10 commands")
    
    # Qwen path test
    print("\nQwen Path Benchmark (2 iterations):")
    start = time.time()
    count = 0
    for i in range(2):
        try:
            result = execute_smart("tell me something useful")
            count += 1
        except:
            pass
    elapsed = time.time() - start
    if count > 0:
        avg_time = elapsed / count
        print(f"  Average time: {avg_time*1000:.1f}ms per command")
        print(f"  Total: {elapsed:.2f}s for {count} commands")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("SMART EXECUTION ROUTER INTEGRATION TEST")
    print("="*60)
    
    try:
        # Run tests
        test_fast_path()
        test_qwen_path()
        test_decision_consistency()
        test_backward_compatibility()
        test_performance_summary()
        
        print("\n" + "="*60)
        print("✅ INTEGRATION TEST COMPLETE")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
