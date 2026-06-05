from pathlib import Path

for file in [Path("docs/index.html"), Path("docs/site/index.html")]:
    if not file.exists():
        continue

    text = file.read_text(encoding="utf-8")

    if 'href="research.html"' in text:
        print(f"research button already exists in {file}")
        continue

    old = '''<a class="button purple" href="https://maheshofficial0011.github.io/SurakshaDrishti-AI/final-review.html" target="_blank">
                Final Review Note
            </a>'''

    new = old + '''

            <a class="button green" href="research.html" target="_blank">
                Related Research Papers
            </a>'''

    if old not in text:
        print(f"button insertion point not found in {file}")
        continue

    text = text.replace(old, new, 1)
    file.write_text(text, encoding="utf-8")
    print(f"added research button to {file}")