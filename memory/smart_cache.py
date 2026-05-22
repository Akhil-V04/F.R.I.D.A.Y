"""
Smart Learning Cache System for FRIDAY

Stores and retrieves command results with fuzzy matching,
learns usage patterns, and improves performance over time.
"""

import json
import os
from datetime import datetime, timedelta
from difflib import SequenceMatcher
import re


class SmartCache:
    """
    Intelligent cache that learns from FRIDAY's usage patterns.
    
    Features:
    - Exact and fuzzy matching (>85% similarity)
    - Usage statistics and trending commands
    - Automatic cleanup of stale entries (30+ days)
    - Persistent storage in JSON
    - Response time tracking for optimization
    """
    
    CACHE_FILE = "memory/command_cache.json"
    FILLER_WORDS = {
        "please", "hey", "friday", "boss", "can you", "can i", "could you",
        "would you", "will you", "do you", "thanks", "thank you", "okay",
        "ok", "alright", "sure", "now", "just", "simply"
    }
    
    def __init__(self):
        """Load cache from disk or create new one"""
        self.cache = {}
        self._load_cache()
        self.clear_bad_entries()  # Clean up bad cache entries on startup
    
    def _load_cache(self):
        """Load cache from JSON file if exists"""
        try:
            if os.path.exists(self.CACHE_FILE):
                with open(self.CACHE_FILE, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
                    print(f"[CACHE] Loaded {len(self.cache)} entries from cache")
            else:
                self.cache = {}
                print("[CACHE] Starting with empty cache")
        except Exception as e:
            print(f"[CACHE ERROR] Failed to load cache: {e}")
            self.cache = {}
    
    def _save_cache(self):
        """Save cache to JSON file"""
        try:
            os.makedirs("memory", exist_ok=True)
            with open(self.CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[CACHE ERROR] Failed to save cache: {e}")
    
    def normalize(self, text):
        """
        Normalize text for consistent matching.
        - Lowercase
        - Remove punctuation
        - Remove filler words
        - Strip whitespace
        
        Args:
            text (str): Raw user input
        
        Returns:
            str: Normalized text
        """
        if not text:
            return ""
        
        # Lowercase
        text = text.lower()
        
        # Remove punctuation
        text = re.sub(r'[^\w\s]', '', text)
        
        # Remove filler words
        words = text.split()
        words = [w for w in words if w not in self.FILLER_WORDS]
        text = ' '.join(words)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def _fuzzy_match(self, normalized_input, threshold=0.85):
        """
        Find best fuzzy match in cache.
        
        Args:
            normalized_input (str): Normalized search text
            threshold (float): Similarity threshold (0-1)
        
        Returns:
            str or None: Best matching cache key, or None if no match
        """
        best_match = None
        best_ratio = threshold
        
        for cached_key in self.cache.keys():
            # Compare with stored normalized keys
            ratio = SequenceMatcher(None, normalized_input, cached_key).ratio()
            
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = cached_key
        
        return best_match
    
    def get(self, user_input):
        """
        Get cached result for user input.
        Tries exact match first, then fuzzy match.
        
        Args:
            user_input (str): User's voice command
        
        Returns:
            dict or None: Cache entry with tool, result, etc. or None if not found
        """
        if not user_input:
            return None
        
        normalized = self.normalize(user_input)
        
        # Try exact match first
        if normalized in self.cache:
            entry = self.cache[normalized]
            # Increment usage
            self.increment_usage(normalized)
            return entry
        
        # Try fuzzy match
        match_key = self._fuzzy_match(normalized)
        if match_key:
            entry = self.cache[match_key]
            # Increment usage
            self.increment_usage(match_key)
            return entry
        
        return None
    
    def set(self, user_input, result, tool_name, response_ms=0):
        """
        Save command result to cache.
        
        Args:
            user_input (str): Original user input
            result (str): Result/response from tool
            tool_name (str): Name of tool used (e.g., "open_app", "whatsapp_flow")
            response_ms (int): Response time in milliseconds (optional)
        """
        if not user_input:
            return
        
        normalized = self.normalize(user_input)
        
        # Create or update cache entry
        if normalized in self.cache:
            # Update existing entry
            entry = self.cache[normalized]
            entry["result"] = result
            entry["tool"] = tool_name
            entry["usage_count"] = entry.get("usage_count", 0) + 1
            entry["last_used"] = datetime.now().isoformat()
            
            # Update average response time
            if response_ms > 0:
                old_avg = entry.get("avg_response_ms", 0)
                old_count = entry.get("usage_count", 1) - 1
                new_avg = (old_avg * old_count + response_ms) / entry.get("usage_count", 1)
                entry["avg_response_ms"] = round(new_avg, 2)
        else:
            # Create new entry
            self.cache[normalized] = {
                "original": user_input,
                "tool": tool_name,
                "result": result,
                "usage_count": 1,
                "avg_response_ms": response_ms if response_ms > 0 else 0,
                "last_used": datetime.now().isoformat(),
                "created": datetime.now().isoformat()
            }
        
        # Save to disk
        self._save_cache()
    
    def increment_usage(self, normalized_key):
        """
        Increment usage count for a cached entry.
        Called when cached result is served.
        
        Args:
            normalized_key (str): Normalized cache key
        """
        if normalized_key in self.cache:
            self.cache[normalized_key]["usage_count"] = self.cache[normalized_key].get("usage_count", 0) + 1
            self.cache[normalized_key]["last_used"] = datetime.now().isoformat()
            self._save_cache()
    
    def get_stats(self):
        """
        Get cache statistics and top commands.
        
        Returns:
            str: Formatted stats string with top 5 commands
        """
        if not self.cache:
            return "No commands in cache yet boss. Keep asking and I'll remember them."
        
        # Sort by usage count (descending)
        sorted_cmds = sorted(
            self.cache.items(),
            key=lambda x: x[1].get("usage_count", 0),
            reverse=True
        )
        
        # Top 5
        top_5 = sorted_cmds[:5]
        
        # Build response
        lines = ["Here are your top commands boss:"]
        for i, (key, entry) in enumerate(top_5, 1):
            original = entry.get("original", key)
            count = entry.get("usage_count", 0)
            lines.append(f"{i}. {original} ({count} times)")
        
        lines.append(f"\nTotal commands learned: {len(self.cache)}")
        
        return "\n".join(lines)
    
    def cleanup(self):
        """
        Remove cache entries unused for 30+ days.
        
        Returns:
            int: Number of entries removed
        """
        now = datetime.now()
        removed = 0
        keys_to_remove = []
        
        for key, entry in self.cache.items():
            last_used_str = entry.get("last_used", "")
            if not last_used_str:
                continue
            
            try:
                last_used = datetime.fromisoformat(last_used_str)
                days_unused = (now - last_used).days
                
                if days_unused >= 30:
                    keys_to_remove.append(key)
                    removed += 1
            except Exception as e:
                print(f"[CACHE] Error parsing date for {key}: {e}")
        
        # Remove old entries
        for key in keys_to_remove:
            del self.cache[key]
        
        if removed > 0:
            self._save_cache()
            print(f"[CACHE] Cleaned up {removed} old entries")
        
        return removed
    
    def clear_all(self):
        """Clear entire cache (use carefully)"""
        self.cache = {}
        self._save_cache()
        print("[CACHE] Cache cleared")
    
    def clear_bad_entries(self):
        """
        Remove cache entries with invalid/bad results.
        Removes entries where result is None, "None", "", False, or "False".
        
        Returns:
            int: Number of entries removed
        """
        removed = 0
        keys_to_remove = []
        bad_values = {None, "None", "", False, "False"}
        
        for key, entry in self.cache.items():
            result = entry.get("result")
            if result in bad_values:
                keys_to_remove.append(key)
                removed += 1
        
        # Remove bad entries
        for key in keys_to_remove:
            del self.cache[key]
        
        if removed > 0:
            self._save_cache()
            print(f"[CACHE] Cleaned up {removed} bad entries (None/False/empty results)")
        
        return removed
    
    def get_size(self):
        """Get cache size in entries"""
        return len(self.cache)
    
    def get_most_used(self, limit=5):
        """
        Get most frequently used commands.
        
        Args:
            limit (int): Number of top commands to return
        
        Returns:
            list: List of (command, usage_count) tuples
        """
        sorted_cmds = sorted(
            self.cache.items(),
            key=lambda x: x[1].get("usage_count", 0),
            reverse=True
        )
        
        return [(entry[1].get("original", entry[0]), entry[1].get("usage_count", 0)) 
                for entry in sorted_cmds[:limit]]
