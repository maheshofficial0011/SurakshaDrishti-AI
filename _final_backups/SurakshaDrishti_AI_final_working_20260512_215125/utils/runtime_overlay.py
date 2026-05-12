"""
SurakshaDrishti AI — Runtime Camera Overlay

Purpose:
- Draw a clean OpenCV HUD on the live camera frame.
- Keep title/stats on top-left.
- Move LIVE and CAM-01 badges to top-right.
- Prevent text overlap.
- Keep detection/tracking logic unchanged.

Usage:
    from utils.runtime_overlay import draw_runtime_overlay

    frame = draw_runtime_overlay(
        frame,
        camera_id="CAM-01",
        tracked_count=len(tracked_objects),
        frame_id=frame_id,
    )
"""

import cv2


def _safe_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return default


def _fit_text_scale(text, font, max_width, start_scale, thickness, min_scale=0.45):
    """
    Reduce text scale until the text fits max_width.
    Useful when frame width is small or title is long.
    """

    scale = start_scale

    while scale >= min_scale:
        (text_w, _), _ = cv2.getTextSize(text, font, scale, thickness)

        if text_w <= max_width:
            return scale

        scale -= 0.05

    return min_scale


def _draw_badge(
    frame,
    text,
    right_x,
    top_y,
    border_color,
    text_color,
    font,
    font_scale=0.52,
    thickness=2,
):
    """
    Draw a rounded-looking rectangular badge using OpenCV rectangles.

    Coordinate logic:
    - right_x is the right edge of the badge.
    - top_y is the top edge.
    - Function returns badge width so another badge can be placed beside it.
    """

    badge_pad_x = 12
    badge_h = 30

    (tw, th), _ = cv2.getTextSize(text, font, font_scale, thickness)

    badge_w = tw + badge_pad_x * 2

    x1 = _safe_int(right_x - badge_w)
    y1 = _safe_int(top_y)
    x2 = _safe_int(right_x)
    y2 = _safe_int(top_y + badge_h)

    # Background
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), -1)

    # Border
    cv2.rectangle(frame, (x1, y1), (x2, y2), border_color, 2)

    # Text
    text_x = x1 + badge_pad_x
    text_y = y1 + 21

    cv2.putText(
        frame,
        text,
        (text_x, text_y),
        font,
        font_scale,
        text_color,
        thickness,
        cv2.LINE_AA,
    )

    return badge_w


def draw_runtime_overlay(
    frame,
    camera_id="CAM-01",
    tracked_count=0,
    frame_id=0,
    project_name="SurakshaDrishti AI",
    mode_label="Final MVP",
):
    """
    Draw SurakshaDrishti AI live runtime overlay.

    Layout:
    - Top-left:
        SurakshaDrishti AI | Final MVP
        Camera: CAM-01 | Tracked: 1 | Frame: 588

    - Top-right:
        [LIVE] [CAM-01]

    Args:
        frame:
            OpenCV BGR frame.

        camera_id:
            Camera label shown in stats and badge.

        tracked_count:
            Number of tracked objects/persons.

        frame_id:
            Current pipeline frame number.

        project_name:
            Visible project name.

        mode_label:
            Runtime mode label.

    Returns:
        frame with overlay drawn.
    """

    if frame is None:
        return frame

    h, w = frame.shape[:2]

    if h <= 0 or w <= 0:
        return frame

    font = cv2.FONT_HERSHEY_SIMPLEX

    title_text = f"{project_name} | {mode_label}"
    stats_text = (
        f"Camera: {camera_id} | "
        f"Tracked: {_safe_int(tracked_count)} | "
        f"Frame: {_safe_int(frame_id)}"
    )

    # Colors are BGR because OpenCV uses BGR.
    black = (0, 0, 0)
    dark_border = (45, 45, 45)
    white = (255, 255, 255)
    soft_white = (210, 220, 230)
    green = (0, 255, 120)
    orange = (255, 180, 0)

    # Top-left panel position.
    panel_x = 18
    panel_y = 18
    panel_pad_x = 16
    panel_pad_y = 12
    line_gap = 12

    # Reserve space on the right for badges.
    right_badge_reserved_width = 190
    max_panel_width = max(260, w - panel_x - right_badge_reserved_width - 24)

    title_thickness = 2
    stats_thickness = 1

    title_scale = _fit_text_scale(
        title_text,
        font,
        max_panel_width - panel_pad_x * 2,
        start_scale=0.78,
        thickness=title_thickness,
        min_scale=0.5,
    )

    stats_scale = _fit_text_scale(
        stats_text,
        font,
        max_panel_width - panel_pad_x * 2,
        start_scale=0.55,
        thickness=stats_thickness,
        min_scale=0.42,
    )

    (title_w, title_h), _ = cv2.getTextSize(
        title_text,
        font,
        title_scale,
        title_thickness,
    )

    (stats_w, stats_h), _ = cv2.getTextSize(
        stats_text,
        font,
        stats_scale,
        stats_thickness,
    )

    panel_w = max(title_w, stats_w) + panel_pad_x * 2
    panel_w = min(panel_w, max_panel_width)

    panel_h = title_h + stats_h + panel_pad_y * 2 + line_gap

    # Draw black title panel.
    cv2.rectangle(
        frame,
        (panel_x, panel_y),
        (panel_x + panel_w, panel_y + panel_h),
        black,
        -1,
    )

    # Border for professional look.
    cv2.rectangle(
        frame,
        (panel_x, panel_y),
        (panel_x + panel_w, panel_y + panel_h),
        dark_border,
        1,
    )

    title_pos = (
        panel_x + panel_pad_x,
        panel_y + panel_pad_y + title_h,
    )

    stats_pos = (
        panel_x + panel_pad_x,
        panel_y + panel_pad_y + title_h + line_gap + stats_h,
    )

    cv2.putText(
        frame,
        title_text,
        title_pos,
        font,
        title_scale,
        white,
        title_thickness,
        cv2.LINE_AA,
    )

    cv2.putText(
        frame,
        stats_text,
        stats_pos,
        font,
        stats_scale,
        soft_white,
        stats_thickness,
        cv2.LINE_AA,
    )

    # Top-right badges.
    right_margin = 18
    top_margin = 18
    badge_gap = 10

    cam_right = w - right_margin

    cam_badge_width = _draw_badge(
        frame=frame,
        text=camera_id,
        right_x=cam_right,
        top_y=top_margin,
        border_color=orange,
        text_color=white,
        font=font,
    )

    live_right = cam_right - cam_badge_width - badge_gap

    _draw_badge(
        frame=frame,
        text="LIVE",
        right_x=live_right,
        top_y=top_margin,
        border_color=green,
        text_color=green,
        font=font,
    )

    return frame