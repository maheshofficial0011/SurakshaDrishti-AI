"""
SurakshaDrishti AI — Assistant Auto Scroll Patch

Purpose:
- Automatically scroll assistant chat to the latest message.
- Fixes issue where user must manually scroll down after many messages.
- Applies to:
  1. Sidebar AI Assistant chat
  2. Floating bottom-right assistant chat

Safety:
- Only modifies frontend/dashboard/src/App.jsx.
- No backend changes.
- No API changes.
- No new packages.
"""

from pathlib import Path


APP_PATH = Path("frontend/dashboard/src/App.jsx")
BACKUP_PATH = Path("frontend/dashboard/src/App.jsx.backup_before_assistant_autoscroll")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"Could not find expected block: {label}")
    return text.replace(old, new, 1)


def main():
    if not APP_PATH.exists():
        raise FileNotFoundError(APP_PATH)

    source = APP_PATH.read_text(encoding="utf-8")

    if not BACKUP_PATH.exists():
        BACKUP_PATH.write_text(source, encoding="utf-8")

    text = source

    # ------------------------------------------------------------
    # 1. Add sidebar assistant scroll ref + effect
    # ------------------------------------------------------------

    old_sidebar_state = '''    const [sectionAssistantInput, setSectionAssistantInput] = useState("")
    const [sectionAssistantMessages, setSectionAssistantMessages] = useState(['''

    new_sidebar_state = '''    const sectionAssistantEndRef = useRef(null)
    const [sectionAssistantInput, setSectionAssistantInput] = useState("")
    const [sectionAssistantMessages, setSectionAssistantMessages] = useState(['''

    text = replace_once(
        text,
        old_sidebar_state,
        new_sidebar_state,
        "sidebar assistant scroll ref",
    )

    old_sidebar_after_state = '''    const latestEvent = events && events.length > 0 ? events[0] : null'''

    new_sidebar_after_state = '''    useEffect(() => {
        sectionAssistantEndRef.current?.scrollIntoView({
            behavior: "smooth",
            block: "end",
        })
    }, [sectionAssistantMessages])

    const latestEvent = events && events.length > 0 ? events[0] : null'''

    text = replace_once(
        text,
        old_sidebar_after_state,
        new_sidebar_after_state,
        "sidebar assistant auto scroll effect",
    )

    # ------------------------------------------------------------
    # 2. Add sidebar end marker after sidebar messages map
    # ------------------------------------------------------------

    old_sidebar_messages_end = '''                        {sectionAssistantMessages.map((message, index) => (
                            <div
                                key={`${message.role}-${index}`}
                                style={{
                                    justifySelf: message.role === "user" ? "end" : "start",
                                    maxWidth: "84%",
                                    background:
                                        message.role === "user" ? "#2563eb" : "#111827",
                                    color: "white",
                                    border:
                                        message.role === "user"
                                            ? "1px solid #93c5fd"
                                            : "1px solid #334155",
                                    borderRadius: "15px",
                                    padding: "11px 13px",
                                    whiteSpace: "pre-wrap",
                                    lineHeight: 1.55,
                                    fontSize: "14px",
                                }}
                            >
                                {message.text}
                            </div>
                        ))}
                    </div>'''

    new_sidebar_messages_end = '''                        {sectionAssistantMessages.map((message, index) => (
                            <div
                                key={`${message.role}-${index}`}
                                style={{
                                    justifySelf: message.role === "user" ? "end" : "start",
                                    maxWidth: "84%",
                                    background:
                                        message.role === "user" ? "#2563eb" : "#111827",
                                    color: "white",
                                    border:
                                        message.role === "user"
                                            ? "1px solid #93c5fd"
                                            : "1px solid #334155",
                                    borderRadius: "15px",
                                    padding: "11px 13px",
                                    whiteSpace: "pre-wrap",
                                    lineHeight: 1.55,
                                    fontSize: "14px",
                                }}
                            >
                                {message.text}
                            </div>
                        ))}

                        <div ref={sectionAssistantEndRef} />
                    </div>'''

    text = replace_once(
        text,
        old_sidebar_messages_end,
        new_sidebar_messages_end,
        "sidebar assistant end marker",
    )

    # ------------------------------------------------------------
    # 3. Add floating assistant scroll ref + effect
    # ------------------------------------------------------------

    old_floating_state = '''    const [assistantOpen, setAssistantOpen] = useState(false)
    const [assistantInput, setAssistantInput] = useState("")'''

    new_floating_state = '''    const assistantEndRef = useRef(null)
    const [assistantOpen, setAssistantOpen] = useState(false)
    const [assistantInput, setAssistantInput] = useState("")'''

    text = replace_once(
        text,
        old_floating_state,
        new_floating_state,
        "floating assistant scroll ref",
    )

    old_floating_after_state = '''    function getDispatchSummary() {'''

    new_floating_after_state = '''    useEffect(() => {
        if (!assistantOpen) {
            return
        }

        assistantEndRef.current?.scrollIntoView({
            behavior: "smooth",
            block: "end",
        })
    }, [assistantMessages, assistantOpen])

    function getDispatchSummary() {'''

    text = replace_once(
        text,
        old_floating_after_state,
        new_floating_after_state,
        "floating assistant auto scroll effect",
    )

    # ------------------------------------------------------------
    # 4. Add floating end marker after floating messages map
    # ------------------------------------------------------------

    old_floating_messages_end = '''                        {assistantMessages.map((message, index) => (
                            <div
                                key={`${message.role}-${index}`}
                                style={{
                                    justifySelf:
                                        message.role === "user" ? "end" : "start",
                                    maxWidth: "86%",
                                    background:
                                        message.role === "user" ? "#2563eb" : "#111827",
                                    color: "white",
                                    border:
                                        message.role === "user"
                                            ? "1px solid #93c5fd"
                                            : "1px solid #334155",
                                    borderRadius: "14px",
                                    padding: "10px 12px",
                                    whiteSpace: "pre-wrap",
                                    lineHeight: 1.5,
                                    fontSize: "13px",
                                }}
                            >
                                {message.text}
                            </div>
                        ))}
                    </div>'''

    new_floating_messages_end = '''                        {assistantMessages.map((message, index) => (
                            <div
                                key={`${message.role}-${index}`}
                                style={{
                                    justifySelf:
                                        message.role === "user" ? "end" : "start",
                                    maxWidth: "86%",
                                    background:
                                        message.role === "user" ? "#2563eb" : "#111827",
                                    color: "white",
                                    border:
                                        message.role === "user"
                                            ? "1px solid #93c5fd"
                                            : "1px solid #334155",
                                    borderRadius: "14px",
                                    padding: "10px 12px",
                                    whiteSpace: "pre-wrap",
                                    lineHeight: 1.5,
                                    fontSize: "13px",
                                }}
                            >
                                {message.text}
                            </div>
                        ))}

                        <div ref={assistantEndRef} />
                    </div>'''

    text = replace_once(
        text,
        old_floating_messages_end,
        new_floating_messages_end,
        "floating assistant end marker",
    )

    APP_PATH.write_text(text, encoding="utf-8")

    print("assistant autoscroll patch ok")
    print(f"backup: {BACKUP_PATH}")
    print(f"updated: {APP_PATH}")


if __name__ == "__main__":
    main()