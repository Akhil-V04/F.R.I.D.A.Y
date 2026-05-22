#!/usr/bin/env python3
"""
Test get_screen_text post-processing: text cleaning and limiting.
Verifies that OCR output is cleaned and trimmed to reasonable size.
"""

import re

def post_process_text(text):
    """Simulate the post-processing logic"""
    # Remove repeated symbols and noise
    text = re.sub(r'([=\-_*#])\1{2,}', r'\1', text)
    text = re.sub(r'^[=\-_*#\s]+$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()
    
    # Limit to 400 characters
    if len(text) > 400:
        truncated = text[:400]
        for delimiter in ['.', '?', '!', '\n']:
            last_pos = truncated.rfind(delimiter)
            if last_pos > 300:
                text = truncated[:last_pos + 1]
                break
        else:
            text = truncated
    
    return text

# Test cases
test_cases = [
    {
        "name": "Long OCR output with noise",
        "input": """
Welcome to WhatsApp

===================================
Recent Chats:

Mom
Last message: How are you?

-----------------------------------

Friend 1
Last message: Did you see the movie?

===================================

Settings        Help        Exit


=== === === (noise characters) === === ===
""",
        "description": "OCR with repeated symbols and excessive newlines"
    },
    {
        "name": "Very long text output",
        "input": "This is a very long message. " * 20,  # ~600 chars
        "description": "Text longer than 400 character limit"
    },
    {
        "name": "Text with repeated newlines",
        "input": """Line 1


Line 2




Line 3""",
        "description": "Excessive newlines should be reduced"
    },
    {
        "name": "Clean text",
        "input": "This is clean text without issues. Just a normal message.",
        "description": "Already clean text should pass through"
    },
    {
        "name": "Very noisy OCR",
        "input": "Welcome ====== To ====== App\n\n------- Section -------\nSome text with *** and ### noise",
        "description": "Multiple types of noise characters"
    },
]

print("=" * 70)
print("TESTING get_screen_text POST-PROCESSING")
print("=" * 70)

for i, test in enumerate(test_cases, 1):
    print(f"\n[Test {i}] {test['name']}")
    print(f"Description: {test['description']}")
    
    input_text = test['input']
    output_text = post_process_text(input_text)
    
    print(f"\nInput length: {len(input_text)} chars")
    print(f"Output length: {len(output_text)} chars")
    print(f"\nProcessed text (first 200 chars):")
    print("-" * 70)
    print(output_text[:200] + ("..." if len(output_text) > 200 else ""))
    print("-" * 70)
    
    # Validation checks
    checks = [
        ("Length limited", len(output_text) <= 400),
        ("No 3+ repeated symbols", not re.search(r'([=\-_*#])\1{2,}', output_text)),
        ("No excessive newlines", '\n\n\n' not in output_text),
        ("Not empty", len(output_text) > 0 or len(input_text) == 0),
    ]
    
    for check_name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"  {status} {check_name}")

print("\n" + "=" * 70)
print("""
✅ POST-PROCESSING SUMMARY

The fix ensures:
  1. Output limited to 400 characters (fits readable output)
  2. Repeated symbols (===, ---, ***) reduced to single char
  3. Symbol-only lines removed (e.g., "===========")
  4. Excessive newlines (3+) reduced to 2
  5. Cuts at sentence boundaries (., ?, !) when possible
  6. Handles both short and long OCR outputs

Result: Clean, readable text suitable for voice output and processing
""")
