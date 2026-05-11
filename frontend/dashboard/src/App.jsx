import { useEffect, useMemo, useRef, useState } from "react"

const API_BASE = "http://127.0.0.1:8000"
const WS_URL = "ws://127.0.0.1:8000/ws/events"

export default function App() {
    const [events, setEvents] = useState([])
    const [connectionStatus, setConnectionStatus] = useState("CONNECTING")
    const [latestToast, setLatestToast] = useState(null)

    // 🟢 CHANGED: Dashboard login state
    // REASON: Keep existing demo-level dashboard authentication

    const [authToken, setAuthToken] = useState(
        localStorage.getItem("surakshanet_token") || ""
    )

    const [loginUsername, setLoginUsername] = useState("")
    const [loginPassword, setLoginPassword] = useState("")
    const [loginError, setLoginError] = useState("")
    const isAuthenticated = Boolean(authToken)

    // 🟢 CHANGED: Backend health/loading states
    // REASON: Professional UI needs clear API/WebSocket visibility

    const [backendStatus, setBackendStatus] = useState("CHECKING")
    const [lastError, setLastError] = useState("")

    // 🟢 CHANGED: Backend analytics state
    // REASON: Dashboard syncs with analytics APIs

    const [backendAnalytics, setBackendAnalytics] = useState(null)
    const [analyticsByType, setAnalyticsByType] = useState([])
    const [riskZones, setRiskZones] = useState([])

    // 🟢 CHANGED: Dashboard filters
    // REASON: Operator can filter event history

    const [typeFilter, setTypeFilter] = useState("")
    const [severityFilter, setSeverityFilter] = useState("")
    const [limitFilter, setLimitFilter] = useState(100)

    // 🟢 CHANGED: Live clock
    // REASON: Professional command dashboards show operator time

    const [clock, setClock] = useState(new Date())

    const audioRef = useRef(null)

    useEffect(() => {
        audioRef.current = new Audio(
            "data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEAESsAACJWAAACABAAZGF0YQAAAAA="
        )
    }, [])

    useEffect(() => {
        const timer = setInterval(() => {
            setClock(new Date())
        }, 1000)

        return () => clearInterval(timer)
    }, [])

    async function handleLogin(event) {
        event.preventDefault()

        try {
            setLoginError("")

            const response = await fetch(`${API_BASE}/auth/login`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    username: loginUsername,
                    password: loginPassword,
                }),
            })

            if (!response.ok) {
                throw new Error("Invalid username or password")
            }

            const data = await response.json()

            localStorage.setItem("surakshanet_token", data.token)
            setAuthToken(data.token)
            setLoginPassword("")
        } catch (err) {
            console.error("Login failed:", err)
            setLoginError("Invalid username or password")
        }
    }

    function handleLogout() {
        localStorage.removeItem("surakshanet_token")
        setAuthToken("")
        setEvents([])
        setLatestToast(null)
        setConnectionStatus("CONNECTING")
        setBackendStatus("CHECKING")
    }

    async function checkBackendHealth() {
        try {
            const response = await fetch(`${API_BASE}/health`)

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

            const response = await fetch(`${API_BASE}/events?${params.toString()}`)

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
            setLastError("")
        } catch (err) {
            console.error("Failed to load backend analytics:", err)
            setLastError("Could not load backend analytics")
        }
    }

    async function clearEventHistory() {
        try {
            const response = await fetch(`${API_BASE}/events`, {
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

        window.open(`${API_BASE}/reports/events/${format}?${params.toString()}`, "_blank")
    }

    function exportDailySummary() {
        window.open(`${API_BASE}/reports/daily-summary/json`, "_blank")
    }

    async function triggerTestAlert() {
        try {
            const response = await fetch(`${API_BASE}/events/test`, {
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
        if (!isAuthenticated) {
            return
        }

        checkBackendHealth()
        loadEventHistory()
        loadBackendAnalytics()
    }, [isAuthenticated, typeFilter, severityFilter, limitFilter])

    useEffect(() => {
        if (!isAuthenticated) {
            return
        }

        const ws = new WebSocket(WS_URL)

        ws.onopen = () => {
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
            setConnectionStatus("DISCONNECTED")
        }

        return () => ws.close()
    }, [isAuthenticated, typeFilter, severityFilter, limitFilter])

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
        let evidenceCount = 0

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

            if (e.snapshot_url || e.clip_url) {
                evidenceCount++
            }
        })

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
            highPriorityCount,
            highPriorityPercent,
            evidenceCount,
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

    function getSystemHealthColor() {
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

    const latestEvent = events[0]
    const topEventType = analyticsByType[0]?.type || "No events"
    const topRiskZone = riskZones[0]?.zone || "No zone data"

    if (!isAuthenticated) {
        return (
            <LoginScreen
                username={loginUsername}
                password={loginPassword}
                error={loginError}
                onUsernameChange={setLoginUsername}
                onPasswordChange={setLoginPassword}
                onSubmit={handleLogin}
            />
        )
    }

    return (
        <div
            style={{
                minHeight: "100vh",
                background: "#020617",
                color: "white",
                fontFamily: "Inter, Arial, sans-serif",
                display: "grid",
                gridTemplateColumns: "260px 1fr",
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

                    select, button, input {
                        outline: none;
                    }

                    button:hover {
                        filter: brightness(1.15);
                        cursor: pointer;
                    }

                    .scroll-soft::-webkit-scrollbar {
                        width: 8px;
                    }

                    .scroll-soft::-webkit-scrollbar-thumb {
                        background: #334155;
                        border-radius: 999px;
                    }

                    .scroll-soft::-webkit-scrollbar-track {
                        background: #0f172a;
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

            {/* SIDEBAR */}

            <aside
                style={{
                    background: "#020617",
                    borderRight: "1px solid #1e293b",
                    padding: "22px 18px",
                    position: "sticky",
                    top: 0,
                    height: "100vh",
                    boxSizing: "border-box",
                }}
            >
                <div style={{ marginBottom: "26px" }}>
                    <div
                        style={{
                            width: "46px",
                            height: "46px",
                            borderRadius: "14px",
                            background: "linear-gradient(135deg, #0ea5e9, #1d4ed8)",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            fontSize: "24px",
                            marginBottom: "12px",
                        }}
                    >
                        🛡️
                    </div>

                    <h2 style={{ margin: 0, fontSize: "21px" }}>SurakshaNet AI</h2>
                    <p style={{ color: "#64748b", fontSize: "13px", marginTop: "6px" }}>
                        Surveillance Command OS
                    </p>
                </div>

                <SidebarItem icon="📊" label="Dashboard" active />
                <SidebarItem icon="📹" label="Live Feed" />
                <SidebarItem icon="🚨" label="Alerts" />
                <SidebarItem icon="📈" label="Analytics" />
                <SidebarItem icon="📁" label="Reports" />
                <SidebarItem icon="⚙️" label="Settings" />

                <div
                    style={{
                        marginTop: "28px",
                        background: "#0f172a",
                        border: "1px solid #1e293b",
                        borderRadius: "16px",
                        padding: "14px",
                    }}
                >
                    <div style={{ color: "#94a3b8", fontSize: "12px", marginBottom: "8px" }}>
                        SYSTEM MODE
                    </div>

                    <div style={{ color: "#22c55e", fontWeight: "bold" }}>
                        Snapshot Evidence
                    </div>

                    <div style={{ color: "#64748b", fontSize: "12px", marginTop: "6px" }}>
                        Video clips optional for performance.
                    </div>
                </div>
            </aside>

            {/* MAIN */}

            <main
                className="scroll-soft"
                style={{
                    padding: "22px",
                    overflowY: "auto",
                    maxHeight: "100vh",
                    boxSizing: "border-box",
                }}
            >
                {/* HEADER */}

                <div
                    style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        marginBottom: "18px",
                        gap: "18px",
                    }}
                >
                    <div>
                        <h1 style={{ margin: 0, fontSize: "30px", letterSpacing: "-0.5px" }}>
                            Command Dashboard
                        </h1>

                        <p style={{ color: "#94a3b8", marginTop: "6px" }}>
                            Real-time AI surveillance, event intelligence, and evidence review.
                        </p>
                    </div>

                    <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                        <StatusPill
                            label={`WS: ${connectionStatus}`}
                            color={
                                connectionStatus === "CONNECTED"
                                    ? "#22c55e"
                                    : connectionStatus === "CONNECTING"
                                        ? "#f59e0b"
                                        : "#ef4444"
                            }
                        />

                        <StatusPill
                            label={`API: ${backendStatus}`}
                            color={backendStatus === "ONLINE" ? "#22c55e" : "#ef4444"}
                        />

                        <div
                            style={{
                                background: "#0f172a",
                                border: "1px solid #1e293b",
                                padding: "11px 14px",
                                borderRadius: "12px",
                                color: "#cbd5e1",
                                fontWeight: "bold",
                                whiteSpace: "nowrap",
                            }}
                        >
                            {clock.toLocaleTimeString()}
                        </div>

                        <button
                            onClick={handleLogout}
                            style={{
                                background: "#7f1d1d",
                                color: "white",
                                border: "1px solid #ef4444",
                                borderRadius: "12px",
                                padding: "11px 15px",
                                fontWeight: "bold",
                            }}
                        >
                            Logout
                        </button>
                    </div>
                </div>

                {/* OPERATOR STATUS BAR */}

                <div
                    style={{
                        display: "grid",
                        gridTemplateColumns: "repeat(4, 1fr)",
                        gap: "12px",
                        marginBottom: "18px",
                    }}
                >
                    <OperatorStatus
                        label="System Health"
                        value={
                            connectionStatus === "CONNECTED" && backendStatus === "ONLINE"
                                ? "Operational"
                                : "Needs Attention"
                        }
                        color={getSystemHealthColor()}
                    />

                    <OperatorStatus
                        label="Camera"
                        value="CAM-01 Main Gate"
                        color="#38bdf8"
                    />

                    <OperatorStatus
                        label="Latest Alert"
                        value={latestEvent?.type || "No alerts"}
                        color={latestEvent ? getSeverityColor(latestEvent.severity) : "#64748b"}
                    />

                    <OperatorStatus
                        label="Evidence"
                        value={`${stats.evidenceCount} captured`}
                        color="#a855f7"
                    />
                </div>

                {lastError && (
                    <div
                        style={{
                            background: "#7f1d1d",
                            border: "1px solid #ef4444",
                            color: "#fee2e2",
                            padding: "12px 16px",
                            borderRadius: "14px",
                            marginBottom: "18px",
                            fontWeight: "bold",
                        }}
                    >
                        ⚠ {lastError}
                    </div>
                )}

                {/* FILTERS */}

                <Panel title="Operator Controls" compact>
                    <div
                        style={{
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

                        <ActionButton label="🔄 Refresh" color="#2563eb" onClick={loadEventHistory} />
                        <ActionButton label="🧪 Test Alert" color="#92400e" onClick={triggerTestAlert} />
                        <ActionButton label="⬇ JSON" color="#0f766e" onClick={() => exportReport("json")} />
                        <ActionButton label="⬇ CSV" color="#365314" onClick={() => exportReport("csv")} />
                        <ActionButton label="📊 Daily" color="#581c87" onClick={exportDailySummary} />
                        <ActionButton label="🧹 Clear" color="#7f1d1d" onClick={clearEventHistory} />
                    </div>
                </Panel>

                {/* CRITICAL ALERT BANNER */}

                {latestCritical && (
                    <div
                        style={{
                            background: "linear-gradient(90deg, #7f1d1d, #111827)",
                            border: "1px solid #ef4444",
                            padding: "16px 18px",
                            borderRadius: "18px",
                            marginBottom: "18px",
                            animation: "pulseAlert 1.5s infinite",
                        }}
                    >
                        <div
                            style={{
                                color: "#fecaca",
                                fontSize: "12px",
                                fontWeight: "bold",
                                marginBottom: "7px",
                                letterSpacing: "0.5px",
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

                {/* KPI ROW */}

                <div
                    style={{
                        display: "grid",
                        gridTemplateColumns: "repeat(6, 1fr)",
                        gap: "14px",
                        marginBottom: "18px",
                    }}
                >
                    <StatCard title="Shown Events" value={stats.total} color="#38bdf8" />
                    <StatCard title="Intrusions" value={stats.intrusion} color="#ef4444" />
                    <StatCard title="Loitering" value={stats.loitering} color="#f59e0b" />
                    <StatCard title="Crowd" value={stats.crowd} color="#a855f7" />
                    <StatCard title="Weapons" value={stats.weapon} color="#dc2626" />
                    <StatCard title="PPE" value={stats.ppe} color="#22c55e" />
                </div>

                {/* ANALYTICS ROW */}

                <div
                    style={{
                        display: "grid",
                        gridTemplateColumns: "repeat(4, 1fr)",
                        gap: "14px",
                        marginBottom: "18px",
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
                        value={topRiskZone}
                        subtitle={
                            riskZones[0]
                                ? `${riskZones[0].count} alerts recorded`
                                : "No zone alerts yet"
                        }
                        color="#ef4444"
                    />

                    <AnalyticsCard
                        title="Top Event Type"
                        value={topEventType}
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

                {/* MAIN GRID */}

                <div
                    style={{
                        display: "grid",
                        gridTemplateColumns: "minmax(0, 2fr) minmax(380px, 1fr)",
                        gap: "18px",
                        alignItems: "start",
                    }}
                >
                    <div>
                        <Panel title="📹 Live AI Camera Feed">
                            <div
                                style={{
                                    position: "relative",
                                    background: "#000",
                                    borderRadius: "16px",
                                    overflow: "hidden",
                                    border: "1px solid #1e293b",
                                }}
                            >
                                <img
                                    src={`${API_BASE}/video_feed`}
                                    alt="Live Feed"
                                    style={{
                                        width: "100%",
                                        display: "block",
                                        background: "#000",
                                    }}
                                />

                                <div
                                    style={{
                                        position: "absolute",
                                        top: "12px",
                                        left: "12px",
                                        display: "flex",
                                        gap: "8px",
                                    }}
                                >
                                    <Badge label="LIVE" color="#22c55e" />
                                    <Badge label="CAM-01" color="#38bdf8" />
                                </div>
                            </div>

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
                        </Panel>

                        <div style={{ marginTop: "18px" }}>
                            <Panel title="🧠 System Intelligence">
                                <div
                                    style={{
                                        display: "grid",
                                        gridTemplateColumns: "repeat(3, 1fr)",
                                        gap: "12px",
                                    }}
                                >
                                    <InfoTile
                                        title="Risk Level"
                                        value={
                                            stats.highPriorityCount > 0
                                                ? "Elevated"
                                                : "Normal"
                                        }
                                        color={
                                            stats.highPriorityCount > 0
                                                ? "#f59e0b"
                                                : "#22c55e"
                                        }
                                    />

                                    <InfoTile
                                        title="Evidence Mode"
                                        value="Snapshots"
                                        color="#38bdf8"
                                    />

                                    <InfoTile
                                        title="Backend Analytics"
                                        value={backendAnalytics ? "Synced" : "Loading"}
                                        color={backendAnalytics ? "#22c55e" : "#f59e0b"}
                                    />
                                </div>
                            </Panel>
                        </div>
                    </div>

                    <Panel title="🚨 Live Alert Feed">
                        <div
                            className="scroll-soft"
                            style={{
                                maxHeight: "830px",
                                overflowY: "auto",
                                paddingRight: "4px",
                            }}
                        >
                            {events.length === 0 ? (
                                <EmptyState />
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
                    </Panel>
                </div>
            </main>
        </div>
    )
}

function LoginScreen({
    username,
    password,
    error,
    onUsernameChange,
    onPasswordChange,
    onSubmit,
}) {
    return (
        <div
            style={{
                minHeight: "100vh",
                background: "radial-gradient(circle at top, #0f172a, #020617 55%)",
                color: "white",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontFamily: "Arial, sans-serif",
                padding: "20px",
            }}
        >
            <form
                onSubmit={onSubmit}
                style={{
                    width: "100%",
                    maxWidth: "430px",
                    background: "rgba(15, 23, 42, 0.95)",
                    border: "1px solid #1e293b",
                    borderRadius: "24px",
                    padding: "30px",
                    boxShadow: "0 0 40px rgba(14, 165, 233, 0.16)",
                }}
            >
                <div style={{ marginBottom: "24px", textAlign: "center" }}>
                    <div
                        style={{
                            width: "58px",
                            height: "58px",
                            borderRadius: "18px",
                            background: "linear-gradient(135deg, #0ea5e9, #1d4ed8)",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            margin: "0 auto 14px",
                            fontSize: "30px",
                        }}
                    >
                        🛡️
                    </div>

                    <h1 style={{ margin: 0, fontSize: "30px" }}>SurakshaNet AI</h1>

                    <p style={{ color: "#94a3b8", marginTop: "8px" }}>
                        Secure Command Dashboard
                    </p>
                </div>

                <LoginInput
                    label="Username"
                    value={username}
                    onChange={onUsernameChange}
                    placeholder="admin"
                    type="text"
                />

                <LoginInput
                    label="Password"
                    value={password}
                    onChange={onPasswordChange}
                    placeholder="admin123"
                    type="password"
                />

                {error && (
                    <div
                        style={{
                            background: "#7f1d1d",
                            border: "1px solid #ef4444",
                            color: "#fee2e2",
                            padding: "10px 12px",
                            borderRadius: "10px",
                            marginBottom: "16px",
                            fontWeight: "bold",
                            fontSize: "14px",
                        }}
                    >
                        ⚠ {error}
                    </div>
                )}

                <button
                    type="submit"
                    style={{
                        width: "100%",
                        background: "#2563eb",
                        color: "white",
                        border: "none",
                        borderRadius: "12px",
                        padding: "13px",
                        fontWeight: "bold",
                        fontSize: "16px",
                    }}
                >
                    Login
                </button>

                <div
                    style={{
                        color: "#64748b",
                        fontSize: "12px",
                        marginTop: "16px",
                        lineHeight: 1.5,
                        textAlign: "center",
                    }}
                >
                    Demo credentials: admin / admin123
                </div>
            </form>
        </div>
    )
}

function LoginInput({ label, value, onChange, placeholder, type }) {
    return (
        <label style={{ display: "block", marginBottom: "14px" }}>
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

            <input
                type={type}
                value={value}
                onChange={(e) => onChange(e.target.value)}
                placeholder={placeholder}
                autoComplete={type === "password" ? "current-password" : "username"}
                style={{
                    width: "100%",
                    boxSizing: "border-box",
                    background: "#111827",
                    color: "white",
                    border: "1px solid #334155",
                    borderRadius: "10px",
                    padding: "12px",
                    fontWeight: "bold",
                }}
            />
        </label>
    )
}

function SidebarItem({ icon, label, active }) {
    return (
        <div
            style={{
                display: "flex",
                alignItems: "center",
                gap: "10px",
                padding: "11px 12px",
                borderRadius: "12px",
                marginBottom: "7px",
                color: active ? "#e0f2fe" : "#94a3b8",
                background: active ? "rgba(14, 165, 233, 0.14)" : "transparent",
                border: active ? "1px solid rgba(56, 189, 248, 0.3)" : "1px solid transparent",
                fontWeight: active ? "bold" : "normal",
            }}
        >
            <span>{icon}</span>
            <span>{label}</span>
        </div>
    )
}

function Panel({ title, children, compact }) {
    return (
        <section
            style={{
                background: "#0f172a",
                border: "1px solid #1e293b",
                borderRadius: "18px",
                padding: compact ? "14px" : "16px",
                marginBottom: compact ? "18px" : 0,
            }}
        >
            {title && (
                <h2
                    style={{
                        marginTop: 0,
                        marginBottom: "14px",
                        fontSize: "18px",
                    }}
                >
                    {title}
                </h2>
            )}

            {children}
        </section>
    )
}

function StatusPill({ label, color }) {
    return (
        <div
            style={{
                background: "#0f172a",
                border: `1px solid ${color}`,
                color,
                padding: "10px 12px",
                borderRadius: "999px",
                fontWeight: "bold",
                fontSize: "13px",
                whiteSpace: "nowrap",
            }}
        >
            <span style={{ animation: "liveDot 1s infinite" }}>●</span> {label}
        </div>
    )
}

function OperatorStatus({ label, value, color }) {
    return (
        <div
            style={{
                background: "#0f172a",
                border: "1px solid #1e293b",
                borderRadius: "16px",
                padding: "14px",
            }}
        >
            <div style={{ color: "#64748b", fontSize: "12px", marginBottom: "6px" }}>
                {label}
            </div>

            <div style={{ color, fontSize: "17px", fontWeight: "bold" }}>{value}</div>
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

function ActionButton({ label, color, onClick }) {
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
}

function AnalyticsCard({ title, value, subtitle, color }) {
    return (
        <div
            style={{
                background: "#0f172a",
                border: `1px solid ${color}`,
                borderRadius: "18px",
                padding: "16px",
                minHeight: "112px",
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
                borderRadius: "18px",
                border: `1px solid ${color}`,
            }}
        >
            <div style={{ color: "#94a3b8", marginBottom: "8px", fontSize: "13px" }}>
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
                borderRadius: "14px",
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

function InfoTile({ title, value, color }) {
    return (
        <div
            style={{
                background: "#111827",
                border: "1px solid #1e293b",
                borderRadius: "14px",
                padding: "14px",
            }}
        >
            <div style={{ color: "#64748b", fontSize: "12px", marginBottom: "6px" }}>
                {title}
            </div>

            <div style={{ color, fontSize: "18px", fontWeight: "bold" }}>{value}</div>
        </div>
    )
}

function Badge({ label, color }) {
    return (
        <span
            style={{
                color,
                background: `${color}22`,
                border: `1px solid ${color}`,
                padding: "5px 9px",
                borderRadius: "999px",
                fontSize: "11px",
                fontWeight: "bold",
            }}
        >
            {label}
        </span>
    )
}

function EmptyState() {
    return (
        <div
            style={{
                color: "#94a3b8",
                background: "#111827",
                border: "1px dashed #334155",
                padding: "22px",
                borderRadius: "14px",
                textAlign: "center",
            }}
        >
            <div style={{ fontSize: "28px", marginBottom: "8px" }}>📡</div>
            <div style={{ fontWeight: "bold", color: "#cbd5e1" }}>
                No alerts match current filters.
            </div>
            <div style={{ fontSize: "13px", marginTop: "6px" }}>
                Trigger a test alert or wait for a live camera event.
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
                padding: "14px",
                marginBottom: "12px",
                borderRadius: "14px",
                animation: index === 0 ? "newCardGlow 0.5s ease-out" : "none",
            }}
        >
            <div
                style={{
                    display: "flex",
                    justifyContent: "space-between",
                    gap: "10px",
                    alignItems: "center",
                    marginBottom: "10px",
                }}
            >
                <div style={{ fontWeight: "bold", color, fontSize: "16px" }}>
                    {getEventIcon(event.type)} {event.type}
                </div>

                <Badge label={severity} color={color} />
            </div>

            {event.message && (
                <div style={{ color: "#e5e7eb", marginBottom: "10px", fontSize: "14px" }}>
                    {event.message}
                </div>
            )}

            {event.snapshot_url && (
                <div style={{ marginBottom: "10px" }}>
                    <img
                        src={event.snapshot_url}
                        alt="Alert Snapshot"
                        style={{
                            width: "100%",
                            maxHeight: "180px",
                            objectFit: "cover",
                            borderRadius: "10px",
                            border: "1px solid #334155",
                            background: "#000",
                        }}
                    />

                    <a
                        href={event.snapshot_url}
                        target="_blank"
                        rel="noreferrer"
                        style={{
                            color: "#38bdf8",
                            fontSize: "13px",
                            display: "inline-block",
                            marginTop: "6px",
                            textDecoration: "none",
                        }}
                    >
                        🔎 Open Snapshot
                    </a>
                </div>
            )}

            {event.clip_url && (
                <div style={{ marginBottom: "10px" }}>
                    <video
                        src={event.clip_url}
                        controls
                        muted
                        style={{
                            width: "100%",
                            maxHeight: "220px",
                            borderRadius: "10px",
                            border: "1px solid #334155",
                            background: "#000",
                        }}
                    />

                    <a
                        href={event.clip_url}
                        target="_blank"
                        rel="noreferrer"
                        style={{
                            color: "#38bdf8",
                            fontSize: "13px",
                            display: "inline-block",
                            marginTop: "6px",
                            textDecoration: "none",
                        }}
                    >
                        🎞 Open Video Clip
                    </a>
                </div>
            )}

            <div style={{ color: "#cbd5e1", fontSize: "14px", lineHeight: 1.65 }}>
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

                {event.confidence !== undefined &&
                    event.confidence !== null &&
                    !Number.isNaN(Number(event.confidence)) && (
                        <div>🎯 Confidence: {Number(event.confidence).toFixed(2)}</div>
                    )}

                {event.recording_skipped && <div>⚡ Recording skipped: cooldown active</div>}
                {event.clip_skipped && <div>🎞 Clip skipped: performance mode</div>}
                {event.created_at && <div>🕒 Time: {event.created_at}</div>}
            </div>
        </div>
    )
}