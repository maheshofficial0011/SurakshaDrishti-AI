"""
SurakshaDrishti AI — Fix Duplicate assistantProReply

Purpose:
- Fix Vite compile error:
  Identifier 'assistantProReply' has already been declared.
- Remove duplicate assistantProReply blocks if they were inserted twice.
- Keep one assistantProReply block in each assistant reply function.
- Do not change backend.
- Do not change dashboard architecture.

Safety:
- Only modifies frontend/dashboard/src/App.jsx.
- Creates backup before editing.
"""

from pathlib import Path


APP_PATH = Path("frontend/dashboard/src/App.jsx")
BACKUP_PATH = Path("frontend/dashboard/src/App.jsx.backup_before_fix_duplicate_assistantProReply")


ASSISTANT_PRO_BLOCK = '''        const assistantProReply = getAssistantProReply({
            query,
            events,
            dispatches,
            heatmapData,
            backendAnalytics,
            setActiveSection,
        })

        if (assistantProReply) {
            return assistantProReply
        }

'''


def cleanup_duplicate_blocks(text: str, function_name: str) -> str:
    """
    Inside a function, keep only the first assistantProReply block.
    Remove extra duplicate blocks.
    """

    start_marker = f"function {function_name}("
    start = text.find(start_marker)

    if start == -1:
        print(f"warning: function not found: {function_name}")
        return text

    # Find next top-level function after this one.
    next_function = text.find("\nfunction ", start + len(start_marker))

    if next_function == -1:
        before = text[:start]
        body = text[start:]
        after = ""
    else:
        before = text[:start]
        body = text[start:next_function]
        after = text[next_function:]

    count = body.count(ASSISTANT_PRO_BLOCK)

    if count <= 1:
        print(f"{function_name}: assistantProReply blocks = {count}, no cleanup needed")
        return text

    first_index = body.find(ASSISTANT_PRO_BLOCK)
    first_end = first_index + len(ASSISTANT_PRO_BLOCK)

    body_before_first = body[:first_end]
    body_after_first = body[first_end:]

    body_after_first = body_after_first.replace(ASSISTANT_PRO_BLOCK, "")

    cleaned_body = body_before_first + body_after_first

    print(f"{function_name}: removed {count - 1} duplicate assistantProReply block(s)")

    return before + cleaned_body + after


def main():
    if not APP_PATH.exists():
        raise FileNotFoundError(APP_PATH)

    source = APP_PATH.read_text(encoding="utf-8")

    if not BACKUP_PATH.exists():
        BACKUP_PATH.write_text(source, encoding="utf-8")

    text = source

    text = cleanup_duplicate_blocks(text, "createAssistantReply")
    text = cleanup_duplicate_blocks(text, "generateAssistantReply")

    APP_PATH.write_text(text, encoding="utf-8")

    print("duplicate assistantProReply cleanup ok")
    print(f"backup: {BACKUP_PATH}")
    print(f"updated: {APP_PATH}")


if __name__ == "__main__":
    main()
