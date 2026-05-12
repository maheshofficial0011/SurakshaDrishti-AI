"""
SurakshaDrishti AI — Live Feed Section Only Patch

Purpose:
- Replace only the Live Feed placeholder with the real LiveFeedPanel.
- Keep Overview dashboard unchanged.
- Do not touch backend, SOS, Authority, Heatmap, or Alerts workflow.

Safety:
- Only modifies frontend/dashboard/src/App.jsx.
- Creates backup before editing.
"""

from pathlib import Path


APP_PATH = Path("frontend/dashboard/src/App.jsx")
BACKUP_PATH = Path("frontend/dashboard/src/App.jsx.backup_before_live_section")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"Could not find expected block: {label}")
    return text.replace(old, new, 1)


def main():
    source = APP_PATH.read_text(encoding="utf-8")

    if not BACKUP_PATH.exists():
        BACKUP_PATH.write_text(source, encoding="utf-8")

    text = source

    old_block = '''        live: {
            icon: "📹",
            title: "Live Feed Section",
            description:
                "This section is ready. Next step can move the live camera feed here safely.",
        },'''

    new_block = '''        live: {
            icon: "📹",
            title: "Live AI Camera Feed",
            description:
                "Dedicated live feed section connected to the existing video stream.",
            custom: "live",
        },'''

    text = replace_once(text, old_block, new_block, "live section config")

    old_render_block = '''    return (
        <Panel title={`${config.icon} ${config.title}`}>
            <div
                style={{
                    background: "#111827",
                    border: "1px solid #334155",
                    borderRadius: "16px",
                    padding: "18px",
                    color: "#cbd5e1",
                    lineHeight: 1.7,
                }}
            >'''

    new_render_block = '''    if (config.custom === "live") {
        return (
            <Panel title={`${config.icon} ${config.title}`}>
                <LiveFeedPanel />
            </Panel>
        )
    }

    return (
        <Panel title={`${config.icon} ${config.title}`}>
            <div
                style={{
                    background: "#111827",
                    border: "1px solid #334155",
                    borderRadius: "16px",
                    padding: "18px",
                    color: "#cbd5e1",
                    lineHeight: 1.7,
                }}
            >'''

    text = replace_once(text, old_render_block, new_render_block, "placeholder render live custom")

    APP_PATH.write_text(text, encoding="utf-8")

    print("live section patch ok")
    print(f"backup: {BACKUP_PATH}")
    print(f"updated: {APP_PATH}")


if __name__ == "__main__":
    main()
