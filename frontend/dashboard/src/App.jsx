import { useEffect, useMemo, useRef, useState } from "react"

export default function App() {
    const [events, setEvents] = useState([])
    const [connectionStatus, setConnectionStatus] = useState("CONNECTING")
    const [latestToast, setLatestToast] = useState(null)

    // 🟢 CHANGED: Added backend health/loading states
    // REASON: Dashboard should clearly show backend availability during demos

    const [backendStatus, setBackendStatus] = useState("CHECKING")
    const [lastError, setLastError] = useState("")

    // 🟢 CHANGED: Added backend analytics state
    // REASON: Dashboard should sync summary data from backend analytics APIs

    const [backendAnalytics, setBackendAnalytics] = useState(null)
    const [analyticsByType, setAnalyticsByType] = useState([])
    const [riskZones, setRiskZones] = useState([])

    // 🟢 CHANGED: Added dashboard filter state
    // REASON: Allow operator to filter saved event history from database

    const [typeFilter, setTypeFilter] = useState("")
    const [severityFilter, setSeverityFilter] = useState("")
    const [limitFilter, setLimitFilter] = useState(100)

    const audioRef = useRef(null)

    useEffect(() => {
        audioRef.current = new Audio(
            "data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEAESsAACJWAAACABAAZGF0YQAAAAA="
        )
    }, [])

    async function checkBackendHealth() {
        try {
            const response = await fetch("http://127.0.0.1:8000/health")

            if (!response.ok) {
                throw new Error("Backend health check failed")
            }

            setBackendStatus("ONLINE")
            setLastError("")
        } catch (err) {
            console.error("Backend health error:", err)
            setBackendStatus("OFFLINE")
            setLastError("Backend is offline or not reachable")
        }
    }

    async function loadEventHistory() {
        try {
            const params = new URLSearchParams()

            if (typeFilter) {
                params.append("type", typeFilter)
            }

            if (severityFilter) {
                params.append("severity", severityFilter)
            }

            params.append("limit", limitFilter)

            const response = await fetch(
                `http://127.0.0.1:8000/events?${params.toString()}`
            )

            if (!response.ok) {
                throw new Error("Failed to fetch event history")
            }

            const data = await response.json()

            setEvents(data.events || [])
            setLastError("")
        } catch (err) {
            console.error("Failed to load event history:", err)
            setLastError("Could not load event history")
        }
    }

    async function loadBackendAnalytics() {
        try {
            const [summaryRes, typeRes, zonesRes] = await Promise.all([
                fetch("http://127.0.0.1:8000/analytics/summary"),
                fetch("http://127.0.0.1:8000/analytics/by-type"),
                fetch("http://127.0.0.1:8000/analytics/risk-zones"),
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
            setLastError("")
        } catch (err) {
            console.error("Failed to load backend analytics:", err)
            setLastError("Could not load backend analytics")
        }
    }

    async function clearEventHistory() {
        try {
            const response = await fetch("http://127.0.0.1:8000/events", {
                method: "DELETE",
            })

            if (!response.ok) {
                throw new Error("Failed to clear events")
            }

            setEvents([])
            setLatestToast(null)
            await loadBackendAnalytics()
            setLastError("")
        } catch (err) {
            console.error("Failed to clear events:", err)
            setLastError("Could not clear event history")
        }
    }

    function exportReport(format) {
        const params = new URLSearchParams()

        if (typeFilter) {
            params.append("type", typeFilter)
        }

        if (severityFilter) {
            params.append("severity", severityFilter)
        }

        params.append("limit", limitFilter)

        const url = `http://127.0.0.1:8000/reports/events/${format}?${params.toString()}`

        window.open(url, "_blank")
    }

    function exportDailySummary() {
        const url = "http://127.0.0.1:8000/reports/daily-summary/json"

        window.open(url, "_blank")
    }

    // 🟢 CHANGED: Added manual test alert trigger
    // REASON: Allows demo/testing without camera event being triggered

    async function triggerTestAlert() {
        try {
            const response = await fetch("http://127.0.0.1:8000/events/test", {
                method: "POST",
            })

            if (!response.ok) {
                throw new Error("Failed to trigger test alert")
            }

            await loadEventHistory()
            await loadBackendAnalytics()
            setLastError("")
        } catch (err) {
            console.error("Failed to trigger test alert:", err)
            setLastError("Could not trigger test alert")
        }
    }

    useEffect(() => {
        // 🟢 CHANGED: Check backend health with every dashboard refresh/filter change
        // REASON: Operator should know if backend APIs are online

        checkBackendHealth()
        loadEventHistory()
        loadBackendAnalytics()
    }, [typeFilter, severityFilter, limitFilter])

    useEffect(() => {
        const ws = new WebSocket("ws://127.0.0.1:8000/ws/events")

        ws.onopen = () => {
            console.log("🟢 WebSocket connected")
            setConnectionStatus("CONNECTED")
        }

        ws.onmessage = (message) => {
            let event = null

            try {
                event = JSON.parse(message.data)
            } catch (err) {
                console.error("Invalid websocket event:", err)
                return
            }

            if (typeFilter && event.type !== typeFilter) {
                return
            }

            if (severityFilter && event.severity !== severityFilter) {
                return
            }

            loadBackendAnalytics()

            setEvents((prev) => {
                if (event.db_id && prev.some((e) => e.db_id === event.db_id)) {
                    return prev
                }

                return [event, ...prev].slice(0, Number(limitFilter))
            })

            setLatestToast(event)

            setTimeout(() => {
                setLatestToast(null)
            }, 3500)

            if (
                event.severity === "CRITICAL" ||
                event.severity === "HIGH" ||
                event.type === "INTRUSION"
            ) {
                try {
                    if (audioRef.current) {
                        audioRef.current.currentTime = 0
                        audioRef.current.play()
                    }
                } catch (err) {
                    console.log("Audio blocked until user interaction")
                }
            }
        }

        ws.onerror = () => {
            setConnectionStatus("ERROR")
            setLastError("WebSocket connection error")
        }

        ws.onclose = () => {
            console.log("🔴 WebSocket disconnected")
            setConnectionStatus("DISCONNECTED")
        }

        return () => ws.close()
    }, [typeFilter, severityFilter, limitFilter])

    const stats = useMemo(() => {
        let intrusion = 0
        let loitering = 0
        let crowd = 0
        let weapon = 0
        let ppe = 0
        let critical = 0
        let high = 0
        let medium = 0
        let low = 0
        let info = 0

        const zoneCounts = {}
        const typeCounts = {}

        events.forEach((e) => {
            if (e.type === "INTRUSION") intrusion++
            if (e.type === "LOITERING") loitering++
            if (e.type === "CROWD_ALERT") crowd++
            if (e.type === "WEAPON_DETECTED") weapon++
            if (e.type === "PPE_VIOLATION") ppe++

            if (e.severity === "CRITICAL") critical++
            else if (e.severity === "HIGH") high++
            else if (e.severity === "MEDIUM") medium++
            else if (e.severity === "LOW") low++
            else info++

            if (e.zone) {
                zoneCounts[e.zone] = (zoneCounts[e.zone] || 0) + 1
            }

            if (e.type) {
                typeCounts[e.type] = (typeCounts[e.type] || 0) + 1
            }
        })

        const highestRiskZone =
            Object.entries(zoneCounts).sort((a, b) => b[1] - a[1])[0]?.[0] ||
            "No zone data"

        const topEventType =
            Object.entries(typeCounts).sort((a, b) => b[1] - a[1])[0]?.[0] ||
            "No events"

        const highPriorityCount = critical + high

        const highPriorityPercent =
            events.length > 0 ? Math.round((highPriorityCount / events.length) * 100) : 0

        return {
            intrusion,
            loitering,
            crowd,
            weapon,
            ppe,
            critical,
            high,
            medium,
            low,
            info,
            total: events.length,
            highestRiskZone,
            topEventType,
            highPriorityCount,
            highPriorityPercent,
        }
    }, [events])

    function getSeverityColor(severity) {
        if (severity === "CRITICAL") return "#dc2626"
        if (severity === "HIGH") return "#ef4444"
        if (severity === "MEDIUM") return "#f59e0b"
        if (severity === "LOW") return "#22c55e"

        return "#38bdf8"
    }

    function getEventIcon(type) {
        if (type === "INTRUSION") return "🚨"
        if (type === "LOITERING") return "🕵️"
        if (type === "CROWD_ALERT") return "👥"
        if (type === "WEAPON_DETECTED") return "🔴"
        if (type === "PPE_VIOLATION") return "🦺"

        return "📡"
    }

    function getStatusColor() {
        if (connectionStatus === "CONNECTED" && backendStatus === "ONLINE") {
            return "#22c55e"
        }

        if (connectionStatus === "CONNECTING" || backendStatus === "CHECKING") {
            return "#f59e0b"
        }

        return "#ef4444"
    }

    const latestCritical = events.find(
        (e) => e.severity === "CRITICAL" || e.severity === "HIGH"
    )

    return (
        <div
            style={{
                background: "#020617",
                minHeight: "100vh",
                color: "white",
                padding: "20px",
                fontFamily: "Arial, sans-serif",
                position: "relative",
                overflowX: "hidden",
            }}
        >
            <style>
                {`
                    @keyframes pulseAlert {
                        0% { box-shadow: 0 0 8px rgba(239, 68, 68, 0.25); }
                        50% { box-shadow: 0 0 28px rgba(239, 68, 68, 0.85); }
                        100% { box-shadow: 0 0 8px rgba(239, 68, 68, 0.25); }
                    }

                    @keyframes slideToast {
                        from { transform: translateX(120%); opacity: 0; }
                        to { transform: translateX(0); opacity: 1; }
                    }

                    @keyframes newCardGlow {
                        0% { transform: scale(1.02); filter: brightness(1.3); }
                        100% { transform: scale(1); filter: brightness(1); }
                    }

                    @keyframes liveDot {
                        0% { opacity: 0.35; }
                        50% { opacity: 1; }
                        100% { opacity: 0.35; }
                    }

                    select, button {
                        outline: none;
                    }

                    button:hover {
                        filter: brightness(1.15);
                        cursor: pointer;
                    }
                `}
            </style>

            {latestToast && (
                <ToastAlert
                    event={latestToast}
                    getSeverityColor={getSeverityColor}
                    getEventIcon={getEventIcon}
                />
            )}

            {/* HEADER */}

            <div
                style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    marginBottom: "20px",
                }}
            >
                <div>
                    <h1 style={{ margin: 0, fontSize: "32px" }}>🛡️ SurakshaNet AI</h1>

                    <p style={{ color: "#94a3b8", marginTop: "6px" }}>
                        Professional Real-Time Surveillance Command Dashboard
                    </p>
                </div>

                <div
                    style={{
                        background: "#0f172a",
                        padding: "12px 20px",
                        borderRadius: "12px",
                        border: `1px solid ${getStatusColor()}`,
                        color: getStatusColor(),
                        fontWeight: "bold",
                    }}
                >
                    <span style={{ animation: "liveDot 1s infinite" }}>●</span>{" "}
                    WS: {connectionStatus} | API: {backendStatus}
                </div>
            </div>

            {/* 🟢 CHANGED: Operator error banner */}
            {/* REASON: Show backend/API/WebSocket problems clearly instead of silent failure */}

            {lastError && (
                <div
                    style={{
                        background: "#7f1d1d",
                        border: "1px solid #ef4444",
                        color: "#fee2e2",
                        padding: "12px 16px",
                        borderRadius: "12px",
                        marginBottom: "20px",
                        fontWeight: "bold",
                    }}
                >
                    ⚠ {lastError}
                </div>
            )}

            {/* FILTER BAR */}

            <div
                style={{
                    background: "#0f172a",
                    border: "1px solid #1e293b",
                    borderRadius: "16px",
                    padding: "16px",
                    marginBottom: "20px",
                    display: "grid",
                    gridTemplateColumns: "1fr 1fr 1fr auto auto auto auto auto auto",
                    gap: "12px",
                    alignItems: "end",
                }}
            >
                <FilterSelect
                    label="Event Type"
                    value={typeFilter}
                    onChange={setTypeFilter}
                    options={[
                        ["", "All Types"],
                        ["INTRUSION", "Intrusion"],
                        ["LOITERING", "Loitering"],
                        ["CROWD_ALERT", "Crowd Alert"],
                        ["WEAPON_DETECTED", "Weapon Detected"],
                        ["PPE_VIOLATION", "PPE Violation"],
                    ]}
                />

                <FilterSelect
                    label="Severity"
                    value={severityFilter}
                    onChange={setSeverityFilter}
                    options={[
                        ["", "All Severity"],
                        ["CRITICAL", "Critical"],
                        ["HIGH", "High"],
                        ["MEDIUM", "Medium"],
                        ["LOW", "Low"],
                        ["INFO", "Info"],
                    ]}
                />

                <FilterSelect
                    label="Limit"
                    value={String(limitFilter)}
                    onChange={(value) => setLimitFilter(Number(value))}
                    options={[
                        ["20", "20 Events"],
                        ["50", "50 Events"],
                        ["100", "100 Events"],
                        ["200", "200 Events"],
                        ["500", "500 Events"],
                    ]}
                />

                <button
                    onClick={loadEventHistory}
                    style={{
                        background: "#2563eb",
                        color: "white",
                        border: "none",
                        borderRadius: "10px",
                        padding: "12px 14px",
                        fontWeight: "bold",
                    }}
                >
                    🔄 Refresh
                </button>

                <button
                    onClick={triggerTestAlert}
                    style={{
                        background: "#92400e",
                        color: "white",
                        border: "1px solid #f59e0b",
                        borderRadius: "10px",
                        padding: "12px 14px",
                        fontWeight: "bold",
                    }}
                >
                    🧪 Test Alert
                </button>

                <button
                    onClick={() => exportReport("json")}
                    style={{
                        background: "#0f766e",
                        color: "white",
                        border: "1px solid #14b8a6",
                        borderRadius: "10px",
                        padding: "12px 14px",
                        fontWeight: "bold",
                    }}
                >
                    ⬇ JSON
                </button>

                <button
                    onClick={() => exportReport("csv")}
                    style={{
                        background: "#365314",
                        color: "white",
                        border: "1px solid #84cc16",
                        borderRadius: "10px",
                        padding: "12px 14px",
                        fontWeight: "bold",
                    }}
                >
                    ⬇ CSV
                </button>

                <button
                    onClick={exportDailySummary}
                    style={{
                        background: "#581c87",
                        color: "white",
                        border: "1px solid #a855f7",
                        borderRadius: "10px",
                        padding: "12px 14px",
                        fontWeight: "bold",
                    }}
                >
                    📊 Daily
                </button>

                <button
                    onClick={clearEventHistory}
                    style={{
                        background: "#7f1d1d",
                        color: "white",
                        border: "1px solid #ef4444",
                        borderRadius: "10px",
                        padding: "12px 14px",
                        fontWeight: "bold",
                    }}
                >
                    🧹 Clear
                </button>
            </div>

            {/* CRITICAL ALERT BANNER */}

            {latestCritical && (
                <div
                    style={{
                        background: "linear-gradient(90deg, #7f1d1d, #111827)",
                        border: "2px solid #ef4444",
                        padding: "15px 20px",
                        borderRadius: "14px",
                        marginBottom: "20px",
                        animation: "pulseAlert 1.5s infinite",
                    }}
                >
                    <div
                        style={{
                            fontSize: "14px",
                            color: "#fecaca",
                            marginBottom: "6px",
                            fontWeight: "bold",
                        }}
                    >
                        ACTIVE HIGH PRIORITY ALERT
                    </div>

                    <div style={{ fontSize: "22px", fontWeight: "bold" }}>
                        {getEventIcon(latestCritical.type)} {latestCritical.type}
                    </div>

                    <div style={{ color: "#e5e7eb", marginTop: "6px" }}>
                        {latestCritical.message || "Critical surveillance event detected"}
                    </div>
                </div>
            )}

            {/* STATS */}

            <div
                style={{
                    display: "grid",
                    gridTemplateColumns: "repeat(6, 1fr)",
                    gap: "14px",
                    marginBottom: "22px",
                }}
            >
                <StatCard title="Shown Events" value={stats.total} color="#38bdf8" />
                <StatCard title="Intrusions" value={stats.intrusion} color="#ef4444" />
                <StatCard title="Loitering" value={stats.loitering} color="#f59e0b" />
                <StatCard title="Crowd" value={stats.crowd} color="#a855f7" />
                <StatCard title="Weapons" value={stats.weapon} color="#dc2626" />
                <StatCard title="PPE" value={stats.ppe} color="#22c55e" />
            </div>

            {/* ANALYTICS CARDS */}

            <div
                style={{
                    display: "grid",
                    gridTemplateColumns: "repeat(4, 1fr)",
                    gap: "14px",
                    marginBottom: "22px",
                }}
            >
                <AnalyticsCard
                    title="Database Events"
                    value={backendAnalytics?.total_events ?? stats.total}
                    subtitle="Total saved alerts in SQLite"
                    color="#38bdf8"
                />

                <AnalyticsCard
                    title="Highest Risk Zone"
                    value={riskZones[0]?.zone || "No zone data"}
                    subtitle={
                        riskZones[0]
                            ? `${riskZones[0].count} alerts recorded`
                            : "No zone alerts yet"
                    }
                    color="#ef4444"
                />

                <AnalyticsCard
                    title="Top Event Type"
                    value={analyticsByType[0]?.type || "No events"}
                    subtitle={
                        analyticsByType[0]
                            ? `${analyticsByType[0].count} events recorded`
                            : "No event type data"
                    }
                    color="#a855f7"
                />

                <AnalyticsCard
                    title="High Priority"
                    value={`${backendAnalytics?.high_priority_percent ?? stats.highPriorityPercent}%`}
                    subtitle={`${backendAnalytics?.high_priority_count ?? stats.highPriorityCount} high/critical database events`}
                    color="#f59e0b"
                />
            </div>

            {/* BACKEND ANALYTICS STATUS */}

            <div
                style={{
                    background: "#0f172a",
                    border: "1px solid #1e293b",
                    borderRadius: "14px",
                    padding: "12px 16px",
                    marginBottom: "22px",
                    color: "#94a3b8",
                    fontSize: "13px",
                }}
            >
                Backend Analytics API:{" "}
                <span style={{ color: backendAnalytics ? "#22c55e" : "#f59e0b" }}>
                    {backendAnalytics ? "SYNCED" : "LOADING"}
                </span>
            </div>

            {/* MAIN GRID */}

            <div
                style={{
                    display: "grid",
                    gridTemplateColumns: "2fr 1fr",
                    gap: "20px",
                    alignItems: "start",
                }}
            >
                <div
                    style={{
                        background: "#0f172a",
                        padding: "16px",
                        borderRadius: "16px",
                        border: "1px solid #1e293b",
                    }}
                >
                    <div
                        style={{
                            display: "flex",
                            justifyContent: "space-between",
                            alignItems: "center",
                            marginBottom: "12px",
                        }}
                    >
                        <h2 style={{ margin: 0 }}>📹 Live Camera Feed</h2>

                        <span
                            style={{
                                color: "#22c55e",
                                background: "rgba(34, 197, 94, 0.12)",
                                border: "1px solid #22c55e",
                                padding: "6px 10px",
                                borderRadius: "999px",
                                fontSize: "12px",
                                fontWeight: "bold",
                            }}
                        >
                            LIVE
                        </span>
                    </div>

                    <img
                        src="http://127.0.0.1:8000/video_feed"
                        alt="Live Feed"
                        style={{
                            width: "100%",
                            borderRadius: "12px",
                            border: "2px solid #22c55e",
                            background: "#000",
                        }}
                    />

                    <div
                        style={{
                            display: "grid",
                            gridTemplateColumns: "repeat(5, 1fr)",
                            gap: "12px",
                            marginTop: "14px",
                        }}
                    >
                        <MiniSeverityCard
                            title="Critical"
                            value={backendAnalytics?.severity?.critical ?? stats.critical}
                            color="#dc2626"
                        />

                        <MiniSeverityCard
                            title="High"
                            value={backendAnalytics?.severity?.high ?? stats.high}
                            color="#ef4444"
                        />

                        <MiniSeverityCard
                            title="Medium"
                            value={backendAnalytics?.severity?.medium ?? stats.medium}
                            color="#f59e0b"
                        />

                        <MiniSeverityCard
                            title="Low"
                            value={backendAnalytics?.severity?.low ?? stats.low}
                            color="#22c55e"
                        />

                        <MiniSeverityCard
                            title="Info"
                            value={stats.info}
                            color="#38bdf8"
                        />
                    </div>
                </div>

                <div
                    style={{
                        background: "#0f172a",
                        padding: "16px",
                        borderRadius: "16px",
                        border: "1px solid #1e293b",
                        maxHeight: "760px",
                        overflowY: "auto",
                    }}
                >
                    <h2 style={{ marginTop: 0 }}>🚨 Filtered Alerts</h2>

                    {events.length === 0 ? (
                        <div
                            style={{
                                color: "#94a3b8",
                                background: "#111827",
                                padding: "14px",
                                borderRadius: "10px",
                            }}
                        >
                            No alerts match current filters.
                        </div>
                    ) : (
                        events.map((event, index) => (
                            <AlertCard
                                key={`${event.db_id || event.type}-${index}`}
                                event={event}
                                index={index}
                                getSeverityColor={getSeverityColor}
                                getEventIcon={getEventIcon}
                            />
                        ))
                    )}
                </div>
            </div>
        </div>
    )
}

