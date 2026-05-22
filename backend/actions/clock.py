import pyautogui
import pytesseract
import cv2
import numpy as np
import time
import subprocess
import os
import re
import pygetwindow as gw
from datetime import datetime, timedelta


TESSERACT_PATH = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


def focus_window(window_title):
    """Focus a window by clicking on it."""
    try:
        # Try using pygetwindow
        windows = gw.getWindowsWithTitle(window_title)
        if windows:
            try:
                windows[0].activate()
                time.sleep(0.5)
                return True
            except:
                # If activate fails, try clicking on the window instead
                try:
                    x, y = windows[0].center
                    pyautogui.click(int(x), int(y))
                    time.sleep(0.5)
                    return True
                except:
                    pass
        
        # Fallback: just click in the middle of the screen (Clock app opens centered)
        print("[DEBUG] Window not found, clicking center of screen...")
        pyautogui.click(640, 360)
        time.sleep(0.5)
        return True
    
    except Exception as e:
        print(f"Error focusing window: {str(e)}")
        # Fallback: click center
        try:
            pyautogui.click(640, 360)
            time.sleep(0.5)
            return True
        except:
            return False


def open_clock():
    """
    Open Windows Clock app and make it fullscreen.
    
    Returns:
        bool: True if successful
    """
    try:
        print("[DEBUG] Opening Windows Clock app...")
        
        # Kill any existing Clock windows first
        try:
            subprocess.run(['taskkill', '/IM', 'WindowsAlarms.exe', '/F'], capture_output=True, stderr=subprocess.DEVNULL)
            time.sleep(1)
        except:
            pass
        
        # Open Clock app fresh
        print("[DEBUG] Launching Clock app with ms-clock: URI...")
        os.system("start ms-clock:")
        time.sleep(4)
        
        # Focus the Clock window
        print("[DEBUG] Focusing Clock app...")
        focus_window("Clock")
        time.sleep(1)
        
        # Make it fullscreen - use Alt+F10 to maximize
        print("[DEBUG] Making Clock app fullscreen...")
        pyautogui.hotkey('alt', 'f10')  # Maximize window
        time.sleep(2)
        
        # Also try to click maximize button as backup
        pyautogui.click(1497, 19)  # Maximize button on title bar
        time.sleep(2)
        
        # Wait for fullscreen animations to complete
        time.sleep(1)
        
        print("[DEBUG] Clock app opened and fullscreen!")
        return True
    
    except Exception as e:
        print(f"[ERROR] Error opening Clock: {str(e)}")
        return False


def click_timer_tab():
    """
    Click the Timer tab in the Clock app sidebar.
    Timer tab is the 2nd item in the left sidebar.
    """
    try:
        print("[DEBUG] Clicking Timer tab...")
        # Timer is the 2nd menu item, below Focus sessions
        # Y coordinate around 100 is the Timer option
        pyautogui.click(67, 100)
        time.sleep(1.5)
        print("[DEBUG] Timer tab clicked!")
        return True
    except Exception as e:
        print(f"[ERROR] Error clicking Timer tab: {str(e)}")
        return False


def is_clock_loaded():
    """
    Check if Clock app is loaded using OCR.
    
    Returns:
        bool: True if Clock UI is loaded
    """
    try:
        screenshot = pyautogui.screenshot()
        img_array = np.array(screenshot)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
        
        for i in range(len(data['text'])):
            word = data['text'][i].lower()
            if "alarm" in word or "timer" in word or "clock" in word:
                print(f"[DEBUG] Clock loaded! Detected: '{word}'")
                return True
        
        return False
    except Exception as e:
        print(f"Error checking Clock load status: {str(e)}")
        return False


def wait_for_clock_load(max_wait=5):
    """
    Wait for Clock app to load.
    
    Args:
        max_wait (int): Maximum seconds to wait
    
    Returns:
        bool: True if Clock loaded, False if timeout
    """
    print(f"[DEBUG] Waiting for Clock to load (max {max_wait} seconds)...")
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        if is_clock_loaded():
            elapsed = time.time() - start_time
            print(f"[DEBUG] Clock loaded in {elapsed:.1f} seconds")
            return True
        time.sleep(0.3)
    
    print(f"[DEBUG] Clock did not load after {max_wait} seconds")
    return False


