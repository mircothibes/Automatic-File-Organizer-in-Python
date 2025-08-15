from __future__ import annotations

from pathlib import Path
import shutil
from typing import List, Tuple, Dict

# Main map: category -> list of extensions (lowercase)
CATEGORY_MAP: Dict[str, List[str]] = {
    "Documents": [".pdf", ".docx", ".xlsx", ".pptx", ".txt", ".md"],
    "Imagens":    [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg"],
    "Audio":      [".mp3", ".wav", ".flac", ".m4a"],
    "Videos":     [".mp4", ".mov", ".mkv", ".avi"],
    "Compressed": [".zip", ".rar", ".7z", ".tar", ".gz"],
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
    Returns only files (non-recursive) in `src`,
    sorted by name for predictable output.
    """
    files = [p for p in src.iterdir() if p.is_file()]
    files.sort(key=lambda p: p.name.lower())
    return files


def decide_destination(file: Path, dst_root: Path) -> Path:
    """
    Determines the destination folder based on the file extension.
    If the extension is not mapped, it uses the 'Other' category.
    Returns the suggested full path (folder + file name).
    """
    ext = file.suffix.lower()
    category = EXT_TO_CATEGORY.get(ext, "Outros")
    dest_dir = dst_root / category
    return dest_dir / file.name


def ensure_unique_path(target: Path) -> Path:
    """
    Ensures that `target` will not be overwritten.
    If it already exists, generates 'name-1.ext', 'name-2.ext', ... until a free one is found.
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
    Generates the complete movement plan (origin, final_destination).
    The final destination already considers name conflicts (unique path).
    """
    plan: List[Tuple[Path, Path]] = []
    for f in files:
        suggested = decide_destination(f, dst_root)
        final = ensure_unique_path(suggested)
        plan.append((f, final))
    return plan


def execute_moves(plan: List[Tuple[Path, Path]]) -> None:
    """
    Executes planned movements. Creates destination folders when necessary.
    """
    for src, dst in plan:
        dst.parent.mkdir(parents=True, exist_ok=True)
        # str() for broad compatibility on Windows
        shutil.move(str(src), str(dst))


def summarize(plan: List[Tuple[Path, Path]]) -> Dict[str, int]:
    """
    Returns a summary by category (destination subfolder name).
    Ex.: {"Images": 5, "Documents": 3, "Others": 2}
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

