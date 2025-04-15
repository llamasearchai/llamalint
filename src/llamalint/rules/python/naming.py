"""
Rule for checking Python naming conventions
"""

from pathlib import Path
from typing import List

from llamalint.rules.base import Rule, RuleOption, RuleResult


class NamingConventionsRule(Rule):
    """
    Rule for checking Python naming conventions
    """

    id = "python-naming"
    name = "Python Naming Conventions"
    description = "Enforces naming conventions for Python code elements"
    languages = ["python"]
    file_patterns = ["**/*.py"]
    default_severity = "warning"

    options = {
        "class_style": RuleOption(
            name="class_style",
            description="Style for class names",
            default="PascalCase",
            choices=["PascalCase", "camelCase", "snake_case"],
        ),
        "function_style": RuleOption(
            name="function_style",
            description="Style for function names",
            default="snake_case",
            choices=["PascalCase", "camelCase", "snake_case"],
        ),
        "variable_style": RuleOption(
            name="variable_style",
            description="Style for variable names",
            default="snake_case",
            choices=["PascalCase", "camelCase", "snake_case"],
        ),
        "constant_style": RuleOption(
            name="constant_style",
            description="Style for constant names",
            default="UPPER_CASE",
            choices=["PascalCase", "camelCase", "snake_case", "UPPER_CASE"],
        ),
    }

    examples = [
        {
            "invalid": "class myClass:\n    pass",
            "valid": "class MyClass:\n    pass",
            "explanation": "Class names should be in PascalCase",
        },
        {
            "invalid": "def GetValue():\n    return 42",
            "valid": "def get_value():\n    return 42",
            "explanation": "Function names should be in snake_case",
        },
    ]

    def check(self, file_path: Path, content: str) -> List[RuleResult]:
        """
        Check the file for naming convention issues

        Args:
            file_path: Path to the file
            content: File content

        Returns:
            List of rule results
        """
        # This is a stub implementation
        # Full implementation would parse the file and check naming conventions
        return []
