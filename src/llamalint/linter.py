"""
Core linting engine for LlamaLint
"""

import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Set, Type, Union

from llamalint.config import Config
from llamalint.formatters import Formatter
from llamalint.rules import Rule, RuleResult
from llamalint.utils import FileUtils


class LlamaLint:
    """
    Main linting engine that coordinates rules and formatters
    """

    def __init__(self, config: Config):
        """
        Initialize the linter with a configuration

        Args:
            config: Configuration for the linter
        """
        self.config = config
        self._rules = {}
        self._formatters = {}

        # Load rules and formatters
        self._load_rules()
        self._load_formatters()

    @classmethod
    def from_config(cls, config_path: Union[str, Path]) -> "LlamaLint":
        """
        Create a linter from a configuration file

        Args:
            config_path: Path to the configuration file

        Returns:
            Configured LlamaLint instance
        """
        config = Config.from_file(config_path)
        return cls(config)

    @classmethod
    def auto_config(cls) -> "LlamaLint":
        """
        Create a linter by automatically detecting a configuration file

        Returns:
            Configured LlamaLint instance
        """
        config = Config.find_and_load()
        return cls(config)

    def _load_rules(self) -> None:
        """
        Load all rules based on configuration
        """
        from llamalint.rules import get_all_rules

        all_rules = get_all_rules()

        # Filter and configure rules based on config
        for rule_cls in all_rules:
            rule_id = rule_cls.id

            # Skip disabled rules
            if rule_id in self.config.disabled_rules:
                continue

            # Create and configure rule
            rule_config = self.config.rule_configs.get(rule_id, {})
            rule = rule_cls(config=rule_config)

            # Override severity if specified in config
            if rule_id in self.config.rule_severity:
                rule.severity = self.config.rule_severity[rule_id]

            self._rules[rule_id] = rule

    def _load_formatters(self) -> None:
        """
        Load all formatters based on configuration
        """
        from llamalint.formatters import get_all_formatters

        all_formatters = get_all_formatters()

        # Filter and configure formatters based on config
        for formatter_cls in all_formatters:
            formatter_id = formatter_cls.id

            # Skip disabled formatters
            if formatter_id in self.config.disabled_formatters:
                continue

            # Create and configure formatter
            formatter_config = self.config.formatter_configs.get(formatter_id, {})
            formatter = formatter_cls(config=formatter_config)

            self._formatters[formatter_id] = formatter

    def get_available_rules(self) -> List[Rule]:
        """
        Get all available rules

        Returns:
            List of rule instances
        """
        return list(self._rules.values())

    def get_rule(self, rule_id: str) -> Optional[Rule]:
        """
        Get a specific rule by ID

        Args:
            rule_id: ID of the rule to retrieve

        Returns:
            Rule instance or None if not found
        """
        return self._rules.get(rule_id)

    def get_formatter(self, formatter_id: str) -> Optional[Formatter]:
        """
        Get a specific formatter by ID

        Args:
            formatter_id: ID of the formatter to retrieve

        Returns:
            Formatter instance or None if not found
        """
        return self._formatters.get(formatter_id)

    def lint_file(
        self, file_path: Union[str, Path], fix: bool = False
    ) -> List[RuleResult]:
        """
        Lint a single file

        Args:
            file_path: Path to the file to lint
            fix: Whether to apply fixes

        Returns:
            List of rule results
        """
        file_path = Path(file_path)

        # Skip if file is ignored
        if self._is_ignored(file_path):
            return []

        # Get the file content
        try:
            content = file_path.read_text()
        except Exception as e:
            return [
                RuleResult(
                    rule_id="file-error",
                    file_path=str(file_path),
                    line=0,
                    column=0,
                    message=f"Error reading file: {e}",
                    severity="error",
                )
            ]

        # Get file extension
        extension = file_path.suffix.lstrip(".")

        # Find applicable rules for this file type
        applicable_rules = []
        for rule in self._rules.values():
            # Check if rule applies to this file type
            if rule.applies_to_file(file_path):
                applicable_rules.append(rule)

        # Apply rules
        results = []
        for rule in applicable_rules:
            try:
                rule_results = rule.check(file_path, content)
                results.extend(rule_results)
            except Exception as e:
                # Rule execution failed
                results.append(
                    RuleResult(
                        rule_id=rule.id,
                        file_path=str(file_path),
                        line=0,
                        column=0,
                        message=f"Rule execution error: {e}",
                        severity="error",
                    )
                )

        # Apply fixes if requested
        if fix and results:
            content = self._apply_fixes(file_path, content, results)
            file_path.write_text(content)

            # Re-run to check remaining issues
            remaining_results = []
            for rule in applicable_rules:
                try:
                    rule_results = rule.check(file_path, content)
                    remaining_results.extend(rule_results)
                except Exception:
                    # Skip rules that failed after fixing
                    pass

            results = remaining_results

        return results

    def lint_directory(
        self, directory: Union[str, Path], fix: bool = False
    ) -> List[RuleResult]:
        """
        Lint all files in a directory

        Args:
            directory: Path to the directory to lint
            fix: Whether to apply fixes

        Returns:
            List of rule results
        """
        directory = Path(directory)

        # Skip if directory doesn't exist
        if not directory.exists() or not directory.is_dir():
            return [
                RuleResult(
                    rule_id="directory-error",
                    file_path=str(directory),
                    line=0,
                    column=0,
                    message=f"Directory not found: {directory}",
                    severity="error",
                )
            ]

        # Get all files
        all_files = FileUtils.find_files(
            directory,
            include_patterns=self.config.include,
            exclude_patterns=self.config.exclude,
        )

        # Lint each file
        results = []
        for file_path in all_files:
            file_results = self.lint_file(file_path, fix=fix)
            results.extend(file_results)

        return results

    def format_file(self, file_path: Union[str, Path]) -> str:
        """
        Format a file using the configured formatters

        Args:
            file_path: Path to the file to format

        Returns:
            Formatted content
        """
        file_path = Path(file_path)

        # Skip if file is ignored
        if self._is_ignored(file_path):
            return file_path.read_text()

        # Get the file content
        content = file_path.read_text()

        # Find applicable formatters for this file type
        applicable_formatters = []
        for formatter in self._formatters.values():
            # Check if formatter applies to this file type
            if formatter.applies_to_file(file_path):
                applicable_formatters.append(formatter)

        # Sort formatters by priority
        applicable_formatters.sort(key=lambda f: f.priority)

        # Apply formatters in sequence
        formatted_content = content
        for formatter in applicable_formatters:
            formatted_content = formatter.format(file_path, formatted_content)

        return formatted_content

    def _is_ignored(self, file_path: Path) -> bool:
        """
        Check if a file should be ignored based on the configuration

        Args:
            file_path: Path to check

        Returns:
            True if the file should be ignored, False otherwise
        """
        return FileUtils.is_ignored(
            file_path,
            include_patterns=self.config.include,
            exclude_patterns=self.config.exclude,
        )

    def _apply_fixes(
        self, file_path: Path, content: str, results: List[RuleResult]
    ) -> str:
        """
        Apply fixes to file content

        Args:
            file_path: Path to the file
            content: Original file content
            results: Rule results with fixes

        Returns:
            Fixed content
        """
        # Get results with fixes
        fixable_results = [r for r in results if r.fix is not None]

        # Sort by position in reverse order to avoid invalidating positions
        fixable_results.sort(key=lambda r: (r.line, r.column), reverse=True)

        # Apply fixes
        lines = content.splitlines(True)  # Keep line endings

        for result in fixable_results:
            if result.fix and result.line > 0 and result.line <= len(lines):
                line_idx = result.line - 1
                line = lines[line_idx]

                if result.fix_type == "replace_line":
                    lines[line_idx] = result.fix
                elif result.fix_type == "replace_range":
                    if result.fix_range:
                        start_col, end_col = result.fix_range
                        lines[line_idx] = line[:start_col] + result.fix + line[end_col:]

        return "".join(lines)

    def results_to_xml(self, results: List[RuleResult]) -> str:
        """
        Convert rule results to XML format (compatible with CI tools)

        Args:
            results: Rule results to convert

        Returns:
            XML representation of the results
        """
        root = ET.Element("results")

        for result in results:
            issue = ET.SubElement(root, "issue")
            issue.set("rule_id", result.rule_id)
            issue.set("severity", result.severity)
            issue.set("file", result.file_path)
            issue.set("line", str(result.line))
            issue.set("column", str(result.column))
            issue.text = result.message

        return ET.tostring(root, encoding="unicode")
