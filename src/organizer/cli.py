"""
Command-Line Interface (CLI) for the File Organizer project.

This module provides a command-line entry point to organize files from a source
directory into categorized subfolders within a destination directory.

Features:
---------
- Parses user-provided arguments such as:
  * --src: source folder containing files to organize.
  * --dst: destination folder where organized files will be placed.
  * --dry-run: simulate the organization process without moving files.
- Validates the source and destination directories.
- Builds a plan of file moves using core logic (`plan_moves`).
- Executes moves (or prints the plan if dry-run mode is enabled).
- Prints a summary report of the categorized files.

Usage example:
--------------
Dry-run simulation:
    python -m organizer.cli --src ~/Downloads --dst ~/Organized --dry-run

Actual execution:
    python -m organizer.cli --src ~/Downloads --dst ~/Organized

This CLI acts as the primary interface for end-users, wrapping the internal
core functions into a simple and user-friendly command-line tool.
"""

import argparse
from pathlib import Path
import sys
from organizer import discover_files, plan_moves, execute_moves, summarize


def build_parser():
    """
    Build and configure the command-line argument parser.

    Returns:
        argparse.ArgumentParser: A parser with configured options:
            - --src (str): Source directory containing files to organize.
            - --dst (str): Destination directory for organized files.
                           Defaults to '~/Downloads/Organized'.
            - --dry-run (flag): If set, only simulates the organization
                                without moving any files.
    """
    parser = argparse.ArgumentParser(
        prog = "organizer",
        description="Organizes files by extension into subfolders (dry-run mode by default for testing).",
        )
    parser.add_argument(
        "--src",
        type=str,
        help="Source folder, (default: ~/Downloads)",
        )
    parser.add_argument(
        "--dst",
        type=str,
        default="~/Downloads/Organized",
        help="Destination folder (default: ~/Downloads/Organized)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only simulates (does not move files).",
    )
    return parser


def main():
    """
    Main entry point for the CLI.

    Steps performed:
    ----------------
    1. Parse command-line arguments.
    2. Resolve and validate source and destination directories.
    3. Build a list of files to move using `discover_files` and `plan_moves`.
    4. If dry-run mode is enabled:
       - Print the planned moves and a summary report.
    5. Otherwise:
       - Execute file moves with `execute_moves`.
       - Print a summary report of moved files.

    Exits with status code 1 if the source directory is invalid.
    """
    parser = build_parser()
    args = parser.parse_args()

    src = Path(args.src).expanduser().resolve()
    dst = Path(args.dst).expanduser().resolve()

# basic validations
    if not src.exists() or not src.is_dir():
        print(f"[error] Invalid source folder: {src}")
        sys.exit(1)

    dst.mkdir(parents=True, exist_ok=True)

    # basic pipeline 
    files = discover_files(src)
    plan = plan_moves(files, dst)

    if args.dry_run:
        # print plan (source -> destination)
        for s, d in plan:
            # category = target subfolder name
            category = d.parent.name
            print(f"{s} -> {d} [{category}]")
        summary = summarize(plan)
        print("\nSummary (dry-run):")
        for cat, count in summary.items():
            print(f"- {cat}: {count}")
        return

    # actual execution
    execute_moves(plan)
    summary = summarize(plan)
    print("\nSummary (moved):")
    for cat, count in summary.items():
        print(f"- {cat}: {count}")

    
if __name__ == "__main__": 
    main()