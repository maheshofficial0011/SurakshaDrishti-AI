"""
SurakshaDrishti AI — Heatmap Section Only Patch

Purpose:
- Replace only the Heatmap placeholder with the real HeatmapPanel.
- Keep Overview dashboard unchanged.
- Keep Live Feed and Alerts sections unchanged.
- Do not touch backend, SOS, Authority, or analytics workflow.

Safety:
- Only modifies frontend/dashboard/src/App.jsx.
- Creates backup before editing.
"""

from pathlib import Path


APP_PATH = Path("frontend/dashboard/src/App.jsx")
BACKUP_PATH = Path("frontend/dashboard/src/App.jsx.backup_before_heatmap_section")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"Could not find expected block: {label}")
    return text.replace(old, new, 1)


def main():
    source = APP_PATH.read_text(encoding="utf-8")

    if not BACKUP_PATH.exists():
        BACKUP_PATH.write_text(source, encoding="utf-8")

    text = source

    # ------------------------------------------------------------
    # 1. Mark heatmap section as custom
    # ------------------------------------------------------------

    old_heatmap_config = '''        heatmap: {
            icon: "🗺️",
            title: "Heatmap Section",
            description:
                "This section is ready. Next step can move the predictive heatmap here safely.",
        },'''

    new_heatmap_config = '''        heatmap: {
            icon: "🗺️",
            title: "Predictive Safety Heatmap",
            description:
                "Dedicated heatmap section connected to /analytics/heatmap.",
            custom: "heatmap",
        },'''

    text = replace_once(text, old_heatmap_config, new_heatmap_config, "heatmap section config")

    # ------------------------------------------------------------
    # 2. Add custom heatmap render after alerts custom render
    # ------------------------------------------------------------

    old_alerts_render_end = '''    if (config.custom === "alerts") {
        return (
            <Panel title={`${config.icon} ${config.title}`}>
                <div
                    className="scroll-soft"
                    style={{
                        maxHeight: "calc(100vh - 230px)",
                        overflowY: "auto",
                        paddingRight: "4px",
                    }}
                >
                    {events.length === 0 ? (
                        <EmptyState />
                    ) : (
                        events.map((event, index) => {
                            const key = getEventKey(event, index)
                            const isReviewed = reviewedEventKeys.includes(key)

                            return (
                                <AlertCard
                                    key={key}
                                    event={event}
                                    index={index}
                                    isReviewed={isReviewed}
                                    onMarkReviewed={() => markEventReviewed(event, index)}
                                    onMarkUnreviewed={() => markEventUnreviewed(event, index)}
                                    getSeverityColor={getSeverityColor}
                                    getEventIcon={getEventIcon}
                                />
                            )
                        })
                    )}
                </div>
            </Panel>
        )
    }

    return ('''

    new_alerts_render_end = '''    if (config.custom === "alerts") {
        return (
            <Panel title={`${config.icon} ${config.title}`}>
                <div
                    className="scroll-soft"
                    style={{
                        maxHeight: "calc(100vh - 230px)",
                        overflowY: "auto",
                        paddingRight: "4px",
                    }}
                >
                    {events.length === 0 ? (
                        <EmptyState />
                    ) : (
                        events.map((event, index) => {
                            const key = getEventKey(event, index)
                            const isReviewed = reviewedEventKeys.includes(key)

                            return (
                                <AlertCard
                                    key={key}
                                    event={event}
                                    index={index}
                                    isReviewed={isReviewed}
                                    onMarkReviewed={() => markEventReviewed(event, index)}
                                    onMarkUnreviewed={() => markEventUnreviewed(event, index)}
                                    getSeverityColor={getSeverityColor}
                                    getEventIcon={getEventIcon}
                                />
                            )
                        })
                    )}
                </div>
            </Panel>
        )
    }

    if (config.custom === "heatmap") {
        return <HeatmapPanel heatmapData={heatmapData} />
    }

    return ('''

    text = replace_once(text, old_alerts_render_end, new_alerts_render_end, "custom heatmap render")

    APP_PATH.write_text(text, encoding="utf-8")

    print("heatmap section patch ok")
    print(f"backup: {BACKUP_PATH}")
    print(f"updated: {APP_PATH}")


if __name__ == "__main__":
    main()