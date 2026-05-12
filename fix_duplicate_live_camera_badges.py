"""
SurakshaDrishti AI — Duplicate Live Camera Badge Fix

Problem:
- The Python/OpenCV camera frame already draws LIVE and CAM-01 badges
  on the top-right.
- The React dashboard also draws small LIVE and CAM-01 overlay badges
  on the top-left of the live camera panel.
- Result: duplicate badges and visual clutter.

Fix:
- Hide/remove only the React dashboard overlay badges.
- Keep the Python/OpenCV overlay badges because they are embedded in
  the actual streamed camera frame.

Safety:
- Only modifies frontend/dashboard/src/App.jsx.
- Creates backup before editing.
- Does not touch backend, detection, tracking, event engine, or pipeline.
"""

from pathlib import Path
import re


APP_PATH = Path("frontend/dashboard/src/App.jsx")
BACKUP_PATH = Path("frontend/dashboard/src/App.jsx.backup_before_duplicate_live_badge_fix_script")


def main():
    if not APP_PATH.exists():
        raise FileNotFoundError(APP_PATH)

    source = APP_PATH.read_text(encoding="utf-8")

    if not BACKUP_PATH.exists():
        BACKUP_PATH.write_text(source, encoding="utf-8")

    text = source

    original = text

    # ------------------------------------------------------------------
    # Fix pattern 1:
    # Remove JSX blocks that render small overlay badges containing LIVE
    # and CAM-01 near the live feed.
    #
    # This targets common JSX structures like:
    # <div style={...}>LIVE</div>
    # <div style={...}>CAM-01</div>
    #
    # It does NOT remove Python/OpenCV badges because those are not in JSX.
    # ------------------------------------------------------------------

    badge_text_patterns = [
        r'''<div\s+style=\{\{[^{}]*position:\s*["']absolute["'][\s\S]*?\}\}\>\s*LIVE\s*</div>''',
        r'''<span\s+style=\{\{[^{}]*position:\s*["']absolute["'][\s\S]*?\}\}\>\s*LIVE\s*</span>''',
        r'''<div\s+style=\{\{[^{}]*position:\s*["']absolute["'][\s\S]*?\}\}\>\s*CAM-01\s*</div>''',
        r'''<span\s+style=\{\{[^{}]*position:\s*["']absolute["'][\s\S]*?\}\}\>\s*CAM-01\s*</span>''',
    ]

    removed_count = 0

    for pattern in badge_text_patterns:
        text, count = re.subn(pattern, "", text, flags=re.MULTILINE)
        removed_count += count

    # ------------------------------------------------------------------
    # Fix pattern 2:
    # Some code may render both badges inside one absolute container:
    #
    # <div style={{ position: "absolute", top: ..., left: ... }}>
    #   <span>LIVE</span>
    #   <span>CAM-01</span>
    # </div>
    #
    # Remove only containers that contain BOTH LIVE and CAM-01.
    # ------------------------------------------------------------------

    combined_badge_pattern = re.compile(
        r'''<div\s+style=\{\{[\s\S]*?position:\s*["']absolute["'][\s\S]*?\}\}\>\s*[\s\S]*?LIVE[\s\S]*?CAM-01[\s\S]*?</div>''',
        re.MULTILINE,
    )

    text, combined_count = combined_badge_pattern.subn("", text)
    removed_count += combined_count

    # ------------------------------------------------------------------
    # Fix pattern 3:
    # If badges use class names instead of inline styles, hide those
    # classes by injecting a safe CSS override into the dashboard.
    #
    # This is a fallback and only affects visual duplicate badges.
    # ------------------------------------------------------------------

    css_override = '''
/* SurakshaDrishti AI duplicate live badge fix
   Python/OpenCV already draws LIVE and CAM-01 inside the video frame.
   These classes are hidden only if duplicate React overlay badges exist. */
.live-badge,
.camera-badge,
.live-camera-badge,
.live-feed-badge,
.camera-feed-badge,
.video-live-badge,
.video-camera-badge {
    display: none !important;
}
'''

    if "duplicate live badge fix" not in text:
        # Inject CSS into an existing <style> block if App.jsx contains one as string.
        # If not, this section will safely do nothing.
        style_inserted = False

        if "</style>" in text:
            text = text.replace("</style>", css_override + "\n</style>", 1)
            style_inserted = True

        # If App.jsx has a global CSS string or JSX style tag, we leave it alone.
        # Most of your dashboard styling is inline, so this is only a fallback.

    if text == original:
        print("No exact duplicate badge JSX blocks were removed.")
        print("This means the badges may be rendered with a different structure.")
        print("Run the Select-String command below and send the output.")
    else:
        APP_PATH.write_text(text, encoding="utf-8")
        print("duplicate dashboard badge fix ok")
        print(f"removed badge block count: {removed_count}")
        print(f"backup: {BACKUP_PATH}")
        print(f"updated: {APP_PATH}")


if __name__ == "__main__":
    main()