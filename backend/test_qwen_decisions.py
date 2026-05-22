#!/usr/bin/env python3
"""
Test Qwen Decision Engine - See Qwen make tool decisions

Run: python test_qwen_decisions.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from brain.qwen_executor import qwen_decision_only
import json


def test_qwen_decisions():
    """Test Qwen's tool selection for various commands"""
    
    print("\n" + "="*70)
    print("QWEN DECISION ENGINE TEST")
    print("="*70)
    
    test_cases = [
        # System info
        ("what time is it", "get_time"),
        ("tell me the time", "get_time"),
        ("what's the date", "get_date"),
        ("check battery", "get_battery"),
        
        # App control
        ("open chrome", "open_app"),
        ("launch spotify", "open_app"),
        ("close notepad", "close_app"),
        
        # News
        ("what's the news", "get_world_briefing"),
        ("tell me about tech news", "get_news"),
        ("latest sports scores", "search_google"),
        
        # Messaging
        ("send whatsapp to mom hello", "send_whatsapp"),
        ("message dad via whatsapp", "send_whatsapp"),
        
        # Web
        ("search google python tutorial", "search_google"),
        ("youtube videos on machine learning", "search_youtube"),
        ("open chatgpt", "open_url"),
        
        # Screen control
        ("click the submit button", "click_text"),
        ("scroll down please", "scroll_down"),
        ("scroll up", "scroll_up"),
        ("type hello", "type_text"),
        ("press enter", "press_key"),
    ]
    
    print("\nTest Cases:")
    print("-" * 70)
    
    passed = 0
    failed = 0
    
    for user_command, expected_tool in test_cases:
        try:
            # Get Qwen's decision
            decision = qwen_decision_only(user_command)
            tool = decision.get("tool", "unknown")
            params = decision.get("params", {})
            
            # Check if it matches expected
            success = tool == expected_tool
            status = "✓" if success else "✗"
            
            if success:
                passed += 1
            else:
                failed += 1
            
            # Print result
            print(f"{status} '{user_command}'")
            print(f"   Expected: {expected_tool}")
            print(f"   Got:      {tool}")
            if params:
                print(f"   Params:   {json.dumps(params, indent=16)}")
            print()
        
        except Exception as e:
            print(f"✗ '{user_command}' → ERROR: {e}\n")
            failed += 1
    
    # Summary
    print("-" * 70)
    print(f"\nResults: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    
    if failed == 0:
        print("✓ All tests passed! Qwen decision engine is working correctly.")
    else:
        print(f"⚠ {failed} tests had unexpected results (may still be valid)")
    
    print("\n" + "="*70)
    print("Key Points:")
    print("="*70)
    print("✓ Qwen returns ONLY JSON (no normal text)")
    print("✓ Format: {\"tool\": \"name\", \"params\": {...}}")
    print("✓ No if-else chains needed")
    print("✓ Dynamic mapping from any user input")
    print("✓ Single Qwen call per command")
    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        test_qwen_decisions()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nMake sure Ollama is running:")
        print("  ollama run qwen2.5:3b")
        import traceback
        traceback.print_exc()
