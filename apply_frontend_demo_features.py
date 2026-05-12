"""
SurakshaNet AI — Frontend Demo Feature Patch

Purpose:
- Safely update frontend/dashboard/src/App.jsx.
- Add Leaflet heatmap panel.
- Add SOS demo button.
- Add Authority Response Dispatcher panel.
- Show object/location/source fields in alert cards.

Safety:
- Only modifies frontend/dashboard/src/App.jsx.
- Creates a backup before editing.
- Does not touch backend, detection, tracking, pipeline, database, or event engine.
- Fails loudly if expected code blocks are not found.
"""

from pathlib import Path


APP_PATH = Path("frontend/dashboard/src/App.jsx")
BACKUP_PATH = Path("frontend/dashboard/src/App.jsx.backup_before_demo_features")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    """
    Replace one exact block.

    Raises an error if the expected old block is not found.
    This prevents accidental partial/corrupt edits.
    """

    if old not in text:
        raise RuntimeError(f"Could not find expected block: {label}")

    return text.replace(old, new, 1)


def insert_before(text: str, marker: str, insert: str, label: str) -> str:
    """
    Insert text before a known marker.
    """

    if marker not in text:
        raise RuntimeError(f"Could not find insert marker: {label}")

    return text.replace(marker, insert + marker, 1)


