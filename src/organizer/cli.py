import argparse
from pathlib import Path
import sys
from .core import discover_files, plan_moves, execute_moves, summarize


def build_parser():
    """
    Creates and returns the configured ArgumentParser for the CLI 
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