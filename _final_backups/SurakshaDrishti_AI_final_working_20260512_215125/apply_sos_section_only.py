"""
SurakshaDrishti AI — SOS Control Section Only Patch

Purpose:
- Replace only the SOS Control placeholder with a realistic SOS form.
- Keep Overview, Live Feed, Alerts, and Heatmap sections unchanged.
- Use the existing /sos backend endpoint.
- Do not modify Authority UI yet.

Safety:
- Only modifies frontend/dashboard/src/App.jsx.
- Creates backup before editing.
"""

from pathlib import Path


APP_PATH = Path("frontend/dashboard/src/App.jsx")
BACKUP_PATH = Path("frontend/dashboard/src/App.jsx.backup_before_sos_section")


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
    # 1. Add realistic SOS form state after existing demo states
    # ------------------------------------------------------------

    old_state = '''    const [heatmapData, setHeatmapData] = useState(null)
    const [dispatches, setDispatches] = useState([])
    const [sosLoading, setSosLoading] = useState(false)'''

    new_state = '''    const [heatmapData, setHeatmapData] = useState(null)
    const [dispatches, setDispatches] = useState([])
    const [sosLoading, setSosLoading] = useState(false)

    /*
    |--------------------------------------------------------------------------
    | Realistic SOS Form State
    |--------------------------------------------------------------------------
    | Used only by the SOS Control section.
    | Submits to the existing /sos backend endpoint.
    */
    const [sosForm, setSosForm] = useState({
        user_name: "Demo User",
        phone: "demo",
        incident_location: "Demo Laptop Location",
        incident_type: "Medical Emergency",
        help_needed: ["POLICE", "AMBULANCE"],
        details: "Person injured near main gate",
    })'''

    text = replace_once(text, old_state, new_state, "SOS form state")

    # ------------------------------------------------------------
    # 2. Replace triggerSosDemo with form-aware version
    # ------------------------------------------------------------

    old_trigger = '''    async function triggerSosDemo() {
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
    }'''

    new_trigger = '''    async function triggerSosDemo(customPayload = null) {
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
    }'''

    text = replace_once(text, old_trigger, new_trigger, "SOS trigger function")

    # ------------------------------------------------------------
    # 3. Pass SOS props into SectionPlaceholder
    # ------------------------------------------------------------

    old_props = '''                        getSeverityColor={getSeverityColor}
                        getEventIcon={getEventIcon}
                    />'''

    new_props = '''                        getSeverityColor={getSeverityColor}
                        getEventIcon={getEventIcon}
                        sosForm={sosForm}
                        updateSosFormField={updateSosFormField}
                        toggleSosHelpNeeded={toggleSosHelpNeeded}
                        triggerSosDemo={triggerSosDemo}
                        sosLoading={sosLoading}
                    />'''

    text = replace_once(text, old_props, new_props, "SectionPlaceholder SOS props")

    # ------------------------------------------------------------
    # 4. Update SectionPlaceholder signature
    # ------------------------------------------------------------

    old_signature = '''    getSeverityColor,
    getEventIcon,
}) {'''

    new_signature = '''    getSeverityColor,
    getEventIcon,
    sosForm,
    updateSosFormField,
    toggleSosHelpNeeded,
    triggerSosDemo,
    sosLoading,
}) {'''

    text = replace_once(text, old_signature, new_signature, "SectionPlaceholder SOS signature")

    # ------------------------------------------------------------
    # 5. Mark SOS section as custom
    # ------------------------------------------------------------

    old_sos_config = '''        sos: {
            icon: "🆘",
            title: "SOS Control Section",
            description:
                "This section is ready. Next step can add the realistic SOS form here safely.",
        },'''

    new_sos_config = '''        sos: {
            icon: "🆘",
            title: "Mobile SOS Emergency Panel",
            description:
                "Realistic SOS form connected to the existing /sos backend endpoint.",
            custom: "sos",
        },'''

    text = replace_once(text, old_sos_config, new_sos_config, "SOS section config")

    # ------------------------------------------------------------
    # 6. Add custom SOS render after heatmap render
    # ------------------------------------------------------------

    old_heatmap_render = '''    if (config.custom === "heatmap") {
        return <HeatmapPanel heatmapData={heatmapData} />
    }

    return ('''

    new_heatmap_render = '''    if (config.custom === "heatmap") {
        return <HeatmapPanel heatmapData={heatmapData} />
    }

    if (config.custom === "sos") {
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

    text = replace_once(text, old_heatmap_render, new_heatmap_render, "custom SOS render")

    # ------------------------------------------------------------
    # 7. Add SOS Control Panel + FormInput before LiveFeedPanel
    # ------------------------------------------------------------

    sos_components = r'''function SosControlPanel({
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
                        This creates an SOS alert and sends matching PENDING incidents
                        to Authority Response.
                    </div>
                </div>
            </div>
        </Panel>
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

'''

    text = insert_before(text, "function LiveFeedPanel() {", sos_components, "before LiveFeedPanel")

    APP_PATH.write_text(text, encoding="utf-8")

    print("sos section patch ok")
    print(f"backup: {BACKUP_PATH}")
    print(f"updated: {APP_PATH}")


if __name__ == "__main__":
    main()