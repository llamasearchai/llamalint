"""
Integration tests for LlamaLint
"""

import os
import tempfile
import unittest
from pathlib import Path

from llamalint.config import Config
from llamalint.linter import LlamaLint


class IntegrationTest(unittest.TestCase):
    """Integration tests for the linter"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config = Config()
        self.linter = LlamaLint(self.config)

    def tearDown(self):
        """Clean up test environment"""
        self.temp_dir.cleanup()

    def create_test_file(self, filename, content):
        """Create a test file"""
        file_path = Path(self.temp_dir.name) / filename
        with open(file_path, "w") as f:
            f.write(content)
        return file_path

    def test_python_docstrings(self):
        """Test Python docstrings rule"""
        # Create a Python file with missing docstrings
        content = """
def add(a, b):
    return a + b
        
class User:
    def __init__(self, name):
        self.name = name
"""
        file_path = self.create_test_file("test_docstrings.py", content)

        # Run the linter
        results = self.linter.lint_file(file_path)

        # There should be docstring issues
        self.assertTrue(any(r.rule_id == "python-docstrings" for r in results))

    def test_python_imports(self):
        """Test Python imports rule"""
        # Create a Python file with import issues
        content = """
import sys, os
from math import *

def test():
    return os.path.join('a', 'b')
"""
        file_path = self.create_test_file("test_imports.py", content)

        # Run the linter
        results = self.linter.lint_file(file_path)

        # There should be import issues
        self.assertTrue(any(r.rule_id == "python-imports" for r in results))

    def test_javascript_format(self):
        """Test JavaScript formatting"""
        # Create a JavaScript file with formatting issues
        content = """
function hello(  name ){
return "Hello, "+name+"!";
}
"""
        file_path = self.create_test_file("test_format.js", content)

        # Apply formatting
        formatted = self.linter.format_file(file_path)

        # Verify that formatting changed the content
        self.assertNotEqual(content, formatted)

    def test_config_loading(self):
        """Test configuration loading"""
        # Create a config file
        config_content = """
include:
  - "**/*.py"
disabled_rules:
  - "python-docstrings"
"""
        config_path = self.create_test_file(".llamalint.yaml", config_content)

        # Load config from file
        config = Config.from_file(config_path)

        # Verify config was loaded correctly
        self.assertIn("python-docstrings", config.disabled_rules)
        self.assertIn("**/*.py", config.include)


if __name__ == "__main__":
    unittest.main()
