from pathlib import Path

p = Path("frontend/dashboard/src/App.jsx")
text = p.read_text(encoding="utf-8")

backup = p.with_name("App.jsx.backup_before_remove_livefeed_duplicate_badges_exact")
backup.write_text(text, encoding="utf-8")

old = '''            <div
                style={{
                    position: "absolute",
                    top: "12px",
                    left: "12px",
                    display: "flex",
                    gap: "8px",
                }}
            >
                <Badge label="LIVE" color="#22c55e" />
                <Badge label="CAM-01" color="#38bdf8" />
            </div>'''

if old not in text:
    raise SystemExit("Exact duplicate badge block not found. No changes made.")

text = text.replace(old, "", 1)

p.write_text(text, encoding="utf-8")
print("removed duplicate React LIVE/CAM-01 badges")
print(f"backup: {backup}")