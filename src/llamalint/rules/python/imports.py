"""
Rule for checking Python imports
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Set

from llamalint.rules.base import Rule, RuleOption, RuleResult


class ImportsRule(Rule):
    """
    Rule for checking Python imports
    """

    id = "python-imports"
    name = "Python Imports"
    description = "Enforces import standards for Python code"
    languages = ["python"]
    file_patterns = ["**/*.py"]
    default_severity = "warning"

    options = {
        "check_order": RuleOption(
            name="check_order",
            description="Check that imports are properly ordered",
            default=True,
        ),
        "require_absolute_imports": RuleOption(
            name="require_absolute_imports",
            description="Require absolute imports instead of relative imports",
            default=False,
        ),
        "allow_unused_imports": RuleOption(
            name="allow_unused_imports",
            description="Allow unused imports",
            default=False,
        ),
        "max_import_line_length": RuleOption(
            name="max_import_line_length",
            description="Maximum line length for a single import",
            default=100,
        ),
    }

    examples = [
        {
            "invalid": "import sys, os\nfrom math import *",
            "valid": "import os\nimport sys\n\nfrom math import sqrt, sin",
            "explanation": "Imports should be on separate lines, sorted alphabetically, and star imports should be avoided",
        },
        {
            "invalid": "import module1\nimport sys\nimport os",
            "valid": "import os\nimport sys\n\nimport module1",
            "explanation": "Standard library imports should come before third-party imports",
        },
    ]

    def check(self, file_path: Path, content: str) -> List[RuleResult]:
        """
        Check for import issues

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

        # Get lines
        lines = content.splitlines()

        # Find all imports
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(node)

                # Check for multi-import statements
                if isinstance(node, ast.Import) and len(node.names) > 1:
                    # Multi-import statement like "import os, sys"
                    results.append(
                        RuleResult(
                            rule_id=self.id,
                            file_path=str(file_path),
                            line=node.lineno,
                            column=node.col_offset,
                            message="Multiple modules imported on one line",
                            severity=self.severity,
                            source=lines[node.lineno - 1],
                            fix=self._fix_multi_import(node, lines[node.lineno - 1]),
                            fix_type="replace_line",
                        )
                    )

                # Check for wildcard imports
                if isinstance(node, ast.ImportFrom) and any(
                    name.name == "*" for name in node.names
                ):
                    results.append(
                        RuleResult(
                            rule_id=self.id,
                            file_path=str(file_path),
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Wildcard import from {node.module}",
                            severity=self.severity,
                            source=lines[node.lineno - 1],
                        )
                    )

                # Check for relative imports if not allowed
                if (
                    isinstance(node, ast.ImportFrom)
                    and node.level > 0
                    and self.get_option("require_absolute_imports")
                ):
                    results.append(
                        RuleResult(
                            rule_id=self.id,
                            file_path=str(file_path),
                            line=node.lineno,
                            column=node.col_offset,
                            message="Relative import used",
                            severity=self.severity,
                            source=lines[node.lineno - 1],
                        )
                    )

                # Check import line length
                if len(lines[node.lineno - 1]) > self.get_option(
                    "max_import_line_length"
                ):
                    results.append(
                        RuleResult(
                            rule_id=self.id,
                            file_path=str(file_path),
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Import line too long ({len(lines[node.lineno - 1])} > {self.get_option('max_import_line_length')})",
                            severity=self.severity,
                            source=lines[node.lineno - 1],
                        )
                    )

        # Check import order if enabled
        if self.get_option("check_order") and len(imports) > 1:
            prev_import = imports[0]
            for import_node in imports[1:]:
                # Check if imports are out of order
                if not self._is_proper_order(prev_import, import_node):
                    results.append(
                        RuleResult(
                            rule_id=self.id,
                            file_path=str(file_path),
                            line=import_node.lineno,
                            column=import_node.col_offset,
                            message="Imports not in proper order",
                            severity=self.severity,
                            source="\n".join(
                                lines[prev_import.lineno - 1 : import_node.lineno]
                            ),
                        )
                    )

                prev_import = import_node

        # Check for unused imports if enabled
        if not self.get_option("allow_unused_imports"):
            # Get all import names
            imported_names = set()
            for node in imports:
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imported_names.add(name.asname or name.name)
                elif isinstance(node, ast.ImportFrom):
                    for name in node.names:
                        if name.name != "*":  # Skip wildcards
                            imported_names.add(name.asname or name.name)

            # Get all names used in the code
            used_names = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    used_names.add(node.id)
                elif isinstance(node, ast.Attribute):
                    # Handle attribute access like "module.function"
                    if isinstance(node.value, ast.Name):
                        used_names.add(node.value.id)

            # Find unused imports
            for node in imports:
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imported_name = name.asname or name.name
                        # Check if import is used
                        if (
                            imported_name not in used_names
                            and imported_name in imported_names
                        ):
                            results.append(
                                RuleResult(
                                    rule_id=self.id,
                                    file_path=str(file_path),
                                    line=node.lineno,
                                    column=node.col_offset,
                                    message=f"Unused import: {imported_name}",
                                    severity=self.severity,
                                    source=lines[node.lineno - 1],
                                )
                            )
                elif isinstance(node, ast.ImportFrom):
                    # Skip if it's a __future__ import
                    if node.module == "__future__":
                        continue

                    for name in node.names:
                        if name.name == "*":  # Skip wildcards
                            continue

                        imported_name = name.asname or name.name
                        # Check if import is used
                        if (
                            imported_name not in used_names
                            and imported_name in imported_names
                        ):
                            results.append(
                                RuleResult(
                                    rule_id=self.id,
                                    file_path=str(file_path),
                                    line=node.lineno,
                                    column=node.col_offset,
                                    message=f"Unused import: {node.module}.{imported_name}",
                                    severity=self.severity,
                                    source=lines[node.lineno - 1],
                                )
                            )

        return results

    def _is_proper_order(self, prev_import: ast.AST, current_import: ast.AST) -> bool:
        """
        Check if imports are in proper order

        Args:
            prev_import: Previous import node
            current_import: Current import node

        Returns:
            True if imports are in proper order, False otherwise
        """
        # Future imports should always come first
        if (
            isinstance(current_import, ast.ImportFrom)
            and current_import.module == "__future__"
        ):
            if not (
                isinstance(prev_import, ast.ImportFrom)
                and prev_import.module == "__future__"
            ):
                return False

        # Standard library imports > third-party imports > local imports
        if isinstance(prev_import, ast.Import) and isinstance(
            current_import, ast.Import
        ):
            # Both are 'import' statements
            if (
                prev_import.names[0].name.split(".")[0]
                > current_import.names[0].name.split(".")[0]
            ):
                return False
        elif isinstance(prev_import, ast.ImportFrom) and isinstance(
            current_import, ast.ImportFrom
        ):
            # Both are 'from' statements
            if prev_import.module and current_import.module:
                if (
                    prev_import.module.split(".")[0]
                    > current_import.module.split(".")[0]
                ):
                    return False
        elif isinstance(prev_import, ast.Import) and isinstance(
            current_import, ast.ImportFrom
        ):
            # 'import' statements should come before 'from' statements for the same module
            if (
                prev_import.names[0].name.split(".")[0]
                == current_import.module.split(".")[0]
            ):
                return False

        return True

    def _fix_multi_import(self, node: ast.Import, line: str) -> str:
        """
        Fix a multi-import statement

        Args:
            node: Import node
            line: Line containing the import

        Returns:
            Fixed import statements
        """
        indentation = " " * node.col_offset
        return "\n".join(f"{indentation}import {name.name}" for name in node.names)
