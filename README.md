# LlamaLint

Code linting and formatting tools for LlamaSearch.ai projects.

## Features

- **Custom Linting Rules**: Specialized rules for LlamaSearch.ai code standards
- **Auto-formatting**: Automatic code formatting according to project style guides
- **Multiple Language Support**: Supports Python, JavaScript, TypeScript, and more
- **Configuration Files**: Standard configuration files for different project types
- **IDE Integration**: Plugins for VS Code, PyCharm, and other popular IDEs
- **CI/CD Integration**: GitHub Actions workflows for automated linting
- **Rule Documentation**: Comprehensive documentation for all linting rules
- **Custom Rule Development**: Framework for developing custom rules
- **API Access**: Programmatic access to linting functionality
- **Project Templates**: Pre-configured templates for new projects

## Installation

### Using pip

```bash
pip install llamalint
```

### From source

```bash
git clone https://llamasearch.ai
cd llamalint
pip install -e .
```

## Quick Start

### Command Line Usage

```bash
# Lint a file
llamalint myfile.py

# Lint a directory
llamalint myproject/

# Auto-format a file
llamalint format myfile.py

# Generate a configuration file
llamalint init

# Check for rule violations without fixing
llamalint check myproject/

# List available rules
llamalint rules list

# Show rule documentation
llamalint rules show import-order
```

### Configuration

Create a `.llamalint.yaml` file in your project root:

```yaml
# Base configuration
extends: llamalint:recommended

# Exclude patterns
exclude:
  - "**/*.test.js"
  - "build/"
  - "dist/"

# Rule customization
rules:
  python:
    line-length: 88
    docstring-style: google
    import-order: alphabetical
  
  javascript:
    semicolons: true
    quotes: single
    
  typescript:
    strict-null-checks: true
    no-any: warning
```

## Supported Languages

### Python

- PEP 8 compliance
- Import ordering
- Docstring validation
- Type hint verification
- Security checks
- Code complexity analysis

### JavaScript/TypeScript

- ESLint rule compatibility
- React best practices
- TypeScript type checking
- Modern JavaScript features
- CommonJS vs ESM consistency

### YAML/JSON

- Schema validation
- Structure validation
- Documentation requirements

### Markdown

- Link checking
- Structure validation
- Table formatting

## IDE Integration

### VS Code

1. Install the LlamaLint VS Code extension
2. Add configuration to your settings.json:

```json
{
  "llamalint.enable": true,
  "llamalint.formatOnSave": true,
  "llamalint.configPath": ".llamalint.yaml"
}
```

### PyCharm

1. Install the LlamaLint PyCharm plugin
2. Configure in Settings → Tools → LlamaLint

## GitHub Actions Integration

```yaml
name: LlamaLint

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install llamalint
    - name: Lint with LlamaLint
      run: |
        llamalint check .
```

## Custom Rules

You can develop custom rules for your specific project needs:

```python
from llamalint.rules import Rule

class NoTodoComments(Rule):
    """Disallow TODO comments in production code."""
    
    id = "no-todo-comments"
    languages = ["python", "javascript", "typescript"]
    
    def check(self, file_content, file_path):
        if "TODO" in file_content:
            return [
                {
                    "message": "TODO comments should be resolved before production",
                    "line": self._find_line_with_todo(file_content),
                    "severity": "warning"
                }
            ]
        return []
    
    def _find_line_with_todo(self, content):
        # Implementation to find the line number
        pass
```

## API Usage

```python
from llamalint import LlamaLint

# Initialize with default config
linter = LlamaLint()

# Or with custom config
linter = LlamaLint.from_config(".llamalint.yaml")

# Lint a file
results = linter.lint_file("myfile.py")

# Format a file
formatted_content = linter.format_file("myfile.py")

# Check a directory
all_results = linter.lint_directory("myproject/")

# Apply fixes
linter.apply_fixes(results)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT 
# Updated in commit 1 - 2025-04-04 17:33:11

# Updated in commit 9 - 2025-04-04 17:33:12

# Updated in commit 17 - 2025-04-04 17:33:13

# Updated in commit 25 - 2025-04-04 17:33:13

# Updated in commit 1 - 2025-04-05 14:36:22

# Updated in commit 9 - 2025-04-05 14:36:22

# Updated in commit 17 - 2025-04-05 14:36:22

# Updated in commit 25 - 2025-04-05 14:36:22

# Updated in commit 1 - 2025-04-05 15:22:52

# Updated in commit 9 - 2025-04-05 15:22:52

# Updated in commit 17 - 2025-04-05 15:22:52

# Updated in commit 25 - 2025-04-05 15:22:52

# Updated in commit 1 - 2025-04-05 15:57:11

# Updated in commit 9 - 2025-04-05 15:57:11

# Updated in commit 17 - 2025-04-05 15:57:11
