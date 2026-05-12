
"""
SurakshaDrishti AI — Assistant Brain V2 Patch

Purpose:
- Make assistant more intelligent and less brittle.
- Fix command/navigation handling.
- Use one stronger local brain for both:
  1. Sidebar assistant
  2. Floating popup assistant

Safety:
- Only modifies frontend/dashboard/src/App.jsx
- No backend changes
- No API changes
- No new npm packages
- Creates backup before editing
"""

from pathlib import Path
import re


APP_PATH = Path("frontend/dashboard/src/App.jsx")
BACKUP_PATH = Path("frontend/dashboard/src/App.jsx.backup_before_assistant_brain_v2")


def insert_before(text: str, marker: str, insert: str, label: str) -> str:
    if marker not in text:
        raise RuntimeError(f"Could not find marker: {label}")
    return text.replace(marker, insert + marker, 1)


def main():
    source = APP_PATH.read_text(encoding="utf-8")

    if not BACKUP_PATH.exists():
        BACKUP_PATH.write_text(source, encoding="utf-8")

    text = source

    # ------------------------------------------------------------
    # 1. Add central Assistant Brain V2
    # ------------------------------------------------------------

    brain_v2 = r'''function normalizeAssistantText(value) {
    return String(value || "")
        .toLowerCase()
        .replace(/[^\w\s]/g, " ")
        .replace(/\s+/g, " ")
        .trim()
}

function assistantTextHas(text, words) {
    return words.some((word) => text.includes(word))
}

function getReadableStatus(status) {
    if (status === "DISPATCHED") return "RUNNING"
    return status || "PENDING"
}

function formatAssistantEvent(event, index = 0) {
    return `${index + 1}. ${event.type || "UNKNOWN"} | ${event.severity || "INFO"} | ${
        event.location_label || event.camera_location || event.incident_location || "Unknown location"
    }`
}

function formatAssistantDispatch(dispatch, index = 0) {
    return `${index + 1}. ${dispatch.dispatch_id || "DSP"} | ${
        dispatch.unit_type || "UNIT"
    } | ${dispatch.event_type || "EVENT"} | ${getReadableStatus(dispatch.status)} | ${
        dispatch.location_label || "Unknown location"
    }`
}

function getAssistantBrainV2Reply({
    query,
    events = [],
    dispatches = [],
    heatmapData = null,
    backendAnalytics = null,
    setActiveSection = null,
}) {
    const text = normalizeAssistantText(query)

    if (!text) {
        return "Ask me about alerts, SOS, authority incidents, heatmap risk, system health, run commands, demo flow, or dashboard sections."
    }

    const totalEvents = backendAnalytics?.total_events ?? events.length
    const riskLevel = heatmapData?.risk_level || "UNKNOWN"
    const riskScore = heatmapData?.risk_score ?? "N/A"
    const latestEvent = events?.[0] || null

    const sosEvents = events.filter((event) => event.type === "SOS_ALERT")
    const criticalEvents = events.filter((event) => event.severity === "CRITICAL")
    const highEvents = events.filter((event) => event.severity === "HIGH")
    const intrusionEvents = events.filter((event) => event.type === "INTRUSION")
    const loiteringEvents = events.filter((event) => event.type === "LOITERING")
    const crowdEvents = events.filter((event) => event.type === "CROWD_ALERT")
    const weaponEvents = events.filter((event) => event.type === "WEAPON_DETECTED")

    const pending = dispatches.filter((d) => d.status === "PENDING")
    const assigned = dispatches.filter((d) => d.status === "ASSIGNED")
    const running = dispatches.filter((d) => d.status === "DISPATCHED")
    const resolved = dispatches.filter((d) => d.status === "RESOLVED")

    const police = dispatches.filter((d) => d.unit_type === "POLICE")
    const ambulance = dispatches.filter((d) => d.unit_type === "AMBULANCE")
    const fire = dispatches.filter((d) => d.unit_type === "FIRE")
    const rescue = dispatches.filter((d) => d.unit_type === "RESCUE")
    const security = dispatches.filter((d) => d.unit_type === "SECURITY")

    const unresolvedSos = sosEvents.filter((event) => {
        const related = dispatches.filter(
            (dispatch) => Number(dispatch.event_id) === Number(event.db_id)
        )

        if (related.length === 0) return true

        return related.some((dispatch) => dispatch.status !== "RESOLVED")
    })

    function openSection(sectionName, label) {
        if (typeof setActiveSection === "function") {
            setActiveSection(sectionName)
            return `Opening ${label}.`
        }

        return `I can guide you to ${label}. Use the sidebar to open it.`
    }

    /*
    |--------------------------------------------------------------------------
    | Navigation commands first
    |--------------------------------------------------------------------------
    | This fixes commands like:
    | - open authority
    | - go to alerts
    | - show heatmap page
    */

    if (
        assistantTextHas(text, ["open authority", "go authority", "authority section", "go to authority", "show authority"])
    ) {
        return openSection("authority", "Authority Response Center")
    }

    if (
        assistantTextHas(text, ["open alerts", "go alerts", "alert section", "go to alerts", "show alerts"])
    ) {
        return openSection("alerts", "Alerts section")
    }

    if (
        assistantTextHas(text, ["open sos", "go sos", "sos section", "go to sos", "show sos"])
    ) {
        return openSection("sos", "SOS Control section")
    }

    if (
        assistantTextHas(text, ["open heatmap", "go heatmap", "heatmap section", "show heatmap"])
    ) {
        return openSection("heatmap", "Heatmap section")
    }

    if (
        assistantTextHas(text, ["open live", "go live", "live feed", "camera feed", "show camera"])
    ) {
        return openSection("live", "Live Feed section")
    }

    if (
        assistantTextHas(text, ["open overview", "go overview", "dashboard overview", "home"])
    ) {
        return openSection("dashboard", "Overview section")
    }

    if (
        assistantTextHas(text, ["open analytics", "go analytics", "analytics section"])
    ) {
        return openSection("analytics", "Analytics section")
    }

    /*
    |--------------------------------------------------------------------------
    | Project/system knowledge
    |--------------------------------------------------------------------------
    */

    if (
        assistantTextHas(text, [
            "project name",
            "team name",
            "who are we",
            "trinetra",
            "surakshadrishti",
            "suraksha drishti",
        ])
    ) {
        return [
            "Project Name: SurakshaDrishti AI",
            "Team Name: TriNetra",
            "",
            "SurakshaDrishti AI is a local real-time AI surveillance and emergency response prototype with live detection, alerts, SOS, heatmap, authority workflow, and dashboard assistant.",
        ].join("\n")
    }

    if (
        assistantTextHas(text, ["explain system", "explain our system", "how it works", "architecture", "system design"])
    ) {
        return [
            "SurakshaDrishti AI system architecture:",
            "",
            "1. Webcam / camera input",
            "2. YOLOv8n object/person detection",
            "3. Tracking Stability V2",
            "4. Event Engine generates alerts",
            "5. FastAPI backend stores events in SQLite",
            "6. WebSocket pushes real-time updates",
            "7. React dashboard shows Live Feed, Alerts, Heatmap, SOS, Authority Response, Analytics, and Assistant",
            "",
            "The system is designed as a local Windows prototype without changing the core architecture.",
        ].join("\n")
    }

    if (
        assistantTextHas(text, ["features", "what can it do", "capabilities"])
    ) {
        return [
            "Main features:",
            "• Live AI camera feed",
            "• Object/person detection",
            "• Stable tracking",
            "• Event alerts",
            "• SOS emergency form",
            "• Pinned emergency banner",
            "• Predictive safety heatmap",
            "• Authority workflow: Pending → Assigned → Running → Resolved",
            "• Reports and analytics",
            "• Local command assistant",
        ].join("\n")
    }

    /*
    |--------------------------------------------------------------------------
    | Live operational intelligence
    |--------------------------------------------------------------------------
    */

    if (
        assistantTextHas(text, ["latest alert", "last alert", "recent alert", "newest alert"])
    ) {
        if (!latestEvent) return "No alerts are available yet."

        return [
            "Latest alert:",
            `Type: ${latestEvent.type || "UNKNOWN"}`,
            `Severity: ${latestEvent.severity || "INFO"}`,
            `Location: ${latestEvent.location_label || latestEvent.camera_location || latestEvent.incident_location || "Unknown"}`,
            `Source: ${latestEvent.source || "camera_ai"}`,
            "",
            latestEvent.message || "No message available.",
        ].join("\n")
    }

    if (assistantTextHas(text, ["critical alert", "critical alerts"])) {
        if (criticalEvents.length === 0) return "No critical alerts found."
        return [`Critical alerts: ${criticalEvents.length}`, ...criticalEvents.slice(0, 8).map(formatAssistantEvent)].join("\n")
    }

    if (assistantTextHas(text, ["high alert", "high alerts", "high severity"])) {
        if (highEvents.length === 0) return "No high severity alerts found."
        return [`High severity alerts: ${highEvents.length}`, ...highEvents.slice(0, 8).map(formatAssistantEvent)].join("\n")
    }

    if (assistantTextHas(text, ["intrusion"])) {
        return intrusionEvents.length
            ? [`Intrusion alerts: ${intrusionEvents.length}`, ...intrusionEvents.slice(0, 6).map(formatAssistantEvent)].join("\n")
            : "No intrusion alerts found."
    }

    if (assistantTextHas(text, ["loitering"])) {
        return loiteringEvents.length
            ? [`Loitering alerts: ${loiteringEvents.length}`, ...loiteringEvents.slice(0, 6).map(formatAssistantEvent)].join("\n")
            : "No loitering alerts found."
    }

    if (assistantTextHas(text, ["crowd"])) {
        return crowdEvents.length
            ? [`Crowd alerts: ${crowdEvents.length}`, ...crowdEvents.slice(0, 6).map(formatAssistantEvent)].join("\n")
            : "No crowd alerts found."
    }

    if (assistantTextHas(text, ["weapon"])) {
        return weaponEvents.length
            ? [`Weapon alerts: ${weaponEvents.length}`, ...weaponEvents.slice(0, 6).map(formatAssistantEvent)].join("\n")
            : "No weapon alerts found."
    }

    /*
    |--------------------------------------------------------------------------
    | SOS and authority response
    |--------------------------------------------------------------------------
    */

    if (assistantTextHas(text, ["sos", "emergency"])) {
        if (unresolvedSos.length === 0) {
            return `No unresolved SOS alerts. Total SOS alerts in history: ${sosEvents.length}.`
        }

        const top = unresolvedSos[0]

        return [
            `Unresolved SOS alerts: ${unresolvedSos.length}`,
            `Latest SOS: ${top.incident_type || top.type}`,
            `Location: ${top.incident_location || top.location_label || "Unknown"}`,
            `Help needed: ${
                Array.isArray(top.help_needed)
                    ? top.help_needed.join(", ")
                    : top.help_needed || "Authority response required"
            }`,
            "",
            "Recommended action: open Authority, assign linked units, mark them Running, then Resolve after handling.",
        ].join("\n")
    }

    if (assistantTextHas(text, ["pending"])) {
        if (pending.length === 0) return "No pending authority incidents."
        return [
            `Pending authority incidents: ${pending.length}`,
            ...pending.slice(0, 8).map(formatAssistantDispatch),
            "",
            "Recommended action: assign these units.",
        ].join("\n")
    }

    if (assistantTextHas(text, ["assigned"])) {
        if (assigned.length === 0) return "No assigned authority incidents."
        return [
            `Assigned incidents: ${assigned.length}`,
            ...assigned.slice(0, 8).map(formatAssistantDispatch),
            "",
            "Recommended action: mark assigned units as Running when they are en route.",
        ].join("\n")
    }

    if (assistantTextHas(text, ["running", "en route", "dispatched"])) {
        if (running.length === 0) return "No authority units are currently Running."
        return [
            `Running authority responses: ${running.length}`,
            ...running.slice(0, 8).map(formatAssistantDispatch),
            "",
            "Recommended action: resolve after response is completed.",
        ].join("\n")
    }

    if (assistantTextHas(text, ["resolved", "closed"])) {
        return `Resolved authority incidents: ${resolved.length}.`
    }

    if (assistantTextHas(text, ["police"])) {
        if (police.length === 0) return "No police incidents found."
        return [`Police incidents: ${police.length}`, ...police.slice(0, 8).map(formatAssistantDispatch)].join("\n")
    }

    if (assistantTextHas(text, ["ambulance", "medical"])) {
        if (ambulance.length === 0) return "No ambulance incidents found."
        return [`Ambulance incidents: ${ambulance.length}`, ...ambulance.slice(0, 8).map(formatAssistantDispatch)].join("\n")
    }

    if (assistantTextHas(text, ["fire"])) {
        if (fire.length === 0) return "No fire incidents found."
        return [`Fire incidents: ${fire.length}`, ...fire.slice(0, 8).map(formatAssistantDispatch)].join("\n")
    }

    if (assistantTextHas(text, ["rescue"])) {
        if (rescue.length === 0) return "No rescue incidents found."
        return [`Rescue incidents: ${rescue.length}`, ...rescue.slice(0, 8).map(formatAssistantDispatch)].join("\n")
    }

    if (assistantTextHas(text, ["security"])) {
        if (security.length === 0) return "No security incidents found."
        return [`Security incidents: ${security.length}`, ...security.slice(0, 8).map(formatAssistantDispatch)].join("\n")
    }

    /*
    |--------------------------------------------------------------------------
    | Heatmap/risk/system status
    |--------------------------------------------------------------------------
    */

    if (assistantTextHas(text, ["risk", "heatmap", "danger level"])) {
        return [
            `Current risk level: ${riskLevel}`,
            `Risk score: ${riskScore}/100`,
            `Total events: ${totalEvents}`,
            `Latest heatmap event: ${heatmapData?.latest_event_type || "NONE"}`,
            `Location: ${heatmapData?.location?.label || "Demo Laptop Location"}`,
        ].join("\n")
    }

    if (assistantTextHas(text, ["system health", "health", "status", "summary"])) {
        return [
            "System health summary:",
            `Project: SurakshaDrishti AI`,
            `Team: TriNetra`,
            `Total events: ${totalEvents}`,
            `Risk: ${riskLevel} (${riskScore}/100)`,
            `SOS alerts: ${sosEvents.length}`,
            `Pending: ${pending.length}`,
            `Assigned: ${assigned.length}`,
            `Running: ${running.length}`,
            `Resolved: ${resolved.length}`,
        ].join("\n")
    }

    /*
    |--------------------------------------------------------------------------
    | Run/demo/troubleshooting
    |--------------------------------------------------------------------------
    */

    if (assistantTextHas(text, ["run full system", "start full system", "run commands", "how to run"])) {
        return [
            "Run SurakshaDrishti AI using 3 terminals:",
            "",
            "1. Backend:",
            "cd E:\\Copycat2",
            ".\\venv\\Scripts\\Activate.ps1",
            "python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000",
            "",
            "2. Frontend:",
            "cd E:\\Copycat2\\frontend\\dashboard",
            "npm run dev",
            "",
            "3. Camera / AI Pipeline:",
            "cd E:\\Copycat2",
            ".\\venv\\Scripts\\Activate.ps1",
            "python pipelines\\tracking_pipeline.py",
        ].join("\n")
    }

    if (assistantTextHas(text, ["demo", "presentation", "how to present", "demo flow"])) {
        return [
            "Recommended demo flow:",
            "1. Start backend",
            "2. Start frontend",
            "3. Start camera pipeline",
            "4. Show Overview",
            "5. Show Live Feed",
            "6. Trigger SOS",
            "7. Show pinned alert",
            "8. Show Heatmap risk update",
            "9. Open Authority",
            "10. Assign Unit",
            "11. Mark Running",
            "12. Resolve",
            "13. Show emergency banner disappears",
            "14. Ask assistant for system summary",
        ].join("\n")
    }

    if (assistantTextHas(text, ["not working", "connection refused", "failed", "error", "troubleshoot"])) {
        return [
            "Troubleshooting:",
            "• If SOS fails: backend is probably not running on port 8000.",
            "• If live feed fails: camera pipeline is probably not running.",
            "• If map is blank: internet may be needed for Leaflet tiles.",
            "• If dashboard is stale: restart npm run dev and refresh browser.",
            "• If patch breaks UI: restore latest App.jsx backup.",
        ].join("\n")
    }

    /*
    |--------------------------------------------------------------------------
    | Operator decision support
    |--------------------------------------------------------------------------
    */

    if (assistantTextHas(text, ["what should i do", "next action", "recommend", "operator action", "what next"])) {
        if (pending.length > 0) {
            return `Recommended action: open Authority and assign ${pending.length} pending incident(s).`
        }

        if (assigned.length > 0) {
            return `Recommended action: mark ${assigned.length} assigned incident(s) as Running.`
        }

        if (running.length > 0) {
            return `Recommended action: monitor ${running.length} running response(s), then resolve after completion.`
        }

        if (unresolvedSos.length > 0) {
            return `Recommended action: review ${unresolvedSos.length} unresolved SOS alert(s) and confirm authority response.`
        }

        return "Recommended action: system is stable. Continue monitoring Live Feed, Alerts, and Heatmap."
    }

    return [
        "I can help, but I need a clearer command.",
        "",
        "Try asking:",
        "• What should I do next?",
        "• Show pending incidents",
        "• Show critical alerts",
        "• Open Authority",
        "• Explain our system",
        "• How to run full system?",
        "• How to demo?",
        "• Troubleshoot connection refused",
    ].join("\n")
}

'''

    if "function getAssistantBrainV2Reply({" not in text:
        # Place before AssistantSection if possible, otherwise before FloatingAssistantWidget.
        if "function AssistantSection({" in text:
            text = insert_before(text, "function AssistantSection({", brain_v2, "before AssistantSection")
        else:
            text = insert_before(text, "function FloatingAssistantWidget({", brain_v2, "before FloatingAssistantWidget")

    # ------------------------------------------------------------
    # Ensure setActiveSection reaches AssistantSection
    # ------------------------------------------------------------

    text = text.replace(
        '''            <AssistantSection
                events={events}
                dispatches={dispatches}
                heatmapData={heatmapData}
                backendAnalytics={backendAnalytics}
            />''',
        '''            <AssistantSection
                events={events}
                dispatches={dispatches}
                heatmapData={heatmapData}
                backendAnalytics={backendAnalytics}
                setActiveSection={setActiveSection}
            />''',
    )

    text = text.replace(
        '''function AssistantSection({
    events,
    dispatches,
    heatmapData,
    backendAnalytics,
}) {''',
        '''function AssistantSection({
    events,
    dispatches,
    heatmapData,
    backendAnalytics,
    setActiveSection,
}) {''',
    )

    # ------------------------------------------------------------
    # Inject Brain V2 at top of sidebar assistant createAssistantReply
    # ------------------------------------------------------------

    pattern_sidebar = r'''function createAssistantReply\(query\) \{
\s*const lower = String\(query \|\| ""\)\.toLowerCase\(\)
'''

    replacement_sidebar = '''function createAssistantReply(query) {
        const lower = String(query || "").toLowerCase()

        const brainV2Reply = getAssistantBrainV2Reply({
            query,
            events,
            dispatches,
            heatmapData,
            backendAnalytics,
            setActiveSection,
        })

        if (brainV2Reply) {
            return brainV2Reply
        }

'''

    if "const brainV2Reply = getAssistantBrainV2Reply({" not in text:
        text, count = re.subn(pattern_sidebar, replacement_sidebar, text, count=1)

        if count == 0:
            print("warning: sidebar createAssistantReply injection not found")

    # ------------------------------------------------------------
    # Inject Brain V2 at top of floating assistant generateAssistantReply
    # ------------------------------------------------------------

    pattern_floating = r'''function generateAssistantReply\(query\) \{
\s*const lower = query\.toLowerCase\(\)
'''

    replacement_floating = '''function generateAssistantReply(query) {
        const lower = query.toLowerCase()

        const brainV2Reply = getAssistantBrainV2Reply({
            query,
            events,
            dispatches,
            heatmapData,
            backendAnalytics,
            setActiveSection,
        })

        if (brainV2Reply) {
            return brainV2Reply
        }

'''

    # Only inject if floating function does not already include Brain V2.
    generate_index = text.find("function generateAssistantReply(query)")
    send_index = text.find("function sendAssistantMessage", generate_index)
    generate_block = text[generate_index:send_index] if generate_index != -1 and send_index != -1 else ""

    if "const brainV2Reply = getAssistantBrainV2Reply({" not in generate_block:
        text, count = re.subn(pattern_floating, replacement_floating, text, count=1)

        if count == 0:
            print("warning: floating generateAssistantReply injection not found")

    # ------------------------------------------------------------
    # Improve quick prompts
    # ------------------------------------------------------------

    text = text.replace(
        '''"Give system summary",''',
        '''"System health",''',
    )

    text = text.replace(
        '''"What is the current risk?",''',
        '''"What is the current risk?",\n        "Open Authority",''',
    )

    APP_PATH.write_text(text, encoding="utf-8")

    print("assistant brain v2 patch ok")
    print(f"backup: {BACKUP_PATH}")
    print(f"updated: {APP_PATH}")


if __name__ == "__main__":
    main()