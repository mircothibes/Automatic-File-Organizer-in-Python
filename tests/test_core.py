"""
Unit tests for the `organizer.core` module.

This test suite validates the core functionality of the File Organizer project,
ensuring that files are correctly discovered, categorized, and moved into
their appropriate destinations. All tests are written using `pytest` and rely
on the `tmp_path` fixture to provide isolated temporary directories and files.

Test coverage:
--------------
1. test_discover_files_lists_only_files
   - Ensures that `discover_files` returns only top-level files within a given
     source directory.
   - Confirms that subdirectories are not traversed recursively.

2. test_decide_destination_maps_by_extension
   - Validates that `decide_destination` correctly assigns a target folder
     based on the file's extension.
   - Checks case-insensitivity (e.g., `.PNG` → "Images").

3. test_ensure_unique_path_generates_suffixes
   - Confirms that `ensure_unique_path` prevents overwriting by generating
     unique filenames with incremental suffixes (e.g., file.pdf → file-1.pdf).

4. test_plan_moves_builds_pairs_and_resolves_conflicts
   - Ensures that `plan_moves` builds a complete mapping of source → target
     paths for all discovered files.
   - Verifies conflict resolution by renaming files if the target already exists.

5. test_execute_moves_and_summarize
   - Validates the end-to-end flow of moving files with `execute_moves`.
   - Confirms that after execution, all target files exist in their respective
     category folders.
   - Verifies that `summarize` correctly counts files per category, including
     unknown extensions (mapped to "Others").

Key points:
-----------
- All tests are self-contained, using temporary directories to avoid affecting
  the developer's filesystem.
- A passing suite ensures that the file organizer's core logic is reliable and
  handles edge cases like naming conflicts and unknown file types.
"""

from pathlib import Path
from organizer import (
    CATEGORY_MAP,
    EXT_TO_CATEGORY,
    discover_files,
    decide_destination,
    ensure_unique_path,
    plan_moves,
    execute_moves,
    summarize,
)


def test_discover_files_lists_only_files(tmp_path: Path):
    # Test that only top-level files are discovered, excluding subdirectories.
    (tmp_path / "a.pdf").write_text("x")
    (tmp_path / "b.jpg").write_text("x")
    (tmp_path / "subdir").mkdir()
    (tmp_path / "subdir" / "c.txt").write_text("x")

    files = discover_files(tmp_path)
    names = sorted(p.name for p in files)
    # only top-level files, no recursion
    assert names == ["a.pdf", "b.jpg"]


def test_decide_destination_maps_by_extension(tmp_path: Path):
    # Test that files are mapped to the correct category folder based on extension (case-insensitive).
    dst = tmp_path / "dst"
    file_img = tmp_path / "photo.PNG"  # uppercase suffix
    file_img.write_text("x")

    target = decide_destination(file_img, dst)
    # should go to Images category
    assert target.parent.name in ("Images",)


def test_ensure_unique_path_generates_suffixes(tmp_path: Path):
    # Test that duplicate filenames are resolved by appending incremental suffixes
    target = tmp_path / "Documents" / "file.pdf"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("x")

    unique = ensure_unique_path(target)
    assert unique.name == "file-1.pdf"
    unique.write_text("y")
    unique2 = ensure_unique_path(target)
    assert unique2.name == "file-2.pdf"


def test_plan_moves_builds_pairs_and_resolves_conflicts(tmp_path: Path):
    # Test that plan_moves builds correct mappings and resolves filename conflicts by renaming.
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    dst.mkdir()

    a = src / "a.pdf"
    b = src / "b.jpg"
    a.write_text("x")
    b.write_text("x")

    # pre-create conflict for b.jpg in destination folder
    pre = dst / "Images" / "b.jpg"
    pre.parent.mkdir(parents=True, exist_ok=True)
    pre.write_text("already there")

    files = discover_files(src)
    plan = plan_moves(files, dst)

    # should have 2 planned moves
    assert len(plan) == 2
    # a.pdf should go to Documents
    dest_a = [d for s, d in plan if s.name == "a.pdf"][0]
    assert dest_a.parent.name == "Documents"
    # b.jpg should become b-1.jpg due to conflict
    dest_b = [d for s, d in plan if s.name == "b.jpg"][0]
    assert dest_b.name == "b-1.jpg"
    assert dest_b.parent.name == "Images"


def test_execute_moves_and_summarize(tmp_path: Path):
    # Test the full pipeline: execution of file moves and summary reporting by category.
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    dst.mkdir()

    (src / "a.pdf").write_text("x")
    (src / "b.jpg").write_text("x")
    (src / "c.unknownext").write_text("x")

    files = discover_files(src)
    plan = plan_moves(files, dst)

    # before moving, none of the targets should exist
    for _, d in plan:
        assert not d.exists()

    execute_moves(plan)

    # after moving, all targets should exist
    for _, d in plan:
        assert d.exists()

    summary = summarize(plan)
    # check counts by category; c.unknownext should go to 'Outros'
    assert summary.get("Documents", 0) == 1
    assert summary.get("Images", 0) == 1
    assert summary.get("Others", 0) == 1
