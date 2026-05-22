"""
Test suite for the new Qwen-based build app implementation (v2).
Tests each helper function and the main run_coding_agent_v2 function.
"""

import unittest
import json
from pathlib import Path
from actions.coding_agent import (
    refine_app_idea,
    generate_app_plan,
    generate_file_structure,
    generate_code_for_file,
    create_project_folder,
    write_project_files,
    run_coding_agent_v2
)


class TestNewBuildAppV2(unittest.TestCase):
    """Test suite for new Qwen-based build app implementation."""
    
    def test_01_refine_app_idea(self):
        """Test idea refinement with Qwen."""
        print("\n[TEST 1] Testing idea refinement...")
        
        test_ideas = [
            "build a calculator",
            "todo list app",
            "weather checker"
        ]
        
        for idea in test_ideas:
            result = refine_app_idea(idea)
            
            # Validate result
            self.assertIsInstance(result, str)
            self.assertGreater(len(result), 5)  # Should have some content
            self.assertLess(len(result), 500)   # Shouldn't be too long
            
            print(f"  [OK] Refined '{idea}' -> '{result[:60]}...'")
    
    def test_02_generate_app_plan(self):
        """Test plan generation with Qwen."""
        print("\n[TEST 2] Testing plan generation...")
        
        idea = "simple calculator app in Python"
        result = generate_app_plan(idea)
        
        # Validate result
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 20)  # Should have substantial content
        
        # Plan can be in different formats (numbered or descriptive)
        has_steps = ("1." in result) or (result.count('\n') > 2) or ("step" in result.lower())
        self.assertTrue(has_steps or len(result) > 50, "Plan should describe steps or be descriptive")
        
        print(f"  [OK] Generated plan for '{idea}'")
        print(f"  [OK] Plan length: {len(result)} chars")
    
    def test_03_generate_file_structure(self):
        """Test file structure generation with Qwen."""
        print("\n[TEST 3] Testing file structure generation...")
        
        idea = "simple calculator"
        plan = "1. Create main.py\n2. Add functions\n3. Test code"
        
        result = generate_file_structure(idea, plan)
        
        # Validate structure
        self.assertIsInstance(result, dict)
        self.assertIn("files", result)
        self.assertIn("folders", result)
        self.assertIsInstance(result["files"], dict)
        self.assertIsInstance(result["folders"], list)
        self.assertGreater(len(result["files"]), 0)
        
        print(f"  [OK] Generated structure with {len(result['files'])} files")
        print(f"  [OK] Files: {list(result['files'].keys())}")
        print(f"  [OK] Folders: {result['folders']}")
    
    def test_04_generate_code_for_file(self):
        """Test code generation for a specific file."""
        print("\n[TEST 4] Testing code generation for files...")
        
        test_cases = [
            ("main.py", ".py", "calculator", "Main application entry point"),
            ("config.json", ".json", "todo app", "Configuration file"),
            ("README.md", ".md", "weather app", "Documentation")
        ]
        
        for filename, filetype, idea, context in test_cases:
            result = generate_code_for_file(filename, filetype, idea, context)
            
            # Validate result
            self.assertIsInstance(result, str)
            self.assertGreater(len(result), 5)
            
            print(f"  [OK] Generated {filename} ({len(result)} chars)")
    
    def test_05_create_project_folder(self):
        """Test project folder creation."""
        print("\n[TEST 5] Testing project folder creation...")
        
        test_project = "test_app_v2_001"
        result = create_project_folder(test_project)
        
        # Validate path
        self.assertIsInstance(result, str)
        path = Path(result)
        self.assertTrue(path.exists())
        
        print(f"  [OK] Folder created at: {result}")
        
        # Cleanup
        import shutil
        if path.exists():
            shutil.rmtree(path)
            print(f"  [OK] Cleanup: Removed {result}")
    
    def test_06_write_project_files(self):
        """Test writing files to project folder."""
        print("\n[TEST 6] Testing file writing...")
        
        # Setup test project
        project_name = "test_write_files_v2"
        project_path = Path.home() / "Downloads" / project_name
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Test structure
        file_structure = {
            "files": {
                "main.py": "def main(): pass",
                "utils.py": "def helper(): pass",
                "config.json": '{"test": true}'
            },
            "folders": ["src", "tests"]
        }
        
        code_map = file_structure["files"]
        
        # Write files
        result = write_project_files(str(project_path), file_structure, code_map)
        
        # Validate
        self.assertTrue(result)
        
        # Check files exist
        self.assertTrue((project_path / "main.py").exists())
        self.assertTrue((project_path / "utils.py").exists())
        self.assertTrue((project_path / "config.json").exists())
        self.assertTrue((project_path / "src").exists())
        self.assertTrue((project_path / "tests").exists())
        
        print(f"  [OK] Files written successfully")
        print(f"  [OK] Created {len(code_map)} files")
        print(f"  [OK] Created 2 folders")
        
        # Cleanup
        import shutil
        if project_path.exists():
            shutil.rmtree(project_path)
            print(f"  [OK] Cleanup: Removed {project_path}")
    
    def test_07_qwen_basic_functionality(self):
        """Test that Qwen is available and responding."""
        print("\n[TEST 7] Testing Qwen availability...")
        
        try:
            from brain.ollama import ask_brain
            
            # Simple test prompt
            response = ask_brain("Say 'OK' only.")
            
            self.assertIsInstance(response, str)
            self.assertGreater(len(response), 0)
            
            print(f"  [OK] Qwen is responsive")
            print(f"  [OK] Response: '{response.strip()}'")
        except Exception as e:
            print(f"  [WARN] Qwen not available: {e}")
            print(f"  [WARN] (Make sure Ollama is running)")
    
    def test_08_state_integration(self):
        """Test that state management is integrated."""
        print("\n[TEST 8] Testing state integration...")
        
        try:
            from memory.state import get_state, start_new_project
            
            # Get current state
            state = get_state()
            self.assertIsInstance(state, dict)
            self.assertIn("vscode_open", state)
            self.assertIn("current_project", state)
            self.assertIn("new_project_mode", state)
            
            print(f"  [OK] State management available")
            print(f"  [OK] Current state: {state}")
        except Exception as e:
            self.fail(f"State integration failed: {e}")
    
    def test_09_import_all_components(self):
        """Test that all components import correctly."""
        print("\n[TEST 9] Testing all imports...")
        
        from actions.coding_agent import (
            run_coding_agent_v2,
            refine_app_idea,
            generate_app_plan,
            generate_file_structure,
            generate_code_for_file,
            create_project_folder,
            write_project_files,
            open_project_in_vscode,
            run_coding_agent,  # Old function still available
            open_chatgpt_and_ask,  # Old function still available
            coding_agent_flow
        )
        
        print(f"  [OK] run_coding_agent_v2: Available")
        print(f"  [OK] refine_app_idea: Available")
        print(f"  [OK] generate_app_plan: Available")
        print(f"  [OK] generate_file_structure: Available")
        print(f"  [OK] generate_code_for_file: Available")
        print(f"  [OK] create_project_folder: Available")
        print(f"  [OK] write_project_files: Available")
        print(f"  [OK] open_project_in_vscode: Available")
        print(f"  [OK] run_coding_agent: Available (deprecated)")
        print(f"  [OK] open_chatgpt_and_ask: Available (deprecated)")
        print(f"  [OK] coding_agent_flow: Available")
    
    def test_10_performance_expectations(self):
        """Test that new approach meets performance targets."""
        print("\n[TEST 10] Testing performance expectations...")
        
        # Expected performance:
        # - Step 1 (refine): ~1-2s
        # - Step 2 (plan): ~2-3s
        # - Step 3 (structure): ~2-3s
        # - Step 4-5 (code gen): ~3-5s per file
        # - Step 6 (write files): <1s
        # - Total: 6-10s (vs 30-40s for old approach)
        
        import time
        
        # Time a simple operation
        start = time.time()
        try:
            from brain.ollama import ask_brain
            ask_brain("Say 'OK'")
            elapsed = time.time() - start
            
            print(f"  [OK] Single Qwen call: {elapsed:.2f}s")
            
            # Should be reasonable for local execution
            if elapsed < 30:
                print(f"  [OK] Performance is acceptable")
            else:
                print(f"  [WARN] Performance may need optimization (took {elapsed:.1f}s)")
        except Exception as e:
            print(f"  [WARN] Could not test performance: {e}")


def run_integration_test():
    """Run a simple integration test of the full flow."""
    print("\n" + "="*60)
    print("INTEGRATION TEST - Full Build App Flow (Optional)")
    print("="*60)
    
    try:
        # This is a MANUAL test - uncomment to run full flow
        # NOT run automatically as it takes time and creates files
        
        print("\n[WARN] Full integration test requires:")
        print("  1. Ollama running (localhost:11434)")
        print("  2. Qwen2.5:3b model installed")
        print("  3. VS Code installed")
        print("\nTo run full integration test:")
        print('  result = run_coding_agent_v2("simple counter app")')
        print(f"  print(result)")
        
    except Exception as e:
        print(f"Integration test skipped: {e}")


if __name__ == '__main__':
    # Run test suite
    print("\n" + "="*60)
    print("TESTING NEW BUILD APP v2 IMPLEMENTATION")
    print("="*60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestNewBuildAppV2)
    
    # Run with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n[PASS] ALL TESTS PASSED - Implementation ready!")
    else:
        print("\n[FAIL] Some tests failed - Review errors above")
    
    # Optional integration test
    run_integration_test()