def main():
    if not APP_PATH.exists():
        raise FileNotFoundError(f"Missing file: {APP_PATH}")

    source = APP_PATH.read_text(encoding="utf-8")

    # Backup once.
    if not BACKUP_PATH.exists():
        BACKUP_PATH.write_text(source, encoding="utf-8")

    text = source

    # ------------------------------------------------------------------
    # 1. Leaflet imports + marker fix
    # ------------------------------------------------------------------

    text = replace_once(
        text,
        'import { useEffect, useMemo, useRef, useState } from "react"',
        '''import { useEffect, useMemo, useRef, useState } from "react"
import { Circle, MapContainer, Marker, Popup, TileLayer } from "react-leaflet"
import L from "leaflet"
import "leaflet/dist/leaflet.css"

/*
|--------------------------------------------------------------------------
| Leaflet Marker Fix
|--------------------------------------------------------------------------
| Reason:
| - Vite sometimes does not resolve Leaflet's default marker image paths.
| - This keeps dashboard map markers visible without changing project
|   architecture or adding custom image assets.
*/
delete L.Icon.Default.prototype._getIconUrl

L.Icon.Default.mergeOptions({
    iconRetinaUrl:
        "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
    iconUrl:
        "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
    shadowUrl:
        "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
})''',
        "React import",
    )

    # ------------------------------------------------------------------
    # 2. Add demo state
    # ------------------------------------------------------------------

    text = replace_once(
        text,
        '''    const [backendAnalytics, setBackendAnalytics] = useState(null)
    const [analyticsByType, setAnalyticsByType] = useState([])
    const [riskZones, setRiskZones] = useState([])''',
        '''    const [backendAnalytics, setBackendAnalytics] = useState(null)
    const [analyticsByType, setAnalyticsByType] = useState([])
    const [riskZones, setRiskZones] = useState([])

    /*
    |--------------------------------------------------------------------------
    | Demo Feature Completion V1 State
    |--------------------------------------------------------------------------
    | heatmapData:
    | - Loaded from GET /analytics/heatmap
    | - Used by the Leaflet safety heatmap panel.
    |
    | dispatches:
    | - Loaded from GET /dispatches
    | - Used by Authority Response Dispatcher panel.
    |
    | sosLoading:
    | - Prevents double-click spam while SOS request is being sent.
    */

    const [heatmapData, setHeatmapData] = useState(null)
    const [dispatches, setDispatches] = useState([])
    const [sosLoading, setSosLoading] = useState(false)''',
        "analytics state",
    )

    # ------------------------------------------------------------------
    # 3. Extend backend analytics loader
    # ------------------------------------------------------------------

    text = replace_once(
        text,
        '''    async function loadBackendAnalytics() {
        try {
            const [summaryRes, typeRes, zonesRes] = await Promise.all([
                fetch(`${API_BASE}/analytics/summary`),
                fetch(`${API_BASE}/analytics/by-type`),
                fetch(`${API_BASE}/analytics/risk-zones`),
            ])

            if (!summaryRes.ok || !typeRes.ok || !zonesRes.ok) {
                throw new Error("Failed to fetch backend analytics")
            }

            const summaryData = await summaryRes.json()
            const typeData = await typeRes.json()
            const zonesData = await zonesRes.json()

            setBackendAnalytics(summaryData)
            setAnalyticsByType(typeData.items || [])
            setRiskZones(zonesData.items || [])
            setLastSyncTime(new Date())
            setLastError("")
        } catch (err) {
            console.error("Failed to load backend analytics:", err)
            setLastError("Could not load backend analytics")
        }
    }''',
        '''    async function loadBackendAnalytics() {
        try {
            const [summaryRes, typeRes, zonesRes, heatmapRes, dispatchRes] =
                await Promise.all([
                    fetch(`${API_BASE}/analytics/summary`),
                    fetch(`${API_BASE}/analytics/by-type`),
                    fetch(`${API_BASE}/analytics/risk-zones`),
                    fetch(`${API_BASE}/analytics/heatmap`),
                    fetch(`${API_BASE}/dispatches`),
                ])

            if (
                !summaryRes.ok ||
                !typeRes.ok ||
                !zonesRes.ok ||
                !heatmapRes.ok ||
                !dispatchRes.ok
            ) {
                throw new Error("Failed to fetch backend analytics")
            }

            const summaryData = await summaryRes.json()
            const typeData = await typeRes.json()
            const zonesData = await zonesRes.json()
            const heatmapResponseData = await heatmapRes.json()
            const dispatchResponseData = await dispatchRes.json()

            setBackendAnalytics(summaryData)
            setAnalyticsByType(typeData.items || [])
            setRiskZones(zonesData.items || [])
            setHeatmapData(heatmapResponseData)
            setDispatches(dispatchResponseData.dispatches || [])
            setLastSyncTime(new Date())
            setLastError("")
        } catch (err) {
            console.error("Failed to load backend analytics:", err)
            setLastError("Could not load backend analytics")
        }
    }''',
        "loadBackendAnalytics",
    )

    # ------------------------------------------------------------------
    # 4. Add SOS function before Initial Data Load
    # ------------------------------------------------------------------

    text = insert_before(
        text,
        '''    /*
    |--------------------------------------------------------------------------
    | Initial Data Load
    |--------------------------------------------------------------------------
    | Runs only after login.
    */''',
        '''    /*
    |--------------------------------------------------------------------------
    | Trigger SOS Demo
    |--------------------------------------------------------------------------
    | Simulates mobile app SOS:
    | Dashboard button → POST /sos → backend creates critical SOS event →
    | dispatcher creates authority response → WebSocket/dashboard updates.
    */

    async function triggerSosDemo() {
        try {
            setSosLoading(true)
            setLastError("")

            const response = await fetch(`${API_BASE}/sos`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    user_name: "Demo User",
                    phone: "demo",
                    message: "Emergency SOS triggered from dashboard demo",
                }),
            })

            if (!response.ok) {
                throw new Error("Failed to trigger SOS demo")
            }

            await loadEventHistory()
            await loadBackendAnalytics()
        } catch (err) {
            console.error("Failed to trigger SOS demo:", err)
            setLastError("Could not trigger SOS demo")
        } finally {
            setSosLoading(false)
        }
    }

''',
        "before Initial Data Load",
    )

    # ------------------------------------------------------------------
    # 5. WebSocket dispatch update handling
    # ------------------------------------------------------------------

    text = replace_once(
        text,
        '''            loadBackendAnalytics()
            setLastEventTime(new Date())''',
        '''            loadBackendAnalytics()
            setLastEventTime(new Date())

            if (event.type === "DISPATCH_UPDATE" && event.dispatch) {
                setDispatches((prev) => {
                    if (event.dispatch.id && prev.some((d) => d.id === event.dispatch.id)) {
                        return prev
                    }

                    return [event.dispatch, ...prev].slice(0, 50)
                })
            }''',
        "websocket dispatch handling",
    )

    # ------------------------------------------------------------------
    # 6. Stats + icons
    # ------------------------------------------------------------------

    text = replace_once(
        text,
        '''        let weapon = 0
        let critical = 0''',
        '''        let weapon = 0
        let sos = 0
        let critical = 0''',
        "stats sos variable",
    )

    text = replace_once(
        text,
        '''            if (e.type === "WEAPON_DETECTED") weapon++

            if (e.severity === "CRITICAL") critical++''',
        '''            if (e.type === "WEAPON_DETECTED") weapon++
            if (e.type === "SOS_ALERT") sos++

            if (e.severity === "CRITICAL") critical++''',
        "stats sos count",
    )

    text = replace_once(
        text,
        '''            weapon,
            critical,''',
        '''            weapon,
            sos,
            critical,''',
        "stats sos return",
    )

    text = replace_once(
        text,
        '''        if (type === "WEAPON_DETECTED") return "🔴"

        return "📡"''',
        '''        if (type === "WEAPON_DETECTED") return "🔴"
        if (type === "SOS_ALERT") return "🆘"
        if (type === "DISPATCH_UPDATE") return "🚓"

        return "📡"''',
        "event icons",
    )

    # ------------------------------------------------------------------
    # 7. Pass props into ControlsPanel and MainDashboardGrid
    # ------------------------------------------------------------------

    text = replace_once(
        text,
        '''                            triggerTestAlert={triggerTestAlert}
                            exportReport={exportReport}''',
        '''                            triggerTestAlert={triggerTestAlert}
                            triggerSosDemo={triggerSosDemo}
                            sosLoading={sosLoading}
                            exportReport={exportReport}''',
        "ControlsPanel props",
    )

    text = replace_once(
        text,
        '''                            backendAnalytics={backendAnalytics}
                            getSeverityColor={getSeverityColor}''',
        '''                            backendAnalytics={backendAnalytics}
                            heatmapData={heatmapData}
                            dispatches={dispatches}
                            getSeverityColor={getSeverityColor}''',
        "MainDashboardGrid props",
    )

    # ------------------------------------------------------------------
    # 8. ControlsPanel function props + button
    # ------------------------------------------------------------------

    text = replace_once(
        text,
        '''function ControlsPanel({
    typeFilter,
    setTypeFilter,
    severityFilter,
    setSeverityFilter,
    limitFilter,
    setLimitFilter,
    loadEventHistory,
    triggerTestAlert,
    exportReport,
    exportDailySummary,
    clearEventHistory,
    clearReviewedState,
}) {''',
        '''function ControlsPanel({
    typeFilter,
    setTypeFilter,
    severityFilter,
    setSeverityFilter,
    limitFilter,
    setLimitFilter,
    loadEventHistory,
    triggerTestAlert,
    triggerSosDemo,
    sosLoading,
    exportReport,
    exportDailySummary,
    clearEventHistory,
    clearReviewedState,
}) {''',
        "ControlsPanel signature",
    )

    text = replace_once(
        text,
        '''gridTemplateColumns: "1fr 1fr 1fr auto auto auto auto auto auto auto",''',
        '''gridTemplateColumns: "1fr 1fr 1fr auto auto auto auto auto auto auto auto",''',
        "ControlsPanel columns",
    )

    text = replace_once(
        text,
        '''                        ["WEAPON_DETECTED", "Weapon Detected"],''',
        '''                        ["WEAPON_DETECTED", "Weapon Detected"],
                        ["SOS_ALERT", "SOS Alert"],
                        ["DISPATCH_UPDATE", "Dispatch Update"],''',
        "event type filter options",
    )

    text = replace_once(
        text,
        '''                <ActionButton label="Test Alert" color="#92400e" onClick={triggerTestAlert} />
                <ActionButton label="Export JSON" color="#0f766e" onClick={() => exportReport("json")} />''',
        '''                <ActionButton label="Test Alert" color="#92400e" onClick={triggerTestAlert} />
                <ActionButton
                    label={sosLoading ? "SOS..." : "Trigger SOS"}
                    color="#dc2626"
                    onClick={triggerSosDemo}
                    disabled={sosLoading}
                />
                <ActionButton label="Export JSON" color="#0f766e" onClick={() => exportReport("json")} />''',
        "SOS button",
    )

    # ------------------------------------------------------------------
    # 9. MainDashboardGrid props + panels
    # ------------------------------------------------------------------

    text = replace_once(
        text,
        '''function MainDashboardGrid({
    events,
    stats,
    backendAnalytics,
    getSeverityColor,''',
        '''function MainDashboardGrid({
    events,
    stats,
    backendAnalytics,
    heatmapData,
    dispatches,
    getSeverityColor,''',
        "MainDashboardGrid signature",
    )

    text = replace_once(
        text,
        '''                <div style={{ marginTop: "18px" }}>
                    <Panel title="🧠 System Intelligence">''',
        '''                <div style={{ marginTop: "18px" }}>
                    <HeatmapPanel heatmapData={heatmapData} />
                </div>

                <div style={{ marginTop: "18px" }}>
                    <AuthorityResponsePanel dispatches={dispatches} />
                </div>

                <div style={{ marginTop: "18px" }}>
                    <Panel title="🧠 System Intelligence">''',
        "insert heatmap and dispatch panels",
    )

    # ------------------------------------------------------------------
    # 10. KpiRow SOS card
    # ------------------------------------------------------------------

    text = replace_once(
        text,
        '''                gridTemplateColumns: "repeat(5, 1fr)",''',
        '''                gridTemplateColumns: "repeat(6, 1fr)",''',
        "KpiRow columns",
    )

    text = replace_once(
        text,
        '''            <StatCard title="Weapons" value={stats.weapon} color="#dc2626" />''',
        '''            <StatCard title="Weapons" value={stats.weapon} color="#dc2626" />
            <StatCard title="SOS" value={stats.sos} color="#dc2626" />''',
        "KpiRow SOS card",
    )

    # ------------------------------------------------------------------
    # 11. Add new components before LiveFeedPanel
    # ------------------------------------------------------------------

    text = insert_before(
        text,
        "function LiveFeedPanel() {",
        r'''function getRiskColor(riskLevel) {
    if (riskLevel === "CRITICAL") return "#dc2626"
    if (riskLevel === "HIGH") return "#ef4444"
    if (riskLevel === "MEDIUM") return "#f59e0b"
    if (riskLevel === "LOW") return "#22c55e"

    return "#38bdf8"
}

function HeatmapPanel({ heatmapData }) {
    const location = heatmapData?.location || {
        lat: 11.1085,
        lng: 77.3411,
        label: "Demo Laptop Location",
    }

    const heatPoints = heatmapData?.heat_points || []
    const riskLevel = heatmapData?.risk_level || "NORMAL"
    const riskScore = heatmapData?.risk_score ?? 5
    const eventCount = heatmapData?.event_count ?? 0
    const latestEventType = heatmapData?.latest_event_type || "NONE"
    const riskColor = getRiskColor(riskLevel)

    return (
        <Panel title="🗺️ Predictive Safety Heatmap">
            <div
                style={{
                    display: "grid",
                    gridTemplateColumns: "minmax(0, 2fr) minmax(260px, 1fr)",
                    gap: "14px",
                }}
            >
                <div
                    style={{
                        height: "320px",
                        borderRadius: "16px",
                        overflow: "hidden",
                        border: `1px solid ${riskColor}`,
                        background: "#020617",
                    }}
                >
                    <MapContainer
                        center={[location.lat, location.lng]}
                        zoom={14}
                        scrollWheelZoom={false}
                        style={{
                            height: "100%",
                            width: "100%",
                        }}
                    >
                        <TileLayer
                            attribution='&copy; OpenStreetMap contributors'
                            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        />

                        <Marker position={[location.lat, location.lng]}>
                            <Popup>
                                <strong>{location.label}</strong>
                                <br />
                                Events: {eventCount}
                                <br />
                                Risk: {riskLevel}
                            </Popup>
                        </Marker>

                        {heatPoints.map((point, index) => {
                            const weight = Number(point.weight || 1)
                            const radius = Math.max(120, Math.min(900, weight * 90))

                            return (
                                <Circle
                                    key={`${point.label}-${index}`}
                                    center={[point.lat, point.lng]}
                                    radius={radius}
                                    pathOptions={{
                                        color: riskColor,
                                        fillColor: riskColor,
                                        fillOpacity: 0.28,
                                        weight: 2,
                                    }}
                                >
                                    <Popup>
                                        <strong>{point.label}</strong>
                                        <br />
                                        Events: {point.event_count}
                                        <br />
                                        Latest: {point.latest_event_type}
                                    </Popup>
                                </Circle>
                            )
                        })}
                    </MapContainer>
                </div>

                <div
                    style={{
                        background: "#111827",
                        border: "1px solid #1e293b",
                        borderRadius: "16px",
                        padding: "15px",
                    }}
                >
                    <div style={{ color: "#94a3b8", fontSize: "12px", marginBottom: "8px" }}>
                        DEMO LOCATION
                    </div>

                    <div style={{ color: "#e5e7eb", fontWeight: "bold", fontSize: "18px" }}>
                        📍 {location.label}
                    </div>

                    <div style={{ color: "#94a3b8", fontSize: "13px", marginTop: "8px" }}>
                        Lat: {Number(location.lat).toFixed(4)}
                        <br />
                        Lng: {Number(location.lng).toFixed(4)}
                    </div>

                    <div
                        style={{
                            marginTop: "16px",
                            background: `${riskColor}22`,
                            border: `1px solid ${riskColor}`,
                            borderRadius: "14px",
                            padding: "13px",
                        }}
                    >
                        <div style={{ color: "#94a3b8", fontSize: "12px" }}>RISK LEVEL</div>
                        <div style={{ color: riskColor, fontWeight: "bold", fontSize: "24px" }}>
                            {riskLevel}
                        </div>
                    </div>

                    <div style={{ marginTop: "14px", color: "#cbd5e1", lineHeight: 1.7 }}>
                        <div>🔥 Risk Score: {riskScore}/100</div>
                        <div>📊 Event Count: {eventCount}</div>
                        <div>🚨 Latest Event: {latestEventType}</div>
                    </div>
                </div>
            </div>
        </Panel>
    )
}

function AuthorityResponsePanel({ dispatches }) {
    return (
        <Panel title="🚓 Authority Response Dispatcher">
            {dispatches.length === 0 ? (
                <div
                    style={{
                        color: "#94a3b8",
                        background: "#111827",
                        border: "1px dashed #334155",
                        borderRadius: "14px",
                        padding: "16px",
                        textAlign: "center",
                    }}
                >
                    No active dispatches. Trigger SOS or a high-priority alert.
                </div>
            ) : (
                <div style={{ display: "grid", gap: "10px" }}>
                    {dispatches.slice(0, 5).map((dispatch) => (
                        <div
                            key={dispatch.id || dispatch.dispatch_id}
                            style={{
                                background: "#111827",
                                border: "1px solid #2563eb",
                                borderRadius: "14px",
                                padding: "13px",
                            }}
                        >
                            <div
                                style={{
                                    display: "flex",
                                    justifyContent: "space-between",
                                    gap: "10px",
                                    alignItems: "center",
                                    marginBottom: "8px",
                                }}
                            >
                                <strong style={{ color: "#93c5fd" }}>
                                    {dispatch.unit_name}
                                </strong>

                                <Badge
                                    label={dispatch.status || "DISPATCHED"}
                                    color="#22c55e"
                                />
                            </div>

                            <div style={{ color: "#cbd5e1", fontSize: "13px", lineHeight: 1.6 }}>
                                <div>🆔 Dispatch: {dispatch.dispatch_id}</div>
                                <div>🚨 Event: {dispatch.event_type}</div>
                                <div>🚔 Unit Type: {dispatch.unit_type}</div>
                                <div>📍 Location: {dispatch.location_label}</div>
                                <div>⏱ ETA: {dispatch.eta_minutes} min</div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </Panel>
    )
}

''',
        "before LiveFeedPanel",
    )

    # ------------------------------------------------------------------
    # 12. Update ActionButton to support disabled
    # ------------------------------------------------------------------

    text = replace_once(
        text,
        '''function ActionButton({ label, color, onClick }) {
    return (
        <button
            onClick={onClick}
            style={{
                background: color,
                color: "white",
                border: "1px solid rgba(255,255,255,0.18)",
                borderRadius: "10px",
                padding: "12px 14px",
                fontWeight: "bold",
                whiteSpace: "nowrap",
            }}
        >
            {label}
        </button>
    )
}''',
        '''function ActionButton({ label, color, onClick, disabled }) {
    return (
        <button
            onClick={disabled ? undefined : onClick}
            disabled={disabled}
            style={{
                background: color,
                color: "white",
                border: "1px solid rgba(255,255,255,0.18)",
                borderRadius: "10px",
                padding: "12px 14px",
                fontWeight: "bold",
                whiteSpace: "nowrap",
                opacity: disabled ? 0.65 : 1,
            }}
        >
            {label}
        </button>
    )
}''',
        "ActionButton disabled support",
    )

    # ------------------------------------------------------------------
    # 13. Alert card richer details
    # ------------------------------------------------------------------

    text = replace_once(
        text,
        '''                {event.class && <div>🧠 Class: {event.class}</div>}

                {event.confidence !== undefined &&
                    event.confidence !== null &&
                    !Number.isNaN(Number(event.confidence)) && (
                        <div>🎯 Confidence: {Number(event.confidence).toFixed(2)}</div>
                    )}''',
        '''                {event.object_label && <div>🧠 Object: {event.object_label}</div>}
                {event.class && <div>🏷 Class: {event.class}</div>}
                {event.location_label && <div>📌 Event Location: {event.location_label}</div>}
                {event.source && <div>📡 Source: {event.source}</div>}

                {event.object_confidence !== undefined &&
                    event.object_confidence !== null &&
                    !Number.isNaN(Number(event.object_confidence)) && (
                        <div>🎯 Object Confidence: {Number(event.object_confidence).toFixed(2)}</div>
                    )}

                {event.confidence !== undefined &&
                    event.confidence !== null &&
                    !Number.isNaN(Number(event.confidence)) && (
                        <div>📈 Rule Confidence: {Number(event.confidence).toFixed(2)}</div>
                    )}''',
        "AlertCard object details",
    )

    APP_PATH.write_text(text, encoding="utf-8")

    print("frontend patch ok")
    print(f"backup: {BACKUP_PATH}")
    print(f"updated: {APP_PATH}")


if __name__ == "__main__":
    main()