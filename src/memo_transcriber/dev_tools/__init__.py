"""
Development-only tools for memo-transcriber.

This package contains development and debugging commands that are NOT included
in production distributions. These tools are only available when developing
the project locally.

Usage:
    # Only works in development environment
    from memo_transcriber.dev_tools.dev_commands import register_dev_commands

Note:
    This package is excluded from wheel distributions via pyproject.toml.
    Do NOT import from production code (cli.py, comparator.py, etc.).
"""
