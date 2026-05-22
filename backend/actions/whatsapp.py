import pyautogui
import pytesseract
import cv2
import numpy as np
from PIL import Image
import time
import pyperclip
import subprocess
import os
import webbrowser
import json
from pathlib import Path
from datetime import datetime


# Contact name aliases for easier voice commands
CONTACT_ALIASES = {
    "myself": "+91 93925 24228 (You)",
    "my own number": "+91 93925 24228 (You)",
    "my number": "+91 93925 24228 (You)",
    "me": "+91 93925 24228 (You)",
    "personal": "+91 93925 24228 (You)",
    "minegang": "Minegang",
    "mine gang": "Minegang",
}


# Contact memory file for caching recently used contacts
CONTACT_MEMORY_FILE = str(Path(__file__).parent.parent / "memory" / "whatsapp_contacts.json")


# Tesseract OCR path
TESSERACT_PATH = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


# ============================================================================
# CONTACT MEMORY SYSTEM - Cache frequently used contacts
# ============================================================================


def load_contact_memory():
    """
    Load cached contact mappings from memory file.
    
    Returns:
        dict: Contact memory {normalized_name: actual_name}
    """
    try:
        if os.path.exists(CONTACT_MEMORY_FILE):
            with open(CONTACT_MEMORY_FILE, 'r') as f:
                data = json.load(f)
                return data.get('contacts', {})
    except Exception as e:
        print(f"[DEBUG] Could not load contact memory: {e}")
    
    return {}


def save_contact_memory(contacts):
    """
    Save contact mappings to memory file.
    
    Args:
        contacts (dict): Contact memory to save
    """
    try:
        os.makedirs(os.path.dirname(CONTACT_MEMORY_FILE), exist_ok=True)
        data = {
            'contacts': contacts,
            'last_updated': datetime.now().isoformat()
        }
        with open(CONTACT_MEMORY_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"[DEBUG] Could not save contact memory: {e}")


def add_to_contact_memory(contact_name):
    """
    Add or update contact in memory cache.
    
    Args:
        contact_name (str): Contact name to cache
    """
    contacts = load_contact_memory()
    normalized = contact_name.lower().strip()
    contacts[normalized] = contact_name
    save_contact_memory(contacts)
    print(f"[DEBUG] Cached contact: {contact_name}")


def resolve_contact_from_memory(contact_query):
    """
    Try to resolve contact name from memory cache.
    Useful for recognizing frequently used contacts even with slight input variations.
    
    Args:
        contact_query (str): Raw contact name/query
    
    Returns:
        str: Resolved contact name, or original if not found
    """
    contacts = load_contact_memory()
    query_lower = contact_query.lower().strip()
    
    # Direct match
    if query_lower in contacts:
        resolved = contacts[query_lower]
        print(f"[DEBUG] Resolved '{contact_query}' to '{resolved}' from memory")
        return resolved
    
    # Fuzzy match - check if query is contained in any cached contact
    for cached_lower, cached_actual in contacts.items():
        if query_lower in cached_lower or cached_lower in query_lower:
            print(f"[DEBUG] Fuzzy matched '{contact_query}' to '{cached_actual}'")
            return cached_actual
    
    return contact_query


# ============================================================================
# IMPROVED UI DETECTION - Reduce coordinate dependency
# ============================================================================


def find_message_input_box():
    """
    Dynamically find the message input box using OCR.
    Falls back to hardcoded coordinates if OCR fails.
    
    Returns:
        tuple: (x, y) coordinates of message input box
    """
    try:
        screenshot = pyautogui.screenshot()
        img_array = np.array(screenshot)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
        
        # Look for message input placeholder text
        for i in range(len(data['text'])):
            word = data['text'][i].lower()
            if 'type a message' in word or 'message' in word:
                # Found message box, return its center
                x = data['left'][i] + data['width'][i] // 2
                y = data['top'][i] + data['height'][i] // 2
                print(f"[DEBUG] Found message box via OCR at ({x}, {y})")
                return (x, y)
        
        # If OCR search fails, look for the input field by color
        # WhatsApp input box is typically lighter/white area at bottom
        # Falling back to hardcoded coordinates
        print("[DEBUG] OCR message box detection failed, using fallback coordinates")
        return (900, 732)
    
    except Exception as e:
        print(f"[DEBUG] Could not detect message box dynamically: {e}")
        # Fallback to hardcoded coordinates
        return (900, 732)


