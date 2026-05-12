"""
SurakshaDrishti AI — Human-like Assistant Patch

Purpose:
- Make assistant responses feel more natural and operator-like.
- Keep existing command logic intact.
- Improve greeting, fallback, action guidance, and response tone.
- Frontend-only change.

Safety:
- Only modifies frontend/dashboard/src/App.jsx.
- No backend changes.
- No API changes.
- No new npm packages.
"""

from pathlib import Path


APP_PATH = Path("frontend/dashboard/src/App.jsx")
BACKUP_PATH = Path("frontend/dashboard/src/App.jsx.backup_before_human_like_assistant")


def insert_before(text: str, marker: str, insert: str, label: str) -> str:
    if marker not in text:
        raise RuntimeError(f"Could not find marker: {label}")
    return text.replace(marker, insert + marker, 1)


def replace_all(text: str, old: str, new: str) -> str:
    return text.replace(old, new)


def main():
    source = APP_PATH.read_text(encoding="utf-8")

    if not BACKUP_PATH.exists():
        BACKUP_PATH.write_text(source, encoding="utf-8")

    text = source

    human_layer = r'''function createHumanAssistantTone({
    query,
    baseReply,
    events = [],
    dispatches = [],
    heatmapData = null,
    backendAnalytics = null,
}) {
    /*
    |--------------------------------------------------------------------------
    | Human-like Assistant Tone Layer
    |--------------------------------------------------------------------------
    | This does not replace the assistant brain.
    | It only makes replies feel more natural, calm, and operator-friendly.
    */

    const text = normalizeAssistantText(query)
    const totalEvents = backendAnalytics?.total_events ?? events.length
    const riskLevel = heatmapData?.risk_level || "UNKNOWN"

    const pending = dispatches.filter((d) => d.status === "PENDING").length
    const assigned = dispatches.filter((d) => d.status === "ASSIGNED").length
    const running = dispatches.filter((d) => d.status === "DISPATCHED").length
    const unresolvedSos = events.filter((event) => {
        if (event.type !== "SOS_ALERT") return false

        const related = dispatches.filter(
            (dispatch) => Number(dispatch.event_id) === Number(event.db_id)
        )

        if (related.length === 0) return true

        return related.some((dispatch) => dispatch.status !== "RESOLVED")
    }).length

    if (
        text === "hi" ||
        text === "hello" ||
        text === "hey" ||
        text === "hii" ||
        text === "help me"
    ) {
        return [
            "I’m online and watching the dashboard with you.",
            "",
            `Current snapshot: ${totalEvents} events, risk level ${riskLevel}, ${pending} pending authority incident(s), ${running} running response(s).`,
            "",
            "You can ask me things like:",
            "• What should I do next?",
            "• Show pending incidents",
            "• Explain our system",
            "• Open Authority",
            "• How to demo?",
        ].join("\n")
    }

    if (!baseReply) {
        return [
            "I’m not fully sure what you mean, but I can still help with the command dashboard.",
            "",
            "Try asking in a simple way, for example:",
            "• latest alert",
            "• pending incidents",
            "• current risk",
            "• open authority",
            "• what should I do next",
        ].join("\n")
    }

    const lowerReply = String(baseReply).toLowerCase()

    const shouldNotWrap =
        lowerReply.startsWith("opening") ||
        lowerReply.includes("run surakshadrishti") ||
        lowerReply.includes("recommended demo flow") ||
        lowerReply.includes("troubleshooting") ||
        lowerReply.includes("project name:")

    if (shouldNotWrap) {
        return baseReply
    }

    let priorityLine = "I checked the current dashboard state."

    if (unresolvedSos > 0) {
        priorityLine = `I found ${unresolvedSos} unresolved SOS alert(s). Treat these as highest priority.`
    } else if (pending > 0) {
        priorityLine = `I found ${pending} pending authority incident(s) that need operator action.`
    } else if (assigned > 0) {
        priorityLine = `I found ${assigned} assigned incident(s) waiting to be marked Running.`
    } else if (running > 0) {
        priorityLine = `I found ${running} running response(s). Monitor them until they can be resolved.`
    } else if (riskLevel === "CRITICAL" || riskLevel === "HIGH") {
        priorityLine = `Risk level is ${riskLevel}. Keep monitoring alerts and authority response.`
    }

    return [
        priorityLine,
        "",
        baseReply,
    ].join("\n")
}

'''

    if "function createHumanAssistantTone({" not in text:
        text = insert_before(
            text,
            "function getAssistantBrainV2Reply({",
            human_layer,
            "before Assistant Brain V2",
        )

    # Wrap sidebar assistant brain reply
    text = replace_all(
        text,
        '''        if (brainV2Reply) {
            return brainV2Reply
        }''',
        '''        if (brainV2Reply) {
            return createHumanAssistantTone({
                query,
                baseReply: brainV2Reply,
                events,
                dispatches,
                heatmapData,
                backendAnalytics,
            })
        }'''
    )

    # Wrap project knowledge replies too
    text = replace_all(
        text,
        '''        if (projectKnowledgeReply) {
            return projectKnowledgeReply
        }''',
        '''        if (projectKnowledgeReply) {
            return createHumanAssistantTone({
                query,
                baseReply: projectKnowledgeReply,
                events,
                dispatches,
                heatmapData,
                backendAnalytics,
            })
        }'''
    )

    # Improve default assistant greeting texts
    text = replace_all(
        text,
        "Hello, I am SurakshaDrishti AI Command Assistant for Team TriNetra. Ask about alerts, SOS, heatmap risk, authority workflow, project architecture, demo flow, or run commands.",
        "Hi, I’m your SurakshaDrishti AI command assistant. I can help you monitor alerts, understand risk, guide SOS response, explain the system, and suggest what to do next."
    )

    text = replace_all(
        text,
        "SurakshaDrishti AI Command Assistant online. I know the live dashboard, SOS, authority workflow, heatmap, run commands, demo flow, and Team TriNetra project context.",
        "I’m online. I can read the dashboard context, explain SurakshaDrishti AI, and guide you through SOS, alerts, heatmap, and authority response."
    )

    # Improve fallback texts
    text = replace_all(
        text,
        '''    return [
        "I can help, but I need a clearer command.",
        "",
        "Try asking:",
        "• What should I do next?",
        "• Show pending incidents",
        "• Show critical alerts",
        "• Open Authority",
        "• Explain our system",
        "• How to run full system?",
        "• How to demo?",
        "• Troubleshoot connection refused",
    ].join("\\n")''',
        '''    return [
        "I’m not completely sure what you’re asking, but I can help with the live command dashboard.",
        "",
        "You can ask naturally, for example:",
        "• What should I do next?",
        "• Are there any active emergencies?",
        "• Show pending authority incidents",
        "• Open Authority",
        "• Explain our system",
        "• How do I run the full system?",
        "• How should I present the demo?",
    ].join("\\n")'''
    )

    APP_PATH.write_text(text, encoding="utf-8")

    print("human-like assistant patch ok")
    print(f"backup: {BACKUP_PATH}")
    print(f"updated: {APP_PATH}")


if __name__ == "__main__":
    main()
