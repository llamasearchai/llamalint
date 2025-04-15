"""
Rule for checking Python docstrings
"""

import ast
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from llamalint.rules.base import Rule, RuleOption, RuleResult


class DocstringsRule(Rule):
    """
    Rule for checking Python docstrings
    """

    id = "python-docstrings"
    name = "Python Docstrings"
    description = "Enforces docstring standards for Python code"
    languages = ["python"]
    file_patterns = ["**/*.py"]
    default_severity = "warning"

    options = {
        "required_modules": RuleOption(
            name="required_modules",
            description="Whether module docstrings are required",
            default=True,
        ),
        "required_classes": RuleOption(
            name="required_classes",
            description="Whether class docstrings are required",
            default=True,
        ),
        "required_methods": RuleOption(
            name="required_methods",
            description="Whether method and function docstrings are required",
            default=True,
        ),
        "ignore_private": RuleOption(
            name="ignore_private",
            description="Whether to ignore private methods (starting with _)",
            default=True,
        ),
        "ignore_dunder": RuleOption(
            name="ignore_dunder",
            description="Whether to ignore dunder methods (like __init__)",
            default=True,
        ),
        "ignore_test_methods": RuleOption(
            name="ignore_test_methods",
            description="Whether to ignore test methods (starting with test_)",
            default=True,
        ),
        "style": RuleOption(
            name="style",
            description="Docstring style to enforce",
            default="google",
            choices=["google", "sphinx", "numpy", "any"],
        ),
    }

    examples = [
        {
            "invalid": "def calculate_total(items, tax_rate):\n    total = sum(items)\n    return total * (1 + tax_rate)",
            "valid": 'def calculate_total(items, tax_rate):\n    """Calculate the total cost with tax.\n    \n    Args:\n        items: List of item prices\n        tax_rate: The tax rate as a decimal\n        \n    Returns:\n        Total cost including tax\n    """\n    total = sum(items)\n    return total * (1 + tax_rate)',
            "explanation": "Functions should have docstrings describing parameters and return values",
        },
        {
            "invalid": "class User:\n    def __init__(self, name, email):\n        self.name = name\n        self.email = email",
            "valid": 'class User:\n    """User class representing app users.\n    \n    Attributes:\n        name: The user\'s full name\n        email: The user\'s email address\n    """\n    \n    def __init__(self, name, email):\n        """Initialize a new User.\n        \n        Args:\n            name: User\'s full name\n            email: User\'s email address\n        """\n        self.name = name\n        self.email = email',
            "explanation": "Classes should have docstrings describing their purpose and attributes",
        },
    ]

    def check(self, file_path: Path, content: str) -> List[RuleResult]:
        """
        Check the file for docstring issues

        Args:
            file_path: Path to the file
            content: File content

        Returns:
            List of rule results
        """
        results = []

        # Parse the file
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            # Skip files with syntax errors
            return [
                RuleResult(
                    rule_id=self.id,
                    file_path=str(file_path),
                    line=e.lineno or 0,
                    column=e.offset or 0,
                    message=f"Syntax error: {e}",
                    severity=self.severity,
                )
            ]

        # Get line offsets for accurate line numbers
        line_offsets = [0]
        for line in content.splitlines(True):
            line_offsets.append(line_offsets[-1] + len(line))

        # Check module docstring
        if self.get_option("required_modules") and not ast.get_docstring(tree):
            results.append(
                RuleResult(
                    rule_id=self.id,
                    file_path=str(file_path),
                    line=1,
                    column=0,
                    message="Module lacks a docstring",
                    severity=self.severity,
                    source=self._get_source_lines(content, 1, 3),
                    fix='"""Module docstring.\n\nAdd a description of this module here.\n"""\n\n',
                    fix_type="replace_line",
                )
            )

        # Check class docstrings
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                self._check_class_docstring(
                    node, content, file_path, line_offsets, results
                )
            elif isinstance(node, ast.FunctionDef):
                self._check_function_docstring(
                    node, content, file_path, line_offsets, results
                )

        return results

    def _check_class_docstring(
        self,
        node: ast.ClassDef,
        content: str,
        file_path: Path,
        line_offsets: List[int],
        results: List[RuleResult],
    ) -> None:
        """
        Check a class for docstring issues

        Args:
            node: AST class node
            content: File content
            file_path: Path to the file
            line_offsets: Line offsets for accurate line numbers
            results: List to append results to
        """
        if not self.get_option("required_classes"):
            return

        # Get the docstring
        docstring = ast.get_docstring(node)

        if not docstring:
            # Find the first line after class definition to insert the docstring
            # Get the class source code
            source_lines = self._get_source_lines(content, node.lineno, node.lineno + 1)

            results.append(
                RuleResult(
                    rule_id=self.id,
                    file_path=str(file_path),
                    line=node.lineno,
                    column=node.col_offset,
                    message=f"Class '{node.name}' lacks a docstring",
                    severity=self.severity,
                    source=source_lines,
                    fix=f'    """{node.name} class.\n    \n    Add a description of this class here.\n    """',
                    fix_type="replace_line",
                )
            )
        else:
            # Check docstring style
            style_issues = self._check_docstring_style(docstring, "class")
            if style_issues and self.get_option("style") != "any":
                results.append(
                    RuleResult(
                        rule_id=self.id,
                        file_path=str(file_path),
                        line=node.lineno,
                        column=node.col_offset,
                        message=f"Class '{node.name}' docstring style issues: {', '.join(style_issues)}",
                        severity=self.severity,
                        source=self._get_source_lines(
                            content, node.lineno, node.lineno + 3
                        ),
                    )
                )

    def _check_function_docstring(
        self,
        node: ast.FunctionDef,
        content: str,
        file_path: Path,
        line_offsets: List[int],
        results: List[RuleResult],
    ) -> None:
        """
        Check a function for docstring issues

        Args:
            node: AST function node
            content: File content
            file_path: Path to the file
            line_offsets: Line offsets for accurate line numbers
            results: List to append results to
        """
        if not self.get_option("required_methods"):
            return

        # Check if this is a method we should ignore
        if self._should_ignore_function(node):
            return

        # Get the docstring
        docstring = ast.get_docstring(node)

        if not docstring:
            # Get the function source code
            source_lines = self._get_source_lines(content, node.lineno, node.lineno + 1)

            # Generate a fix with function parameters in docstring
            indentation = " " * node.col_offset
            params = []
            returns_annotation = None

            for arg in node.args.args:
                if arg.arg != "self" and arg.arg != "cls":
                    params.append(f"{arg.arg}: Description")

            if node.returns:
                returns_annotation = "Value"

            # Create the docstring
            docstring_lines = [
                f'{indentation}    """Function description.',
                f"{indentation}    ",
            ]

            if params:
                docstring_lines.append(f"{indentation}    Args:")
                for param in params:
                    docstring_lines.append(f"{indentation}        {param}")
                docstring_lines.append(f"{indentation}    ")

            if returns_annotation:
                docstring_lines.append(f"{indentation}    Returns:")
                docstring_lines.append(f"{indentation}        {returns_annotation}")
                docstring_lines.append(f"{indentation}    ")

            docstring_lines.append(f'{indentation}    """')

            fixed_docstring = "\n".join(docstring_lines)

            results.append(
                RuleResult(
                    rule_id=self.id,
                    file_path=str(file_path),
                    line=node.lineno,
                    column=node.col_offset,
                    message=f"Function '{node.name}' lacks a docstring",
                    severity=self.severity,
                    source=source_lines,
                    fix=fixed_docstring,
                    fix_type="replace_line",
                )
            )
        else:
            # Check docstring style
            style_issues = self._check_docstring_style(docstring, "function")
            if style_issues and self.get_option("style") != "any":
                results.append(
                    RuleResult(
                        rule_id=self.id,
                        file_path=str(file_path),
                        line=node.lineno,
                        column=node.col_offset,
                        message=f"Function '{node.name}' docstring style issues: {', '.join(style_issues)}",
                        severity=self.severity,
                        source=self._get_source_lines(
                            content, node.lineno, node.lineno + 3
                        ),
                    )
                )

    def _should_ignore_function(self, node: ast.FunctionDef) -> bool:
        """
        Check if a function should be ignored

        Args:
            node: AST function node

        Returns:
            True if the function should be ignored, False otherwise
        """
        # Check if it's a private method and we're ignoring those
        if (
            self.get_option("ignore_private")
            and node.name.startswith("_")
            and not node.name.startswith("__")
        ):
            return True

        # Check if it's a dunder method and we're ignoring those
        if (
            self.get_option("ignore_dunder")
            and node.name.startswith("__")
            and node.name.endswith("__")
        ):
            return True

        # Check if it's a test method and we're ignoring those
        if self.get_option("ignore_test_methods") and node.name.startswith("test_"):
            return True

        return False

    def _check_docstring_style(self, docstring: str, node_type: str) -> List[str]:
        """
        Check docstring style

        Args:
            docstring: The docstring to check
            node_type: The type of node ("class" or "function")

        Returns:
            List of style issues
        """
        style = self.get_option("style")
        issues = []

        if style == "google":
            # Check for Google style docstring sections
            if (
                node_type == "function"
                and "Args:" not in docstring
                and "Parameters:" not in docstring
            ):
                issues.append("missing Args/Parameters section")

            if (
                node_type == "function"
                and "Returns:" not in docstring
                and "Yields:" not in docstring
            ):
                # Only flag missing Returns if there isn't a Yields section
                issues.append("missing Returns/Yields section")

            if node_type == "class" and "Attributes:" not in docstring:
                issues.append("missing Attributes section")

        elif style == "sphinx":
            # Check for Sphinx style docstring parameters
            if node_type == "function" and ":param" not in docstring:
                issues.append("missing :param directives")

            if node_type == "function" and ":return:" not in docstring:
                issues.append("missing :return: directive")

        elif style == "numpy":
            # Check for NumPy style docstring sections
            if node_type == "function" and "Parameters\n---------" not in docstring:
                issues.append("missing Parameters section")

            if node_type == "function" and "Returns\n-------" not in docstring:
                issues.append("missing Returns section")

        return issues

    def _get_source_lines(self, content: str, start_line: int, end_line: int) -> str:
        """
        Get a range of source lines

        Args:
            content: File content
            start_line: Start line number (1-indexed)
            end_line: End line number (1-indexed, inclusive)

        Returns:
            Source lines as a string
        """
        lines = content.splitlines()
        start_idx = max(0, start_line - 1)
        end_idx = min(len(lines), end_line)

        return "\n".join(lines[start_idx:end_idx])