def find_search_box():
    """
    Dynamically find the search/compose box using OCR.
    
    Returns:
        tuple: (x, y) coordinates of search box, or None if not found
    """
    try:
        screenshot = pyautogui.screenshot()
        img_array = np.array(screenshot)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
        
        # Look for search box indicators
        for i in range(len(data['text'])):
            word = data['text'][i].lower()
            if 'search' in word or 'new chat' in word:
                x = data['left'][i] + data['width'][i] // 2
                y = data['top'][i] + data['height'][i] // 2
                print(f"[DEBUG] Found search box via OCR at ({x}, {y})")
                return (x, y)
        
        return None
    except Exception as e:
        print(f"[DEBUG] Could not detect search box: {e}")
        return None


def find_text_on_screen(search_text, confidence=50):
    """
    Find text on screen using OCR.
    
    Args:
        search_text (str): Text to search for
        confidence (int): Minimum confidence threshold (0-100)
    
    Returns:
        tuple: (center_x, center_y) if found, None otherwise
    """
    try:
        # Take full screenshot
        screenshot = pyautogui.screenshot()
        
        # Convert to numpy array
        img_array = np.array(screenshot)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Apply threshold
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        
        # Use OCR to extract text data
        data = pytesseract.image_to_data(thresh, output_type=pytesseract.Output.DICT)
        
        # Loop through detected words
        for i in range(len(data['text'])):
            word = data['text'][i].lower()
            conf = int(data['conf'][i])
            
            if search_text.lower() in word and conf > confidence:
                # Calculate center of detected text
                x = data['left'][i] + data['width'][i] // 2
                y = data['top'][i] + data['height'][i] // 2
                return (x, y)
        
        return None
    
    except Exception as e:
        print(f"Error finding text on screen: {str(e)}")
        return None


def click_on_text(search_text, confidence=50):
    """
    Find text on screen and click on it.
    
    Args:
        search_text (str): Text to search for
        confidence (int): Minimum confidence threshold (0-100)
    
    Returns:
        bool: True if found and clicked, False otherwise
    """
    try:
        coords = find_text_on_screen(search_text, confidence)
        
        if coords:
            pyautogui.click(coords[0], coords[1])
            time.sleep(0.5)
            return True
        
        return False
    
    except Exception as e:
        print(f"Error clicking on text: {str(e)}")
        return False


def is_whatsapp_loaded():
    """
    Check if WhatsApp is fully loaded using OCR.
    Detects the search box text "Search or start a new chat"
    
    Returns:
        bool: True if WhatsApp UI is loaded
    """
    try:
        screenshot = pyautogui.screenshot()
        img_array = np.array(screenshot)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
        
        # Look for WhatsApp UI indicators
        for i in range(len(data['text'])):
            word = data['text'][i].lower()
            if "search" in word and ("chat" in word or "start" in word):
                print(f"[DEBUG] WhatsApp loaded! Detected: '{word}'")
                return True
            elif word == "chats":
                print(f"[DEBUG] WhatsApp loaded! Detected: 'Chats' heading")
                return True
        
        return False
    except Exception as e:
        print(f"Error checking WhatsApp load status: {str(e)}")
        return False


