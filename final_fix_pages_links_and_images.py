from pathlib import Path

ROOT = Path(".")

page_files = [
    Path("docs/index.html"),
    Path("docs/site/index.html"),
    Path("docs/final-review.html"),
]

# Correct hosted links
repo_url = "https://github.com/maheshofficial0011/SurakshaDrishti-AI"
readme_url = "https://github.com/maheshofficial0011/SurakshaDrishti-AI#readme"
review_url = "https://maheshofficial0011.github.io/SurakshaDrishti-AI/final-review.html"

# Fix all HTML links and screenshot paths
for path in page_files:
    if not path.exists():
        continue

    text = path.read_text(encoding="utf-8")

    # Fix README button/link
    text = text.replace('href="../README.md"', f'href="{readme_url}"')
    text = text.replace('href="README.md"', f'href="{readme_url}"')
    text = text.replace('href="./README.md"', f'href="{readme_url}"')
    text = text.replace(
        'href="https://maheshofficial0011.github.io/SurakshaDrishti-AI/README.md"',
        f'href="{readme_url}"'
    )

    # Fix final review button/link
    text = text.replace('href="../FINAL_REVIEW_NOTE_ORGANIZED.html"', f'href="{review_url}"')
    text = text.replace('href="../FINAL_REVIEW_NOTE.html"', f'href="{review_url}"')
    text = text.replace('href="FINAL_REVIEW_NOTE.html"', f'href="{review_url}"')
    text = text.replace('href="./FINAL_REVIEW_NOTE.html"', f'href="{review_url}"')
    text = text.replace('href="final-review.html"', f'href="{review_url}"')

    # Fix screenshot paths.
    # Your actual folder is docs/screenshots, so from docs/final-review.html
    # the correct relative path is screenshots/filename.
    text = text.replace('src="images/', 'src="screenshots/')
    text = text.replace("src='images/", "src='screenshots/")

    path.write_text(text, encoding="utf-8")
    print(f"fixed: {path}")

print("done")