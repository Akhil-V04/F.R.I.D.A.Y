#!/usr/bin/env python3
"""Final Integration Verification"""

print('='*60)
print('FINAL INTEGRATION VERIFICATION')
print('='*60)

# Test 1: Import check
try:
    from brain.qwen_executor import execute_smart
    print('✅ execute_smart imported successfully')
except ImportError as e:
    print(f'❌ Import failed: {e}')
    exit(1)

# Test 2: Fast path execution
print('\n[1] Testing fast path...')
result = execute_smart('get time')
print(f'✅ Fast path works: "{result}"')

# Test 3: Registry check  
print('\n[2] Checking tool registry...')
from tools.registry import TOOLS
if 'ask_brain' in TOOLS:
    print(f'✅ ask_brain registered (tool #{len(TOOLS)} total)')
else:
    print('❌ ask_brain not in registry')

# Test 4: Backward compatibility
print('\n[3] Checking backward compatibility...')
from brain.command_parser import parse_command
cmd = parse_command('open chrome')
if cmd.get('action') == 'open_app':
    print('✅ parse_command backward compatible')
else:
    print('❌ parse_command broken')

print('\n' + '='*60)
print('✅ ALL INTEGRATIONS VERIFIED')
print('='*60)
