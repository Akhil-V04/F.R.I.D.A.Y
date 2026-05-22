#!/usr/bin/env python3
"""
Example: Using F.R.I.D.A.Y Tool System

Shows 3 approaches:
1. Legacy (unchanged)
2. Tool-based JSON
3. Ollama integration
"""

import json
from tools.executor import ToolExecutor, execute_tool
from tools.integration import (
    get_ai_tool_description,
    get_ai_tool_json_schema,
    command_to_tool_request,
    execute_command_as_tool
)
from tools.registry import list_tools


def example_1_legacy():
    """Example 1: Legacy approach (no changes needed)"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Legacy Approach (All Existing Code Works)")
    print("="*60)
    
    # This is how the code worked before - still works!
    from actions.system import get_time, get_date
    
    time = get_time()
    date = get_date()
    
    print(f"Time: {time}")
    print(f"Date: {date}")
    print("✓ All existing code continues to work")


def example_2_json_execute():
    """Example 2: JSON-based tool execution"""
    print("\n" + "="*60)
    print("EXAMPLE 2: JSON-Based Execution (New Way)")
    print("="*60)
    
    # Example: Get system info
    print("\nGetting time with JSON request:")
    request = {"tool": "get_time", "params": {}}
    result = ToolExecutor.execute(request)
    print(f"Request: {request}")
    print(f"Result: {result}")
    
    # Example: Send WhatsApp
    print("\n\nBuilding WhatsApp request:")
    request = {
        "tool": "send_whatsapp",
        "params": {
            "contact": "mom",
            "message": "Hi mom, checking in!"
        }
    }
    print(f"Request: {json.dumps(request, indent=2)}")
    print("(Would execute on actual WhatsApp setup)")
    
    # Example: Search news
    print("\n\nGetting news with parameters:")
    request = {
        "tool": "get_news",
        "params": {
            "category": "technology",
            "limit": 3
        }
    }
    result = ToolExecutor.execute(request)
    print(f"Request: {request}")
    print(f"Result: {result['result'][:100]}...")


def example_3_convenience():
    """Example 3: Convenience function approach"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Convenience Functions (Pythonic)")
    print("="*60)
    
    # Simple one-liners
    print("\nGetting information:")
    time = execute_tool("get_time")
    print(f"Time: {time}")
    
    battery = execute_tool("get_battery")
    print(f"Battery: {battery}")
    
    # With parameters
    print("\n\nGetting news:")
    news = execute_tool("get_news", category="world", limit=2)
    print(f"News: {news[:100]}...")


def example_4_legacy_command_conversion():
    """Example 4: Converting legacy commands to tools"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Legacy Command → Tool Conversion")
    print("="*60)
    
    # Old system: action + target
    # New system: tool + params
    
    conversions = [
        ("send_whatsapp", "mom|Hello mom"),
        ("search_google", "python tutorial"),
        ("open_app", "chrome"),
        ("get_news", "sports"),
    ]
    
    for action, target in conversions:
        tool_req = command_to_tool_request(action, target)
        print(f"\n{action} + '{target}'")
        print(f"  → {json.dumps(tool_req, indent=4)}")


def example_5_ai_tool_descriptions():
    """Example 5: Getting tool descriptions for AI"""
    print("\n" + "="*60)
    print("EXAMPLE 5: AI Tool Descriptions (for Ollama Prompts)")
    print("="*60)
    
    # For AI to understand what tools are available
    desc = get_ai_tool_description()
    
    # Show first few lines
    lines = desc.split('\n')[:8]
    print("\nTool descriptions for AI:")
    for line in lines:
        print(line)
    
    print(f"\n... and {len(list_tools())-5} more tools")
    print(f"\nTotal tools available: {len(list_tools())}")


def example_6_ollama_json_schema():
    """Example 6: JSON Schema for AI function calling"""
    print("\n" + "="*60)
    print("EXAMPLE 6: JSON Schema for Function Calling")
    print("="*60)
    
    schemas = get_ai_tool_json_schema()
    
    # Show one example schema
    print("\nExample: send_whatsapp schema")
    example = next(s for s in schemas if s['name'] == 'send_whatsapp')
    print(json.dumps(example, indent=2))
    
    print(f"\n... Total {len(schemas)} tool schemas available")


def example_7_error_handling():
    """Example 7: Error handling"""
    print("\n" + "="*60)
    print("EXAMPLE 7: Error Handling")
    print("="*60)
    
    # Missing required parameters
    print("\nAttempting invalid request:")
    result = ToolExecutor.execute({
        "tool": "send_whatsapp",
        "params": {}  # Missing contact and message
    })
    
    print(f"Success: {result['success']}")
    print(f"Error: {result['error']}")
    
    # Non-existent tool
    print("\n\nAttempting non-existent tool:")
    result = ToolExecutor.execute({
        "tool": "teleport_user",
        "params": {}
    })
    
    print(f"Success: {result['success']}")
    print(f"Error: {result['error']}")


def example_8_complete_workflow():
    """Example 8: Complete workflow - AI makes decisions"""
    print("\n" + "="*60)
    print("EXAMPLE 8: Complete AI Workflow")
    print("="*60)
    
    print("\nScenario: User says 'Get me the latest tech news'")
    print("\nSteps:")
    
    # Step 1: Prepare tool request (AI would generate this)
    print("\n1. AI generates tool request:")
    request = {
        "tool": "get_news",
        "params": {
            "category": "technology",
            "limit": 5
        }
    }
    print(f"   {json.dumps(request, indent=6)}")
    
    # Step 2: Execute tool
    print("\n2. Execute tool:")
    result = ToolExecutor.execute(request)
    print(f"   Success: {result['success']}")
    print(f"   Result: {result['result'][:80]}...")
    
    # Step 3: Return to user
    print("\n3. Present to user:")
    print(f"   '{result['result']}'")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("F.R.I.D.A.Y Tool System - Example Workflows")
    print("="*60)
    
    try:
        # Run examples
        example_1_legacy()
        example_2_json_execute()
        example_3_convenience()
        example_4_legacy_command_conversion()
        example_5_ai_tool_descriptions()
        example_6_ollama_json_schema()
        example_7_error_handling()
        example_8_complete_workflow()
        
        print("\n" + "="*60)
        print("✓ All examples completed successfully!")
        print("="*60)
        print("\nRead TOOL_SYSTEM.md for full documentation")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
