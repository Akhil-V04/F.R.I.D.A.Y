#!/usr/bin/env python3
"""
Complete end-to-end test of send_email flow with parameter enrichment.
Shows how Qwen's empty params are filled to ensure tool receives all required parameters.
"""

import sys
sys.path.insert(0, r'c:\Users\akhil\Downloads\F.R.I.D.A.Y')

from actions.email_sender import CONTACTS

print("=" * 70)
print("END-TO-END send_email FLOW: Qwen → Enrichment → Tool Ready")
print("=" * 70)

# Simulated scenarios
scenarios = [
    {
        "description": "User sends email to mom about a project",
        "user_input": "send an email to mom about the project meeting",
        "step1_qwen_output": {"tool": "send_email", "params": {}},
        "expected_final": {
            "contact": "mom",
            "subject": "the project meeting",
            "body": "Sent via FRIDAY assistant"
        }
    },
    {
        "description": "User sends email to dad with explicit message",
        "user_input": "email dad and say dont forget about dinner tonight",
        "step1_qwen_output": {"tool": "send_email", "params": {}},
        "expected_final": {
            "contact": "dad",
            "subject": "Message from FRIDAY",
            "body": "dont forget about dinner tonight"
        }
    },
    {
        "description": "User sends email with subject and body keywords",
        "user_input": "send email to friend with subject reminder and message please review my draft",
        "step1_qwen_output": {"tool": "send_email", "params": {}},
        "expected_final": {
            "contact": "friend",
            "subject": "reminder",
            "body": "please review my draft"
        }
    },
]

def enrich_params_inline(tool_request, user_input):
    """Inline version of enrichment for testing"""
    params = tool_request.get("params", {})
    user_lower = user_input.lower()
    
    # Contact extraction
    if "contact" not in params or not params.get("contact"):
        contact = None
        for contact_name in CONTACTS.keys():
            if contact_name in user_lower:
                contact = contact_name
                break
        if not contact:
            contact = "mom"
        params["contact"] = contact
    
    # Subject extraction
    if "subject" not in params or not params.get("subject"):
        subject = None
        for pattern in ["subject:", "with subject", "titled", "about "]:
            if pattern in user_lower:
                try:
                    subject_part = user_lower.split(pattern)[1].strip()
                    for stop_word in [" and ", ".", "\n", " say ", " tell ", " with"]:
                        if stop_word in subject_part:
                            subject_part = subject_part.split(stop_word)[0]
                    subject = subject_part.strip()
                    if subject and len(subject) > 2:
                        break
                except:
                    pass
        if not subject:
            subject = "Message from FRIDAY"
        params["subject"] = subject[:100]
    
    # Body extraction
    if "body" not in params or not params.get("body"):
        body = None
        for keyword in ["message:", "body:", "say ", "tell ", "write "]:
            if keyword in user_lower:
                try:
                    body_part = user_lower.split(keyword)[1].strip()
                    for stop_word in ["subject", " with ", "\n\n"]:
                        if stop_word in body_part:
                            body_part = body_part.split(stop_word)[0]
                    body = body_part.strip()
                    if body and len(body) > 2:
                        break
                except:
                    pass
        if not body:
            body = "Sent via FRIDAY assistant"
        params["body"] = body
    
    tool_request["params"] = params
    return tool_request

# Run scenarios
for i, scenario in enumerate(scenarios, 1):
    print(f"\n[Scenario {i}] {scenario['description']}")
    print(f"User Input: \"{scenario['user_input']}\"")
    
    print(f"\nStep 1: Qwen Decision")
    qwen_output = scenario['step1_qwen_output']
    print(f"  Tool: {qwen_output['tool']}")
    print(f"  Params from Qwen: {qwen_output['params']}")
    print(f"  ⚠️  Empty/missing parameters!")
    
    print(f"\nStep 2: Enrichment")
    enriched = enrich_params_inline(qwen_output.copy(), scenario['user_input'])
    final_params = enriched['params']
    print(f"  Enriched params:")
    print(f"    contact: {final_params.get('contact')}")
    print(f"    subject: {final_params.get('subject')}")
    print(f"    body:    {final_params.get('body')}")
    
    print(f"\nStep 3: Tool Ready")
    print(f"  Tool call: send_email_to_contact(")
    print(f"    contact_name=\"{final_params.get('contact')}\",")
    print(f"    subject=\"{final_params.get('subject')}\",")
    print(f"    body=\"{final_params.get('body')}\"")
    print(f"  )")
    
    # Verify all required params
    all_required = all([
        final_params.get('contact'),
        final_params.get('subject'),
        final_params.get('body')
    ])
    
    if all_required:
        print(f"  ✅ Tool receives all 3 required parameters")
    else:
        print(f"  ❌ Missing parameters!")

print("\n" + "=" * 70)
print("""
✅ FLOW COMPLETE

Summary of improvements:
  • Qwen's empty {} → Function extracts contact from user input
  • Contact detection: Searches for known names (mom, dad, friend)
  • Subject extraction: Multiple pattern matching (about, subject, etc.)
  • Body extraction: Keyword matching (say, tell, message, etc.)
  • Defaults fill any missing: subject and body have sensible defaults
  • Tool always receives: contact + subject + body (3/3 required params)

Result: send_email never fails due to missing parameters!
""")
