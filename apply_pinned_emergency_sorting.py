"""
SurakshaNet AI — Pinned Emergency Sorting Patch

Purpose:
- Keep unresolved SOS / CRITICAL / HIGH incidents pinned at the top.
- Once linked authority dispatches are RESOLVED, the alert returns to normal
  chronological history.
- Modify only frontend/dashboard/src/App.jsx.

Safety:
- No backend changes.
- No architecture changes.
- No section layout changes.
- Creates backup before editing.
"""

from pathlib import Path


APP_PATH = Path("frontend/dashboard/src/App.jsx")
BACKUP_PATH = Path("frontend/dashboard/src/App.jsx.backup_before_pinned_sorting")


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
    # 1. Add emergency sorting helpers before latestCritical
    # ------------------------------------------------------------

    marker = '''    const latestCritical = events.find(
        (e) => e.severity === "CRITICAL" || e.severity === "HIGH"
    )'''

    helper_code = '''    /*
    |--------------------------------------------------------------------------
    | Pinned Emergency Sorting
    |--------------------------------------------------------------------------
    | Requirement:
    | - SOS / CRITICAL / HIGH alerts should stay on top until their linked
    |   authority dispatch records are resolved.
    |
    | Logic:
    | - If an event has related dispatch records and all are RESOLVED,
    |   it is not pinned anymore.
    | - If it is SOS_ALERT / CRITICAL / HIGH and not fully resolved,
    |   it stays at the top.
    */

    function isEventResolvedByAuthority(event) {
        if (!event || !event.db_id) {
            return false
        }

        const relatedDispatches = (dispatches || []).filter(
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

    function getEventTimestampValue(event) {
        const rawTime = event?.created_at || event?.timestamp || 0
        const parsedTime = new Date(rawTime).getTime()

        if (Number.isNaN(parsedTime)) {
            return Number(rawTime) || 0
        }

        return parsedTime
    }

    function sortEventsForPriority(eventList) {
        return [...(eventList || [])].sort((a, b) => {
            const aPinned = isPinnedEmergencyEvent(a)
            const bPinned = isPinnedEmergencyEvent(b)

            if (aPinned && !bPinned) return -1
            if (bPinned && !aPinned) return 1

            const severityPriority = {
                CRITICAL: 1,
                HIGH: 2,
                MEDIUM: 3,
                LOW: 4,
                INFO: 5,
            }

            const aSeverityPriority = severityPriority[a.severity] || 6
            const bSeverityPriority = severityPriority[b.severity] || 6

            if (aPinned && bPinned && aSeverityPriority !== bSeverityPriority) {
                return aSeverityPriority - bSeverityPriority
            }

            return getEventTimestampValue(b) - getEventTimestampValue(a)
        })
    }

    const sortedEvents = useMemo(
        () => sortEventsForPriority(events),
        [events, dispatches]
    )

'''

    text = insert_before(text, marker, helper_code, "before latestCritical")

    # ------------------------------------------------------------
    # 2. Make latestCritical use sorted unresolved emergency
    # ------------------------------------------------------------

    text = replace_once(
        text,
        '''    const latestCritical = events.find(
        (e) => e.severity === "CRITICAL" || e.severity === "HIGH"
    )''',
        '''    const latestCritical = sortedEvents.find((event) =>
        isPinnedEmergencyEvent(event)
    )''',
        "latestCritical pinned emergency",
    )

    # ------------------------------------------------------------
    # 3. Pass sorted events to SectionPlaceholder
    # ------------------------------------------------------------

    text = replace_once(
        text,
        '''                        events={events}''',
        '''                        events={sortedEvents}''',
        "SectionPlaceholder sorted events",
    )

    # ------------------------------------------------------------
    # 4. Pass sorted events to MainDashboardGrid in Overview/main dashboard
    # ------------------------------------------------------------
    # This replaces the first remaining MainDashboardGrid events prop in the
    # original overview dashboard render.
    # If it has already been sectioned, this still safely improves overview.
    # ------------------------------------------------------------

    text = replace_once(
        text,
        '''                            events={events}
                            stats={stats}''',
        '''                            events={sortedEvents}
                            stats={stats}''',
        "MainDashboardGrid sorted events",
    )

    APP_PATH.write_text(text, encoding="utf-8")

    print("pinned emergency sorting patch ok")
    print(f"backup: {BACKUP_PATH}")
    print(f"updated: {APP_PATH}")


if __name__ == "__main__":
    main()