def wait_for_whatsapp_load(max_wait=10):
    """
    Wait for WhatsApp to load by monitoring screen for UI elements.
    
    Args:
        max_wait (int): Maximum seconds to wait
    
    Returns:
        bool: True if WhatsApp loaded, False if timeout
    """
    print(f"[DEBUG] Waiting for WhatsApp to load (max {max_wait} seconds)...")
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        if is_whatsapp_loaded():
            elapsed = time.time() - start_time
            print(f"[DEBUG] WhatsApp loaded in {elapsed:.1f} seconds")
            return True
        time.sleep(0.5)  # Check every 500ms
    
    print(f"[DEBUG] WhatsApp did not load after {max_wait} seconds")
    return False


def is_chat_message_box_ready():
    """
    Check if the chat message input box is visible using OCR.
    Detects "Type a message" placeholder text
    
    Returns:
        bool: True if message box is ready
    """
    try:
        screenshot = pyautogui.screenshot()
        img_array = np.array(screenshot)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
        
        for i in range(len(data['text'])):
            word = data['text'][i].lower()
            if "message" in word or "type" in word:
                print(f"[DEBUG] Chat message box detected: '{word}'")
                return True
        
        return False
    except Exception as e:
        print(f"Error checking message box: {str(e)}")
        return False


def wait_for_chat_load(max_wait=8):
    """
    Wait for chat window to fully load.
    
    Args:
        max_wait (int): Maximum seconds to wait
    
    Returns:
        bool: True if chat loaded, False if timeout
    """
    print(f"[DEBUG] Waiting for chat window to load (max {max_wait} seconds)...")
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        if is_chat_message_box_ready():
            elapsed = time.time() - start_time
            print(f"[DEBUG] Chat loaded in {elapsed:.1f} seconds")
            return True
        time.sleep(0.5)
    
    print(f"[DEBUG] Chat did not load after {max_wait} seconds")
    return False


def open_whatsapp():
    """
    Open WhatsApp application.
    Tries multiple paths for desktop app, falls back to web version.
    
    Returns:
        bool: True if successful
    """
    try:
        # Try multiple WhatsApp paths
        paths = [
            "C:\\Program Files\\WindowsApps\\5319275A.WhatsAppDesktop_2.2613.101.0_x64__cv1g1gvanyjgm\\WhatsApp.Root.exe",
            "C:\\Users\\akhil\\AppData\\Local\\Microsoft\\WindowsApps\\WhatsApp.exe",
            "C:\\Program Files\\WindowsApps\\WhatsApp.exe",
        ]
        
        for path in paths:
            if os.path.exists(path):
                subprocess.Popen([path])
                time.sleep(5)
                return True
        
        # Fallback: Open web WhatsApp
        webbrowser.open("https://web.whatsapp.com")
        time.sleep(5)
        return True
    
    except Exception as e:
        print(f"Error opening WhatsApp: {str(e)}")
        return False


