from pathlib import Path

p = Path("frontend/dashboard/src/App.jsx")
text = p.read_text(encoding="utf-8")

backup = p.with_name("App.jsx.backup_before_sos_pin_top_fix")
backup.write_text(text, encoding="utf-8")

old = '''            if (!response.ok) {
                const errorText = await response.text()
                throw new Error(`Failed to trigger SOS demo: ${response.status} ${errorText}`)
            }

            await loadEventHistory()'''

new = '''            if (!response.ok) {
                const errorText = await response.text()
                throw new Error(`Failed to trigger SOS demo: ${response.status} ${errorText}`)
            }

            const result = await response.json()
            const createdSosEvent = result?.event || null

            /*
            ------------------------------------------------------------
            SOS pin-to-top fix
            ------------------------------------------------------------
            Why:
            - Backend creates SOS correctly.
            - Dashboard refresh can take a moment.
            - We immediately inject the created SOS event at the top so
              Alerts and emergency banner show it without waiting/stale order.
            */

            if (createdSosEvent) {
                setEvents((prevEvents) => {
                    const existingEvents = Array.isArray(prevEvents) ? prevEvents : []

                    const createdKey =
                        createdSosEvent.db_id ||
                        createdSosEvent.id ||
                        createdSosEvent.event_id ||
                        createdSosEvent.timestamp ||
                        createdSosEvent.message

                    const withoutDuplicate = existingEvents.filter((event) => {
                        const eventKey =
                            event.db_id ||
                            event.id ||
                            event.event_id ||
                            event.timestamp ||
                            event.message

                        return String(eventKey) !== String(createdKey)
                    })

                    return [
                        {
                            ...createdSosEvent,
                            type: createdSosEvent.type || "SOS_ALERT",
                            severity: createdSosEvent.severity || "CRITICAL",
                            source: createdSosEvent.source || "mobile_sos",
                            isPinnedEmergency: true,
                        },
                        ...withoutDuplicate,
                    ]
                })
            }

            await loadEventHistory()

            if (typeof loadDispatches === "function") {
                await loadDispatches()
            }

            if (typeof loadDispatchSummary === "function") {
                await loadDispatchSummary()
            }

            setActiveSection("alerts")'''

if old not in text:
    raise SystemExit("Expected SOS response block not found. No changes made.")

text = text.replace(old, new, 1)
p.write_text(text, encoding="utf-8")

print("SOS pin-to-top fix applied")
print(f"backup: {backup}")