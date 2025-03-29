"""
Command-line interface for LlamaLint
"""
import os
import sys
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from llamalint import __version__
from llamalint.linter import LlamaLint
from llamalint.config import Config

app = typer.Typer(help="LlamaLint - Code linting and formatting tools for LlamaSearch.ai projects")
console = Console()

# Create subcommands
format_app = typer.Typer(help="Format files")
check_app = typer.Typer(help="Check files for issues without fixing")
rules_app = typer.Typer(help="Manage linting rules")
app.add_typer(format_app, name="format")
app.add_typer(check_app, name="check")
app.add_typer(rules_app, name="rules")


def version_callback(value: bool):
    """Print version information and exit"""
    if value:
        console.print(f"LlamaLint version: {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", callback=version_callback, is_eager=True, 
        help="Show version information and exit"
    ),
    config_file: Optional[str] = typer.Option(
        None, "--config", "-c", help="Path to configuration file"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", help="Enable verbose output"
    ),
):
    """
    LlamaLint - Code linting and formatting tools for LlamaSearch.ai projects
    """
    # Store context values
    ctx.obj = {
        "verbose": verbose,
        "config_file": config_file,
    }


@app.command()
def init(
    directory: str = typer.Argument(
        ".", help="Directory to initialize configuration in"
    ),
    config_format: str = typer.Option(
        "yaml", "--format", "-f", help="Configuration file format (yaml, json, toml)"
    ),
):
    """
    Initialize a new LlamaLint configuration file
    """
    path = Path(directory) / f".llamalint.{config_format}"
    
    if path.exists():
        overwrite = typer.confirm(f"{path} already exists. Overwrite?", default=False)
        if not overwrite:
            console.print("Initialization cancelled.")
            return
    
    # Create a default configuration
    config = Config.create_default()
    
    # Write the configuration to file
    with open(path, "w") as f:
        if config_format == "yaml":
            f.write(config.to_yaml())
        elif config_format == "json":
            f.write(config.to_json())
        elif config_format == "toml":
            f.write(config.to_toml())
        else:
            console.print(f"[red]Unsupported format: {config_format}")
            raise typer.Exit(1)
    
    console.print(f"[green]Created configuration file: {path}")


@app.command()
def lint(
    ctx: typer.Context,
    paths: List[str] = typer.Argument(
        None, help="Files or directories to lint"
    ),
    fix: bool = typer.Option(
        False, "--fix", help="Automatically fix issues where possible"
    ),
    ignore: List[str] = typer.Option(
        [], "--ignore", "-i", help="Rules to ignore"
    ),
    output_format: str = typer.Option(
        "text", "--format", "-f", help="Output format (text, json, xml)"
    ),
):
    """
    Lint files and directories
    """
    if not paths:
        paths = ["."]
    
    # Initialize the linter
    config_file = ctx.obj.get("config_file")
    verbose = ctx.obj.get("verbose", False)
    
    try:
        if config_file:
            linter = LlamaLint.from_config(config_file)
        else:
            # Look for config in current directory or parent directories
            linter = LlamaLint.auto_config()
            
        # Override ignored rules if specified
        if ignore:
            linter.config.ignore_rules(ignore)
            
        # Process each path
        all_results = []
        for path in paths:
            path_obj = Path(path)
            
            if path_obj.is_file():
                if verbose:
                    console.print(f"Linting file: {path}")
                results = linter.lint_file(path, fix=fix)
                all_results.extend(results)
            elif path_obj.is_dir():
                if verbose:
                    console.print(f"Linting directory: {path}")
                results = linter.lint_directory(path, fix=fix)
                all_results.extend(results)
            else:
                console.print(f"[yellow]Warning: {path} is not a file or directory")
        
        # Output results
        if output_format == "json":
            console.print_json(data=[r.to_dict() for r in all_results])
        elif output_format == "xml":
            xml_output = linter.results_to_xml(all_results)
            console.print(xml_output)
        else:
            # Text output (default)
            if not all_results:
                console.print("[green]No issues found")
            else:
                error_count = sum(1 for r in all_results if r.severity == "error")
                warning_count = sum(1 for r in all_results if r.severity == "warning")
                
                console.print(f"Found [bold red]{error_count}[/] errors and [bold yellow]{warning_count}[/] warnings")
                
                for result in all_results:
                    color = "red" if result.severity == "error" else "yellow"
                    console.print(f"[{color}]{result.rule_id}[/]: {result.message}")
                    console.print(f"  [dim]{result.file_path}:{result.line}:{result.column}[/]")
                    
                    if result.source:
                        syntax = Syntax(result.source, "python", line_numbers=True, start_line=max(1, result.line - 2), highlight_lines=[result.line])
                        console.print(Panel(syntax, expand=False))
        
        # Exit with error code if issues were found
        if any(r.severity == "error" for r in all_results):
            raise typer.Exit(1)
            
    except Exception as e:
        console.print(f"[red]Error: {e}")
        if verbose:
            import traceback
            console.print(traceback.format_exc())
        raise typer.Exit(1)


