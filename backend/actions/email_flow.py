"""
Email Flow - Automated Gmail Sending
Handles personal and college Gmail accounts with voice automation.
"""

import time
import subprocess
import pyautogui
from voice.tts import speak
from voice.stt import listen


# ============================================================================
# CONFIGURATION (Hardcoded)
# ============================================================================

PERSONAL_EMAIL = "akhilvaddeboina25@gmail.com"
COLLEGE_EMAIL = "23p61a05m5@vbithyd.ac.in"

PERSONAL_GMAIL_URL = "https://mail.google.com/mail/u/0/#inbox"
COLLEGE_GMAIL_URL = "https://mail.google.com/mail/u/1/#inbox"

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PERSONAL_PROFILE = "--profile-directory=Default"
COLLEGE_PROFILE = "--profile-directory=Profile 1"



# ============================================================================
# MAIN EMAIL FLOW - 10 Step Fully Automated Process
# ============================================================================


def start_email_flow(voice_input: str) -> str:
    """
    Completely automated email sending flow with voice control.
    
    STEP 1: Determine which account to open
    STEP 2: Open correct Chrome profile with Gmail
    STEP 3: Navigate to Gmail inbox
    STEP 4: Click Compose
    STEP 5: Ask for recipient (or use auto-detected)
    STEP 6: Type recipient email
    STEP 7: Ask for subject
    STEP 8: Ask for body
    STEP 9: Ask about file attachments
    STEP 10: Ask to send and execute
    
    Args:
        voice_input (str): Voice command that triggered email flow
    
    Returns:
        str: Status message
    """
    try:
        # ===== STEP 1: Determine which account to open =====
        print("[STEP 1] Determining account from voice input...")
        voice_lower = voice_input.lower()
        account = "personal"  # Default
        auto_recipient = None
        
        # Check for "personal to college" or "personal AND college"
        if ("personal to college" in voice_lower or 
            ("personal" in voice_lower and "college" in voice_lower and "to" not in voice_lower)):
            account = "personal"
            auto_recipient = COLLEGE_EMAIL
            print("[OK] Personal to College detected")
        
        # Check for "college to personal"
        elif "college to personal" in voice_lower:
            account = "college"
            auto_recipient = PERSONAL_EMAIL
            print("[OK] College to Personal detected")
        
        # Check for just "college" (send from college to personal)
        elif "college" in voice_lower and "personal" not in voice_lower:
            account = "college"
            print("[OK] College account selected")
        
        # Check for just "personal" (send from personal)
        elif "personal" in voice_lower and "college" not in voice_lower:
            account = "personal"
            print("[OK] Personal account selected")
        
        # ===== STEP 2: Open correct Chrome profile with Gmail =====
        print(f"[STEP 2] Opening {account} Chrome profile...")
        speak(f"Opening {account} Gmail for you boss.")
        
        try:
            if account == "personal":
                subprocess.Popen([CHROME_PATH, PERSONAL_PROFILE, PERSONAL_GMAIL_URL])
            else:  # college
                subprocess.Popen([CHROME_PATH, COLLEGE_PROFILE, COLLEGE_GMAIL_URL])
            
            time.sleep(4)  # Wait for Chrome to open
        except Exception as e:
            return f"[FAILED - STEP 2] Could not open Chrome: {str(e)}"
        
        # ===== STEP 3: Press Ctrl+T to ensure new tab, then navigate =====
        print("[STEP 3] Navigating to Gmail...")
        try:
            pyautogui.hotkey('ctrl', 't')
            time.sleep(1)
            
            if account == "personal":
                pyautogui.hotkey('ctrl', 'l')
                pyautogui.typewrite(PERSONAL_GMAIL_URL, interval=0.05)
            else:  # college
                pyautogui.hotkey('ctrl', 'l')
                pyautogui.typewrite(COLLEGE_GMAIL_URL, interval=0.05)
            
            pyautogui.press('enter')
            time.sleep(3)
        except Exception as e:
            return f"[FAILED - STEP 3] Could not navigate to Gmail: {str(e)}"
        
        # ===== STEP 4: Click Compose using keyboard shortcut =====
        print("[STEP 4] Opening Compose...")
        speak("Opening compose boss.")
        
        try:
            pyautogui.press('c')  # Gmail compose shortcut
            time.sleep(2)
        except Exception as e:
            return f"[FAILED - STEP 4] Could not open Compose: {str(e)}"
        
        # ===== STEP 5: Ask for recipient (conversational) =====
        print("[STEP 5] Handling recipient...")
        try:
            if auto_recipient:
                recipient = auto_recipient
                print(f"[OK] Using auto-recipient: {recipient}")
                speak(f"Sending to {recipient} boss.")
            else:
                speak("Who should I send this to boss?")
                recipient = listen()
                
                if not recipient:
                    return "No recipient provided boss."
                
                # Check for special keywords
                if "myself" in recipient.lower() or "me" in recipient.lower():
                    recipient = PERSONAL_EMAIL if account == "personal" else COLLEGE_EMAIL
                elif "college" in recipient.lower():
                    recipient = COLLEGE_EMAIL
                elif "personal" in recipient.lower():
                    recipient = PERSONAL_EMAIL
                else:
                    # Assume it's an email address as-is
                    if "@" not in recipient:
                        recipient = recipient + "@gmail.com"
        except Exception as e:
            return f"[FAILED - STEP 5] Could not get recipient: {str(e)}"
        
        # ===== STEP 6: Type recipient email in To field =====
        print(f"[STEP 6] Typing recipient: {recipient}")
        try:
            pyautogui.typewrite(recipient, interval=0.05)
            pyautogui.press('tab')
            time.sleep(0.5)
        except Exception as e:
            return f"[FAILED - STEP 6] Could not enter recipient: {str(e)}"
        
        # ===== STEP 7: Ask for subject =====
        print("[STEP 7] Asking for subject...")
        try:
            speak("What's the subject boss?")
            subject = listen()
            
            if not subject:
                subject = "(No subject)"
            
            pyautogui.typewrite(subject, interval=0.05)
            pyautogui.press('tab')
            time.sleep(0.5)
        except Exception as e:
            return f"[FAILED - STEP 7] Could not enter subject: {str(e)}"
        
        # ===== STEP 8: Ask for body =====
        print("[STEP 8] Asking for body...")
        try:
            speak("What should I write in the mail boss?")
            body = listen()
            
            if not body:
                body = "(No message)"
            
            pyautogui.typewrite(body, interval=0.05)
        except Exception as e:
            return f"[FAILED - STEP 8] Could not enter body: {str(e)}"
        
        # ===== STEP 9: Ask for files =====
        print("[STEP 9] Asking about attachments...")
        try:
            speak("Should I attach any files boss?")
            file_response = listen()
            
            if file_response and ("yes" in file_response.lower() or 
                                  "attach" in file_response.lower() or 
                                  "add" in file_response.lower()):
                speak("Please attach the files manually boss, I'll wait 15 seconds")
                time.sleep(15)
        except Exception as e:
            return f"[FAILED - STEP 9] Could not handle attachments: {str(e)}"
        
        # ===== STEP 10: Ask to send =====
        print("[STEP 10] Asking for confirmation to send...")
        try:
            speak("Mail is ready boss. Should I send it?")
            confirm = listen()
            
            if confirm and ("yes" in confirm.lower() or 
                          "send" in confirm.lower() or 
                          "go" in confirm.lower()):
                pyautogui.hotkey('ctrl', 'enter')
                time.sleep(1)
                print("[SUCCESS] Email sent!")
                speak("Mail sent successfully boss")
                return "Mail sent successfully boss"
            else:
                print("[OK] Email saved as draft")
                speak("Mail saved as draft boss")
                return "Mail saved as draft boss"
        except Exception as e:
            return f"[FAILED - STEP 10] Could not send email: {str(e)}"
    
    except Exception as e:
        # Catch-all for unexpected errors
        error_msg = f"Email flow error boss: {str(e)}"
        print(f"[FAILED] {error_msg}")
        speak(error_msg)
        return error_msg


# ============================================================================
# LEGACY COMPATIBILITY (Deprecated)
# ============================================================================


def ask(question):
    """
    DEPRECATED: Use start_email_flow instead.
    Ask a question and get voice response from user.
    """
    speak(question)
    time.sleep(0.5)
    response = listen()
    if not response:
        speak("Say that again boss.")
        time.sleep(0.3)
        response = listen()
    return response.lower().strip() if response else ""


def is_cancellation(response):
    """
    DEPRECATED: Use start_email_flow instead.
    Check if the response indicates cancellation.
    """
    cancel_words = ["forget", "cancel", "stop", "never mind", "abort", "quit", "exit"]
    return any(word in response.lower() for word in cancel_words)


def run_email_flow(initial_command=""):
    """
    DEPRECATED: Use start_email_flow instead.
    Calls the new start_email_flow function for backward compatibility.
    """
    return start_email_flow(initial_command)


