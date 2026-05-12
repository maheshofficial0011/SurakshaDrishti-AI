"""
SurakshaDrishti AI — Remove Broken Raw CSS From App.jsx

Problem:
- A previous duplicate badge fix inserted raw CSS directly into App.jsx:
    .live-badge,
    .camera-badge {
        display: none !important;
    }

- That is valid CSS, but invalid JavaScript/JSX unless inside a style tag/string.
- Vite fails with:
    Expected `}` but found `:`
    display: none !important;

Fix:
- Remove the broken raw CSS block from App.jsx.
- Do not touch backend, pipeline, detection, tracking, SOS, authority, or assistant.
"""

from pathlib import Path
import re


APP_PATH = Path("frontend/dashboard/src/App.jsx")
BACKUP_PATH = Path("frontend/dashboard/src/App.jsx.backup_before_removing_broken_css")


def main():
    if not APP_PATH.exists():
        raise FileNotFoundError(APP_PATH)

    source = APP_PATH.read_text(encoding="utf-8")

    if not BACKUP_PATH.exists():
        BACKUP_PATH.write_text(source, encoding="utf-8")

    text = source
    original = text

    # Remove the exact broken CSS comment block if present.
    text = re.sub(
        r"""/\*\s*SurakshaDrishti AI duplicate live badge fix[\s\S]*?\*/\s*
\.live-badge,\s*
\.camera-badge,\s*
\.live-camera-badge,\s*
\.live-feed-badge,\s*
\.camera-feed-badge,\s*
\.video-live-badge,\s*
\.video-camera-badge\s*
\{\s*
display:\s*none\s*!important;\s*
\}\s*""",
        "",
        text,
        flags=re.MULTILINE,
    )

    # More defensive cleanup: remove any raw CSS class block containing display none.
    text = re.sub(
        r"""\.live-badge,[\s\S]*?\.video-camera-badge\s*\{\s*display:\s*none\s*!important;\s*\}\s*""",
        "",
        text,
        flags=re.MULTILINE,
    )

    # Final defensive cleanup: remove nearby standalone raw CSS if only partial block remains.
    text = re.sub(
        r"""\s*\.live-badge,[\s\S]{0,600}?display:\s*none\s*!important;\s*\}\s*""",
        "\n",
        text,
        flags=re.MULTILINE,
    )

    if text == original:
        print("No broken CSS block found. App.jsx was not changed.")
    else:
        APP_PATH.write_text(text, encoding="utf-8")
        print("broken CSS cleanup ok")
        print(f"backup: {BACKUP_PATH}")
        print(f"updated: {APP_PATH}")


if __name__ == "__main__":
    main()