function FilterSelect({ label, value, onChange, options }) {
    return (
        <label>
            <div
                style={{
                    color: "#94a3b8",
                    marginBottom: "6px",
                    fontSize: "13px",
                    fontWeight: "bold",
                }}
            >
                {label}
            </div>

            <select
                value={value}
                onChange={(e) => onChange(e.target.value)}
                style={{
                    width: "100%",
                    background: "#111827",
                    color: "white",
                    border: "1px solid #334155",
                    borderRadius: "10px",
                    padding: "11px",
                    fontWeight: "bold",
                }}
            >
                {options.map(([optionValue, optionLabel]) => (
                    <option key={optionValue} value={optionValue}>
                        {optionLabel}
                    </option>
                ))}
            </select>
        </label>
    )
}

function AnalyticsCard({ title, value, subtitle, color }) {
    return (
        <div
            style={{
                background: "#0f172a",
                border: `1px solid ${color}`,
                borderRadius: "16px",
                padding: "16px",
                minHeight: "110px",
            }}
        >
            <div
                style={{
                    color: "#94a3b8",
                    fontSize: "13px",
                    fontWeight: "bold",
                    marginBottom: "10px",
                }}
            >
                {title}
            </div>

            <div
                style={{
                    color,
                    fontSize: typeof value === "number" ? "34px" : "22px",
                    fontWeight: "bold",
                    marginBottom: "8px",
                    wordBreak: "break-word",
                }}
            >
                {value}
            </div>

            <div
                style={{
                    color: "#cbd5e1",
                    fontSize: "13px",
                    lineHeight: 1.4,
                }}
            >
                {subtitle}
            </div>
        </div>
    )
}

