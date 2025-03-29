#!/usr/bin/env python
"""
Example of using the LlamaLint CLI
"""
import os
import subprocess
import sys
from pathlib import Path

# Ensure the example can be run from any directory
EXAMPLE_DIR = Path(__file__).parent
PROJECT_ROOT = EXAMPLE_DIR.parent

def run_command(command, cwd=None):
    """Run a command and print its output"""
    print(f"$ {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=cwd)
    print(result.stdout)
    if result.stderr:
        print("Errors:")
        print(result.stderr)
    print("-" * 80)
    return result

def main():
    """Run the examples"""
    print("LlamaLint CLI Usage Examples")
    print("=" * 80)
    
    # Create a temporary directory for examples
    temp_dir = EXAMPLE_DIR / "temp"
    temp_dir.mkdir(exist_ok=True)
    
    # Create a sample Python file with issues
    sample_py = temp_dir / "sample.py"
    with open(sample_py, "w") as f:
        f.write("""
import sys, os
from math import *

# This function lacks a docstring
def calculate(x, y):
    return x + sin(y)

class badlyNamedClass:
    def __init__(self, value):
        self.value = value
        
    # This method has a docstring but poor formatting
    def getValue(self):
        '''Get the value'''
        return self.value
""")
    
    # Show the original file
    print("\nOriginal file:")
    with open(sample_py, "r") as f:
        print(f.read())
    print("-" * 80)
    
    # Initialize a llamalint config
    run_command(f"python -m llamalint init --format yaml {temp_dir}")
    
    # Check the file for issues
    run_command(f"python -m llamalint lint {sample_py}")
    
    # Format the file
    run_command(f"python -m llamalint format file {sample_py}")
    
    # Show the fixed file
    print("\nFixed file:")
    with open(sample_py, "r") as f:
        print(f.read())
    print("-" * 80)
    
    # List available rules
    run_command("python -m llamalint rules list")
    
    # Show details for a specific rule
    run_command("python -m llamalint rules show python-docstrings")
    
    # Clean up
    print("\nCleaning up...")
    import shutil
    shutil.rmtree(temp_dir)
    print("Temporary files removed.")

if __name__ == "__main__":
    main() 