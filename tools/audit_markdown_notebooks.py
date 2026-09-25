#!/usr/bin/env python3
"""Audit notebook-to-Markdown parity and write a concise traceability report."""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import nbformat


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "docs" / "maintenance"


def load_manifest():
    path = ROOT / "tools" / "promote_markdown_course.py"
    spec = importlib.util.spec_from_file_location("course_manifest", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.META


def main() -> int:
    meta = load_manifest()
    rows = []
    failures = []
    notebooks = sorted(ROOT.glob("level_*/*.ipynb"))
    for notebook in notebooks:
        number = int(re.search(r"lesson_(\d+)_", notebook.name).group(1))
        lesson = notebook.parent / "markdown" / f"{notebook.stem}.md"
        nb = nbformat.read(notebook, as_version=4)
        text = lesson.read_text(encoding="utf-8")
        worked_match = re.search(r"^## Worked example and interpretation\n(.*?)(?=^## |\Z)", text, flags=re.M | re.S)
        notebook_worked = [cell.source.strip() for cell in nb.cells
                           if cell.cell_type == "markdown" and cell.source.startswith("## Worked example and interpretation")]
        if not worked_match or len(notebook_worked) != 1 or worked_match.group(0).strip() != notebook_worked[0]:
            failures.append(f"{notebook.name}: worked interpretation differs from the authoritative lesson")
        analysis_cells = [cell for index, cell in enumerate(nb.cells) if cell.cell_type == "code" and index != 3]
        code_matches = sum(cell.source.strip() in text for cell in analysis_cells)
        figures = sum(
            "image/png" in output.get("data", {})
            for cell in nb.cells if cell.cell_type == "code"
            for output in cell.get("outputs", [])
        )
        figure_links = len(re.findall(r"!\[[^\]]*\]\([^)]+\.png\)", text))
        datasets = sorted(set(re.findall(r'DATA_DIR\s*/\s*["\']([^"\']+\.csv)["\']', "\n".join(c.source for c in analysis_cells))))
        status = "pass" if code_matches == len(analysis_cells) and figures == figure_links else "fail"
        if status == "fail":
            failures.append(notebook.name)
        rows.append(
            f"| {number} | [{notebook.name}](../../{notebook.relative_to(ROOT)}) | "
            f"[{lesson.name}](../../{lesson.relative_to(ROOT)}) | {', '.join(f'`{item}`' for item in datasets)} | "
            f"{code_matches}/{len(analysis_cells)} | {figures}/{figure_links} | {len(meta[number]['concepts'])} | {status} |"
        )

    support_docs = [
        ("../../readme.md", "Course entry point and three-level learning path"),
        ("../syllabus.md", "Outcomes, pacing, assessment, and data progression"),
        ("../test_selection_guide.md", "Cross-lesson method-selection reference"),
        ("../glossary.md", "Terminology used by notebooks and lessons"),
        ("../../data/readme.md", "Dataset provenance, cleaning, lesson mapping, and limits"),
        ("notebook_toolkit.md", "Shared notebook setup, data loading, resampling, and warnings"),
        ("course_coverage_index.md", "Notebook-to-concept and API traceability"),
    ]
    support_rows = "\n".join(
        f"| [{Path(path).name}]({path}) | {purpose} | {'pass' if (REPORT_DIR / path).exists() else 'missing'} |"
        for path, purpose in support_docs
    )
    report = f"""# Markdown and Notebook Alignment Audit

## Audit scope

This audit checks every executed notebook against its authoritative Markdown lesson. It verifies that analytical code
cells appear verbatim in the lesson, stored notebook figures have matching Markdown assets, real dataset filenames are
visible, and each lesson remains connected to the maintained concept manifest.

## Lesson parity

| Lesson | Supporting notebook | Authoritative Markdown | Real datasets loaded | Code cells matched | Figures notebook/Markdown | Concepts | Status |
|---:|---|---|---|---:|---:|---:|---|
{chr(10).join(rows)}

## Supporting Markdown review

| Markdown file | Relationship to notebook work | Status |
|---|---|---|
{support_rows}

## Result

All {len(notebooks)} notebooks and their authoritative lessons {'passed' if not failures else 'did not pass'} the
parity audit. The detailed statistical coverage remains in the [course coverage index](course_coverage_index.md), and
dataset-specific interpretation boundaries remain in the [data guide](../../data/readme.md).
"""
    (REPORT_DIR / "markdown_notebook_audit.md").write_text(report, encoding="utf-8")
    if failures:
        print("Parity failures:", ", ".join(failures))
        return 1
    print(f"Audited {len(notebooks)} notebook/Markdown pairs successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
