#!/usr/bin/env python3
"""Validate course structure and, optionally, execute each notebook."""

from __future__ import annotations

import argparse
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError


ROOT = Path(__file__).resolve().parents[1]


def validate(execute: bool) -> int:
    failures = []
    level_dirs = [
        ROOT / "level_1_foundations",
        ROOT / "level_2_applied_testing",
        ROOT / "level_3_advanced_practice",
    ]
    notebooks = sorted(path for level in level_dirs for path in level.glob("lesson_*.ipynb"))
    if len(notebooks) != 15:
        raise SystemExit(f"Expected 15 lessons, found {len(notebooks)}")

    for level in level_dirs:
        lesson_count = len(list(level.glob("lesson_*.ipynb")))
        markdown_count = len(list((level / "markdown").glob("lesson_*.md"))) if (level / "markdown").exists() else 0
        if lesson_count != 5:
            failures.append(f"{level.name}: expected 5 notebooks, found {lesson_count}")
        if markdown_count != 5:
            failures.append(f"{level.name}: expected 5 authoritative Markdown lessons, found {markdown_count}")

    for path in notebooks:
        nb = nbformat.read(path, as_version=4)
        nbformat.validate(nb)
        if not nb.cells or nb.cells[0].cell_type != "markdown" or not nb.cells[0].source.startswith("# Lesson"):
            failures.append(f"{path.name}: missing lesson title")
        if sum(cell.cell_type == "code" for cell in nb.cells) < 1:
            failures.append(f"{path.name}: no code cells")
        if any(output.output_type == "error" for cell in nb.cells if cell.cell_type == "code"
               for output in cell.get("outputs", [])):
            failures.append(f"{path.name}: stored error output")
        if execute:
            try:
                client = NotebookClient(nb, timeout=180, kernel_name="python3", resources={"metadata": {"path": str(path.parent)}})
                client.execute()
                nbformat.write(nb, path)
            except CellExecutionError as exc:
                failures.append(f"{path.name}: execution failed: {exc}")
        print(f"OK {path.name}")

    for name in ["readme.md", "docs/readme.md", "docs/syllabus.md", "docs/test_selection_guide.md",
                 "docs/glossary.md", "docs/maintenance/course_coverage_index.md",
                 "docs/maintenance/notebook_toolkit.md", "docs/maintenance/markdown_notebook_audit.md",
                 "requirements.txt"]:
        if not (ROOT / name).exists():
            failures.append(f"missing {name}")

    for level in level_dirs:
        if not (level / "readme.md").exists():
            failures.append(f"missing {level.name}/readme.md")
        for lesson_md in sorted((level / "markdown").glob("lesson_*.md")):
            text = lesson_md.read_text(encoding="utf-8")
            required = [
                "> **Authoritative lesson:**", "## Lesson overview", "## Learning objectives",
                "## Concept map", "## Data used in this lesson", "## Implementation reference", "## Best practices",
                "## Common mistakes and edge cases", "## Additional practice",
                "## Related lessons and source material",
            ]
            for marker in required:
                if marker not in text:
                    failures.append(f"{lesson_md.name}: missing {marker}")

    for name in ["readme.md", "anes96_clean.csv", "rand_hie_teaching_sample.csv",
                 "grunfeld_investment.csv", "heart_transplant_survival.csv", "spector_program.csv"]:
        if not (ROOT / "data" / name).exists():
            failures.append(f"missing data/{name}")

    coverage_path = ROOT / "docs" / "maintenance" / "course_coverage_index.md"
    coverage = coverage_path.read_text(encoding="utf-8") if coverage_path.exists() else ""
    for path in notebooks:
        if path.name not in coverage:
            failures.append(f"coverage index missing {path.name}")

    if failures:
        print("\nFAILURES")
        for item in failures:
            print(f"- {item}")
        return 1
    print(f"\nValidated {len(notebooks)} notebooks successfully.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true", help="Execute notebooks and save outputs")
    args = parser.parse_args()
    raise SystemExit(validate(args.execute))
