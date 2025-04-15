"""
JavaScript code formatter
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from llamalint.formatters.base import Formatter


class JavaScriptFormatter(Formatter):
    """
    JavaScript code formatter using Prettier
    """

    id = "javascript-formatter"
    name = "JavaScript Formatter"
    description = "Formats JavaScript code using Prettier"
    languages = ["javascript"]
    file_patterns = ["**/*.js", "**/*.jsx", "**/*.json"]
    priority = 80

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the JavaScript formatter

        Args:
            config: Configuration options
        """
        super().__init__(config)

    def format(self, file_path: Path, content: str) -> str:
        """
        Format JavaScript code

        Args:
            file_path: Path to the file
            content: File content

        Returns:
            Formatted content
        """
        # Apply prettier
        return self._apply_prettier(content, file_path)

    def _apply_prettier(self, content: str, file_path: Path) -> str:
        """
        Format code using Prettier

        Args:
            content: Code content
            file_path: Path to the file

        Returns:
            Formatted content
        """
        try:
            # Get configuration options
            tab_width = self.get_option("tab_width", 2)
            use_tabs = self.get_option("use_tabs", False)
            single_quote = self.get_option("single_quote", False)
            trailing_comma = self.get_option("trailing_comma", "es5")
            bracket_spacing = self.get_option("bracket_spacing", True)

            # Create a temporary file
            with tempfile.NamedTemporaryFile(
                suffix=file_path.suffix, mode="w+", delete=False
            ) as temp:
                temp.write(content)
                temp_path = temp.name

            try:
                # Build prettier command
                prettier_cmd = ["npx", "prettier", "--write"]

                # Add options
                prettier_cmd.extend(["--tab-width", str(tab_width)])
                prettier_cmd.append("--use-tabs" if use_tabs else "--no-use-tabs")
                prettier_cmd.append(
                    "--single-quote" if single_quote else "--no-single-quote"
                )
                prettier_cmd.extend(["--trailing-comma", trailing_comma])
                prettier_cmd.append(
                    "--bracket-spacing" if bracket_spacing else "--no-bracket-spacing"
                )

                # Add file path
                prettier_cmd.append(temp_path)

                # Run prettier
                subprocess.run(prettier_cmd, check=True, capture_output=True)

                # Read the formatted content
                with open(temp_path, "r") as f:
                    return f.read()

            finally:
                os.unlink(temp_path)

        except Exception as e:
            # If prettier fails, return the original content
            print(f"Warning: Prettier formatting failed: {e}")
            return content