function ToastAlert({ event, getSeverityColor, getEventIcon }) {
    const severity = event.severity || "INFO"
    const color = getSeverityColor(severity)

    return (
        <div
            style={{
                position: "fixed",
                top: "24px",
                right: "24px",
                zIndex: 9999,
                width: "360px",
                background: "#111827",
                border: `2px solid ${color}`,
                borderLeft: `8px solid ${color}`,
                borderRadius: "14px",
                padding: "16px",
                animation: "slideToast 0.35s ease-out",
                boxShadow: `0 0 24px ${color}66`,
            }}
        >
            <div style={{ color, fontWeight: "bold", fontSize: "16px", marginBottom: "8px" }}>
                {getEventIcon(event.type)} {event.type}
            </div>

            <div style={{ color: "#e5e7eb", fontSize: "14px", lineHeight: 1.5 }}>
                {event.message || "New realtime surveillance event received"}
            </div>

            <div style={{ marginTop: "10px", color, fontSize: "12px", fontWeight: "bold" }}>
                {severity}
            </div>
        </div>
    )
}

function StatCard({ title, value, color }) {
    return (
        <div
            style={{
                background: "#0f172a",
                padding: "16px",
                borderRadius: "15px",
                border: `2px solid ${color}`,
            }}
        >
            <div style={{ color: "#94a3b8", marginBottom: "8px", fontSize: "14px" }}>
                {title}
            </div>

            <div style={{ fontSize: "30px", fontWeight: "bold", color }}>{value}</div>
        </div>
    )
}

