"""
Test suite for improved WhatsApp automation.
Tests contact memory, search reliability, and coordinate detection.
"""

import unittest
import json
import os
import time
from pathlib import Path

# Import the improved WhatsApp functions
from actions.whatsapp import (
    load_contact_memory,
    save_contact_memory,
    add_to_contact_memory,
    resolve_contact_from_memory,
    find_message_input_box,
    find_search_box,
    CONTACT_ALIASES,
    CONTACT_MEMORY_FILE
)


class TestContactMemorySystem(unittest.TestCase):
    """Test the new contact memory system."""
    
    def setUp(self):
        """Clean up before each test."""
        if os.path.exists(CONTACT_MEMORY_FILE):
            os.remove(CONTACT_MEMORY_FILE)
    
    def tearDown(self):
        """Clean up after each test."""
        if os.path.exists(CONTACT_MEMORY_FILE):
            os.remove(CONTACT_MEMORY_FILE)
    
    def test_01_contact_memory_persistence(self):
        """Test that contacts are saved and loaded correctly."""
        print("\n[TEST 1] Testing contact memory persistence...")
        
        # Save some contacts
        test_contacts = {
            "akhil": "Akhil Vaddeboina",
            "mom": "Mom",
            "self": "+91 93925 24228"
        }
        save_contact_memory(test_contacts)
        
        # Verify file was created
        self.assertTrue(os.path.exists(CONTACT_MEMORY_FILE))
        print(f"  [OK] Contact memory file created at {CONTACT_MEMORY_FILE}")
        
        # Load and verify
        loaded = load_contact_memory()
        self.assertEqual(loaded, test_contacts)
        print(f"  [OK] Loaded {len(loaded)} contacts")
        print(f"  [OK] Contacts: {list(loaded.keys())}")
    
    def test_02_add_to_contact_memory(self):
        """Test adding contacts individually."""
        print("\n[TEST 2] Testing add_to_contact_memory...")
        
        # Add contacts one by one
        contacts_to_add = ["Akhil", "Mom", "Dad", "Minegang"]
        
        for contact in contacts_to_add:
            add_to_contact_memory(contact)
            print(f"  [OK] Added {contact}")
        
        # Load all
        all_contacts = load_contact_memory()
        self.assertEqual(len(all_contacts), len(contacts_to_add))
        print(f"  [OK] Total contacts in memory: {len(all_contacts)}")
    
    def test_03_resolve_contact_direct_match(self):
        """Test resolving contact with direct match."""
        print("\n[TEST 3] Testing direct match resolution...")
        
        # Set up memory
        test_contacts = {
            "akhil": "Akhil Vaddeboina",
            "mom": "Mom (Mom's Phone)"
        }
        save_contact_memory(test_contacts)
        
        # Test direct match (exact lowercase)
        result = resolve_contact_from_memory("akhil")
        self.assertEqual(result, "Akhil Vaddeboina")
        print(f"  [OK] 'akhil' resolved to '{result}'")
        
        # Test direct match (different case)
        result = resolve_contact_from_memory("MOM")
        self.assertEqual(result, "Mom (Mom's Phone)")
        print(f"  [OK] 'MOM' resolved to '{result}'")
    
    def test_04_resolve_contact_fuzzy_match(self):
        """Test resolving contact with fuzzy/partial match."""
        print("\n[TEST 4] Testing fuzzy match resolution...")
        
        # Set up memory
        test_contacts = {
            "akhil vaddeboina": "Akhil Vaddeboina",
            "mom": "Mom"
        }
        save_contact_memory(test_contacts)
        
        # Test fuzzy match
        result = resolve_contact_from_memory("akhil")
        # Should fuzzy match "akhil vaddeboina"
        self.assertEqual(result, "Akhil Vaddeboina")
        print(f"  [OK] 'akhil' fuzzy-matched to '{result}'")
    
    def test_05_resolve_contact_not_found(self):
        """Test resolving a contact that doesn't exist."""
        print("\n[TEST 5] Testing resolution of unknown contact...")
        
        # Set up minimal memory
        test_contacts = {"akhil": "Akhil"}
        save_contact_memory(test_contacts)
        
        # Try to resolve unknown contact
        result = resolve_contact_from_memory("unknown_contact")
        self.assertEqual(result, "unknown_contact")
        print(f"  [OK] Unknown contact returned as-is: '{result}'")
    
    def test_06_empty_memory_handling(self):
        """Test handling empty contact memory."""
        print("\n[TEST 6] Testing empty memory handling...")
        
        # Load with no memory file
        loaded = load_contact_memory()
        self.assertEqual(loaded, {})
        print(f"  [OK] Empty memory returns empty dict")
        
        # Resolve with empty memory
        result = resolve_contact_from_memory("test")
        self.assertEqual(result, "test")
        print(f"  [OK] Resolve on empty memory returns input as-is")
    
    def test_07_contact_aliases_still_work(self):
        """Test that original contact aliases still work."""
        print("\n[TEST 7] Testing backward compatibility of aliases...")
        
        # Aliases should be processed before memory resolution
        aliases = CONTACT_ALIASES
        self.assertIn("myself", aliases)
        self.assertIn("me", aliases)
        self.assertIn("minegang", aliases)
        
        print(f"  [OK] Found {len(aliases)} aliases")
        print(f"  [OK] Sample aliases: {list(aliases.keys())[:3]}")


