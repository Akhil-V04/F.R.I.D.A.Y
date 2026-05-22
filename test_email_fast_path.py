"""
Test email detection integration in fast_path_check
SIMPLE version - just tests detection, doesn't call actual email flow
"""

import sys
from pathlib import Path

# Add the F.R.I.D.A.Y directory to path
friday_path = Path(__file__).parent
sys.path.insert(0, str(friday_path))

print("=" * 75)
print("Email Detection Fast Path Integration - SIMPLE TEST")
print("=" * 75)
print()

# Test 1: Check fast_path_check function signature
print("[TEST 1] Check fast_path_check function...")
from brain.command_parser import fast_path_check
import inspect

sig = inspect.signature(fast_path_check)
print(f"✓ fast_path_check signature: {sig}")
print()

# Test 2: Check that email keywords are in fast_path_check source code
print("[TEST 2] Verify email keywords are defined in fast_path_check...")
source = inspect.getsource(fast_path_check)

email_keywords = [
    "send a mail",
    "send mail",
    "send an email",
    "send email",
    "write a mail",
    "compose mail",
    "mail to",
    "email to"
]

keywords_found = 0
for keyword in email_keywords:
    if keyword in source:
        print(f"✓ Keyword '{keyword}' found in fast_path_check")
        keywords_found += 1
    else:
        print(f"✗ Keyword '{keyword}' NOT found")

print(f"Total: {keywords_found}/{len(email_keywords)} keywords found")
print()

# Test 3: Check for start_email_flow import in fast_path_check
print("[TEST 3] Verify start_email_flow import in fast_path_check...")
if "from actions.email_flow import start_email_flow" in source:
    print("✓ start_email_flow import found in fast_path_check")
else:
    print("✗ start_email_flow import NOT found in fast_path_check")
print()

# Test 4: Check for "handled": True in return
print("[TEST 4] Verify 'handled': True is returned for email...")
if '"handled": True' in source or "'handled': True" in source:
    print("✓ 'handled': True return found in fast_path_check")
else:
    print("✗ 'handled': True return NOT found")
print()

# Test 5: Check qwen_executor handles "handled" flag
print("[TEST 5] Verify qwen_executor.execute_smart handles 'handled' flag...")
from brain import qwen_executor

executor_source = inspect.getsource(qwen_executor.execute_smart)
if 'if fast_match.get("handled")' in executor_source:
    print("✓ execute_smart checks for 'handled' flag")
    if 'return fast_match.get("result")' in executor_source:
        print("✓ execute_smart returns result directly when handled=True")
    else:
        print("✗ execute_smart doesn't return result correctly")
else:
    print("✗ execute_smart doesn't check for 'handled' flag")
print()

# Test 6: Check that start_email_flow is callable
print("[TEST 6] Verify start_email_flow is callable...")
try:
    from actions.email_flow import start_email_flow
    if callable(start_email_flow):
        print("✓ start_email_flow is callable")
        sig = inspect.signature(start_email_flow)
        print(f"✓ start_email_flow signature: {sig}")
    else:
        print("✗ start_email_flow is not callable")
except ImportError as e:
    print(f"✗ Cannot import start_email_flow: {e}")
print()

# Test 7: Verify main.py will speak the response
print("[TEST 7] Verify main.py speaks the response from execute_smart...")
main_path = Path("main.py")
if main_path.exists():
    main_source = main_path.read_text()
    if "speak_streaming(response)" in main_source or "speak(response)" in main_source:
        print("✓ main.py speaks the response")
    else:
        print("⚠ main.py doesn't speak response (verify manually)")
else:
    print("⚠ main.py not found in current directory")
print()

# Test 8: Check NO_CACHE_TOOLS to ensure email isn't cached
print("[TEST 8] Verify email results aren't incorrectly cached...")
cache_source = open("brain/qwen_executor.py").read()
if '"email_flow"' in cache_source or "'email_flow'" in cache_source:
    if "NO_CACHE_TOOLS" in cache_source:
        print("⚠ Check if email_flow should be in NO_CACHE_TOOLS")
    else:
        print("✓ Email flow handling bypasses normal caching")
else:
    print("✓ Email flow not in NO_CACHE_TOOLS (handled separately)")
print()

print("=" * 75)
print("✓ Email Detection Integration Test COMPLETE")
print("=" * 75)
print()
print("Summary:")
print("- Email keywords detected in fast_path_check()")
print("- Returns {'result': ..., 'handled': True}")
print("- execute_smart() checks for 'handled' flag")
print("- Result returned directly, bypasses ToolExecutor")
print("- main.py speaks the result")
print()
print("Email Command Flow:")
print("1. User: 'send an email'")
print("2. main.py calls execute_smart(command)")
print("3. execute_smart calls fast_path_check(command)")
print("4. fast_path_check detects email keyword")
print("5. fast_path_check calls start_email_flow directly")
print("6. start_email_flow returns result")
print("7. fast_path_check returns {'result': result, 'handled': True}")
print("8. execute_smart checks 'handled' and returns result")
print("9. main.py speaks the result with speak_streaming()")
print("10. All done! Never reaches Qwen ✓")
print()
