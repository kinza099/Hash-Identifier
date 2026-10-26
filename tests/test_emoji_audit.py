import os
import re
import unicodedata
import pytest

EMOJI_PATTERN = re.compile(
    r'['
    r'\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF'
    r'\U0001F1E0-\U0001F1FF\U0001F900-\U0001F9FF\U0001FA70-\U0001FAFF'
    r'\u2600-\u26FF\u2700-\u27BF\u2300-\u23FF\u2B50-\u2B55\u2B05-\u2B07\u2190-\u21FF\u2139\uFE0E-\uFE0F'
    r']+',
    flags=re.UNICODE
)

TARGET_DIRS = ["templates", "static/js", "static/css", "core"]

def test_zero_emojis_in_frontend_and_core():
    """Verify that zero unicode emojis exist in templates, js, css, and core."""
    violations = []
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    for target in TARGET_DIRS:
        dir_path = os.path.join(base_dir, target)
        if not os.path.exists(dir_path):
            continue
        for root, _, files in os.walk(dir_path):
            for file in files:
                if not file.endswith((".html", ".js", ".css", ".py")):
                    continue
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8", errors="ignore") as fp:
                    for line_no, line in enumerate(fp, 1):
                        matches = EMOJI_PATTERN.findall(line)
                        if matches:
                            rel_path = os.path.relpath(file_path, base_dir)
                            violations.append(f"{rel_path}:{line_no} -> {matches} | {line.strip()}")

    assert not violations, f"Remaining emojis detected:\n" + "\n".join(violations)

def test_material_symbols_stylesheet_in_base_html():
    """Verify that Google Material Symbols stylesheet is present in base.html."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    base_html_path = os.path.join(base_dir, "templates", "base.html")
    with open(base_html_path, "r", encoding="utf-8") as f:
        content = f.read()

    expected_link = "https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined"
    assert expected_link in content, "Material Symbols stylesheet missing from templates/base.html"
