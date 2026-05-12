"""
SurakshaDrishti AI — Video Overlay Branding Fix

Purpose:
- Replace old visible video overlay branding:
  SurakshaDrishti AI -> SurakshaDrishti AI

Safety:
- Only edits project .py files.
- Skips venv.
- Skips backup files.
- Creates .backup_before_overlay_branding for each edited file.
"""

from pathlib import Path


ROOT = Path(".")
OLD = "SurakshaDrishti AI"
NEW = "SurakshaDrishti AI"


def should_skip(path: Path) -> bool:
    parts = {p.lower() for p in path.parts}

    if "venv" in parts:
        return True

    if "node_modules" in parts:
        return True

    if "backup" in path.name.lower():
        return True

    return False


changed = []

for path in ROOT.rglob("*.py"):
    if should_skip(path):
        continue

    text = path.read_text(encoding="utf-8", errors="ignore")

    if OLD not in text:
        continue

    backup = path.with_name(path.name + ".backup_before_overlay_branding")

    if not backup.exists():
        backup.write_text(text, encoding="utf-8")

    text = text.replace(OLD, NEW)
    path.write_text(text, encoding="utf-8")

    changed.append(str(path))


print("overlay branding fix complete")
print("changed files:")

for item in changed:
    print("-", item)