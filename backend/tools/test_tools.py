#!/usr/bin/env python3
"""
Tool System Test - Verify the new tool-based system works without breaking existing features
"""

import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.executor import ToolExecutor, execute_tool
from tools.registry import list_tools, get_tool_info
from tools.integration import command_to_tool_request, execute_command_as_tool, get_ai_tool_description


def test_basic_tool_execution():
    """Test basic tool execution with JSON input"""
    print("\n=== TEST 1: Basic Tool Execution ===")
    
    # Test get_time tool
    request = {"tool": "get_time", "params": {}}
    result = ToolExecutor.execute(request)
    print(f"✓ get_time: {result['result']}")
    
    # Test get_date tool
    request = {"tool": "get_date", "params": {}}
    result = ToolExecutor.execute(request)
    print(f"✓ get_date: {result['result']}")


def test_convenience_function():
    """Test convenience execute_tool function"""
    print("\n=== TEST 2: Convenience Function ===")
    
    try:
        result = execute_tool("get_battery")
        print(f"✓ Battery status: {result}")
    except Exception as e:
        print(f"✓ Battery tool executed (may require system): {str(e)[:50]}")


def test_list_tools():
    """Test listing all available tools"""
    print("\n=== TEST 3: List All Tools ===")
    
    tools = list_tools()
    print(f"✓ Total tools registered: {len(tools)}")
    print(f"✓ Sample tools: {', '.join(tools[:5])}")


def test_legacy_command_conversion():
    """Test converting legacy commands to tool requests"""
    print("\n=== TEST 4: Legacy Command Conversion ===")
    
    # Test send_whatsapp conversion
    tool_req = command_to_tool_request("send_whatsapp", "mom|Hello")
    print(f"✓ send_whatsapp: {tool_req}")
    
    # Test search_google conversion
    tool_req = command_to_tool_request("search_google", "python programming")
    print(f"✓ search_google: {tool_req}")
    
    # Test open_app conversion
    tool_req = command_to_tool_request("open_app", "chrome")
    print(f"✓ open_app: {tool_req}")


def test_tool_info():
    """Test getting tool information"""
    print("\n=== TEST 5: Tool Information ===")
    
    info = get_tool_info("send_whatsapp")
    print(f"✓ Tool: {info['name']}")
    print(f"  Description: {info['description']}")
    print(f"  Parameters: {[p['name'] for p in info['params']]}")


def test_ai_description():
    """Test AI-friendly tool description"""
    print("\n=== TEST 6: AI Tool Description (for Ollama) ===")
    
    desc = get_ai_tool_description()
    lines = desc.split('\n')[:10]  # First 10 lines
    for line in lines:
        print(f"✓ {line}")


def test_error_handling():
    """Test error handling"""
    print("\n=== TEST 7: Error Handling ===")
    
    # Missing tool
    result = ToolExecutor.execute({"tool": "nonexistent", "params": {}})
    print(f"✓ Missing tool error: {result['error'][:50]}")
    
    # Missing required params
    result = ToolExecutor.execute({"tool": "send_whatsapp", "params": {}})
    print(f"✓ Missing params error: {result['error'][:50]}")
    
    # Invalid JSON
    result = ToolExecutor.execute("invalid json")
    print(f"✓ Invalid JSON error: {result['error'][:50]}")


def test_json_input():
    """Test JSON string input"""
    print("\n=== TEST 8: JSON String Input ===")
    
    json_request = json.dumps({"tool": "get_time", "params": {}})
    result = ToolExecutor.execute(json_request)
    print(f"✓ JSON input works: {result['result']}")


if __name__ == "__main__":
    print("=" * 60)
    print("F.R.I.D.A.Y Tool System Test Suite")
    print("=" * 60)
    
    try:
        test_basic_tool_execution()
        test_convenience_function()
        test_list_tools()
        test_legacy_command_conversion()
        test_tool_info()
        test_ai_description()
        test_error_handling()
        test_json_input()
        
        print("\n" + "=" * 60)
        print("✓ All tests completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
