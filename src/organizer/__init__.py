"""
Organizer package
=================

This package provides tools to automatically organize files into subfolders
based on their file extensions. It is designed to be simple, extensible, 
and suitable both for **command-line usage** and **programmatic integration**.

Modules
-------
- core.py:
    Contains the core logic for categorizing files, planning moves,
    resolving conflicts, executing file operations, and summarizing results.
- cli.py:
    Provides a command-line interface (CLI) for end users.
- tests/:
    Unit tests to validate functionality and ensure reliability.

Key Features
------------
- Categorize files into predefined folders such as *Documents*, *Images*,
  *Videos*, *Audio*, *Archives*, *Installers*, *Code*, and *Others*.
- Prevent overwriting by ensuring unique filenames when conflicts occur.
- Execute real moves or run in dry-run mode (preview without changes).
- Generate summaries of organized files by category.

Example
-------
    >>> from organizer import discover_files, plan_moves, execute_moves, summarize
    >>> from pathlib import Path
    >>>
    >>> src = Path("~/Downloads").expanduser()
    >>> dst = Path("~/Downloads/Organized").expanduser()
    >>>
    >>> files = discover_files(src)
    >>> plan = plan_moves(files, dst)
    >>> execute_moves(plan)
    >>> print(summarize(plan))
    {'Documents': 3, 'Images': 5, 'Others': 1}

Metadata
--------
- Author: Marcos Vinicius Thibes Kemer
- Version: 0.1.0
"""

__version__ = "0.1.0"
__author__ = "Marcos Vinicius Thibes Kemer"

from .core import (
    CATEGORY_MAP,
    EXT_TO_CATEGORY,
    discover_files,
    decide_destination,
    ensure_unique_path,
    plan_moves,
    execute_moves,
    summarize,
)

__all__ = [
    "CATEGORY_MAP",
    "EXT_TO_CATEGORY",
    "discover_files",
    "decide_destination",
    "ensure_unique_path",
    "plan_moves",
    "execute_moves",
    "summarize",
]
