"""
SurakshaDrishti AI — Authority Labels Only Patch

Purpose:
- Improve frontend labels only.
- Display backend status DISPATCHED as RUNNING everywhere in the UI.
- Keep database/backend status unchanged as DISPATCHED.
- Do not change architecture, backend, API, workflow, or logic.

Safety:
- Only modifies frontend/dashboard/src/App.jsx.
- Creates backup before editing.
"""

from pathlib import Path


APP_PATH = Path("frontend/dashboard/src/App.jsx")
BACKUP_PATH = Path("frontend/dashboard/src/App.jsx.backup_before_authority_labels")


def replace_all(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"Could not find expected text: {label}")

    return text.replace(old, new)


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
    # 1. Add central status label helper before Authority section
    # ------------------------------------------------------------
    # This keeps display logic consistent and avoids changing backend values.
    # ------------------------------------------------------------

    helper_code = r'''function getAuthorityStatusLabel(status) {
    /*
    |--------------------------------------------------------------------------
    | Authority Status Display Helper
    |--------------------------------------------------------------------------
    | Backend/database value:
    | - DISPATCHED
    |
    | Operator-facing dashboard label:
    | - RUNNING
    |
    | Reason:
    | - DISPATCHED is technically accurate for storage/workflow.
    | - RUNNING is easier for demo users to understand as "unit is en route".
    */

    if (status === "DISPATCHED") {
        return "RUNNING"
    }

    return status || "PENDING"
}

'''

    text = insert_before(
        text,
        "function getAuthoritySummary(dispatches) {",
        helper_code,
        "before getAuthoritySummary",
    )

    # ------------------------------------------------------------
    # 2. Replace local inline DISPATCHED/RUNNING label logic
    # ------------------------------------------------------------

    text = replace_all(
        text,
        '''dispatch.status === "DISPATCHED" ? "RUNNING" : dispatch.status''',
        '''getAuthorityStatusLabel(dispatch.status)''',
        "inline dispatch status label mapping",
    )

    text = replace_all(
        text,
        '''const statusLabel = status === "DISPATCHED" ? "RUNNING" : status''',
        '''const statusLabel = getAuthorityStatusLabel(status)''',
        "AuthorityIncidentCard status label",
    )

    # ------------------------------------------------------------
    # 3. Improve button label
    # ------------------------------------------------------------

    text = replace_all(
        text,
        '''label="Dispatch / Running"''',
        '''label="Mark Running"''',
        "Dispatch button label",
    )

    # ------------------------------------------------------------
    # 4. Improve created/running timeline text
    # ------------------------------------------------------------

    text = replace_all(
        text,
        '''{dispatch.dispatched_at && <div>🚓 Running: {dispatch.dispatched_at}</div>}''',
        '''{dispatch.dispatched_at && <div>🚓 Marked Running: {dispatch.dispatched_at}</div>}''',
        "Running timestamp label",
    )

    # ------------------------------------------------------------
    # 5. Improve status menu label if needed
    # ------------------------------------------------------------

    text = replace_all(
        text,
        '''["RUNNING", "Running"],''',
        '''["RUNNING", "Running"],''',
        "Running filter label unchanged check",
    )

    APP_PATH.write_text(text, encoding="utf-8")

    print("authority labels patch ok")
    print(f"backup: {BACKUP_PATH}")
    print(f"updated: {APP_PATH}")


if __name__ == "__main__":
    main()