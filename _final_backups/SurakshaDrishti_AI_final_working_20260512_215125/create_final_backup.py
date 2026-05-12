"""
SurakshaDrishti AI — Final Working Backup

Purpose:
- Creates a timestamped backup of the currently working project.
- Skips heavy folders like venv, node_modules, dist, cache folders.
- Keeps backend, frontend source, pipeline, tracking, event engine, database code, and configs safe.

Run:
    python create_final_backup.py
"""

from pathlib import Path
from datetime import datetime
import shutil


ROOT = Path(".").resolve()
BACKUP_ROOT = ROOT / "_final_backups"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
DEST = BACKUP_ROOT / f"SurakshaDrishti_AI_final_working_{TIMESTAMP}"

SKIP_DIRS = {
    "venv",
    ".venv",
    "node_modules",
    "dist",
    "__pycache__",
    ".git",
    ".pytest_cache",
    ".mypy_cache",
    "_final_backups",
}

SKIP_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".log",
}


def should_skip(path: Path) -> bool:
    parts = set(path.parts)

    if any(part in SKIP_DIRS for part in parts):
        return True

    if path.suffix.lower() in SKIP_SUFFIXES:
        return True

    return False


def copy_project():
    BACKUP_ROOT.mkdir(exist_ok=True)
    DEST.mkdir(parents=True, exist_ok=True)

    copied = 0

    for item in ROOT.rglob("*"):
        if should_skip(item):
            continue

        rel = item.relative_to(ROOT)
        target = DEST / rel

        if item.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue

        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, target)
        copied += 1

    print("final backup created")
    print(f"backup path: {DEST}")
    print(f"files copied: {copied}")


if __name__ == "__main__":
    copy_project()