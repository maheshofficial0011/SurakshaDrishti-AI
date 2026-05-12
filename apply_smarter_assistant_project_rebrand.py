"""
SurakshaDrishti AI — Smarter Assistant + Dashboard Rebrand Patch

Purpose:
- Change visible dashboard branding from SurakshaDrishti AI to SurakshaDrishti AI.
- Add project/team/system knowledge to assistant.
- Improve both:
  1. Floating bottom-right assistant
  2. Sidebar AI Assistant section chat

Safety:
- Only modifies frontend/dashboard/src/App.jsx.
- No backend changes.
- No API changes.
- No detection/tracking/pipeline changes.
- No new npm packages.
- Creates backup before editing.
"""

from pathlib import Path


APP_PATH = Path("frontend/dashboard/src/App.jsx")
BACKUP_PATH = Path("frontend/dashboard/src/App.jsx.backup_before_smarter_assistant_rebrand")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"Could not find expected block: {label}")

    return text.replace(old, new, 1)


def insert_before(text: str, marker: str, insert: str, label: str) -> str:
    if marker not in text:
        raise RuntimeError(f"Could not find marker: {label}")

    return text.replace(marker, insert + marker, 1)


def main():
    if not APP_PATH.exists():
        raise FileNotFoundError(APP_PATH)

    source = APP_PATH.read_text(encoding="utf-8")

    if not BACKUP_PATH.exists():
        BACKUP_PATH.write_text(source, encoding="utf-8")

    text = source

    # ------------------------------------------------------------
    # 1. Visible dashboard rebrand only
    # ------------------------------------------------------------
    # Replace user-facing project name text in the React dashboard.
    # Backend module names, API paths, and Python imports are NOT touched.
    # ------------------------------------------------------------

    text = text.replace("SurakshaDrishti AI", "SurakshaDrishti AI")
    text = text.replace("SurakshaNet Command Assistant", "SurakshaDrishti Command Assistant")
    text = text.replace("SURAKSHANET COMMAND ASSISTANT", "SURAKSHADRISHTI COMMAND ASSISTANT")
    text = text.replace("SurakshaNet", "SurakshaDrishti")

    # ------------------------------------------------------------
    # 2. Add central local knowledge base before AssistantSection
    # ------------------------------------------------------------

    knowledge_base = r'''const PROJECT_KNOWLEDGE = {
    projectName: "SurakshaDrishti AI",
    teamName: "TriNetra",
    systemType: "Local Windows real-time AI surveillance and emergency response prototype",
    stack: [
        "Python",
        "OpenCV",
        "Ultralytics YOLOv8n",
        "FastAPI",
        "SQLite",
        "WebSocket",
        "React",
        "Vite",
        "Leaflet",
    ],
    modules: [
        "Live camera feed",
        "Object/person detection",
        "Stable tracking",
        "Event engine",
        "Alert feed",
        "SOS emergency workflow",
        "Predictive safety heatmap",
        "Authority Response Center",
        "Reports and analytics",
        "Local dashboard command assistant",
    ],
    runCommands: {
        backend:
            "cd E:\\Copycat2 && .\\venv\\Scripts\\Activate.ps1 && python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000",
        frontend:
            "cd E:\\Copycat2\\frontend\\dashboard && npm run dev",
        pipeline:
            "cd E:\\Copycat2 && .\\venv\\Scripts\\Activate.ps1 && python pipelines\\tracking_pipeline.py",
    },
    demoFlow: [
        "Start backend API on port 8000",
        "Start frontend dashboard on localhost:5173",
        "Start camera/tracking pipeline",
        "Open Overview and Live Feed",
        "Trigger SOS from SOS Control",
        "Show pinned alert in Alerts",
        "Show heatmap risk update",
        "Open Authority Response Center",
        "Assign Unit",
        "Mark Running",
        "Resolve incident",
        "Show active emergency banner disappears after resolution",
    ],
}

function getProjectKnowledgeReply(query) {
    const lower = String(query || "").toLowerCase()

    if (
        lower.includes("project name") ||
        lower.includes("what is this project") ||
        lower.includes("about project") ||
        lower.includes("explain project") ||
        lower.includes("explain our system") ||
        lower.includes("what is suraksha")
    ) {
        return [
            `${PROJECT_KNOWLEDGE.projectName} is a ${PROJECT_KNOWLEDGE.systemType}.`,
            "",
            "It combines real-time camera monitoring, AI detection, tracking, event generation, SOS emergency reporting, heatmap visualization, and authority response workflow into one connected command dashboard.",
            "",
            `Team: ${PROJECT_KNOWLEDGE.teamName}`,
        ].join("\n")
    }

    if (
        lower.includes("team") ||
        lower.includes("trinetra") ||
        lower.includes("who built") ||
        lower.includes("members")
    ) {
        return [
            `Team Name: ${PROJECT_KNOWLEDGE.teamName}`,
            `Project: ${PROJECT_KNOWLEDGE.projectName}`,
            "",
            "Team member details were not specified in the dashboard knowledge base yet.",
        ].join("\n")
    }

    if (
        lower.includes("architecture") ||
        lower.includes("modules") ||
        lower.includes("how it works") ||
        lower.includes("system design")
    ) {
        return [
            `${PROJECT_KNOWLEDGE.projectName} architecture:`,
            "",
            "Camera / webcam input",
            "↓",
            "YOLOv8n detection",
            "↓",
            "Tracking Stability V2",
            "↓",
            "Event Engine",
            "↓",
            "FastAPI backend + SQLite database",
            "↓",
            "WebSocket live updates",
            "↓",
            "React dashboard with Alerts, SOS, Heatmap, Authority Response, Reports, and Assistant",
        ].join("\n")
    }

    if (
        lower.includes("tech stack") ||
        lower.includes("technology") ||
        lower.includes("tools used") ||
        lower.includes("stack")
    ) {
        return [
            "Technology stack:",
            ...PROJECT_KNOWLEDGE.stack.map((item) => `• ${item}`),
        ].join("\n")
    }

    if (
        lower.includes("features") ||
        lower.includes("what can it do") ||
        lower.includes("capabilities")
    ) {
        return [
            `${PROJECT_KNOWLEDGE.projectName} features:`,
            ...PROJECT_KNOWLEDGE.modules.map((item) => `• ${item}`),
        ].join("\n")
    }

    if (
        lower.includes("run") ||
        lower.includes("start") ||
        lower.includes("command") ||
        lower.includes("terminal")
    ) {
        return [
            "Run full system using 3 terminals:",
            "",
            "1. Backend:",
            PROJECT_KNOWLEDGE.runCommands.backend,
            "",
            "2. Frontend:",
            PROJECT_KNOWLEDGE.runCommands.frontend,
            "",
            "3. Camera / AI Pipeline:",
            PROJECT_KNOWLEDGE.runCommands.pipeline,
        ].join("\n")
    }

    if (
        lower.includes("demo") ||
        lower.includes("presentation") ||
        lower.includes("showcase") ||
        lower.includes("present")
    ) {
        return [
            "Recommended demo flow:",
            ...PROJECT_KNOWLEDGE.demoFlow.map((step, index) => `${index + 1}. ${step}`),
        ].join("\n")
    }

    if (
        lower.includes("sos") &&
        (lower.includes("work") || lower.includes("flow") || lower.includes("explain"))
    ) {
        return [
            "SOS workflow:",
            "1. Operator opens SOS Control.",
            "2. Enters reporter, phone, incident location, incident type, help needed, and details.",
            "3. Backend creates a CRITICAL SOS_ALERT.",
            "4. Alert appears in Alerts and active emergency banner.",
            "5. Authority Response Center receives PENDING units based on help needed.",
            "6. Operator assigns, marks running, and resolves the incident.",
        ].join("\n")
    }

    if (
        lower.includes("authority") &&
        (lower.includes("work") || lower.includes("flow") || lower.includes("explain"))
    ) {
        return [
            "Authority Response workflow:",
            "PENDING → ASSIGNED → RUNNING → RESOLVED",
            "",
            "Backend stores RUNNING as DISPATCHED, but the dashboard shows it as RUNNING for clarity.",
            "This simulates a real emergency response center where incidents are reviewed, assigned, dispatched, and closed.",
        ].join("\n")
    }

    if (
        lower.includes("heatmap") &&
        (lower.includes("mean") || lower.includes("work") || lower.includes("explain"))
    ) {
        return [
            "Heatmap meaning:",
            "The heatmap shows event concentration and risk level around the configured demo laptop location.",
            "Risk increases as more incidents are stored in the database.",
            "It is used to visually explain where safety risk is concentrated during the demo.",
        ].join("\n")
    }

    if (
        lower.includes("troubleshoot") ||
        lower.includes("not working") ||
        lower.includes("error") ||
        lower.includes("connection refused")
    ) {
        return [
            "Troubleshooting checklist:",
            "1. Check backend is running on http://127.0.0.1:8000",
            "2. Check frontend is running on http://localhost:5173",
            "3. If SOS fails with connection refused, start backend first.",
            "4. If live feed fails, start camera pipeline.",
            "5. If dashboard looks old, refresh browser and restart Vite.",
            "6. If a patch breaks UI, restore the latest App.jsx backup.",
        ].join("\n")
    }

    return null
}

'''

    if "const PROJECT_KNOWLEDGE = {" not in text:
        text = insert_before(
            text,
            "function AssistantSection({",
            knowledge_base,
            "before AssistantSection",
        )

    # ------------------------------------------------------------
    # 3. Inject knowledge reply into sidebar assistant
    # ------------------------------------------------------------

    sidebar_marker = '''    function createAssistantReply(query) {
        const lower = String(query || "").toLowerCase()
'''

    sidebar_injection = '''    function createAssistantReply(query) {
        const lower = String(query || "").toLowerCase()

        const projectKnowledgeReply = getProjectKnowledgeReply(query)

        if (projectKnowledgeReply) {
            return projectKnowledgeReply
        }
'''

    if sidebar_marker in text and "const projectKnowledgeReply = getProjectKnowledgeReply(query)" not in text:
        text = replace_once(
            text,
            sidebar_marker,
            sidebar_injection,
            "inject sidebar assistant knowledge",
        )

    # ------------------------------------------------------------
    # 4. Inject knowledge reply into floating assistant
    # ------------------------------------------------------------

    floating_marker = '''    function generateAssistantReply(query) {
        const lower = query.toLowerCase()
'''

    floating_injection = '''    function generateAssistantReply(query) {
        const lower = query.toLowerCase()

        const projectKnowledgeReply = getProjectKnowledgeReply(query)

        if (projectKnowledgeReply) {
            return projectKnowledgeReply
        }
'''

    if floating_marker in text and "function generateAssistantReply(query)" in text:
        # Avoid double insert into generate function if already added.
        generate_start = text.find("function generateAssistantReply(query)")
        next_function = text.find("function sendAssistantMessage", generate_start)
        generate_block = text[generate_start:next_function] if next_function != -1 else ""

        if "const projectKnowledgeReply = getProjectKnowledgeReply(query)" not in generate_block:
            text = replace_once(
                text,
                floating_marker,
                floating_injection,
                "inject floating assistant knowledge",
            )

    # ------------------------------------------------------------
    # 5. Improve assistant default intro strings after rebrand
    # ------------------------------------------------------------

    text = text.replace(
        "Hello, I am SurakshaDrishti AI Command Assistant. Ask about alerts, SOS, heatmap risk, pending incidents, or what to do next.",
        "Hello, I am SurakshaDrishti AI Command Assistant for Team TriNetra. Ask about alerts, SOS, heatmap risk, authority workflow, project architecture, demo flow, or run commands.",
    )

    text = text.replace(
        "Command Assistant online. I can analyze alerts, SOS incidents, authority workflow, heatmap risk, and suggest the next operator action.",
        "SurakshaDrishti AI Command Assistant online. I know the live dashboard, SOS, authority workflow, heatmap, run commands, demo flow, and Team TriNetra project context.",
    )

    # ------------------------------------------------------------
    # 6. Improve quick prompts in assistant section if present
    # ------------------------------------------------------------

    text = text.replace(
        '''    const quickPrompts = [
        "Give system summary",
        "What should I do next?",
        "Show pending incidents",
        "Show unresolved SOS",
        "What is the current risk?",
        "Show running responses",
    ]''',
        '''    const quickPrompts = [
        "Give system summary",
        "Explain our system",
        "How to demo?",
        "How to run full system?",
        "Show pending incidents",
        "What should I do next?",
        "What is the current risk?",
        "What is our team name?",
    ]''',
    )

    text = text.replace(
        '''    const quickPrompts = [
        "What is the latest alert?",
        "Show pending incidents",
        "What is the current risk?",
        "What should I do next?",
    ]''',
        '''    const quickPrompts = [
        "What is the latest alert?",
        "Explain our system",
        "How to demo?",
        "Show pending incidents",
        "What should I do next?",
    ]''',
    )

    APP_PATH.write_text(text, encoding="utf-8")

    print("smarter assistant + rebrand patch ok")
    print(f"backup: {BACKUP_PATH}")
    print(f"updated: {APP_PATH}")


if __name__ == "__main__":
    main()
