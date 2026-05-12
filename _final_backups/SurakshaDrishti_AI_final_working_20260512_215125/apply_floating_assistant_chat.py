"""
SurakshaDrishti AI — Floating Assistant Chat Patch

Purpose:
- Add a floating AI Assistant button at bottom-right.
- Clicking it opens a local assistant chat panel.
- Assistant answers from existing dashboard state:
  events, dispatches, heatmapData, backendAnalytics.
- No backend changes.
- No new npm packages.
- No architecture changes.

Safety:
- Only modifies frontend/dashboard/src/App.jsx.
- Creates backup before editing.
"""

from pathlib import Path


APP_PATH = Path("frontend/dashboard/src/App.jsx")
BACKUP_PATH = Path("frontend/dashboard/src/App.jsx.backup_before_floating_assistant_chat")


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
    # 1. Render floating assistant after active emergency banner
    # ------------------------------------------------------------

    old_banner_block = '''                {latestCritical && (
                    <ActiveEmergencyBanner
                        event={latestCritical}
                        dispatches={dispatches}
                        getEventIcon={getEventIcon}
                        setActiveSection={setActiveSection}
                    />
                )}'''

    new_banner_block = '''                {latestCritical && (
                    <ActiveEmergencyBanner
                        event={latestCritical}
                        dispatches={dispatches}
                        getEventIcon={getEventIcon}
                        setActiveSection={setActiveSection}
                    />
                )}

                <FloatingAssistantWidget
                    events={events}
                    dispatches={dispatches}
                    heatmapData={heatmapData}
                    backendAnalytics={backendAnalytics}
                    setActiveSection={setActiveSection}
                />'''

    text = replace_once(
        text,
        old_banner_block,
        new_banner_block,
        "insert floating assistant widget",
    )

    # ------------------------------------------------------------
    # 2. Add FloatingAssistantWidget component before SectionPlaceholder
    # ------------------------------------------------------------

    assistant_component = r'''function FloatingAssistantWidget({
    events,
    dispatches,
    heatmapData,
    backendAnalytics,
    setActiveSection,
}) {
    const [assistantOpen, setAssistantOpen] = useState(false)
    const [assistantInput, setAssistantInput] = useState("")
    const [assistantMessages, setAssistantMessages] = useState([
        {
            role: "assistant",
            text:
                "Hello, I am SurakshaNet Command Assistant. Ask about alerts, SOS, heatmap risk, pending incidents, or what to do next.",
        },
    ])

    function getDispatchSummary() {
        const summary = {
            pending: 0,
            assigned: 0,
            running: 0,
            resolved: 0,
        }

        ;(dispatches || []).forEach((dispatch) => {
            const status = dispatch.status || "PENDING"

            if (status === "PENDING") summary.pending += 1
            else if (status === "ASSIGNED") summary.assigned += 1
            else if (status === "DISPATCHED") summary.running += 1
            else if (status === "RESOLVED") summary.resolved += 1
        })

        return summary
    }

    function getLatestEvent() {
        if (!events || events.length === 0) {
            return null
        }

        return [...events].sort((a, b) => {
            const aTime = new Date(a.created_at || a.timestamp || 0).getTime()
            const bTime = new Date(b.created_at || b.timestamp || 0).getTime()

            return bTime - aTime
        })[0]
    }

    function formatDispatch(dispatch, index) {
        const statusLabel =
            dispatch.status === "DISPATCHED" ? "RUNNING" : dispatch.status || "PENDING"

        return `${index + 1}. ${dispatch.dispatch_id} — ${dispatch.unit_type} — ${dispatch.event_type} — ${statusLabel} — ${dispatch.location_label}`
    }

    function generateAssistantReply(query) {
        const lower = query.toLowerCase()
        const summary = getDispatchSummary()
        const latestEvent = getLatestEvent()
        const totalEvents = backendAnalytics?.total_events ?? events?.length ?? 0
        const riskLevel = heatmapData?.risk_level || "UNKNOWN"
        const riskScore = heatmapData?.risk_score ?? "N/A"
        const latestHeatmapEvent = heatmapData?.latest_event_type || "NONE"

        const pendingDispatches = (dispatches || []).filter(
            (dispatch) => dispatch.status === "PENDING"
        )

        const runningDispatches = (dispatches || []).filter(
            (dispatch) => dispatch.status === "DISPATCHED"
        )

        const unresolvedSos = (events || []).filter((event) => {
            if (event.type !== "SOS_ALERT") return false

            const related = (dispatches || []).filter(
                (dispatch) => Number(dispatch.event_id) === Number(event.db_id)
            )

            if (related.length === 0) return true

            return related.some((dispatch) => dispatch.status !== "RESOLVED")
        })

        if (
            lower.includes("latest") ||
            lower.includes("last alert") ||
            lower.includes("recent alert")
        ) {
            if (!latestEvent) {
                return "No alerts are currently available in the dashboard history."
            }

            return [
                `Latest alert: ${latestEvent.type || "UNKNOWN"}`,
                `Severity: ${latestEvent.severity || "INFO"}`,
                `Message: ${latestEvent.message || "No message"}`,
                `Location: ${latestEvent.location_label || latestEvent.camera_location || "Unknown"}`,
                `Source: ${latestEvent.source || "camera_ai"}`,
            ].join("\\n")
        }

        if (
            lower.includes("pending") ||
            lower.includes("authority") ||
            lower.includes("dispatch")
        ) {
            if (pendingDispatches.length === 0) {
                return `There are no pending authority incidents. Current counts: Pending ${summary.pending}, Assigned ${summary.assigned}, Running ${summary.running}, Resolved ${summary.resolved}.`
            }

            return [
                `There are ${pendingDispatches.length} pending authority incidents:`,
                ...pendingDispatches.slice(0, 6).map(formatDispatch),
                "",
                "Recommended action: open Authority section, assign pending units, then mark them Running.",
            ].join("\\n")
        }

        if (lower.includes("running") || lower.includes("en route")) {
            if (runningDispatches.length === 0) {
                return "No authority units are currently marked as Running."
            }

            return [
                `There are ${runningDispatches.length} running authority responses:`,
                ...runningDispatches.slice(0, 6).map(formatDispatch),
            ].join("\\n")
        }

        if (lower.includes("sos") || lower.includes("emergency")) {
            if (unresolvedSos.length === 0) {
                return "There are no unresolved SOS alerts right now."
            }

            return [
                `There are ${unresolvedSos.length} unresolved SOS alert(s).`,
                `Top SOS: ${unresolvedSos[0].incident_type || unresolvedSos[0].type}`,
                `Location: ${
                    unresolvedSos[0].incident_location ||
                    unresolvedSos[0].location_label ||
                    "Unknown"
                }`,
                `Help needed: ${
                    Array.isArray(unresolvedSos[0].help_needed)
                        ? unresolvedSos[0].help_needed.join(", ")
                        : unresolvedSos[0].help_needed || "Authority response required"
                }`,
                "",
                "Recommended action: go to Authority section and resolve linked response units after handling.",
            ].join("\\n")
        }

        if (
            lower.includes("risk") ||
            lower.includes("heatmap") ||
            lower.includes("location")
        ) {
            return [
                `Current heatmap risk level: ${riskLevel}`,
                `Risk score: ${riskScore}/100`,
                `Total events: ${totalEvents}`,
                `Latest heatmap event: ${latestHeatmapEvent}`,
                `Demo location: ${heatmapData?.location?.label || "Demo Laptop Location"}`,
            ].join("\\n")
        }

        if (
            lower.includes("summary") ||
            lower.includes("today") ||
            lower.includes("status")
        ) {
            return [
                "Current system summary:",
                `Total events: ${totalEvents}`,
                `Heatmap risk: ${riskLevel}`,
                `Pending authority incidents: ${summary.pending}`,
                `Assigned incidents: ${summary.assigned}`,
                `Running incidents: ${summary.running}`,
                `Resolved incidents: ${summary.resolved}`,
                `Unresolved SOS alerts: ${unresolvedSos.length}`,
            ].join("\\n")
        }

        if (
            lower.includes("what should") ||
            lower.includes("next") ||
            lower.includes("recommend")
        ) {
            if (summary.pending > 0) {
                return "Recommended next action: open Authority section and assign all pending incidents. After assigning, mark units as Running, then Resolve after response is completed."
            }

            if (summary.running > 0) {
                return "Recommended next action: monitor Running authority responses. Resolve each incident after the response is completed."
            }

            if (unresolvedSos.length > 0) {
                return "Recommended next action: review unresolved SOS alerts and verify all linked authority units are handled."
            }

            return "System looks stable. Continue monitoring Live Feed, Alerts, Heatmap, and Authority sections."
        }

        if (lower.includes("open alerts")) {
            setActiveSection("alerts")
            return "Opening Alerts section."
        }

        if (lower.includes("open authority")) {
            setActiveSection("authority")
            return "Opening Authority section."
        }

        if (lower.includes("open sos")) {
            setActiveSection("sos")
            return "Opening SOS Control section."
        }

        if (lower.includes("open heatmap")) {
            setActiveSection("heatmap")
            return "Opening Heatmap section."
        }

        return [
            "I can help with:",
            "• latest alert",
            "• pending incidents",
            "• running responses",
            "• unresolved SOS",
            "• heatmap risk",
            "• current summary",
            "• what should I do next",
            "",
            "Try asking: “What should I do next?”",
        ].join("\\n")
    }

    function sendAssistantMessage(message = assistantInput) {
        const cleanMessage = String(message || "").trim()

        if (!cleanMessage) {
            return
        }

        const reply = generateAssistantReply(cleanMessage)

        setAssistantMessages((prev) => [
            ...prev,
            {
                role: "user",
                text: cleanMessage,
            },
            {
                role: "assistant",
                text: reply,
            },
        ])

        setAssistantInput("")
    }

    const quickPrompts = [
        "What is the latest alert?",
        "Show pending incidents",
        "What is the current risk?",
        "What should I do next?",
    ]

    return (
        <>
            {assistantOpen && (
                <div
                    style={{
                        position: "fixed",
                        right: "22px",
                        bottom: "92px",
                        width: "390px",
                        maxWidth: "calc(100vw - 32px)",
                        height: "560px",
                        maxHeight: "calc(100vh - 120px)",
                        background: "#020617",
                        border: "1px solid #2563eb",
                        borderRadius: "20px",
                        boxShadow: "0 24px 80px rgba(0,0,0,0.45)",
                        zIndex: 9999,
                        display: "flex",
                        flexDirection: "column",
                        overflow: "hidden",
                    }}
                >
                    <div
                        style={{
                            padding: "14px 16px",
                            borderBottom: "1px solid #1e293b",
                            background: "linear-gradient(90deg, #1e3a8a, #020617)",
                            display: "flex",
                            justifyContent: "space-between",
                            alignItems: "center",
                            gap: "10px",
                        }}
                    >
                        <div>
                            <div style={{ color: "#bfdbfe", fontSize: "12px", fontWeight: "bold" }}>
                                SURAKSHANET COMMAND ASSISTANT
                            </div>
                            <div style={{ color: "white", fontWeight: "bold", fontSize: "16px" }}>
                                🤖 Ask about alerts, SOS, heatmap, authority
                            </div>
                        </div>

                        <button
                            onClick={() => setAssistantOpen(false)}
                            style={{
                                background: "#111827",
                                color: "white",
                                border: "1px solid #334155",
                                borderRadius: "10px",
                                padding: "6px 9px",
                                fontWeight: "bold",
                            }}
                        >
                            ✕
                        </button>
                    </div>

                    <div
                        style={{
                            padding: "12px",
                            display: "flex",
                            flexWrap: "wrap",
                            gap: "8px",
                            borderBottom: "1px solid #1e293b",
                        }}
                    >
                        {quickPrompts.map((prompt) => (
                            <button
                                key={prompt}
                                onClick={() => sendAssistantMessage(prompt)}
                                style={{
                                    background: "#111827",
                                    color: "#cbd5e1",
                                    border: "1px solid #334155",
                                    borderRadius: "999px",
                                    padding: "7px 10px",
                                    fontSize: "12px",
                                    fontWeight: "bold",
                                }}
                            >
                                {prompt}
                            </button>
                        ))}
                    </div>

                    <div
                        className="scroll-soft"
                        style={{
                            flex: 1,
                            overflowY: "auto",
                            padding: "14px",
                            display: "grid",
                            gap: "10px",
                            alignContent: "start",
                        }}
                    >
                        {assistantMessages.map((message, index) => (
                            <div
                                key={`${message.role}-${index}`}
                                style={{
                                    justifySelf:
                                        message.role === "user" ? "end" : "start",
                                    maxWidth: "86%",
                                    background:
                                        message.role === "user" ? "#2563eb" : "#111827",
                                    color: "white",
                                    border:
                                        message.role === "user"
                                            ? "1px solid #93c5fd"
                                            : "1px solid #334155",
                                    borderRadius: "14px",
                                    padding: "10px 12px",
                                    whiteSpace: "pre-wrap",
                                    lineHeight: 1.5,
                                    fontSize: "13px",
                                }}
                            >
                                {message.text}
                            </div>
                        ))}
                    </div>

                    <form
                        onSubmit={(event) => {
                            event.preventDefault()
                            sendAssistantMessage()
                        }}
                        style={{
                            padding: "12px",
                            borderTop: "1px solid #1e293b",
                            display: "flex",
                            gap: "8px",
                        }}
                    >
                        <input
                            value={assistantInput}
                            onChange={(event) => setAssistantInput(event.target.value)}
                            placeholder="Ask about alerts, SOS, risk..."
                            style={{
                                flex: 1,
                                background: "#111827",
                                color: "white",
                                border: "1px solid #334155",
                                borderRadius: "12px",
                                padding: "11px",
                                fontWeight: "bold",
                                minWidth: 0,
                            }}
                        />

                        <button
                            type="submit"
                            style={{
                                background: "#2563eb",
                                color: "white",
                                border: "1px solid #93c5fd",
                                borderRadius: "12px",
                                padding: "0 14px",
                                fontWeight: "bold",
                            }}
                        >
                            Send
                        </button>
                    </form>
                </div>
            )}

            <button
                onClick={() => setAssistantOpen((prev) => !prev)}
                title="Open SurakshaNet Command Assistant"
                style={{
                    position: "fixed",
                    right: "22px",
                    bottom: "22px",
                    width: "58px",
                    height: "58px",
                    borderRadius: "999px",
                    background: assistantOpen
                        ? "linear-gradient(135deg, #2563eb, #1d4ed8)"
                        : "linear-gradient(135deg, #22c55e, #2563eb)",
                    color: "white",
                    border: "1px solid rgba(255,255,255,0.45)",
                    boxShadow: "0 18px 50px rgba(37, 99, 235, 0.45)",
                    zIndex: 10000,
                    fontSize: "26px",
                    cursor: "pointer",
                }}
            >
                🤖
            </button>
        </>
    )
}

'''

    text = insert_before(
        text,
        "function SectionPlaceholder({",
        assistant_component,
        "before SectionPlaceholder",
    )

    APP_PATH.write_text(text, encoding="utf-8")

    print("floating assistant chat patch ok")
    print(f"backup: {BACKUP_PATH}")
    print(f"updated: {APP_PATH}")


if __name__ == "__main__":
    main()
