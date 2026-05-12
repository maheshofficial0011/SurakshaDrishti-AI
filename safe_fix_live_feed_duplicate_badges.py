"""
SurakshaDrishti AI — Safe Live Feed Duplicate Badge Fix

Problem:
- Python/OpenCV already draws LIVE and CAM-01 inside the camera frame.
- React dashboard also shows LIVE and CAM-01 badges above/over the same feed.
- Result: duplicate labels.

Fix:
- Remove only the React duplicate badge elements from the Live Feed section.
- Do not inject raw CSS.
- Do not touch backend, pipeline, detection, tracking, SOS, authority, or assistant.

Safety:
- Creates backup before editing.
- If exact pattern is not found, it prints instructions and does not corrupt App.jsx.
"""

from pathlib import Path
import re


APP_PATH = Path("frontend/dashboard/src/App.jsx")
BACKUP_PATH = Path("frontend/dashboard/src/App.jsx.backup_before_safe_live_badge_fix")


def main():
    if not APP_PATH.exists():
        raise FileNotFoundError(APP_PATH)

    source = APP_PATH.read_text(encoding="utf-8")

    if not BACKUP_PATH.exists():
        BACKUP_PATH.write_text(source, encoding="utf-8")

    text = source
    original = text

    # ------------------------------------------------------------------
    # Pattern A:
    # Remove a small React overlay/container that contains both LIVE and CAM-01.
    # This is the safest broad match because the duplicate dashboard overlay
    # is usually a small absolute-positioned div near the live image.
    # ------------------------------------------------------------------

    patterns = [
        # div container with absolute positioning and both LIVE + CAM-01
        r'''
        <div
            \s+style=\{\{[\s\S]*?
            position:\s*["']absolute["'][\s\S]*?
            \}\}
        >
            [\s\S]*?
            LIVE
            [\s\S]*?
            CAM-01
            [\s\S]*?
        </div>
        ''',

        # compact one-line absolute div with LIVE + CAM-01
        r'''<div\s+style=\{\{[\s\S]*?position:\s*["']absolute["'][\s\S]*?\}\}>[\s\S]*?LIVE[\s\S]*?CAM-01[\s\S]*?</div>''',
    ]

    removed = 0

    for pattern in patterns:
        text, count = re.subn(
            pattern,
            "",
            text,
            count=1,
            flags=re.VERBOSE | re.MULTILINE,
        )
        removed += count

        if count > 0:
            break

    # ------------------------------------------------------------------
    # Pattern B:
    # If duplicate badges are two separate JSX nodes, remove only nodes
    # that are absolute-positioned and contain literal LIVE / CAM-01.
    # ------------------------------------------------------------------

    if removed == 0:
        separate_patterns = [
            r'''<div\s+style=\{\{[\s\S]*?position:\s*["']absolute["'][\s\S]*?\}\}>\s*LIVE\s*</div>''',
            r'''<div\s+style=\{\{[\s\S]*?position:\s*["']absolute["'][\s\S]*?\}\}>\s*CAM-01\s*</div>''',
            r'''<span\s+style=\{\{[\s\S]*?position:\s*["']absolute["'][\s\S]*?\}\}>\s*LIVE\s*</span>''',
            r'''<span\s+style=\{\{[\s\S]*?position:\s*["']absolute["'][\s\S]*?\}\}>\s*CAM-01\s*</span>''',
        ]

        for pattern in separate_patterns:
            text, count = re.subn(
                pattern,
                "",
                text,
                flags=re.MULTILINE,
            )
            removed += count

    if removed == 0:
        print("No duplicate React badge block was removed.")
        print("App.jsx was not changed.")
        print("")
        print("Run this command and send output:")
        print('Select-String -Path frontend\\dashboard\\src\\App.jsx -Pattern "LIVE|CAM-01|Live AI Camera Feed" -Context 8,12')
        return

    APP_PATH.write_text(text, encoding="utf-8")

    print("safe duplicate live badge fix ok")
    print(f"removed JSX badge block count: {removed}")
    print(f"backup: {BACKUP_PATH}")
    print(f"updated: {APP_PATH}")


if __name__ == "__main__":
    main()

