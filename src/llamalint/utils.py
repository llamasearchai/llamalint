"""
Utility functions for LlamaLint
"""

import fnmatch
import os
import re
from pathlib import Path
from typing import List, Optional, Pattern, Set, Union


class FileUtils:
    """
    Utilities for file operations
    """

    @staticmethod
    def find_files(
        directory: Union[str, Path],
        include_patterns: List[str] = None,
        exclude_patterns: List[str] = None,
    ) -> List[Path]:
        """
        Find files in a directory matching patterns

        Args:
            directory: Directory to search
            include_patterns: Patterns of files to include
            exclude_patterns: Patterns of files to exclude

        Returns:
            List of matching file paths
        """
        directory = Path(directory)
        include_patterns = include_patterns or ["**/*"]
        exclude_patterns = exclude_patterns or []

        # Convert glob patterns to regex
        include_regexes = [FileUtils._glob_to_regex(p) for p in include_patterns]
        exclude_regexes = [FileUtils._glob_to_regex(p) for p in exclude_patterns]

        matching_files = []

        for root, dirs, files in os.walk(directory):
            # Convert root to a Path object
            root_path = Path(root)

            # Remove excluded directories
            dirs[:] = [
                d
                for d in dirs
                if not any(
                    r.search(str(root_path / d).replace("\\", "/"))
                    for r in exclude_regexes
                )
            ]

            # Check each file
            for file in files:
                file_path = root_path / file
                rel_path = file_path.relative_to(directory)
                rel_path_str = str(rel_path).replace("\\", "/")

                # Check if path matches include pattern and not exclude pattern
                if any(r.search(rel_path_str) for r in include_regexes) and not any(
                    r.search(rel_path_str) for r in exclude_regexes
                ):
                    matching_files.append(file_path)

        return matching_files

    @staticmethod
    def is_ignored(
        file_path: Union[str, Path],
        include_patterns: List[str] = None,
        exclude_patterns: List[str] = None,
    ) -> bool:
        """
        Check if a file should be ignored

        Args:
            file_path: Path to check
            include_patterns: Patterns of files to include
            exclude_patterns: Patterns of files to exclude

        Returns:
            True if the file should be ignored, False otherwise
        """
        file_path = Path(file_path)
        include_patterns = include_patterns or ["**/*"]
        exclude_patterns = exclude_patterns or []

        # Convert file path to string
        file_path_str = str(file_path).replace("\\", "/")

        # Convert glob patterns to regex
        include_regexes = [FileUtils._glob_to_regex(p) for p in include_patterns]
        exclude_regexes = [FileUtils._glob_to_regex(p) for p in exclude_patterns]

        # Check if file matches exclude pattern or doesn't match include pattern
        if any(r.search(file_path_str) for r in exclude_regexes):
            return True

        if not any(r.search(file_path_str) for r in include_regexes):
            return True

        return False

    @staticmethod
    def _glob_to_regex(pattern: str) -> Pattern:
        """
        Convert a glob pattern to a regex pattern

        Args:
            pattern: Glob pattern (e.g., "**/*.py")

        Returns:
            Compiled regex pattern
        """
        # Convert ** to a special marker
        pattern = pattern.replace("**", "__DOUBLE_STAR__")

        # Convert * to match anything except directory separator
        pattern = pattern.replace("*", "[^/]*")

        # Convert back ** to match anything including directory separators
        pattern = pattern.replace("__DOUBLE_STAR__", ".*")

        # Convert ? to match any character except directory separator
        pattern = pattern.replace("?", "[^/]")

        # Convert . to escape it in regex
        pattern = pattern.replace(".", "\\.")

        # Ensure the pattern matches the entire string
        pattern = f"^{pattern}$"

        return re.compile(pattern)


class TextUtils:
    """
    Utilities for text processing
    """

    @staticmethod
    def get_lines_around(content: str, line: int, context: int = 2) -> str:
        """
        Get lines around a specific line with context

        Args:
            content: Text content
            line: Line number (1-indexed)
            context: Number of lines of context before and after

        Returns:
            Text with context lines
        """
        lines = content.splitlines()

        start = max(0, line - context - 1)
        end = min(len(lines), line + context)

        return "\n".join(lines[start:end])

    @staticmethod
    def get_indentation(line: str) -> str:
        """
        Get the indentation prefix of a line

        Args:
            line: Line of text

        Returns:
            Indentation string
        """
        match = re.match(r"^(\s*)", line)
        return match.group(1) if match else ""
