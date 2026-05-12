from pathlib import Path
import re

p = Path("frontend/dashboard/src/App.jsx")
text = p.read_text(encoding="utf-8")

p.with_name("App.jsx.backup_before_quick_css_fix").write_text(text, encoding="utf-8")

text = re.sub(
    r"/\*\s*SurakshaDrishti AI duplicate live badge fix[\s\S]*?display:\s*none\s*!important;\s*\}\s*",
    "",
    text,
    flags=re.MULTILINE,
)

p.write_text(text, encoding="utf-8")
print("fixed broken css")
