"""
Core logic for the File Organizer project.

This module contains the primary functionality for categorizing and moving files
based on their extensions. It defines mappings between file extensions and categories,
and provides utility functions for discovering files, deciding destinations,
resolving conflicts, planning moves, executing them, and generating summaries.

Features:
---------
- CATEGORY_MAP: Main dictionary mapping categories to a list of extensions.
- EXT_TO_CATEGORY: Reverse lookup dictionary mapping extension -> category.
- discover_files(): Lists files in a given directory.
- decide_destination(): Determines the destination subfolder based on file type.
- ensure_unique_path(): Prevents overwriting by generating unique file names.
- plan_moves(): Builds the complete plan of file moves.
- execute_moves(): Executes the plan, moving files to their destinations.
- summarize(): Produces a summary of moved files by category.

Example usage:
--------------
    from pathlib import Path
    from organizer.core import discover_files, plan_moves, execute_moves, summarize

    src = Path("~/Downloads").expanduser()
    dst = Path("~/Downloads/Organized").expanduser()

    files = discover_files(src)
    plan = plan_moves(files, dst)
    execute_moves(plan)
    print(summarize(plan))
"""
from __future__ import annotations

from pathlib import Path
import shutil
from typing import List, Tuple, Dict

# Main map: category -> list of extensions (lowercase)
CATEGORY_MAP: Dict[str, List[str]] = {
    "Documents": [".pdf", ".docx", ".xlsx", ".pptx", ".txt", ".md"],
    "Images":    [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg"],
    "Audio":      [".mp3", ".wav", ".flac", ".m4a"],
    "Videos":     [".mp4", ".mov", ".mkv", ".avi"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Installers": [".exe", ".msi", ".dmg", ".pkg"],
    "Code":     [".py", ".js", ".ts", ".html", ".css", ".json", ".yaml", ".yml", ".xml"],
}

# Quick lookup: extension -> category
EXT_TO_CATEGORY: Dict[str, str] = {
    ext: category
    for category, exts in CATEGORY_MAP.items()
    for ext in exts
}


def discover_files(src: Path) -> List[Path]:
    """
    Discover all files in the given source directory (non-recursive).

    Args:
        src (Path): The source directory.

    Returns:
        List[Path]: Sorted list of files (excluding subdirectories).

    Notes:
        - Sorting is case-insensitive for predictable output.
        - Does not include files from nested subdirectories.
    """
    files = [p for p in src.iterdir() if p.is_file()]
    files.sort(key=lambda p: p.name.lower())
    return files


def decide_destination(file: Path, dst_root: Path) -> Path:
    """
    Determine the destination path for a file based on its extension.

    Args:
        file (Path): The file to be organized.
        dst_root (Path): The root destination directory.

    Returns:
        Path: The full destination path (category folder + filename).

    Notes:
        - If the file extension is not in CATEGORY_MAP, it is placed in "Others".
        - Destination directories are not created here (handled later).
    """
    ext = file.suffix.lower()
    category = EXT_TO_CATEGORY.get(ext, "Others")
    dest_dir = dst_root / category
    return dest_dir / file.name


def ensure_unique_path(target: Path) -> Path:
    """
    Ensure the target path is unique, avoiding overwriting existing files.

    Args:
        target (Path): Proposed destination file path.

    Returns:
        Path: A unique file path. If the original exists, suffixes like
              '-1', '-2', ... are appended before the extension.

    Example:
        file.pdf  -> file.pdf (if available)
                  -> file-1.pdf (if file.pdf exists)
                  -> file-2.pdf (if file.pdf and file-1.pdf exist)
    """
    if not target.exists():
        return target

    stem, suffix = target.stem, target.suffix
    counter = 1
    while True:
        candidate = target.with_name(f"{stem}-{counter}{suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def plan_moves(files: List[Path], dst_root: Path) -> List[Tuple[Path, Path]]:
    """
    Build a list of planned moves (source -> destination).

    Args:
        files (List[Path]): List of files to organize.
        dst_root (Path): Root destination directory.

    Returns:
        List[Tuple[Path, Path]]: List of pairs (source_file, final_destination).

    Notes:
        - Uses `decide_destination` to select a category folder.
        - Uses `ensure_unique_path` to resolve filename conflicts.
    """
    plan: List[Tuple[Path, Path]] = []
    for f in files:
        suggested = decide_destination(f, dst_root)
        final = ensure_unique_path(suggested)
        plan.append((f, final))
    return plan


def execute_moves(plan: List[Tuple[Path, Path]]) -> None:
    """
    Execute all file moves from the provided plan.

    Args:
        plan (List[Tuple[Path, Path]]): List of (source, destination) pairs.

    Notes:
        - Creates destination directories if they do not exist.
        - Uses `shutil.move` for cross-platform compatibility.
    """
    for src, dst in plan:
        dst.parent.mkdir(parents=True, exist_ok=True)
        # str() for broad compatibility on Windows
        shutil.move(str(src), str(dst))


def summarize(plan: List[Tuple[Path, Path]]) -> Dict[str, int]:
    """
    Summarize the results of a move plan by category.

    Args:
        plan (List[Tuple[Path, Path]]): List of executed or planned moves.

    Returns:
        Dict[str, int]: A dictionary with category names as keys
                        and counts of files as values.

    Example:
        {"Documents": 3, "Images": 5, "Others": 2}

    Notes:
        - The summary is sorted alphabetically by category name.
    """
    summary: Dict[str, int] = {}
    for _, dst in plan:
        category = dst.parent.name
        summary[category] = summary.get(category, 0) + 1
    # sort by category name for stable output
    return dict(sorted(summary.items(), key=lambda kv: kv[0].lower()))


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

