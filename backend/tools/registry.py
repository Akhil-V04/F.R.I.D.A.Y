"""
Central Tool Registry for F.R.I.D.A.Y
Registers all available tools without modifying existing functions.
"""

from actions.whatsapp import send_message_to_contact, send_whatsapp_flow
from actions.apps import open_app, close_app, close_all_apps
from actions.news_reader import get_news, get_world_briefing, get_india_briefing, get_news_by_topic
from actions.screen import click_text, find_text_on_screen, get_screen_text, scroll_down, scroll_up, type_text, press_key, ScreenAgent
from actions.system import get_time, get_date, get_battery, take_screenshot, shutdown_pc, restart_pc
from actions.web import (open_url, search_google, search_youtube, 
                         open_world_monitor, open_claude, open_chatgpt, open_and_search)
from actions.email_sender import send_email_to_contact
from actions.clock import open_clock, set_timer, set_alarm, close_clock
from brain.ollama import ask_brain as ask_brain_func

# ===== SCREEN AGENT INSTANCE =====
_screen_agent = ScreenAgent()


# ===== TOOL REGISTRY =====
# Each tool is defined with:
# - name: unique identifier
# - func: reference to actual function
# - params: list of {name, type, description, required}
# - description: what the tool does

TOOLS = {
    # ===== MESSAGING TOOLS =====
    "send_whatsapp": {
        "name": "send_whatsapp",
        "func": send_message_to_contact,
        "params": [
            {"name": "contact_name", "type": "str", "description": "Contact name or phone number", "required": True},
            {"name": "message", "type": "str", "description": "Message text", "required": True},
        ],
        "description": "Send WhatsApp message to a contact"
    },
    
    "send_whatsapp_flow": {
        "name": "send_whatsapp_flow",
        "func": send_whatsapp_flow,
        "params": [
            {"name": "initial_contact", "type": "str", "description": "Initial contact name", "required": False},
        ],
        "description": "Interactive WhatsApp flow"
    },
    
    "send_email": {
        "name": "send_email",
        "func": send_email_to_contact,
        "params": [
            {"name": "contact", "type": "str", "description": "Recipient email", "required": True},
            {"name": "subject", "type": "str", "description": "Email subject", "required": True},
            {"name": "body", "type": "str", "description": "Email body", "required": True},
        ],
        "description": "Send email to contact"
    },
    
    # ===== APP CONTROL TOOLS =====
    "open_app": {
        "name": "open_app",
        "func": open_app,
        "params": [
            {"name": "app_name", "type": "str", "description": "Application name", "required": True},
        ],
        "description": "Open an application"
    },
    
    "close_app": {
        "name": "close_app",
        "func": close_app,
        "params": [
            {"name": "app_name", "type": "str", "description": "Application name", "required": True},
        ],
        "description": "Close an application"
    },
    
    "close_all_apps": {
        "name": "close_all_apps",
        "func": close_all_apps,
        "params": [],
        "description": "Close all running applications"
    },
    
    # ===== NEWS TOOLS =====
    "get_news": {
        "name": "get_news",
        "func": get_news,
        "params": [
            {"name": "category", "type": "str", "description": "News category (world, technology, sports, india, business)", "required": False, "default": "world"},
            {"name": "limit", "type": "int", "description": "Number of headlines", "required": False, "default": 5},
        ],
        "description": "Fetch news headlines"
    },
    
    "get_world_briefing": {
        "name": "get_world_briefing",
        "func": get_world_briefing,
        "params": [],
        "description": "Get global and India news briefing"
    },
    
    "get_india_briefing": {
        "name": "get_india_briefing",
        "func": get_india_briefing,
        "params": [],
        "description": "Get India news briefing"
    },
    
    "get_news_by_topic": {
        "name": "get_news_by_topic",
        "func": get_news_by_topic,
        "params": [
            {"name": "topic", "type": "str", "description": "News topic", "required": True},
        ],
        "description": "Get news filtered by topic"
    },
    
    # ===== SCREEN TOOLS =====
    "click_text": {
        "name": "click_text",
        "func": click_text,
        "params": [
            {"name": "text", "type": "str", "description": "Text to find and click", "required": True},
        ],
        "description": "Find and click text on screen using OCR"
    },
    
    "find_text": {
        "name": "find_text",
        "func": find_text_on_screen,
        "params": [
            {"name": "search_text", "type": "str", "description": "Text to search for", "required": True},
            {"name": "confidence", "type": "int", "description": "Confidence threshold (0-100)", "required": False, "default": 50},
        ],
        "description": "Find text position on screen"
    },
    
    "get_screen_text": {
        "name": "get_screen_text",
        "func": get_screen_text,
        "params": [],
        "description": "Read all text from screen"
    },
    
    "scroll_down": {
        "name": "scroll_down",
        "func": scroll_down,
        "params": [
            {"name": "amount", "type": "int", "description": "Scroll amount", "required": False, "default": 5},
        ],
        "description": "Scroll down"
    },
    
    "scroll_up": {
        "name": "scroll_up",
        "func": scroll_up,
        "params": [
            {"name": "amount", "type": "int", "description": "Scroll amount", "required": False, "default": 5},
        ],
        "description": "Scroll up"
    },
    
    "type_text": {
        "name": "type_text",
        "func": type_text,
        "params": [
            {"name": "text", "type": "str", "description": "Text to type", "required": True},
        ],
        "description": "Type text"
    },
    
    "press_key": {
        "name": "press_key",
        "func": press_key,
        "params": [
            {"name": "key", "type": "str", "description": "Key to press (enter, escape, etc.)", "required": True},
        ],
        "description": "Press a keyboard key"
    },
    
    # ===== SCREEN AGENT TOOLS =====
    "read_screen": {
        "name": "read_screen",
        "func": _screen_agent.read_screen_text,
        "params": [],
        "description": "Read text visible on screen (excludes terminal)"
    },
    
    "analyze_screen": {
        "name": "analyze_screen",
        "func": _screen_agent.analyze_screen,
        "params": [
            {"name": "question", "type": "str", "description": "Question about screen content", "required": True},
        ],
        "description": "Analyze screen and answer question"
    },
    
    "click_text": {
        "name": "click_text",
        "func": _screen_agent.find_and_click,
        "params": [
            {"name": "text", "type": "str", "description": "Text to find and click", "required": True},
        ],
        "description": "Click on text visible on screen"
    },
    
    # ===== SYSTEM TOOLS =====
    "get_time": {
        "name": "get_time",
        "func": get_time,
        "params": [],
        "description": "Get current time"
    },
    
    "get_date": {
        "name": "get_date",
        "func": get_date,
        "params": [],
        "description": "Get current date"
    },
    
    "get_battery": {
        "name": "get_battery",
        "func": get_battery,
        "params": [],
        "description": "Get battery status"
    },
    
    "take_screenshot": {
        "name": "take_screenshot",
        "func": take_screenshot,
        "params": [],
        "description": "Take a screenshot"
    },
    
    "shutdown_pc": {
        "name": "shutdown_pc",
        "func": shutdown_pc,
        "params": [],
        "description": "Shutdown computer"
    },
    
    "restart_pc": {
        "name": "restart_pc",
        "func": restart_pc,
        "params": [],
        "description": "Restart computer"
    },
    
    # ===== WEB TOOLS =====
    "open_url": {
        "name": "open_url",
        "func": open_url,
        "params": [
            {"name": "url", "type": "str", "description": "URL to open", "required": True},
        ],
        "description": "Open URL in browser"
    },
    
    "search_google": {
        "name": "search_google",
        "func": search_google,
        "params": [
            {"name": "query", "type": "str", "description": "Search query", "required": True},
        ],
        "description": "Search Google"
    },
    
    "search_youtube": {
        "name": "search_youtube",
        "func": search_youtube,
        "params": [
            {"name": "query", "type": "str", "description": "Search query", "required": True},
        ],
        "description": "Search YouTube"
    },
    
    "open_world_monitor": {
        "name": "open_world_monitor",
        "func": open_world_monitor,
        "params": [],
        "description": "Open world news monitor"
    },
    
    "open_claude": {
        "name": "open_claude",
        "func": open_claude,
        "params": [],
        "description": "Open Claude AI"
    },
    
    "open_chatgpt": {
        "name": "open_chatgpt",
        "func": open_chatgpt,
        "params": [],
        "description": "Open ChatGPT"
    },
    
    "open_and_search": {
        "name": "open_and_search",
        "func": open_and_search,
        "params": [
            {"name": "query", "type": "str", "description": "Search query", "required": True},
        ],
        "description": "Open browser and search"
    },
    
    # ===== CLOCK TOOLS =====
    "open_clock": {
        "name": "open_clock",
        "func": open_clock,
        "params": [],
        "description": "Open clock app"
    },
    
    "set_timer": {
        "name": "set_timer",
        "func": set_timer,
        "params": [
            {"name": "duration_str", "type": "str", "description": "Timer duration (e.g., '5 minutes')", "required": True},
        ],
        "description": "Set a timer"
    },
    
    "set_alarm": {
        "name": "set_alarm",
        "func": set_alarm,
        "params": [
            {"name": "time", "type": "str", "description": "Alarm time (e.g., '7:30 AM')", "required": True},
        ],
        "description": "Set an alarm"
    },
    
    "close_clock": {
        "name": "close_clock",
        "func": close_clock,
        "params": [],
        "description": "Close clock app"
    },
    
    # ===== UTILITY TOOLS =====
    "ask_brain": {
        "name": "ask_brain",
        "func": ask_brain_func,
        "params": [
            {"name": "user_input", "type": "str", "description": "Question or topic to discuss", "required": True},
        ],
        "description": "Ask Qwen for general conversation, advice, or information"
    },
}


def get_tool(tool_name):
    """Get a tool by name"""
    return TOOLS.get(tool_name)


def list_tools():
    """List all available tools"""
    return list(TOOLS.keys())


def get_tool_info(tool_name):
    """Get full tool information"""
    return TOOLS.get(tool_name)