def send_whatsapp_message(contact_name, message):
    """
    Send a WhatsApp message to a contact using screen automation for desktop app.
    
    Enhanced with:
    - Contact memory resolution
    - Multiple fallback search strategies
    - Dynamic UI element detection
    - Better error recovery
    
    Args:
        contact_name (str): Name of the contact
        message (str): Message to send
    
    Returns:
        tuple: (success: bool, response: str)
    """
    try:
        # Step 0: Map contact aliases to actual contact names
        contact_lower = contact_name.lower().strip()
        if contact_lower in CONTACT_ALIASES:
            contact_name = CONTACT_ALIASES[contact_lower]
            print(f"[DEBUG] Mapped '{contact_lower}' to '{contact_name}'")
        
        # Step 0.5: Resolve contact from memory cache
        resolved_contact = resolve_contact_from_memory(contact_name)
        contact_name = resolved_contact
        print(f"[DEBUG] Using contact: {contact_name}")
        
        # Step 1: Open WhatsApp (if not already open)
        open_whatsapp()
        
        # Step 2: Wait for WhatsApp to load by monitoring screen (adaptive wait)
        if not wait_for_whatsapp_load(max_wait=10):
            return False, "WhatsApp took too long to load boss."
        
        # Step 3: Click on WhatsApp window to ensure focus
        print("[DEBUG] Clicking on WhatsApp to ensure focus...")
        pyautogui.click(900, 300)  # Click on the right side to avoid opening chats
        time.sleep(0.3)
        
        # Step 4: Try search-based approach first (most reliable)
        success = try_search_contact(contact_name)
        
        # Step 5: If search failed, try alternative approaches
        if not success:
            print("[DEBUG] Search approach failed, trying fallback strategies...")
            success = try_scroll_contact(contact_name)
        
        if not success:
            print("[DEBUG] Fallback approaches failed, contact may not exist")
            return False, f"Could not find contact '{contact_name}' boss. Check the contact name."
        
        # Step 6: Wait for chat window to load by monitoring screen (adaptive wait)
        if not wait_for_chat_load(max_wait=8):
            print("[DEBUG] Warning: Chat may not have fully loaded, proceeding anyway...")
        
        # Step 7: Find message input box dynamically, then click it
        msg_input_x, msg_input_y = find_message_input_box()
        print(f"[DEBUG] Clicking message input at ({msg_input_x}, {msg_input_y})")
        pyautogui.click(msg_input_x, msg_input_y)
        time.sleep(1)
        
        # Step 8: Try to type the message using clipboard
        print(f"[DEBUG] Typing message: {message}")
        pyperclip.copy(message)
        time.sleep(0.2)
        pyautogui.hotkey('ctrl', 'v')
        print(f"[DEBUG] Message pasted")
        time.sleep(0.5)
        
        # Step 9: Press Enter to send
        print("[DEBUG] Sending message...")
        pyautogui.press('enter')
        time.sleep(0.5)
        
        # Step 10: Cache this contact for future use
        add_to_contact_memory(contact_name)
        
        print("[DEBUG] Message sent successfully!")
        return True, f"Message sent to {contact_name} boss."
    
    except Exception as e:
        print(f"[ERROR] WhatsApp error: {str(e)}")
        return False, f"Failed boss: {str(e)}"


def try_search_contact(contact_name, max_retries=2):
    """
    Try to find and open contact using Ctrl+F search approach.
    Includes retry logic for reliability.
    
    Args:
        contact_name (str): Contact name to search for
        max_retries (int): Number of retry attempts
    
    Returns:
        bool: True if successful, False otherwise
    """
    for attempt in range(max_retries):
        try:
            print(f"[DEBUG] Search attempt {attempt + 1}/{max_retries} for '{contact_name}'")
            
            # Press Ctrl+F to focus search box
            print("[DEBUG] Pressing Ctrl+F to open search...")
            pyautogui.hotkey('ctrl', 'f')
            time.sleep(0.8)  # Give search box time to activate
            
            # Select all text in search box and clear it
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.3)
            
            # Type contact name using clipboard (more reliable than typing)
            print(f"[DEBUG] Pasting contact name: {contact_name}")
            pyperclip.copy(contact_name)
            time.sleep(0.2)
            pyautogui.hotkey('ctrl', 'v')
            print(f"[DEBUG] Pasted: {contact_name}")
            time.sleep(2.5)  # Wait for search results to appear
            
            # Press Down arrow to select from search results
            print("[DEBUG] Selecting first search result...")
            pyautogui.press('down')
            time.sleep(0.5)
            
            # Press Enter to open the selected chat
            print("[DEBUG] Opening chat...")
            pyautogui.press('enter')
            time.sleep(1.5)
            
            # Verify chat opened by checking if message box is ready
            if is_chat_message_box_ready():
                print("[DEBUG] Chat opened successfully via search")
                return True
            else:
                print(f"[DEBUG] Chat may not have opened properly, attempt {attempt + 1} failed")
                time.sleep(1)
                continue
        
        except Exception as e:
            print(f"[DEBUG] Search attempt failed: {e}")
            time.sleep(1)
            continue
    
    return False


