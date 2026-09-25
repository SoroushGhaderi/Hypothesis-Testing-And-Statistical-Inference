#!/usr/bin/env python3
"""Check math in Markdown lessons, references, notebooks, and generated HTML."""

from __future__ import annotations

import re
from pathlib import Path

import mistune
import nbformat
from bs4 import BeautifulSoup

from mathml import LatexParser


ROOT = Path(__file__).resolve().parents[1]
MARKDOWN = mistune.create_markdown(renderer="ast", plugins=["math"])


def check_tokens(tokens: list[dict], label: str, errors: list[str]) -> int:
    count = 0
    for token in tokens:
        kind = token["type"]
        if kind in {"inline_math", "block_math"}:
            count += 1
            try:
                LatexParser(token["raw"]).parse()
            except ValueError as exc:
                errors.append(f"{label}: {exc}")
        elif kind == "text" and "$" in token.get("raw", ""):
            errors.append(f"{label}: unmatched math delimiter in {token['raw'][:80]!r}")
        count += check_tokens(token.get("children", []), label, errors)
    return count


def main() -> int:
    errors: list[str] = []
    markdown_count = 0
    notebook_count = 0
    for path in sorted(ROOT.rglob("*.md")):
        markdown_count += check_tokens(MARKDOWN(path.read_text(encoding="utf-8")), str(path.relative_to(ROOT)), errors)
    for path in sorted(ROOT.glob("level_*/*.ipynb")):
        notebook = nbformat.read(path, as_version=4)
        for index, cell in enumerate(notebook.cells):
            if cell.cell_type == "markdown":
                notebook_count += check_tokens(MARKDOWN(cell.source), f"{path.relative_to(ROOT)} cell {index}", errors)

    html_path = ROOT / "course.html"
    if html_path.exists():
        soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
        maths = soup.select("main math")
        if not maths:
            errors.append("course.html: no rendered MathML")
        for math in maths:
            annotation = math.find("annotation", attrs={"encoding": "application/x-tex"})
            if annotation is None:
                errors.append("course.html: MathML missing source annotation")
        for annotation in soup.select("main annotation"):
            annotation.decompose()
        visible = soup.main.get_text(" ", strip=True)
        if re.search(r"(?<!\\)\$|\\(?:alpha|beta|mu|frac|sqrt|sum|chi|Delta)\b", visible):
            errors.append("course.html: unrendered LaTeX remains in visible text")
    else:
        errors.append("course.html: missing generated page")

    if errors:
        print("Math validation failed:")
        for item in errors:
            print(f"- {item}")
        return 1
    print(f"Validated {markdown_count} Markdown and {notebook_count} notebook math expressions; {len(maths)} rendered in course.html.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
