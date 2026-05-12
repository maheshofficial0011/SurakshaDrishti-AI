"""
SurakshaNet AI — Authority Section Only Patch

Purpose:
- Replace only the Authority placeholder with the real Authority Response Center.
- Keep Overview, Live Feed, Alerts, Heatmap, and SOS sections unchanged.
- Use existing backend workflow endpoints:
  POST /dispatches/{dispatch_id}/assign
  POST /dispatches/{dispatch_id}/dispatch
  POST /dispatches/{dispatch_id}/resolve

Safety:
- Only modifies frontend/dashboard/src/App.jsx.
- Creates backup before editing.
"""

from pathlib import Path


APP_PATH = Path("frontend/dashboard/src/App.jsx")
BACKUP_PATH = Path("frontend/dashboard/src/App.jsx.backup_before_authority_section")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"Could not find expected block: {label}")
    return text.replace(old, new, 1)


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
    # 1. Add authority filter state after SOS loading state
    # ------------------------------------------------------------

    old_state = '''    const [dispatches, setDispatches] = useState([])
    const [sosLoading, setSosLoading] = useState(false)'''

    new_state = '''    const [dispatches, setDispatches] = useState([])
    const [sosLoading, setSosLoading] = useState(false)
    const [authorityFilter, setAuthorityFilter] = useState("ALL")'''

    text = replace_once(text, old_state, new_state, "authority filter state")

    # ------------------------------------------------------------
    # 2. Add workflow update function after SOS helper functions
    # ------------------------------------------------------------

    marker = '''    /*
    |--------------------------------------------------------------------------
    | Initial Data Load
    |--------------------------------------------------------------------------
    | Runs only after login.
    */'''

    authority_function = '''    /*
    |--------------------------------------------------------------------------
    | Authority Workflow Actions
    |--------------------------------------------------------------------------
    | Uses existing backend workflow endpoints:
    | - assign
    | - dispatch
    | - resolve
    */

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
    }

'''

    text = insert_before(text, marker, authority_function, "before Initial Data Load")

    # ------------------------------------------------------------
    # 3. Pass authority props into SectionPlaceholder
    # ------------------------------------------------------------

    old_props = '''                        triggerSosDemo={triggerSosDemo}
                        sosLoading={sosLoading}
                    />'''

    new_props = '''                        triggerSosDemo={triggerSosDemo}
                        sosLoading={sosLoading}
                        authorityFilter={authorityFilter}
                        setAuthorityFilter={setAuthorityFilter}
                        updateDispatchWorkflow={updateDispatchWorkflow}
                    />'''

    text = replace_once(text, old_props, new_props, "SectionPlaceholder authority props")

    # ------------------------------------------------------------
    # 4. Update SectionPlaceholder signature
    # ------------------------------------------------------------

    old_signature = '''    triggerSosDemo,
    sosLoading,
}) {'''

    new_signature = '''    triggerSosDemo,
    sosLoading,
    authorityFilter,
    setAuthorityFilter,
    updateDispatchWorkflow,
}) {'''

    text = replace_once(text, old_signature, new_signature, "SectionPlaceholder authority signature")

    # ------------------------------------------------------------
    # 5. Mark authority section as custom
    # ------------------------------------------------------------

    old_authority_config = '''        authority: {
            icon: "🚓",
            title: "Authority Response Section",
            description:
                "This section is ready. Next step can add Pending / Assigned / Running / Resolved workflow here safely.",
        },'''

    new_authority_config = '''        authority: {
            icon: "🚓",
            title: "Authority Response Center",
            description:
                "Incident workflow connected to Pending / Assigned / Running / Resolved backend APIs.",
            custom: "authority",
        },'''

    text = replace_once(text, old_authority_config, new_authority_config, "authority section config")

    # ------------------------------------------------------------
    # 6. Add custom authority render after SOS render
    # ------------------------------------------------------------

    old_sos_render = '''    if (config.custom === "sos") {
        return (
            <SosControlPanel
                sosForm={sosForm}
                updateSosFormField={updateSosFormField}
                toggleSosHelpNeeded={toggleSosHelpNeeded}
                triggerSosDemo={triggerSosDemo}
                sosLoading={sosLoading}
            />
        )
    }

    return ('''

    new_sos_render = '''    if (config.custom === "sos") {
        return (
            <SosControlPanel
                sosForm={sosForm}
                updateSosFormField={updateSosFormField}
                toggleSosHelpNeeded={toggleSosHelpNeeded}
                triggerSosDemo={triggerSosDemo}
                sosLoading={sosLoading}
            />
        )
    }

    if (config.custom === "authority") {
        return (
            <AuthorityResponseCenter
                dispatches={dispatches}
                authorityFilter={authorityFilter}
                setAuthorityFilter={setAuthorityFilter}
                updateDispatchWorkflow={updateDispatchWorkflow}
            />
        )
    }

    return ('''

    text = replace_once(text, old_sos_render, new_sos_render, "custom authority render")

    # ------------------------------------------------------------
    # 7. Insert Authority components before SosControlPanel
    # ------------------------------------------------------------

    authority_components = r'''function getAuthoritySummary(dispatches) {
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

function AuthorityResponseCenter({
    dispatches,
    authorityFilter,
    setAuthorityFilter,
    updateDispatchWorkflow,
}) {
    const summary = getAuthoritySummary(dispatches)

    const filteredDispatches = (dispatches || []).filter((dispatch) => {
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
            <div
                style={{
                    display: "grid",
                    gridTemplateColumns: "repeat(4, 1fr)",
                    gap: "14px",
                    marginBottom: "18px",
                }}
            >
                <StatCard title="Pending" value={summary.pending} color="#f59e0b" />
                <StatCard title="Assigned" value={summary.assigned} color="#38bdf8" />
                <StatCard title="Running" value={summary.running} color="#22c55e" />
                <StatCard title="Resolved" value={summary.resolved} color="#64748b" />
            </div>

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
                        {dispatch.unit_name || "Authority Unit"}
                    </div>

                    <div style={{ color: "#94a3b8", fontSize: "13px" }}>
                        {dispatch.event_type || "EVENT"} • {dispatch.location_label || "Unknown location"}
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

'''

    text = insert_before(text, "function SosControlPanel(", authority_components, "before SosControlPanel")

    APP_PATH.write_text(text, encoding="utf-8")

    print("authority section patch ok")
    print(f"backup: {BACKUP_PATH}")
    print(f"updated: {APP_PATH}")


if __name__ == "__main__":
    main()