def try_scroll_contact(contact_name):
    """
    Fallback approach: Try to find contact by scrolling through contact list.
    More robust than search but slower.
    
    Args:
        contact_name (str): Contact name to find
    
    Returns:
        bool: True if contact found and opened
    """
    try:
        print(f"[DEBUG] Attempting scroll-based search for '{contact_name}'")
        
        # Open the chat list (click on left panel)
        pyautogui.click(100, 300)
        time.sleep(0.5)
        
        # Scroll up to get to top of contact list
        for _ in range(10):
            pyautogui.scroll(5, 100, 300)  # Scroll up
            time.sleep(0.2)
        
        # Now scroll down and look for contact
        for scroll_attempt in range(20):  # Scroll through ~20 contacts
            # Try to find contact on current screen using OCR
            if click_on_text(contact_name, confidence=40):
                time.sleep(1)
                print(f"[DEBUG] Found contact via scroll at attempt {scroll_attempt + 1}")
                return True
            
            # Scroll down to next batch of contacts
            pyautogui.scroll(-3, 100, 300)
            time.sleep(0.3)
        
        print("[DEBUG] Contact not found by scrolling")
        return False
    
    except Exception as e:
        print(f"[DEBUG] Scroll-based search failed: {e}")
        return False


def send_whatsapp_flow(initial_command=""):
    """
    Interactive flow for sending WhatsApp message using voice.
    Smart contact detection from initial command.
    
    Args:
        initial_command (str): Initial command that triggered this flow (e.g., 'to self', 'minegang')
    
    Returns:
        str: Result message
    """
    try:
        from voice.tts import speak
        from voice.stt import listen
        
        # Step 1: Determine contact
        contact = None
        
        # Debug: Show what we received
        print(f"[DEBUG] send_whatsapp_flow initial_command: '{initial_command}'")
        
        # Parse contact from initial command if available
        if initial_command:
            initial_lower = initial_command.lower().strip()
            print(f"[DEBUG] Checking contact from: '{initial_lower}'")
            
            # First, check for direct contact aliases using word boundaries
            import re
            for alias in CONTACT_ALIASES.keys():
                # Use word boundaries to match whole words only
                pattern = r'\b' + re.escape(alias) + r'\b'
                if re.search(pattern, initial_lower):
                    contact = alias
                    print(f"[DEBUG] Detected alias: {alias}")
                    break
            
            # If no alias found, try to extract contact name from command
            # Look for patterns like "to [name]" or "message [name]"
            if not contact:
                # Pattern: to [word]
                match = re.search(r'to\s+(\w+)', initial_lower)
                if match:
                    contact = match.group(1)
                    print(f"[DEBUG] Extracted contact from command: {contact}")
        
        # If contact found in command, use it
        if contact:
            print(f"[DEBUG] Contact detected from command: {contact}")
            speak(f"Messaging {contact} boss.")
        else:
            # Only ask if contact not detected from command
            print("[DEBUG] No contact detected, asking user")
            speak("Who should I message boss?")
            contact = listen()
        
        if not contact:
            return "Couldn't hear the contact name boss."
        
        # Step 2: Ask for message
        speak(f"What should I say boss?")
        message = listen()
        
        if not message:
            return "Couldn't hear the message boss."
        
        # Step 3: Send message
        speak(f"Sending message boss.")
        success, msg = send_whatsapp_message(contact, message)
        
        return msg
    
    except Exception as e:
        print(f"[ERROR] WhatsApp flow error: {str(e)}")
        return f"WhatsApp flow error: {str(e)}"


def send_message_to_contact(contact_name, message):
    """
    Wrapper function for sending WhatsApp message to a contact.
    
    Args:
        contact_name (str): Name of the contact
        message (str): Message to send
    
    Returns:
        tuple: (success: bool, response: str)
    """
    return send_whatsapp_message(contact_name, message)
