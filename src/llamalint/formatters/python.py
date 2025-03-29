"""
Python code formatter
"""
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from llamalint.formatters.base import Formatter


class PythonFormatter(Formatter):
    """
    Python code formatter using Black and isort
    """
    
    id = "python-formatter"
    name = "Python Formatter"
    description = "Formats Python code using Black and isort"
    languages = ["python"]
    file_patterns = ["**/*.py"]
    priority = 80
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Python formatter
        
        Args:
            config: Configuration options
        """
        super().__init__(config)
        
    def format(self, file_path: Path, content: str) -> str:
        """
        Format Python code
        
        Args:
            file_path: Path to the file
            content: File content
            
        Returns:
            Formatted content
        """
        # Check which formatters to use
        use_black = self.get_option("use_black", True)
        use_isort = self.get_option("use_isort", True)
        
        # Apply formatters in sequence
        formatted_content = content
        
        if use_isort:
            formatted_content = self._apply_isort(formatted_content)
            
        if use_black:
            formatted_content = self._apply_black(formatted_content)
            
        return formatted_content
    
    def _apply_black(self, content: str) -> str:
        """
        Format code using Black
        
        Args:
            content: Code content
            
        Returns:
            Formatted content
        """
        try:
            # Try to import black directly first
            try:
                import black
                
                # Get configuration options
                line_length = self.get_option("black_line_length", 88)
                skip_string_normalization = self.get_option("black_skip_string_normalization", False)
                
                # Apply black formatting
                mode = black.FileMode(
                    line_length=line_length,
                    string_normalization=not skip_string_normalization
                )
                
                return black.format_str(content, mode=mode)
                
            except ImportError:
                # Fall back to subprocess if black is not importable
                with tempfile.NamedTemporaryFile(suffix=".py", mode="w+", delete=False) as temp:
                    temp.write(content)
                    temp_path = temp.name
                    
                try:
                    # Build black command
                    black_cmd = ["black", "--quiet"]
                    
                    # Add options
                    line_length = self.get_option("black_line_length", 88)
                    black_cmd.extend(["--line-length", str(line_length)])
                    
                    if self.get_option("black_skip_string_normalization", False):
                        black_cmd.append("--skip-string-normalization")
                        
                    black_cmd.append(temp_path)
                    
                    # Run black
                    subprocess.run(black_cmd, check=True, capture_output=True)
                    
                    # Read the formatted content
                    with open(temp_path, "r") as f:
                        return f.read()
                        
                finally:
                    os.unlink(temp_path)
                    
        except Exception as e:
            # If black fails, return the original content
            print(f"Warning: Black formatting failed: {e}")
            return content
    
    def _apply_isort(self, content: str) -> str:
        """
        Format imports using isort
        
        Args:
            content: Code content
            
        Returns:
            Formatted content
        """
        try:
            # Try to import isort directly first
            try:
                import isort
                
                # Get configuration options
                profile = self.get_option("isort_profile", "black")
                line_length = self.get_option("isort_line_length", 88)
                
                # Apply isort formatting
                isort_config = isort.Config(
                    profile=profile,
                    line_length=line_length
                )
                
                return isort.code(content, config=isort_config)
                
            except ImportError:
                # Fall back to subprocess if isort is not importable
                with tempfile.NamedTemporaryFile(suffix=".py", mode="w+", delete=False) as temp:
                    temp.write(content)
                    temp_path = temp.name
                    
                try:
                    # Build isort command
                    isort_cmd = ["isort"]
                    
                    # Add options
                    profile = self.get_option("isort_profile", "black")
                    isort_cmd.extend(["--profile", profile])
                    
                    line_length = self.get_option("isort_line_length", 88)
                    isort_cmd.extend(["--line-length", str(line_length)])
                    
                    isort_cmd.append(temp_path)
                    
                    # Run isort
                    subprocess.run(isort_cmd, check=True, capture_output=True)
                    
                    # Read the formatted content
                    with open(temp_path, "r") as f:
                        return f.read()
                        
                finally:
                    os.unlink(temp_path)
                    
        except Exception as e:
            # If isort fails, return the original content
            print(f"Warning: isort formatting failed: {e}")
            return content 