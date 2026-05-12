"""
SurakshaDrishti AI — Assistant Pro Layer Patch

Purpose:
- Make the assistant smarter without changing backend or architecture.
- Add richer live-dashboard reasoning.
- Add navigation commands from sidebar assistant.
- Improve answers about sections, alerts, units, severity, and system status.

Safety:
- Only modifies frontend/dashboard/src/App.jsx.
- No backend changes.
- No new npm packages.
- Creates backup before editing.
"""

from pathlib import Path


APP_PATH = Path("frontend/dashboard/src/App.jsx")
BACKUP_PATH = Path("frontend/dashboard/src/App.jsx.backup_before_assistant_pro_layer")


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
    # 1. Pass setActiveSection into SectionPlaceholder
    # ------------------------------------------------------------

    old_props = '''                        updateDispatchWorkflow={updateDispatchWorkflow}
                    />'''

    new_props = '''                        updateDispatchWorkflow={updateDispatchWorkflow}
                        setActiveSection={setActiveSection}
                    />'''

    if old_props in text and "setActiveSection={setActiveSection}" not in text:
        text = replace_once(text, old_props, new_props, "pass setActiveSection")

    # ------------------------------------------------------------
    # 2. Add setActiveSection to SectionPlaceholder signature
    # ------------------------------------------------------------

    old_signature_tail = '''    authorityFilter,
    setAuthorityFilter,
    updateDispatchWorkflow,
}) {'''

    new_signature_tail = '''    authorityFilter,
    setAuthorityFilter,
    updateDispatchWorkflow,
    setActiveSection,
}) {'''

    if old_signature_tail in text:
        text = replace_once(
            text,
            old_signature_tail,
            new_signature_tail,
            "SectionPlaceholder setActiveSection signature",
        )

    # ------------------------------------------------------------
    # 3. Pass setActiveSection to AssistantSection
    # ------------------------------------------------------------

    old_assistant_call = '''            <AssistantSection
                events={events}
                dispatches={dispatches}
                heatmapData={heatmapData}
                backendAnalytics={backendAnalytics}
            />'''

    new_assistant_call = '''            <AssistantSection
                events={events}
                dispatches={dispatches}
                heatmapData={heatmapData}
                backendAnalytics={backendAnalytics}
                setActiveSection={setActiveSection}
            />'''

    if old_assistant_call in text:
        text = replace_once(
            text,
            old_assistant_call,
            new_assistant_call,
            "AssistantSection setActiveSection prop",
        )

    # ------------------------------------------------------------
    # 4. Add Assistant Pro helper before AssistantSection
    # ------------------------------------------------------------

    pro_helper = r'''function getAssistantProReply({
    query,
    events,
    dispatches,
    heatmapData,
    backendAnalytics,
    setActiveSection,
}) {
    const lower = String(query || "").toLowerCase()
    const eventList = events || []
    const dispatchList = dispatches || []

    function formatEvent(event, index) {
        return `${index + 1}. ${event.type || "UNKNOWN"} — ${event.severity || "INFO"} — ${event.location_label || event.camera_location || "Unknown location"}`
    }

    function formatDispatchLine(dispatch, index) {
        const statusLabel =
            dispatch.status === "DISPATCHED" ? "RUNNING" : dispatch.status || "PENDING"

        return `${index + 1}. ${dispatch.dispatch_id} — ${dispatch.unit_type || "UNIT"} — ${dispatch.event_type || "EVENT"} — ${statusLabel} — ${dispatch.location_label || "Unknown location"}`
    }

    const criticalEvents = eventList.filter((event) => event.severity === "CRITICAL")
    const highEvents = eventList.filter((event) => event.severity === "HIGH")
    const sosEvents = eventList.filter((event) => event.type === "SOS_ALERT")
    const intrusionEvents = eventList.filter((event) => event.type === "INTRUSION")
    const loiteringEvents = eventList.filter((event) => event.type === "LOITERING")
    const crowdEvents = eventList.filter((event) => event.type === "CROWD_ALERT")

    const pending = dispatchList.filter((dispatch) => dispatch.status === "PENDING")
    const assigned = dispatchList.filter((dispatch) => dispatch.status === "ASSIGNED")
    const running = dispatchList.filter((dispatch) => dispatch.status === "DISPATCHED")
    const resolved = dispatchList.filter((dispatch) => dispatch.status === "RESOLVED")

    const policeUnits = dispatchList.filter((dispatch) => dispatch.unit_type === "POLICE")
    const ambulanceUnits = dispatchList.filter((dispatch) => dispatch.unit_type === "AMBULANCE")
    const fireUnits = dispatchList.filter((dispatch) => dispatch.unit_type === "FIRE")
    const rescueUnits = dispatchList.filter((dispatch) => dispatch.unit_type === "RESCUE")
    const securityUnits = dispatchList.filter((dispatch) => dispatch.unit_type === "SECURITY")

    const totalEvents = backendAnalytics?.total_events ?? eventList.length
    const riskLevel = heatmapData?.risk_level || "UNKNOWN"
    const riskScore = heatmapData?.risk_score ?? "N/A"

    if (lower.includes("open overview") || lower.includes("go overview")) {
        setActiveSection?.("dashboard")
        return "Opening Overview section."
    }

    if (lower.includes("open live") || lower.includes("open camera") || lower.includes("go live")) {
        setActiveSection?.("live")
        return "Opening Live Feed section."
    }

    if (lower.includes("open alert") || lower.includes("go alert")) {
        setActiveSection?.("alerts")
        return "Opening Alerts section."
    }

    if (lower.includes("open authority") || lower.includes("go authority")) {
        setActiveSection?.("authority")
        return "Opening Authority Response Center."
    }

    if (lower.includes("open sos") || lower.includes("go sos")) {
        setActiveSection?.("sos")
        return "Opening SOS Control section."
    }

    if (lower.includes("open heatmap") || lower.includes("go heatmap")) {
        setActiveSection?.("heatmap")
        return "Opening Heatmap section."
    }

    if (lower.includes("open analytics") || lower.includes("go analytics")) {
        setActiveSection?.("analytics")
        return "Opening Analytics section."
    }

    if (lower.includes("dashboard section") || lower.includes("sections") || lower.includes("menu")) {
        return [
            "Dashboard sections:",
            "• Overview — complete command summary",
            "• Live Feed — real-time camera stream",
            "• Alerts — event feed with pinned emergencies",
            "• Heatmap — risk map around demo location",
            "• SOS Control — realistic emergency form",
            "• Authority — assign, mark running, and resolve incidents",
            "• Analytics — event/risk summaries",
            "• AI Assistant — command assistant workspace",
            "• Settings — theme and status settings",
        ].join("\\n")
    }

    if (lower.includes("critical")) {
        if (criticalEvents.length === 0) return "No CRITICAL alerts found."

        return [
            `Critical alerts found: ${criticalEvents.length}`,
            ...criticalEvents.slice(0, 8).map(formatEvent),
        ].join("\\n")
    }

    if (lower.includes("high alert") || lower.includes("high severity")) {
        if (highEvents.length === 0) return "No HIGH severity alerts found."

        return [
            `High severity alerts found: ${highEvents.length}`,
            ...highEvents.slice(0, 8).map(formatEvent),
        ].join("\\n")
    }

    if (lower.includes("intrusion")) {
        return `Intrusion alerts: ${intrusionEvents.length}. ${
            intrusionEvents[0]
                ? `Latest: ${intrusionEvents[0].message || "No message"}`
                : "No intrusion alert details available."
        }`
    }

    if (lower.includes("loitering")) {
        return `Loitering alerts: ${loiteringEvents.length}. ${
            loiteringEvents[0]
                ? `Latest: ${loiteringEvents[0].message || "No message"}`
                : "No loitering alert details available."
        }`
    }

    if (lower.includes("crowd")) {
        return `Crowd alerts: ${crowdEvents.length}. ${
            crowdEvents[0]
                ? `Latest: ${crowdEvents[0].message || "No message"}`
                : "No crowd alert details available."
        }`
    }

    if (lower.includes("police")) {
        if (policeUnits.length === 0) return "No police authority incidents found."

        return [
            `Police incidents: ${policeUnits.length}`,
            ...policeUnits.slice(0, 8).map(formatDispatchLine),
        ].join("\\n")
    }

    if (lower.includes("ambulance") || lower.includes("medical")) {
        if (ambulanceUnits.length === 0) return "No ambulance incidents found."

        return [
            `Ambulance incidents: ${ambulanceUnits.length}`,
            ...ambulanceUnits.slice(0, 8).map(formatDispatchLine),
        ].join("\\n")
    }

    if (lower.includes("fire")) {
        if (fireUnits.length === 0) return "No fire response incidents found."

        return [
            `Fire response incidents: ${fireUnits.length}`,
            ...fireUnits.slice(0, 8).map(formatDispatchLine),
        ].join("\\n")
    }

    if (lower.includes("rescue")) {
        if (rescueUnits.length === 0) return "No rescue incidents found."

        return [
            `Rescue incidents: ${rescueUnits.length}`,
            ...rescueUnits.slice(0, 8).map(formatDispatchLine),
        ].join("\\n")
    }

    if (lower.includes("security")) {
        if (securityUnits.length === 0) return "No security patrol incidents found."

        return [
            `Security incidents: ${securityUnits.length}`,
            ...securityUnits.slice(0, 8).map(formatDispatchLine),
        ].join("\\n")
    }

    if (lower.includes("backend") || lower.includes("api status")) {
        return [
            "Backend API status:",
            "The dashboard expects FastAPI backend at http://127.0.0.1:8000.",
            "Important endpoints:",
            "• /health",
            "• /events",
            "• /analytics/heatmap",
            "• /dispatches",
            "• /sos",
            "• /ws/events",
            "",
            "If the dashboard shows connection refused, start backend first.",
        ].join("\\n")
    }

    if (lower.includes("frontend") || lower.includes("dashboard status")) {
        return [
            "Frontend dashboard:",
            "Run with: cd E:\\Copycat2\\frontend\\dashboard && npm run dev",
            "Open: http://localhost:5173/",
            "",
            "If the UI looks stale, restart Vite and refresh the browser.",
        ].join("\\n")
    }

    if (lower.includes("pipeline") || lower.includes("camera pipeline") || lower.includes("tracking pipeline")) {
        return [
            "Camera / AI pipeline:",
            "Run with:",
            "cd E:\\Copycat2",
            ".\\venv\\Scripts\\Activate.ps1",
            "python pipelines\\tracking_pipeline.py",
            "",
            "This sends live frames/events to the backend and dashboard.",
        ].join("\\n")
    }

    if (lower.includes("health") || lower.includes("system health")) {
        return [
            "System health summary:",
            `Total events: ${totalEvents}`,
            `Risk level: ${riskLevel}`,
            `Risk score: ${riskScore}/100`,
            `Pending: ${pending.length}`,
            `Assigned: ${assigned.length}`,
            `Running: ${running.length}`,
            `Resolved: ${resolved.length}`,
            `SOS alerts: ${sosEvents.length}`,
        ].join("\\n")
    }

    if (lower.includes("limitations") || lower.includes("limit") || lower.includes("weakness")) {
        return [
            "Known limitations:",
            "• Runs as a local demo prototype",
            "• Authority dispatch is simulated, not connected to real emergency services",
            "• Heatmap uses demo laptop location and stored events",
            "• CPU-only performance depends on laptop hardware",
            "• Weapon detection is not enabled as a reliable custom model is not included",
            "• Internet is needed for Leaflet map tiles unless cached",
        ].join("\\n")
    }

    if (lower.includes("reset") || lower.includes("clear demo")) {
        return [
            "Demo reset guidance:",
            "Use existing dashboard controls to clear event history where available.",
            "Resolved authority records remain useful for showing workflow history.",
            "For a clean database reset, stop backend first and back up the SQLite file before deleting it.",
        ].join("\\n")
    }

    return null
}

'''

    if "function getAssistantProReply({" not in text:
        text = insert_before(
            text,
            "function AssistantSection({",
            pro_helper,
            "before AssistantSection",
        )

    # ------------------------------------------------------------
    # 5. Add setActiveSection to AssistantSection signature
    # ------------------------------------------------------------

    old_assistant_signature = '''function AssistantSection({
    events,
    dispatches,
    heatmapData,
    backendAnalytics,
}) {'''

    new_assistant_signature = '''function AssistantSection({
    events,
    dispatches,
    heatmapData,
    backendAnalytics,
    setActiveSection,
}) {'''

    if old_assistant_signature in text:
        text = replace_once(
            text,
            old_assistant_signature,
            new_assistant_signature,
            "AssistantSection signature",
        )

    # ------------------------------------------------------------
    # 6. Inject Assistant Pro into sidebar assistant reply
    # ------------------------------------------------------------

    old_sidebar_injection_point = '''        const projectKnowledgeReply = getProjectKnowledgeReply(query)

        if (projectKnowledgeReply) {
            return projectKnowledgeReply
        }
'''

    new_sidebar_injection_point = '''        const projectKnowledgeReply = getProjectKnowledgeReply(query)

        if (projectKnowledgeReply) {
            return projectKnowledgeReply
        }

        const assistantProReply = getAssistantProReply({
            query,
            events,
            dispatches,
            heatmapData,
            backendAnalytics,
            setActiveSection,
        })

        if (assistantProReply) {
            return assistantProReply
        }
'''

    # Replace only first occurrence for AssistantSection createAssistantReply.
    if old_sidebar_injection_point in text and "const assistantProReply = getAssistantProReply({" not in text:
        text = replace_once(
            text,
            old_sidebar_injection_point,
            new_sidebar_injection_point,
            "inject Assistant Pro into sidebar assistant",
        )

    # ------------------------------------------------------------
    # 7. Inject Assistant Pro into floating assistant reply
    # ------------------------------------------------------------
    # If the previous replacement hit the floating assistant instead of sidebar,
    # this second targeted pass inserts into the remaining reply function block.
    # ------------------------------------------------------------

    remaining_occurrences = text.count(old_sidebar_injection_point)

    if remaining_occurrences > 0:
        text = replace_once(
            text,
            old_sidebar_injection_point,
            new_sidebar_injection_point,
            "inject Assistant Pro into floating assistant",
        )

    # ------------------------------------------------------------
    # 8. Improve quick prompts if present
    # ------------------------------------------------------------

    text = text.replace(
        '''    const quickPrompts = [
        "Give system summary",
        "Explain our system",
        "How to demo?",
        "How to run full system?",
        "Show pending incidents",
        "What should I do next?",
        "What is the current risk?",
        "What is our team name?",
    ]''',
        '''    const quickPrompts = [
        "Give system health",
        "Explain our system",
        "Show critical alerts",
        "Show police incidents",
        "Show ambulance incidents",
        "How to demo?",
        "How to run full system?",
        "What should I do next?",
    ]''',
    )

    text = text.replace(
        '''    const quickPrompts = [
        "What is the latest alert?",
        "Explain our system",
        "How to demo?",
        "Show pending incidents",
        "What should I do next?",
    ]''',
        '''    const quickPrompts = [
        "What is the latest alert?",
        "Show critical alerts",
        "Show pending incidents",
        "System health",
        "What should I do next?",
    ]''',
    )

    APP_PATH.write_text(text, encoding="utf-8")

    print("assistant pro layer patch ok")
    print(f"backup: {BACKUP_PATH}")
    print(f"updated: {APP_PATH}")


if __name__ == "__main__":
    main()