@format_app.command("file")
def format_file(
    ctx: typer.Context,
    file_path: str = typer.Argument(..., help="File to format"),
    output: Optional[str] = typer.Option(
        None, "--output", "-o", help="Output file (default: overwrite input)"
    ),
):
    """
    Format a single file
    """
    config_file = ctx.obj.get("config_file")
    verbose = ctx.obj.get("verbose", False)
    
    try:
        if config_file:
            linter = LlamaLint.from_config(config_file)
        else:
            linter = LlamaLint.auto_config()
            
        formatted_content = linter.format_file(file_path)
        
        if output:
            with open(output, "w") as f:
                f.write(formatted_content)
            console.print(f"[green]Formatted {file_path} and saved to {output}")
        else:
            with open(file_path, "w") as f:
                f.write(formatted_content)
            console.print(f"[green]Formatted {file_path}")
            
    except Exception as e:
        console.print(f"[red]Error formatting {file_path}: {e}")
        if verbose:
            import traceback
            console.print(traceback.format_exc())
        raise typer.Exit(1)


@rules_app.command("list")
def list_rules(
    ctx: typer.Context,
    language: Optional[str] = typer.Option(
        None, "--language", "-l", help="Filter rules by language"
    ),
    severity: Optional[str] = typer.Option(
        None, "--severity", "-s", help="Filter rules by severity"
    ),
):
    """
    List available rules
    """
    config_file = ctx.obj.get("config_file")
    
    try:
        if config_file:
            linter = LlamaLint.from_config(config_file)
        else:
            linter = LlamaLint.auto_config()
            
        rules = linter.get_available_rules()
        
        if language:
            rules = [r for r in rules if language in r.languages]
            
        if severity:
            rules = [r for r in rules if r.default_severity == severity]
            
        console.print("[bold]Available Rules[/]")
        console.print()
        
        for rule in rules:
            languages_str = ", ".join(rule.languages)
            severity_color = "red" if rule.default_severity == "error" else "yellow"
            
            console.print(f"[bold]{rule.id}[/]")
            console.print(f"  Description: {rule.description}")
            console.print(f"  Languages: {languages_str}")
            console.print(f"  Severity: [{severity_color}]{rule.default_severity}[/]")
            console.print()
            
    except Exception as e:
        console.print(f"[red]Error: {e}")
        if ctx.obj.get("verbose", False):
            import traceback
            console.print(traceback.format_exc())
        raise typer.Exit(1)


@rules_app.command("show")
def show_rule(
    ctx: typer.Context,
    rule_id: str = typer.Argument(..., help="Rule ID to show details for"),
):
    """
    Show details for a specific rule
    """
    config_file = ctx.obj.get("config_file")
    
    try:
        if config_file:
            linter = LlamaLint.from_config(config_file)
        else:
            linter = LlamaLint.auto_config()
            
        rule = linter.get_rule(rule_id)
        
        if not rule:
            console.print(f"[red]Rule not found: {rule_id}")
            raise typer.Exit(1)
            
        severity_color = "red" if rule.default_severity == "error" else "yellow"
        languages_str = ", ".join(rule.languages)
        
        console.print(f"[bold]{rule.id}[/]")
        console.print(f"Description: {rule.description}")
        console.print(f"Languages: {languages_str}")
        console.print(f"Severity: [{severity_color}]{rule.default_severity}[/]")
        
        if rule.options:
            console.print("\n[bold]Options:[/]")
            for name, option in rule.options.items():
                console.print(f"  {name}: {option.description}")
                console.print(f"    Default: {option.default}")
                if option.choices:
                    console.print(f"    Choices: {', '.join(str(c) for c in option.choices)}")
        
        if rule.examples:
            console.print("\n[bold]Examples:[/]")
            
            for i, example in enumerate(rule.examples):
                console.print(f"\nExample {i+1}:")
                
                if example.get("invalid"):
                    console.print("[bold red]Invalid code:[/]")
                    syntax = Syntax(example["invalid"], "python", theme="monokai")
                    console.print(syntax)
                    
                if example.get("valid"):
                    console.print("[bold green]Valid code:[/]")
                    syntax = Syntax(example["valid"], "python", theme="monokai")
                    console.print(syntax)
                    
                if example.get("explanation"):
                    console.print(f"Explanation: {example['explanation']}")
            
    except Exception as e:
        console.print(f"[red]Error: {e}")
        if ctx.obj.get("verbose", False):
            import traceback
            console.print(traceback.format_exc())
        raise typer.Exit(1)


if __name__ == "__main__":
    app() 