"""
SurakshaNet AI — Sidebar Navigation Only Patch

Purpose:
- Enable sidebar navigation sections safely.
- Keep the existing dashboard working.
- Add simple placeholder pages for sections.
- Do NOT change backend.
- Do NOT change SOS logic.
- Do NOT change authority workflow logic.
- Do NOT change heatmap/dispatch logic.

Sections added:
- Overview
- Live Feed
- Alerts
- Heatmap
- SOS Control
- Authority
- Analytics
- Settings

Rollback:
Copy frontend/dashboard/src/App.jsx.backup_before_sidebar_navigation
back to frontend/dashboard/src/App.jsx
"""

from pathlib import Path


APP_PATH = Path("frontend/dashboard/src/App.jsx")
BACKUP_PATH = Path("frontend/dashboard/src/App.jsx.backup_before_sidebar_navigation")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"Could not find expected block: {label}")

    return text.replace(old, new, 1)


def insert_before(text: str, marker: str, insert: str, label: str) -> str:
    if marker not in text:
        raise RuntimeError(f"Could not find marker: {label}")

    return text.replace(marker, insert + marker, 1)


def main():
    if not APP_PATH.exists():
        raise FileNotFoundError(APP_PATH)

    source = APP_PATH.read_text(encoding="utf-8")

    if not BACKUP_PATH.exists():
        BACKUP_PATH.write_text(source, encoding="utf-8")

    text = source

    # ------------------------------------------------------------
    # 1. Replace sidebar menu only
    # ------------------------------------------------------------

    old_sidebar = '''            <SidebarItem
                icon="📊"
                label="Dashboard"
                active={activeSection === "dashboard"}
                onClick={() => setActiveSection("dashboard")}
            />

            <SidebarItem icon="📹" label="Live Feed" disabled />
            <SidebarItem icon="🚨" label="Alerts" disabled />
            <SidebarItem icon="📈" label="Analytics" disabled />
            <SidebarItem icon="📁" label="Reports" disabled />

            <SidebarItem
                icon="⚙️"
                label="Settings"
                active={activeSection === "settings"}
                onClick={() => setActiveSection("settings")}
            />'''

    new_sidebar = '''            <SidebarItem
                icon="📊"
                label="Overview"
                active={activeSection === "dashboard"}
                onClick={() => setActiveSection("dashboard")}
            />

            <SidebarItem
                icon="📹"
                label="Live Feed"
                active={activeSection === "live"}
                onClick={() => setActiveSection("live")}
            />

            <SidebarItem
                icon="🚨"
                label="Alerts"
                active={activeSection === "alerts"}
                onClick={() => setActiveSection("alerts")}
            />

            <SidebarItem
                icon="🗺️"
                label="Heatmap"
                active={activeSection === "heatmap"}
                onClick={() => setActiveSection("heatmap")}
            />

            <SidebarItem
                icon="🆘"
                label="SOS Control"
                active={activeSection === "sos"}
                onClick={() => setActiveSection("sos")}
            />

            <SidebarItem
                icon="🚓"
                label="Authority"
                active={activeSection === "authority"}
                onClick={() => setActiveSection("authority")}
            />

            <SidebarItem
                icon="📈"
                label="Analytics"
                active={activeSection === "analytics"}
                onClick={() => setActiveSection("analytics")}
            />

            <SidebarItem
                icon="⚙️"
                label="Settings"
                active={activeSection === "settings"}
                onClick={() => setActiveSection("settings")}
            />'''

    text = replace_once(text, old_sidebar, new_sidebar, "sidebar menu")

    # ------------------------------------------------------------
    # 2. Replace active section rendering safely
    # ------------------------------------------------------------
    # Existing logic:
    # settings ? settings : full dashboard
    #
    # New safe logic:
    # settings -> settings
    # dashboard -> original full dashboard
    # other sections -> placeholder page
    #
    # This avoids touching existing dashboard components.
    # ------------------------------------------------------------

    old_render_start = '''                {activeSection === "settings" ? (
                    <SettingsPanel
                        themeMode={themeMode}
                        toggleThemeMode={toggleThemeMode}
                        isLightMode={isLightMode}
                        lastSyncTime={lastSyncTime}
                        lastEventTime={lastEventTime}
                    />
                ) : (
                    <>'''

    new_render_start = '''                {activeSection === "settings" ? (
                    <SettingsPanel
                        themeMode={themeMode}
                        toggleThemeMode={toggleThemeMode}
                        isLightMode={isLightMode}
                        lastSyncTime={lastSyncTime}
                        lastEventTime={lastEventTime}
                    />
                ) : activeSection !== "dashboard" ? (
                    <SectionPlaceholder
                        activeSection={activeSection}
                        events={events}
                        backendAnalytics={backendAnalytics}
                        heatmapData={typeof heatmapData !== "undefined" ? heatmapData : null}
                        dispatches={typeof dispatches !== "undefined" ? dispatches : []}
                    />
                ) : (
                    <>'''

    text = replace_once(text, old_render_start, new_render_start, "active section render start")

    # ------------------------------------------------------------
    # 3. Add placeholder component before DashboardStyles
    # ------------------------------------------------------------

    placeholder_component = r'''function SectionPlaceholder({
    activeSection,
    events,
    backendAnalytics,
    heatmapData,
    dispatches,
}) {
    const sectionConfig = {
        live: {
            icon: "📹",
            title: "Live Feed Section",
            description:
                "This section is ready. Next step can move the live camera feed here safely.",
        },
        alerts: {
            icon: "🚨",
            title: "Alerts Section",
            description:
                "This section is ready. Next step can move the alert feed here safely.",
        },
        heatmap: {
            icon: "🗺️",
            title: "Heatmap Section",
            description:
                "This section is ready. Next step can move the predictive heatmap here safely.",
        },
        sos: {
            icon: "🆘",
            title: "SOS Control Section",
            description:
                "This section is ready. Next step can add the realistic SOS form here safely.",
        },
        authority: {
            icon: "🚓",
            title: "Authority Response Section",
            description:
                "This section is ready. Next step can add Pending / Assigned / Running / Resolved workflow here safely.",
        },
        analytics: {
            icon: "📈",
            title: "Analytics Section",
            description:
                "This section is ready. Next step can move analytics cards and reports here safely.",
        },
    }

    const config = sectionConfig[activeSection] || {
        icon: "📊",
        title: "Section",
        description: "This section is ready.",
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
            >
                <div
                    style={{
                        fontSize: "18px",
                        fontWeight: "bold",
                        color: "#e5e7eb",
                        marginBottom: "8px",
                    }}
                >
                    Navigation is working.
                </div>

                <div>{config.description}</div>

                <div
                    style={{
                        display: "grid",
                        gridTemplateColumns: "repeat(4, minmax(0, 1fr))",
                        gap: "12px",
                        marginTop: "18px",
                    }}
                >
                    <InfoTile
                        title="Loaded Events"
                        value={events?.length || 0}
                        color="#38bdf8"
                    />

                    <InfoTile
                        title="Database Events"
                        value={backendAnalytics?.total_events ?? 0}
                        color="#22c55e"
                    />

                    <InfoTile
                        title="Heatmap Risk"
                        value={heatmapData?.risk_level || "Ready"}
                        color="#f59e0b"
                    />

                    <InfoTile
                        title="Dispatches"
                        value={dispatches?.length || 0}
                        color="#a855f7"
                    />
                </div>

                <div
                    style={{
                        marginTop: "18px",
                        color: "#94a3b8",
                        fontSize: "14px",
                    }}
                >
                    Existing dashboard remains safe under the Overview section.
                </div>
            </div>
        </Panel>
    )
}

'''

    text = insert_before(
        text,
        "function DashboardStyles() {",
        placeholder_component,
        "before DashboardStyles",
    )

    APP_PATH.write_text(text, encoding="utf-8")

    print("sidebar navigation patch ok")
    print(f"backup: {BACKUP_PATH}")
    print(f"updated: {APP_PATH}")


if __name__ == "__main__":
    main()