function MiniSeverityCard({ title, value, color }) {
    return (
        <div
            style={{
                background: "#111827",
                border: `1px solid ${color}`,
                borderRadius: "12px",
                padding: "12px",
            }}
        >
            <div style={{ color: "#94a3b8", fontSize: "13px" }}>{title}</div>

            <div style={{ color, fontSize: "24px", fontWeight: "bold", marginTop: "4px" }}>
                {value}
            </div>
        </div>
    )
}

function AlertCard({ event, index, getSeverityColor, getEventIcon }) {
    const severity = event.severity || "INFO"
    const color = getSeverityColor(severity)

    return (
        <div
            style={{
                background: "#111827",
                borderLeft: `6px solid ${color}`,
                padding: "13px",
                marginBottom: "12px",
                borderRadius: "12px",
                animation: index === 0 ? "newCardGlow 0.5s ease-out" : "none",
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
                <div style={{ fontWeight: "bold", color, fontSize: "16px" }}>
                    {getEventIcon(event.type)} {event.type}
                </div>

                <span
                    style={{
                        background: `${color}22`,
                        color,
                        border: `1px solid ${color}`,
                        padding: "4px 8px",
                        borderRadius: "999px",
                        fontSize: "11px",
                        fontWeight: "bold",
                    }}
                >
                    {severity}
                </span>
            </div>

            {event.message && (
                <div style={{ color: "#e5e7eb", marginBottom: "8px", fontSize: "14px" }}>
                    {event.message}
                </div>
            )}

            <div style={{ color: "#cbd5e1", fontSize: "14px", lineHeight: 1.6 }}>
                {event.db_id !== undefined && <div>🗃 DB ID: {event.db_id}</div>}

                {event.object_id !== undefined && <div>👤 Object ID: {event.object_id}</div>}

                {event.zone && <div>📍 Zone: {event.zone}</div>}

                {event.camera_id && <div>📷 Camera ID: {event.camera_id}</div>}

                {event.camera_name && <div>🎥 Camera: {event.camera_name}</div>}

                {event.camera_location && <div>🗺 Location: {event.camera_location}</div>}

                {event.timestamp && <div>⏱ Event Time: {event.timestamp}</div>}

                {event.person_count !== undefined && <div>👥 Person Count: {event.person_count}</div>}

                {event.duration_seconds !== undefined && <div>⏱ Duration: {event.duration_seconds}s</div>}

                {event.class && <div>🧠 Class: {event.class}</div>}

                {/* 🟢 CHANGED: Safe confidence display */}
                {/* REASON: Old DB events may have null/string confidence and toFixed() can crash dashboard */}

                {event.confidence !== undefined &&
                    event.confidence !== null &&
                    !Number.isNaN(Number(event.confidence)) && (
                        <div>🎯 Confidence: {Number(event.confidence).toFixed(2)}</div>
                    )}

                {event.created_at && <div>🕒 Time: {event.created_at}</div>}
            </div>
        </div>
    )
}