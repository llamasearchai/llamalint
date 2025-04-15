"""
TypeScript code formatter
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from llamalint.formatters.base import Formatter
from llamalint.formatters.javascript import JavaScriptFormatter


class TypeScriptFormatter(Formatter):
    """
    TypeScript code formatter using Prettier and ESLint
    """

    id = "typescript-formatter"
    name = "TypeScript Formatter"
    description = "Formats TypeScript code using Prettier and ESLint"
    languages = ["typescript"]
    file_patterns = ["**/*.ts", "**/*.tsx"]
    priority = 80

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the TypeScript formatter

        Args:
            config: Configuration options
        """
        super().__init__(config)
        # Create a JavaScript formatter for Prettier functionality
        self.js_formatter = JavaScriptFormatter(config)

    def format(self, file_path: Path, content: str) -> str:
        """
        Format TypeScript code

        Args:
            file_path: Path to the file
            content: File content

        Returns:
            Formatted content
        """
        # First apply Prettier through the JavaScript formatter
        formatted_content = self.js_formatter.format(file_path, content)

        # Then apply ESLint if enabled
        if self.get_option("use_eslint", True):
            formatted_content = self._apply_eslint(formatted_content, file_path)

        return formatted_content

    def _apply_eslint(self, content: str, file_path: Path) -> str:
        """
        Format code using ESLint

        Args:
            content: Code content
            file_path: Path to the file

        Returns:
            Formatted content
        """
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(
                suffix=file_path.suffix, mode="w+", delete=False
            ) as temp:
                temp.write(content)
                temp_path = temp.name

            try:
                # Build eslint command
                eslint_cmd = ["npx", "eslint", "--fix"]

                # Add file path
                eslint_cmd.append(temp_path)

                # Run eslint
                subprocess.run(eslint_cmd, check=True, capture_output=True)

                # Read the formatted content
                with open(temp_path, "r") as f:
                    return f.read()

            finally:
                os.unlink(temp_path)

        except Exception as e:
            # If eslint fails, return the original content
            print(f"Warning: ESLint formatting failed: {e}")
            return content
