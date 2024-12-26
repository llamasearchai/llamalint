#!/usr/bin/env python
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="llamalint-llamasearch",
    version="0.1.0",
    author="LlamaSearch AI",
    author_email="nikjois@llamasearch.ai",
    description="Code linting and formatting tools for LlamaSearch.ai projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://llamasearch.ai",
    project_urls={
        "Bug Tracker": "https://github.com/llamasearch/llamalint/issues",
        "Documentation": "https://docs.llamasearch.ai/llamalint",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "pyyaml>=6.0",
        "click>=8.0.0",
        "rich>=10.0.0",
        "flake8>=4.0.0",
        "black>=22.0.0",
        "isort>=5.10.0",
        "pylint>=2.12.0",
        "mypy>=0.910",
        "pydantic>=1.8.0",
        "typer>=0.4.0",
        "pathspec>=0.9.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.12.0",
            "tox>=3.24.0",
        ],
        "javascript": [
            "esprima>=4.0.0",
            "eslint-parser>=0.1.0",
        ],
        "docs": [
            "sphinx>=4.0.2",
            "sphinx-rtd-theme>=0.5.2",
            "sphinx-click>=3.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "llamalint=llamalint.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
) 
# Updated in commit 5 - 2025-04-04 17:33:12

# Updated in commit 13 - 2025-04-04 17:33:12

# Updated in commit 21 - 2025-04-04 17:33:13

# Updated in commit 29 - 2025-04-04 17:33:13

# Updated in commit 5 - 2025-04-05 14:36:22

# Updated in commit 13 - 2025-04-05 14:36:22

# Updated in commit 21 - 2025-04-05 14:36:22

# Updated in commit 29 - 2025-04-05 14:36:22

# Updated in commit 5 - 2025-04-05 15:22:52

# Updated in commit 13 - 2025-04-05 15:22:52

# Updated in commit 21 - 2025-04-05 15:22:52

# Updated in commit 29 - 2025-04-05 15:22:52

# Updated in commit 5 - 2025-04-05 15:57:11

# Updated in commit 13 - 2025-04-05 15:57:11

# Updated in commit 21 - 2025-04-05 15:57:11

# Updated in commit 29 - 2025-04-05 15:57:11

# Updated in commit 5 - 2025-04-05 17:02:37

# Updated in commit 13 - 2025-04-05 17:02:37

# Updated in commit 21 - 2025-04-05 17:02:37

# Updated in commit 29 - 2025-04-05 17:02:37

# Updated in commit 5 - 2025-04-05 17:34:39

# Updated in commit 13 - 2025-04-05 17:34:39

# Updated in commit 21 - 2025-04-05 17:34:39

# Updated in commit 29 - 2025-04-05 17:34:39

# Updated in commit 5 - 2025-04-05 18:21:23
