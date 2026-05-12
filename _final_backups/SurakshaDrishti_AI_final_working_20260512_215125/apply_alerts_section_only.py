"""
SurakshaDrishti AI — Alerts Section Only Patch

Purpose:
- Replace only the Alerts placeholder with the real alert feed.
- Keep Overview dashboard unchanged.
- Keep Live Feed section unchanged.
- Do not touch backend, SOS, Authority, Heatmap, or analytics workflow.

Safety:
- Only modifies frontend/dashboard/src/App.jsx.
- Creates backup before editing.
"""

from pathlib import Path


APP_PATH = Path("frontend/dashboard/src/App.jsx")
BACKUP_PATH = Path("frontend/dashboard/src/App.jsx.backup_before_alerts_section")


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
    # 1. Pass alert-related props into SectionPlaceholder
    # ------------------------------------------------------------

    old_props = '''                    <SectionPlaceholder
                        activeSection={activeSection}
                        events={events}
                        backendAnalytics={backendAnalytics}
                        heatmapData={typeof heatmapData !== "undefined" ? heatmapData : null}
                        dispatches={typeof dispatches !== "undefined" ? dispatches : []}
                    />'''

    new_props = '''                    <SectionPlaceholder
                        activeSection={activeSection}
                        events={events}
                        backendAnalytics={backendAnalytics}
                        heatmapData={typeof heatmapData !== "undefined" ? heatmapData : null}
                        dispatches={typeof dispatches !== "undefined" ? dispatches : []}
                        reviewedEventKeys={reviewedEventKeys}
                        getEventKey={getEventKey}
                        markEventReviewed={markEventReviewed}
                        markEventUnreviewed={markEventUnreviewed}
                        getSeverityColor={getSeverityColor}
                        getEventIcon={getEventIcon}
                    />'''

    text = replace_once(text, old_props, new_props, "SectionPlaceholder props")

    # ------------------------------------------------------------
    # 2. Update SectionPlaceholder function parameters
    # ------------------------------------------------------------

    old_signature = '''function SectionPlaceholder({
    activeSection,
    events,
    backendAnalytics,
    heatmapData,
    dispatches,
}) {'''

    new_signature = '''function SectionPlaceholder({
    activeSection,
    events,
    backendAnalytics,
    heatmapData,
    dispatches,
    reviewedEventKeys,
    getEventKey,
    markEventReviewed,
    markEventUnreviewed,
    getSeverityColor,
    getEventIcon,
}) {'''

    text = replace_once(text, old_signature, new_signature, "SectionPlaceholder signature")

    # ------------------------------------------------------------
    # 3. Mark alerts section as custom
    # ------------------------------------------------------------

    old_alerts_config = '''        alerts: {
            icon: "🚨",
            title: "Alerts Section",
            description:
                "This section is ready. Next step can move the alert feed here safely.",
        },'''

    new_alerts_config = '''        alerts: {
            icon: "🚨",
            title: "Live Alert Feed",
            description:
                "Dedicated alert feed section connected to existing event history and WebSocket updates.",
            custom: "alerts",
        },'''

    text = replace_once(text, old_alerts_config, new_alerts_config, "alerts section config")

    # ------------------------------------------------------------
    # 4. Add custom alerts render after live custom render
    # ------------------------------------------------------------

    old_live_render = '''    if (config.custom === "live") {
        return (
            <Panel title={`${config.icon} ${config.title}`}>
                <LiveFeedPanel />
            </Panel>
        )
    }

    return ('''

    new_live_render = '''    if (config.custom === "live") {
        return (
            <Panel title={`${config.icon} ${config.title}`}>
                <LiveFeedPanel />
            </Panel>
        )
    }

    if (config.custom === "alerts") {
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

    text = replace_once(text, old_live_render, new_live_render, "custom alerts render")

    APP_PATH.write_text(text, encoding="utf-8")

    print("alerts section patch ok")
    print(f"backup: {BACKUP_PATH}")
    print(f"updated: {APP_PATH}")


if __name__ == "__main__":
    main()