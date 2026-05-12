"""
SurakshaDrishti AI — Frontend Authority Workflow Patch

Purpose:
- Modify only frontend/dashboard/src/App.jsx.
- Keep existing dashboard design and architecture safe.
- Reuse current state and components.
- Add section navigation, realistic SOS form, authority workflow actions,
  and pinned unresolved SOS alerts.

Safety:
- Requires existing App.jsx backup.
- Creates another backup before editing.
- Fails loudly if expected blocks are not found.
"""

from pathlib import Path


APP_PATH = Path("frontend/dashboard/src/App.jsx")
BACKUP_PATH = Path("frontend/dashboard/src/App.jsx.backup_before_section_authority_patch")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"Could not find expected block: {label}")

    return text.replace(old, new, 1)


def insert_before(text: str, marker: str, insert: str, label: str) -> str:
    if marker not in text:
        raise RuntimeError(f"Could not find insert marker: {label}")

    return text.replace(marker, insert + marker, 1)


def main():
    if not APP_PATH.exists():
        raise FileNotFoundError(APP_PATH)

    source = APP_PATH.read_text(encoding="utf-8")

    if not BACKUP_PATH.exists():
        BACKUP_PATH.write_text(source, encoding="utf-8")

    text = source

    # ------------------------------------------------------------------
    # 1. Add SOS form state after demo feature state
    # ------------------------------------------------------------------

    text = replace_once(
        text,
        '''    const [heatmapData, setHeatmapData] = useState(null)
    const [dispatches, setDispatches] = useState([])
    const [sosLoading, setSosLoading] = useState(false)''',
        '''    const [heatmapData, setHeatmapData] = useState(null)
    const [dispatches, setDispatches] = useState([])
    const [sosLoading, setSosLoading] = useState(false)
    const [authorityFilter, setAuthorityFilter] = useState("ALL")

    /*
    |--------------------------------------------------------------------------
    | Realistic SOS Form State
    |--------------------------------------------------------------------------
    | This keeps the SOS section realistic while still using the existing
    | /sos backend endpoint.
    */

    const [sosForm, setSosForm] = useState({
        user_name: "Demo User",
        phone: "demo",
        incident_location: "Demo Laptop Location",
        incident_type: "Medical Emergency",
        help_needed: ["POLICE", "AMBULANCE"],
        details: "Person injured near main gate",
    })''',
        "demo state block",
    )

    # ------------------------------------------------------------------
    # 2. Replace simple SOS trigger with form-aware SOS trigger
    # ------------------------------------------------------------------

    text = replace_once(
        text,
        '''    async function triggerSosDemo() {
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
    }''',
        '''    async function triggerSosDemo(customPayload = null) {
        try {
            setSosLoading(true)
            setLastError("")

            const payload = customPayload || sosForm

            const response = await fetch(`${API_BASE}/sos`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(payload),
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

    function updateSosFormField(field, value) {
        setSosForm((prev) => ({
            ...prev,
            [field]: value,
        }))
    }

    function toggleSosHelpNeeded(helpType) {
        setSosForm((prev) => {
            const current = prev.help_needed || []

            if (current.includes(helpType)) {
                const next = current.filter((item) => item !== helpType)

                return {
                    ...prev,
                    help_needed: next.length > 0 ? next : current,
                }
            }

            return {
                ...prev,
                help_needed: [...current, helpType],
            }
        })
    }

    async function updateDispatchWorkflow(dispatchId, action, payload = {}) {
        try {
            setLastError("")

            const response = await fetch(`${API_BASE}/dispatches/${dispatchId}/${action}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(payload),
            })

            if (!response.ok) {
                throw new Error(`Failed to ${action} dispatch`)
            }

            await loadBackendAnalytics()
            await loadEventHistory()
        } catch (err) {
            console.error("Failed to update dispatch workflow:", err)
            setLastError("Could not update authority response status")
        }
    }''',
        "triggerSosDemo function",
    )

    # ------------------------------------------------------------------
    # 3. Add helper computed data before Login Screen
    # ------------------------------------------------------------------

    text = insert_before(
        text,
        '''    /*
    |--------------------------------------------------------------------------
    | Login Screen
    |--------------------------------------------------------------------------
    */''',
        '''    /*
    |--------------------------------------------------------------------------
    | Authority + Priority Helpers
    |--------------------------------------------------------------------------
    */

    const dispatchSummary = useMemo(() => {
        const summary = {
            pending: 0,
            assigned: 0,
            running: 0,
            resolved: 0,
        }

        dispatches.forEach((dispatch) => {
            const status = dispatch.status || "PENDING"

            if (status === "PENDING") summary.pending += 1
            else if (status === "ASSIGNED") summary.assigned += 1
            else if (status === "DISPATCHED") summary.running += 1
            else if (status === "RESOLVED") summary.resolved += 1
        })

        return summary
    }, [dispatches])

    function isEventResolvedByAuthority(event) {
        if (!event || !event.db_id) {
            return false
        }

        const relatedDispatches = dispatches.filter(
            (dispatch) => Number(dispatch.event_id) === Number(event.db_id)
        )

        if (relatedDispatches.length === 0) {
            return false
        }

        return relatedDispatches.every((dispatch) => dispatch.status === "RESOLVED")
    }

    function isPinnedEmergencyEvent(event) {
        if (!event) {
            return false
        }

        const isEmergency =
            event.type === "SOS_ALERT" ||
            event.severity === "CRITICAL" ||
            event.severity === "HIGH"

        return isEmergency && !isEventResolvedByAuthority(event)
    }

    function sortEventsForPriority(eventList) {
        return [...eventList].sort((a, b) => {
            const aPinned = isPinnedEmergencyEvent(a)
            const bPinned = isPinnedEmergencyEvent(b)

            if (aPinned && !bPinned) return -1
            if (bPinned && !aPinned) return 1

            const aTime = new Date(a.created_at || a.timestamp || 0).getTime()
            const bTime = new Date(b.created_at || b.timestamp || 0).getTime()

            return bTime - aTime
        })
    }

    const sortedEvents = useMemo(
        () => sortEventsForPriority(events),
        [events, dispatches]
    )

    const activeEmergency = sortedEvents.find((event) => isPinnedEmergencyEvent(event))

''',
        "before Login Screen",
    )

    # ------------------------------------------------------------------
    # 4. Use activeEmergency for critical banner instead of old latestCritical
    # ------------------------------------------------------------------

    text = replace_once(
        text,
        '''    const latestCritical = events.find(
        (e) => e.severity === "CRITICAL" || e.severity === "HIGH"
    )''',
        '''    const latestCritical = activeEmergency''',
        "latestCritical assignment",
    )

    # ------------------------------------------------------------------
    # 5. Replace Sidebar items with active sections
    # ------------------------------------------------------------------

    text = replace_once(
        text,
        '''            <SidebarItem
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
            />''',
        '''            <SidebarItem
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
            />''',
        "Sidebar section items",
    )

    # ------------------------------------------------------------------
    # 6. Replace main section conditional render
    # ------------------------------------------------------------------

    text = replace_once(
        text,
        '''                {activeSection === "settings" ? (
                    <SettingsPanel
                        themeMode={themeMode}
                        toggleThemeMode={toggleThemeMode}
                        isLightMode={isLightMode}
                        lastSyncTime={lastSyncTime}
                        lastEventTime={lastEventTime}
                    />
                ) : (
                    <>
                        <ControlsPanel
                            typeFilter={typeFilter}
                            setTypeFilter={setTypeFilter}
                            severityFilter={severityFilter}
                            setSeverityFilter={setSeverityFilter}
                            limitFilter={limitFilter}
                            setLimitFilter={setLimitFilter}
                            loadEventHistory={loadEventHistory}
                            triggerTestAlert={triggerTestAlert}
                            triggerSosDemo={triggerSosDemo}
                            sosLoading={sosLoading}
                            exportReport={exportReport}
                            exportDailySummary={exportDailySummary}
                            clearEventHistory={clearEventHistory}
                            clearReviewedState={clearReviewedState}
                        />

                        <DashboardQualityPanels
                            stats={stats}
                            latestEvent={latestEvent}
                            lastSyncTime={lastSyncTime}
                            lastEventTime={lastEventTime}
                            connectionStatus={connectionStatus}
                            backendStatus={backendStatus}
                        />

                        {latestCritical && (
                            <CriticalAlertBanner
                                event={latestCritical}
                                getEventIcon={getEventIcon}
                            />
                        )}

                        <KpiRow stats={stats} />

                        <AnalyticsRow
                            backendAnalytics={backendAnalytics}
                            stats={stats}
                            topRiskZone={topRiskZone}
                            topEventType={topEventType}
                            riskZones={riskZones}
                            analyticsByType={analyticsByType}
                        />

                        <MainDashboardGrid
                            events={events}
                            stats={stats}
                            backendAnalytics={backendAnalytics}
                            heatmapData={heatmapData}
                            dispatches={dispatches}
                            getSeverityColor={getSeverityColor}
                            getEventIcon={getEventIcon}
                            reviewedEventKeys={reviewedEventKeys}
                            getEventKey={getEventKey}
                            markEventReviewed={markEventReviewed}
                            markEventUnreviewed={markEventUnreviewed}
                        />
                    </>
                )}''',
        '''                <ControlsPanel
                    typeFilter={typeFilter}
                    setTypeFilter={setTypeFilter}
                    severityFilter={severityFilter}
                    setSeverityFilter={setSeverityFilter}
                    limitFilter={limitFilter}
                    setLimitFilter={setLimitFilter}
                    loadEventHistory={loadEventHistory}
                    triggerTestAlert={triggerTestAlert}
                    triggerSosDemo={triggerSosDemo}
                    sosLoading={sosLoading}
                    exportReport={exportReport}
                    exportDailySummary={exportDailySummary}
                    clearEventHistory={clearEventHistory}
                    clearReviewedState={clearReviewedState}
                />

                {latestCritical && (
                    <CriticalAlertBanner
                        event={latestCritical}
                        getEventIcon={getEventIcon}
                    />
                )}

                {activeSection === "dashboard" && (
                    <OverviewSection
                        events={sortedEvents}
                        stats={stats}
                        backendAnalytics={backendAnalytics}
                        heatmapData={heatmapData}
                        dispatches={dispatches}
                        dispatchSummary={dispatchSummary}
                        latestEvent={latestEvent}
                        lastSyncTime={lastSyncTime}
                        lastEventTime={lastEventTime}
                        connectionStatus={connectionStatus}
                        backendStatus={backendStatus}
                        topRiskZone={topRiskZone}
                        topEventType={topEventType}
                        riskZones={riskZones}
                        analyticsByType={analyticsByType}
                        getSeverityColor={getSeverityColor}
                        getEventIcon={getEventIcon}
                        reviewedEventKeys={reviewedEventKeys}
                        getEventKey={getEventKey}
                        markEventReviewed={markEventReviewed}
                        markEventUnreviewed={markEventUnreviewed}
                    />
                )}

                {activeSection === "live" && (
                    <LiveSection stats={stats} backendAnalytics={backendAnalytics} />
                )}

                {activeSection === "alerts" && (
                    <AlertsSection
                        events={sortedEvents}
                        reviewedEventKeys={reviewedEventKeys}
                        getEventKey={getEventKey}
                        markEventReviewed={markEventReviewed}
                        markEventUnreviewed={markEventUnreviewed}
                        getSeverityColor={getSeverityColor}
                        getEventIcon={getEventIcon}
                    />
                )}

                {activeSection === "heatmap" && (
                    <HeatmapSection heatmapData={heatmapData} />
                )}

                {activeSection === "sos" && (
                    <SosControlSection
                        sosForm={sosForm}
                        updateSosFormField={updateSosFormField}
                        toggleSosHelpNeeded={toggleSosHelpNeeded}
                        triggerSosDemo={triggerSosDemo}
                        sosLoading={sosLoading}
                    />
                )}

                {activeSection === "authority" && (
                    <AuthoritySection
                        dispatches={dispatches}
                        dispatchSummary={dispatchSummary}
                        authorityFilter={authorityFilter}
                        setAuthorityFilter={setAuthorityFilter}
                        updateDispatchWorkflow={updateDispatchWorkflow}
                    />
                )}

                {activeSection === "analytics" && (
                    <AnalyticsSection
                        backendAnalytics={backendAnalytics}
                        stats={stats}
                        topRiskZone={topRiskZone}
                        topEventType={topEventType}
                        riskZones={riskZones}
                        analyticsByType={analyticsByType}
                    />
                )}

                {activeSection === "settings" && (
                    <SettingsPanel
                        themeMode={themeMode}
                        toggleThemeMode={toggleThemeMode}
                        isLightMode={isLightMode}
                        lastSyncTime={lastSyncTime}
                        lastEventTime={lastEventTime}
                    />
                )}''',
        "main activeSection render",
    )

    # ------------------------------------------------------------------
    # 7. Replace MainDashboardGrid event source with already sorted events
    # ------------------------------------------------------------------

    text = replace_once(
        text,
        '''                        events.map((event, index) => {''',
        '''                        events.map((event, index) => {''',
        "noop ensure event map exists",
    )

    # ------------------------------------------------------------------
    # 8. Insert new section components before MainDashboardGrid
    # ------------------------------------------------------------------

    text = insert_before(
        text,
        "function MainDashboardGrid({",
        r'''function OverviewSection({
    events,
    stats,
    backendAnalytics,
    heatmapData,
    dispatches,
    dispatchSummary,
    latestEvent,
    lastSyncTime,
    lastEventTime,
    connectionStatus,
    backendStatus,
    topRiskZone,
    topEventType,
    riskZones,
    analyticsByType,
    getSeverityColor,
    getEventIcon,
    reviewedEventKeys,
    getEventKey,
    markEventReviewed,
    markEventUnreviewed,
}) {
    return (
        <>
            <DashboardQualityPanels
                stats={stats}
                latestEvent={latestEvent}
                lastSyncTime={lastSyncTime}
                lastEventTime={lastEventTime}
                connectionStatus={connectionStatus}
                backendStatus={backendStatus}
            />

            <KpiRow stats={stats} />

            <AuthorityMiniSummary dispatchSummary={dispatchSummary} />

            <AnalyticsRow
                backendAnalytics={backendAnalytics}
                stats={stats}
                topRiskZone={topRiskZone}
                topEventType={topEventType}
                riskZones={riskZones}
                analyticsByType={analyticsByType}
            />

            <MainDashboardGrid
                events={events}
                stats={stats}
                backendAnalytics={backendAnalytics}
                heatmapData={heatmapData}
                dispatches={dispatches}
                getSeverityColor={getSeverityColor}
                getEventIcon={getEventIcon}
                reviewedEventKeys={reviewedEventKeys}
                getEventKey={getEventKey}
                markEventReviewed={markEventReviewed}
                markEventUnreviewed={markEventUnreviewed}
            />
        </>
    )
}

function LiveSection({ stats, backendAnalytics }) {
    return (
        <Panel title="📹 Live AI Camera Feed">
            <LiveFeedPanel />
            <SeverityGrid stats={stats} backendAnalytics={backendAnalytics} />
        </Panel>
    )
}

function AlertsSection({
    events,
    reviewedEventKeys,
    getEventKey,
    markEventReviewed,
    markEventUnreviewed,
    getSeverityColor,
    getEventIcon,
}) {
    return (
        <Panel title="🚨 Alert Feed — Pinned Until Resolved">
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

function HeatmapSection({ heatmapData }) {
    return <HeatmapPanel heatmapData={heatmapData} />
}

function AnalyticsSection({
    backendAnalytics,
    stats,
    topRiskZone,
    topEventType,
    riskZones,
    analyticsByType,
}) {
    return (
        <>
            <AnalyticsRow
                backendAnalytics={backendAnalytics}
                stats={stats}
                topRiskZone={topRiskZone}
                topEventType={topEventType}
                riskZones={riskZones}
                analyticsByType={analyticsByType}
            />

            <Panel title="📈 Detailed Analytics">
                <div
                    style={{
                        display: "grid",
                        gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
                        gap: "14px",
                    }}
                >
                    <QualityCard
                        title="Event Types"
                        accent="#a855f7"
                        rows={(analyticsByType || []).slice(0, 6).map((item) => [
                            item.type,
                            item.count,
                        ])}
                    />

                    <QualityCard
                        title="Risk Zones"
                        accent="#ef4444"
                        rows={(riskZones || []).slice(0, 6).map((item) => [
                            item.zone,
                            item.count,
                        ])}
                    />
                </div>
            </Panel>
        </>
    )
}

function AuthorityMiniSummary({ dispatchSummary }) {
    return (
        <div
            style={{
                display: "grid",
                gridTemplateColumns: "repeat(4, 1fr)",
                gap: "14px",
                marginBottom: "18px",
            }}
        >
            <StatCard title="Pending" value={dispatchSummary.pending} color="#f59e0b" />
            <StatCard title="Assigned" value={dispatchSummary.assigned} color="#38bdf8" />
            <StatCard title="Running" value={dispatchSummary.running} color="#22c55e" />
            <StatCard title="Resolved" value={dispatchSummary.resolved} color="#64748b" />
        </div>
    )
}

function SosControlSection({
    sosForm,
    updateSosFormField,
    toggleSosHelpNeeded,
    triggerSosDemo,
    sosLoading,
}) {
    const helpOptions = ["POLICE", "AMBULANCE", "FIRE", "RESCUE", "SECURITY"]

    return (
        <Panel title="🆘 Mobile SOS Emergency Panel">
            <div
                style={{
                    display: "grid",
                    gridTemplateColumns: "minmax(0, 1fr) minmax(300px, 0.8fr)",
                    gap: "18px",
                }}
            >
                <div style={{ display: "grid", gap: "14px" }}>
                    <FormInput
                        label="Reporter Name"
                        value={sosForm.user_name}
                        onChange={(value) => updateSosFormField("user_name", value)}
                    />

                    <FormInput
                        label="Phone / Contact"
                        value={sosForm.phone}
                        onChange={(value) => updateSosFormField("phone", value)}
                    />

                    <FormInput
                        label="Incident Location"
                        value={sosForm.incident_location}
                        onChange={(value) => updateSosFormField("incident_location", value)}
                    />

                    <FilterSelect
                        label="Incident Type"
                        value={sosForm.incident_type}
                        onChange={(value) => updateSosFormField("incident_type", value)}
                        options={[
                            ["Medical Emergency", "Medical Emergency"],
                            ["Fire / Smoke", "Fire / Smoke"],
                            ["Violence / Threat", "Violence / Threat"],
                            ["Suspicious Person", "Suspicious Person"],
                            ["Accident", "Accident"],
                            ["Crowd Panic", "Crowd Panic"],
                            ["Women Safety", "Women Safety"],
                            ["General Emergency", "General Emergency"],
                        ]}
                    />

                    <div>
                        <div
                            style={{
                                color: "#94a3b8",
                                marginBottom: "8px",
                                fontSize: "13px",
                                fontWeight: "bold",
                            }}
                        >
                            Help Needed
                        </div>

                        <div style={{ display: "flex", flexWrap: "wrap", gap: "10px" }}>
                            {helpOptions.map((option) => {
                                const active = sosForm.help_needed.includes(option)

                                return (
                                    <button
                                        key={option}
                                        onClick={() => toggleSosHelpNeeded(option)}
                                        style={{
                                            background: active ? "#dc2626" : "#111827",
                                            color: "white",
                                            border: active
                                                ? "1px solid #fecaca"
                                                : "1px solid #334155",
                                            borderRadius: "999px",
                                            padding: "9px 12px",
                                            fontWeight: "bold",
                                        }}
                                    >
                                        {active ? "✓ " : ""}{option}
                                    </button>
                                )
                            })}
                        </div>
                    </div>

                    <label>
                        <div
                            style={{
                                color: "#94a3b8",
                                marginBottom: "6px",
                                fontSize: "13px",
                                fontWeight: "bold",
                            }}
                        >
                            Incident Details
                        </div>

                        <textarea
                            value={sosForm.details}
                            onChange={(e) => updateSosFormField("details", e.target.value)}
                            rows={5}
                            style={{
                                width: "100%",
                                boxSizing: "border-box",
                                background: "#111827",
                                color: "white",
                                border: "1px solid #334155",
                                borderRadius: "10px",
                                padding: "12px",
                                fontWeight: "bold",
                                resize: "vertical",
                            }}
                        />
                    </label>

                    <button
                        onClick={() => triggerSosDemo(sosForm)}
                        disabled={sosLoading}
                        style={{
                            background: "#dc2626",
                            color: "white",
                            border: "1px solid #fecaca",
                            borderRadius: "14px",
                            padding: "14px 18px",
                            fontWeight: "bold",
                            fontSize: "16px",
                            opacity: sosLoading ? 0.7 : 1,
                        }}
                    >
                        {sosLoading ? "Sending SOS..." : "🚨 Trigger Emergency SOS"}
                    </button>
                </div>

                <div
                    style={{
                        background: "#111827",
                        border: "1px solid #dc2626",
                        borderRadius: "18px",
                        padding: "16px",
                    }}
                >
                    <h3 style={{ marginTop: 0, color: "#fecaca" }}>SOS Preview</h3>

                    <div style={{ color: "#cbd5e1", lineHeight: 1.8 }}>
                        <div><strong>Reporter:</strong> {sosForm.user_name}</div>
                        <div><strong>Contact:</strong> {sosForm.phone}</div>
                        <div><strong>Location:</strong> {sosForm.incident_location}</div>
                        <div><strong>Incident:</strong> {sosForm.incident_type}</div>
                        <div><strong>Help:</strong> {sosForm.help_needed.join(", ")}</div>
                        <div><strong>Details:</strong> {sosForm.details}</div>
                    </div>

                    <div
                        style={{
                            marginTop: "16px",
                            background: "#7f1d1d",
                            border: "1px solid #ef4444",
                            borderRadius: "14px",
                            padding: "12px",
                            color: "#fee2e2",
                            fontWeight: "bold",
                        }}
                    >
                        This SOS will stay pinned in Alerts until all linked authority
                        incidents are resolved.
                    </div>
                </div>
            </div>
        </Panel>
    )
}

function AuthoritySection({
    dispatches,
    dispatchSummary,
    authorityFilter,
    setAuthorityFilter,
    updateDispatchWorkflow,
}) {
    const filteredDispatches = dispatches.filter((dispatch) => {
        if (authorityFilter === "ALL") return true
        if (authorityFilter === "RUNNING") return dispatch.status === "DISPATCHED"

        return dispatch.status === authorityFilter
    })

    const sortedDispatches = [...filteredDispatches].sort((a, b) => {
        const priority = {
            PENDING: 1,
            ASSIGNED: 2,
            DISPATCHED: 3,
            RESOLVED: 9,
        }

        const aPriority = priority[a.status] || 5
        const bPriority = priority[b.status] || 5

        if (aPriority !== bPriority) {
            return aPriority - bPriority
        }

        return new Date(b.created_at || 0) - new Date(a.created_at || 0)
    })

    return (
        <Panel title="🚓 Authority Response Center">
            <AuthorityMiniSummary dispatchSummary={dispatchSummary} />

            <div
                style={{
                    display: "flex",
                    flexWrap: "wrap",
                    gap: "10px",
                    marginBottom: "16px",
                }}
            >
                {[
                    ["ALL", "All"],
                    ["PENDING", "Pending"],
                    ["ASSIGNED", "Assigned"],
                    ["RUNNING", "Running"],
                    ["RESOLVED", "Resolved"],
                ].map(([value, label]) => (
                    <button
                        key={value}
                        onClick={() => setAuthorityFilter(value)}
                        style={{
                            background: authorityFilter === value ? "#2563eb" : "#111827",
                            color: "white",
                            border:
                                authorityFilter === value
                                    ? "1px solid #93c5fd"
                                    : "1px solid #334155",
                            borderRadius: "999px",
                            padding: "9px 13px",
                            fontWeight: "bold",
                        }}
                    >
                        {label}
                    </button>
                ))}
            </div>

            {sortedDispatches.length === 0 ? (
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
                    No authority incidents in this status.
                </div>
            ) : (
                <div style={{ display: "grid", gap: "12px" }}>
                    {sortedDispatches.map((dispatch) => (
                        <AuthorityIncidentCard
                            key={dispatch.id || dispatch.dispatch_id}
                            dispatch={dispatch}
                            updateDispatchWorkflow={updateDispatchWorkflow}
                        />
                    ))}
                </div>
            )}
        </Panel>
    )
}

function AuthorityIncidentCard({ dispatch, updateDispatchWorkflow }) {
    const status = dispatch.status || "PENDING"
    const statusLabel = status === "DISPATCHED" ? "RUNNING" : status

    return (
        <div
            style={{
                background: "#111827",
                border: status === "RESOLVED" ? "1px solid #475569" : "1px solid #2563eb",
                borderRadius: "16px",
                padding: "15px",
            }}
        >
            <div
                style={{
                    display: "flex",
                    justifyContent: "space-between",
                    gap: "12px",
                    alignItems: "center",
                    marginBottom: "10px",
                }}
            >
                <div>
                    <div style={{ color: "#93c5fd", fontWeight: "bold", fontSize: "17px" }}>
                        {dispatch.unit_name}
                    </div>
                    <div style={{ color: "#94a3b8", fontSize: "13px" }}>
                        {dispatch.event_type} • {dispatch.location_label}
                    </div>
                </div>

                <Badge
                    label={statusLabel}
                    color={
                        status === "PENDING"
                            ? "#f59e0b"
                            : status === "ASSIGNED"
                                ? "#38bdf8"
                                : status === "DISPATCHED"
                                    ? "#22c55e"
                                    : "#64748b"
                    }
                />
            </div>

            <div style={{ color: "#cbd5e1", fontSize: "13px", lineHeight: 1.7 }}>
                <div>🆔 Dispatch: {dispatch.dispatch_id}</div>
                <div>🚔 Unit Type: {dispatch.unit_type}</div>
                <div>⏱ ETA: {dispatch.eta_minutes} min</div>
                <div>🕒 Created: {dispatch.created_at}</div>
                {dispatch.assigned_at && <div>✅ Assigned: {dispatch.assigned_at}</div>}
                {dispatch.dispatched_at && <div>🚓 Running: {dispatch.dispatched_at}</div>}
                {dispatch.resolved_at && <div>✅ Resolved: {dispatch.resolved_at}</div>}
                {dispatch.resolution_note && <div>📝 Note: {dispatch.resolution_note}</div>}
            </div>

            <div style={{ display: "flex", flexWrap: "wrap", gap: "10px", marginTop: "12px" }}>
                {status === "PENDING" && (
                    <ActionButton
                        label="Assign Unit"
                        color="#2563eb"
                        onClick={() =>
                            updateDispatchWorkflow(dispatch.dispatch_id, "assign", {
                                unit_type: dispatch.unit_type,
                                unit_name: dispatch.unit_name,
                                eta_minutes: dispatch.eta_minutes,
                            })
                        }
                    />
                )}

                {status === "ASSIGNED" && (
                    <ActionButton
                        label="Dispatch / Running"
                        color="#16a34a"
                        onClick={() =>
                            updateDispatchWorkflow(dispatch.dispatch_id, "dispatch", {
                                eta_minutes: dispatch.eta_minutes,
                            })
                        }
                    />
                )}

                {status !== "RESOLVED" && (
                    <ActionButton
                        label="Resolve"
                        color="#475569"
                        onClick={() =>
                            updateDispatchWorkflow(dispatch.dispatch_id, "resolve", {
                                resolution_note:
                                    "Incident checked and resolved by authority unit.",
                            })
                        }
                    />
                )}
            </div>
        </div>
    )
}

function FormInput({ label, value, onChange }) {
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

            <input
                value={value}
                onChange={(e) => onChange(e.target.value)}
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

''',
        "before MainDashboardGrid",
    )

    APP_PATH.write_text(text, encoding="utf-8")

    print("authority workflow frontend patch ok")
    print(f"backup: {BACKUP_PATH}")
    print(f"updated: {APP_PATH}")


if __name__ == "__main__":
    main()