def set_timer(user_input):
    """
    Set a timer using Windows Clock app with voice input.
    
    Extracts duration from voice input:
    - "5 minutes", "set a timer for 5 minutes"
    - "30 seconds", "remind me in 30 seconds"
    - "2 hours", "timer for 2 hours"
    
    Args:
        user_input (str): Voice input with timer duration
    
    Returns:
        str: Status message
    """
    try:
        # ===== STEP 1: Extract number from voice input =====
        match = re.search(r'(\d+)', user_input)
        if not match:
            return "Couldn't find a number in your request boss. Try 'set a timer for 5 minutes'."
        
        number = int(match.group(1))
        
        # ===== STEP 2: Determine time unit and convert to minutes =====
        user_lower = user_input.lower()
        duration_minutes = number
        unit_display = "minutes"
        
        if "hour" in user_lower:
            duration_minutes = number * 60
            unit_display = f"hour{'s' if number > 1 else ''}"
        elif "second" in user_lower:
            duration_minutes = max(1, number // 60)  # Convert seconds to minutes, min 1
            unit_display = f"second{'s' if number > 1 else ''}"
        elif "minute" in user_lower or "min" in user_lower:
            duration_minutes = number
            unit_display = f"minute{'s' if number > 1 else ''}"
        else:
            # Default to minutes if no unit specified
            duration_minutes = number
            unit_display = f"minute{'s' if number > 1 else ''}"
        
        print(f"[TIMER] Extracted: {number} {unit_display} = {duration_minutes} minutes")
        
        # ===== STEP 3: Open Windows Clock app =====
        print("[TIMER] Opening Windows Clock app...")
        try:
            subprocess.Popen(['explorer.exe', 'shell:AppsFolder\\Microsoft.WindowsAlarms_8wekyb3d8bbwe!App'])
            time.sleep(3)
        except Exception as e:
            return f"Could not open Windows Clock app: {str(e)}"
        
        # ===== STEP 4: Navigate to Timer tab using Tab key =====
        print("[TIMER] Navigating to Timer tab...")
        try:
            pyautogui.press('tab')
            time.sleep(0.3)
            pyautogui.press('tab')
            time.sleep(0.3)
            pyautogui.press('tab')
            time.sleep(0.3)
            pyautogui.press('enter')
            time.sleep(1)
        except Exception as e:
            print(f"[TIMER] Tab navigation error: {e}")
        
        # ===== STEP 5: Click + button to set minutes =====
        print(f"[TIMER] Clicking + button {duration_minutes} times...")
        try:
            # The + button is typically in the Clock app for timer duration
            # We'll click it duration_minutes times to set the duration
            for i in range(duration_minutes):
                # Click the + button (coordinates may vary, this is approximate)
                # The + button is usually in the center area of the timer interface
                pyautogui.press('up')  # Alternative: press up arrow key to increment timer
                time.sleep(0.2)
        except Exception as e:
            print(f"[TIMER] Error clicking + button: {e}")
        
        # ===== STEP 6: Press Enter to start timer =====
        print("[TIMER] Starting timer...")
        try:
            pyautogui.press('enter')
            time.sleep(1)
        except Exception as e:
            print(f"[TIMER] Error starting timer: {e}")
        
        # ===== STEP 7: Return confirmation =====
        return f"Timer set for {duration_minutes} minutes boss"
    
    except Exception as e:
        print(f"[ERROR] Timer error: {str(e)}")
        return f"Failed to set timer boss: {str(e)}"


def set_alarm(alarm_time_str):
    """
    Set an alarm using Windows Clock app.
    Time format: "7 AM", "14:30", "2:30 PM", etc.
    
    Args:
        alarm_time_str (str): Alarm time (e.g., "7 AM", "14:30")
    
    Returns:
        tuple: (success: bool, response: str)
    """
    try:
        # Parse time
        # Handle formats: "7 AM", "7:30 AM", "14:30", "2:30 PM"
        time_match = re.search(r'(\d{1,2}):?(\d{0,2})\s*(am|pm)?', alarm_time_str.lower())
        if not time_match:
            return False, "Couldn't understand the alarm time boss."
        
        hour = int(time_match.group(1))
        minute = int(time_match.group(2)) if time_match.group(2) else 0
        meridiem = time_match.group(3)  # am/pm
        
        # Convert to 24-hour format
        if meridiem:
            if meridiem == "pm" and hour != 12:
                hour += 12
            elif meridiem == "am" and hour == 12:
                hour = 0
        
        alarm_display = f"{hour:02d}:{minute:02d}"
        
        # Open Clock app
        open_clock()
        
        # Wait for Clock to load
        if not wait_for_clock_load():
            return False, "Clock app took too long to load boss."
        
        # Click on Alarm tab
        print("[DEBUG] Clicking Alarm tab...")
        pyautogui.click(1100, 100)  # Adjust coordinates as needed
        time.sleep(1)
        
        # Click "Add alarm" or "+" button
        print("[DEBUG] Adding new alarm...")
        pyautogui.click(1300, 150)  # Adjust to actual Add button location
        time.sleep(1)
        
        # Enter alarm time
        print(f"[DEBUG] Setting alarm for {alarm_display}...")
        pyautogui.typewrite(f"{hour:02d}{minute:02d}")
        time.sleep(0.5)
        
        # Click Save/OK button
        pyautogui.click(1100, 600)  # Adjust to actual Save button location
        time.sleep(1)
        
        return True, f"Alarm set for {alarm_display} boss."
    
    except Exception as e:
        print(f"[ERROR] Alarm error: {str(e)}")
        return False, f"Failed to set alarm boss: {str(e)}"


def close_clock():
    """
    Close Windows Clock app.
    
    Returns:
        bool: True if successful
    """
    try:
        print("[DEBUG] Closing Clock app...")
        os.system("taskkill /IM WindowsAlarms.exe /F")
        return True
    except Exception as e:
        print(f"Error closing Clock: {str(e)}")
        return False
