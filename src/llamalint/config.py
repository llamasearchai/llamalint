"""
Configuration management for LlamaLint
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

import toml
import yaml


class Config:
    """
    LlamaLint configuration handler
    """

    def __init__(
        self,
        include: List[str] = None,
        exclude: List[str] = None,
        disabled_rules: List[str] = None,
        disabled_formatters: List[str] = None,
        rule_severity: Dict[str, str] = None,
        rule_configs: Dict[str, Dict[str, Any]] = None,
        formatter_configs: Dict[str, Dict[str, Any]] = None,
    ):
        """
        Initialize a configuration

        Args:
            include: Patterns of files to include
            exclude: Patterns of files to exclude
            disabled_rules: List of rule IDs to disable
            disabled_formatters: List of formatter IDs to disable
            rule_severity: Map of rule IDs to severity levels
            rule_configs: Configuration for specific rules
            formatter_configs: Configuration for specific formatters
        """
        self.include = include or [
            "**/*.py",
            "**/*.js",
            "**/*.ts",
            "**/*.jsx",
            "**/*.tsx",
        ]
        self.exclude = exclude or [
            "**/node_modules/**",
            "**/.venv/**",
            "**/__pycache__/**",
            "**/dist/**",
            "**/build/**",
        ]
        self.disabled_rules = set(disabled_rules or [])
        self.disabled_formatters = set(disabled_formatters or [])
        self.rule_severity = rule_severity or {}
        self.rule_configs = rule_configs or {}
        self.formatter_configs = formatter_configs or {}

    @classmethod
    def create_default(cls) -> "Config":
        """
        Create a default configuration

        Returns:
            Default configuration
        """
        return cls()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """
        Create a configuration from a dictionary

        Args:
            data: Dictionary with configuration values

        Returns:
            Configuration instance
        """
        return cls(
            include=data.get("include"),
            exclude=data.get("exclude"),
            disabled_rules=data.get("disabled_rules"),
            disabled_formatters=data.get("disabled_formatters"),
            rule_severity=data.get("rule_severity"),
            rule_configs=data.get("rules", {}),
            formatter_configs=data.get("formatters", {}),
        )

    @classmethod
    def from_file(cls, path: Union[str, Path]) -> "Config":
        """
        Load a configuration from a file

        Args:
            path: Path to the configuration file

        Returns:
            Configuration instance

        Raises:
            FileNotFoundError: If the file does not exist
            ValueError: If the file format is not supported
        """
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")

        suffix = path.suffix.lower()

        if suffix == ".yaml" or suffix == ".yml":
            with open(path, "r") as f:
                data = yaml.safe_load(f)
        elif suffix == ".json":
            with open(path, "r") as f:
                data = json.load(f)
        elif suffix == ".toml":
            with open(path, "r") as f:
                data = toml.load(f)
        else:
            raise ValueError(f"Unsupported configuration file format: {suffix}")

        return cls.from_dict(data)

    @classmethod
    def find_and_load(cls) -> "Config":
        """
        Find and load a configuration file from the current directory or parents

        Returns:
            Configuration instance (defaults if no file found)
        """
        config_names = [
            ".llamalint.yaml",
            ".llamalint.yml",
            ".llamalint.json",
            ".llamalint.toml",
            "pyproject.toml",  # Look for [tool.llamalint] section
            "package.json",  # Look for llamalint key
        ]

        # Start from current directory and go up
        current_dir = Path.cwd()

        while current_dir != current_dir.parent:
            for name in config_names:
                config_path = current_dir / name

                if config_path.exists():
                    try:
                        if name == "pyproject.toml":
                            with open(config_path, "r") as f:
                                pyproject_data = toml.load(f)
                                if (
                                    "tool" in pyproject_data
                                    and "llamalint" in pyproject_data["tool"]
                                ):
                                    return cls.from_dict(
                                        pyproject_data["tool"]["llamalint"]
                                    )
                        elif name == "package.json":
                            with open(config_path, "r") as f:
                                package_data = json.load(f)
                                if "llamalint" in package_data:
                                    return cls.from_dict(package_data["llamalint"])
                        else:
                            return cls.from_file(config_path)
                    except Exception:
                        # If we can't load this file, try the next one
                        pass

            # Move up to parent directory
            current_dir = current_dir.parent

        # No config found, return default
        return cls.create_default()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the configuration to a dictionary

        Returns:
            Dictionary representation of the configuration
        """
        return {
            "include": self.include,
            "exclude": self.exclude,
            "disabled_rules": list(self.disabled_rules),
            "disabled_formatters": list(self.disabled_formatters),
            "rule_severity": self.rule_severity,
            "rules": self.rule_configs,
            "formatters": self.formatter_configs,
        }

    def to_json(self) -> str:
        """
        Convert the configuration to a JSON string

        Returns:
            JSON representation of the configuration
        """
        return json.dumps(self.to_dict(), indent=2)

    def to_yaml(self) -> str:
        """
        Convert the configuration to a YAML string

        Returns:
            YAML representation of the configuration
        """
        return yaml.dump(self.to_dict(), default_flow_style=False)

    def to_toml(self) -> str:
        """
        Convert the configuration to a TOML string

        Returns:
            TOML representation of the configuration
        """
        return toml.dumps(self.to_dict())

    def disable_rule(self, rule_id: str) -> None:
        """
        Disable a rule

        Args:
            rule_id: ID of the rule to disable
        """
        self.disabled_rules.add(rule_id)

    def enable_rule(self, rule_id: str) -> None:
        """
        Enable a rule

        Args:
            rule_id: ID of the rule to enable
        """
        if rule_id in self.disabled_rules:
            self.disabled_rules.remove(rule_id)

    def disable_formatter(self, formatter_id: str) -> None:
        """
        Disable a formatter

        Args:
            formatter_id: ID of the formatter to disable
        """
        self.disabled_formatters.add(formatter_id)

    def enable_formatter(self, formatter_id: str) -> None:
        """
        Enable a formatter

        Args:
            formatter_id: ID of the formatter to enable
        """
        if formatter_id in self.disabled_formatters:
            self.disabled_formatters.remove(formatter_id)

    def set_rule_severity(self, rule_id: str, severity: str) -> None:
        """
        Set the severity level for a rule

        Args:
            rule_id: ID of the rule
            severity: Severity level ('error', 'warning', 'info')
        """
        self.rule_severity[rule_id] = severity

    def ignore_rules(self, rule_ids: List[str]) -> None:
        """
        Ignore specific rules

        Args:
            rule_ids: List of rule IDs to ignore
        """
        for rule_id in rule_ids:
            self.disable_rule(rule_id)

    def set_rule_config(self, rule_id: str, options: Dict[str, Any]) -> None:
        """
        Set configuration options for a rule

        Args:
            rule_id: ID of the rule
            options: Configuration options
        """
        self.rule_configs[rule_id] = options

    def set_formatter_config(self, formatter_id: str, options: Dict[str, Any]) -> None:
        """
        Set configuration options for a formatter

        Args:
            formatter_id: ID of the formatter
            options: Configuration options
        """
        self.formatter_configs[formatter_id] = options
