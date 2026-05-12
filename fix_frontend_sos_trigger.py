from pathlib import Path
import re

p = Path("frontend/dashboard/src/App.jsx")
text = p.read_text(encoding="utf-8")

backup = p.with_name("App.jsx.backup_before_frontend_sos_fix")
backup.write_text(text, encoding="utf-8")

old = '''    async function triggerSosDemo(customPayload = null) {
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

            await loadEventHistory()'''

new = '''    async function triggerSosDemo(customPayload = null) {
        try {
            setSosLoading(true)
            setLastError("")

            /*
            ------------------------------------------------------------
            SOS frontend payload safety fix
            ------------------------------------------------------------
            Why:
            - Some buttons call triggerSosDemo directly as onClick.
            - React then passes a click event as the first argument.
            - That click event must NOT be sent to /sos.
            - Only use customPayload when it is a real plain object
              containing SOS fields. Otherwise use current sosForm.
            */

            const isValidSosPayload =
                customPayload &&
                typeof customPayload === "object" &&
                !customPayload.nativeEvent &&
                !customPayload.target &&
                (
                    customPayload.incident_location ||
                    customPayload.incident_type ||
                    customPayload.help_needed
                )

            const payload = isValidSosPayload ? customPayload : sosForm

            const cleanPayload = {
                user_name: payload.user_name || "Demo User",
                phone: payload.phone || "demo",
                incident_location:
                    payload.incident_location || "Demo Laptop Location",
                incident_type:
                    payload.incident_type || "Emergency",
                help_needed:
                    Array.isArray(payload.help_needed) && payload.help_needed.length > 0
                        ? payload.help_needed
                        : ["POLICE"],
                details:
                    payload.details || "SOS emergency triggered from dashboard",
            }

            const response = await fetch(`${API_BASE}/sos`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(cleanPayload),
            })

            if (!response.ok) {
                const errorText = await response.text()
                throw new Error(`Failed to trigger SOS demo: ${response.status} ${errorText}`)
            }

            await loadEventHistory()'''

if old not in text:
    raise SystemExit("Exact triggerSosDemo block not found. No changes made.")

text = text.replace(old, new, 1)

p.write_text(text, encoding="utf-8")
print("frontend SOS trigger fix applied")
print(f"backup: {backup}")