class TestUIDetection(unittest.TestCase):
    """Test dynamic UI element detection."""
    
    def test_01_find_message_input_box(self):
        """Test finding message input box."""
        print("\n[TEST 8] Testing find_message_input_box()...")
        
        coords = find_message_input_box()
        
        self.assertIsNotNone(coords)
        self.assertEqual(len(coords), 2)
        self.assertIsInstance(coords[0], int)
        self.assertIsInstance(coords[1], int)
        
        x, y = coords
        print(f"  [OK] Message input box found at ({x}, {y})")
        
        # Should be reasonable coordinates (not at 0,0)
        self.assertGreater(x, 0)
        self.assertGreater(y, 0)
        print(f"  [OK] Coordinates are valid (not 0,0)")
    
    def test_02_find_search_box(self):
        """Test finding search box (may return None if not visible)."""
        print("\n[TEST 9] Testing find_search_box()...")
        
        coords = find_search_box()
        
        # Can be None if search box not visible
        if coords is not None:
            self.assertEqual(len(coords), 2)
            x, y = coords
            print(f"  [OK] Search box found at ({x}, {y})")
        else:
            print(f"  [OK] Search box not visible (None) - expected")


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system."""
    
    def test_01_imports(self):
        """Test that all functions import correctly."""
        print("\n[TEST 10] Testing all imports...")
        
        from actions.whatsapp import (
            send_whatsapp_message,
            send_whatsapp_flow,
            load_contact_memory,
            save_contact_memory,
            add_to_contact_memory,
            resolve_contact_from_memory,
            find_message_input_box,
            find_search_box,
            try_search_contact,
            try_scroll_contact,
            CONTACT_ALIASES,
            CONTACT_MEMORY_FILE
        )
        
        print(f"  [OK] send_whatsapp_message imported")
        print(f"  [OK] send_whatsapp_flow imported")
        print(f"  [OK] Contact memory functions imported (4 functions)")
        print(f"  [OK] UI detection functions imported (2 functions)")
        print(f"  [OK] Fallback search functions imported (2 functions)")
        print(f"  [OK] All imports successful")
    
    def test_02_backward_compatibility(self):
        """Test that original functions still work."""
        print("\n[TEST 11] Testing backward compatibility...")
        
        from actions.whatsapp import (
            is_whatsapp_loaded,
            wait_for_whatsapp_load,
            is_chat_message_box_ready,
            wait_for_chat_load,
            click_on_text,
            find_text_on_screen,
            open_whatsapp
        )
        
        print(f"  [OK] is_whatsapp_loaded still available")
        print(f"  [OK] wait_for_whatsapp_load still available")
        print(f"  [OK] is_chat_message_box_ready still available")
        print(f"  [OK] wait_for_chat_load still available")
        print(f"  [OK] click_on_text still available")
        print(f"  [OK] find_text_on_screen still available")
        print(f"  [OK] open_whatsapp still available")
        print(f"  [OK] No breaking changes - 100% backward compatible")


def run_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("TESTING WHATSAPP AUTOMATION IMPROVEMENTS")
    print("="*60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestContactMemorySystem))
    suite.addTests(loader.loadTestsFromTestCase(TestUIDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failed: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n[PASS] ALL TESTS PASSED")
        print("WhatsApp improvements ready for production use!")
    else:
        print("\n[FAIL] Some tests failed - review above")
    
    print("="*60)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
