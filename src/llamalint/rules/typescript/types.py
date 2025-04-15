"""
Rule for checking TypeScript types
"""

from pathlib import Path
from typing import List

from llamalint.rules.base import Rule, RuleOption, RuleResult


class TypesRule(Rule):
    """
    Rule for checking TypeScript type annotations
    """

    id = "typescript-types"
    name = "TypeScript Types"
    description = "Enforces TypeScript type annotation standards"
    languages = ["typescript"]
    file_patterns = ["**/*.ts", "**/*.tsx"]
    default_severity = "error"

    options = {
        "require_return_types": RuleOption(
            name="require_return_types",
            description="Require explicit return type annotations on functions",
            default=True,
        ),
        "require_parameter_types": RuleOption(
            name="require_parameter_types",
            description="Require explicit parameter type annotations",
            default=True,
        ),
        "no_any": RuleOption(
            name="no_any",
            description="Disallow use of the 'any' type",
            default=True,
        ),
        "prefer_interfaces": RuleOption(
            name="prefer_interfaces",
            description="Prefer interfaces over type aliases for object types",
            default=False,
        ),
    }

    examples = [
        {
            "invalid": 'function getData() {\n  return { id: 1, name: "test" };\n}',
            "valid": 'function getData(): { id: number; name: string } {\n  return { id: 1, name: "test" };\n}',
            "explanation": "Functions should have explicit return type annotations",
        },
        {
            "invalid": "function updateUser(user) {\n  // Update user\n}",
            "valid": "function updateUser(user: User): void {\n  // Update user\n}",
            "explanation": "Function parameters should have explicit type annotations",
        },
    ]

    def check(self, file_path: Path, content: str) -> List[RuleResult]:
        """
        Check for type annotation issues in TypeScript files

        Args:
            file_path: Path to the file
            content: File content

        Returns:
            List of rule results
        """
        # This is a stub implementation
        # Full implementation would parse the TypeScript file and check type annotations
        return []
