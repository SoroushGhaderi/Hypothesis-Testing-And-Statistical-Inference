#!/usr/bin/env python3
"""Validate authoritative Markdown coverage, structure, and local links."""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import nbformat


ROOT = Path(__file__).resolve().parents[1]
SNAKE_CASE_NAME = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*(?:\.[a-z0-9]+)?$")


def load_manifest():
    path = ROOT / "tools" / "promote_markdown_course.py"
    spec = importlib.util.spec_from_file_location("course_manifest", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.META, module.md_anchor


def without_fenced_code(text: str) -> str:
    return re.sub(r"```.*?```", "", text, flags=re.S)


def headings(text: str, anchor_fn):
    clean = without_fenced_code(text)
    return {anchor_fn(match.group(1).strip()) for match in re.finditer(r"^#{1,6}\s+(.+)$", clean, flags=re.M)}


def main() -> int:
    meta, anchor_fn = load_manifest()
    errors = []
    notebooks = sorted(ROOT.glob("level_*/*.ipynb"))
    lessons = sorted(ROOT.glob("level_*/markdown/lesson_*.md"))
    coverage_path = ROOT / "docs" / "maintenance" / "course_coverage_index.md"
    coverage = coverage_path.read_text(encoding="utf-8")
    expected_data = {
        "anes96_clean.csv",
        "rand_hie_teaching_sample.csv",
        "grunfeld_investment.csv",
        "heart_transplant_survival.csv",
        "spector_program.csv",
    }

    if len(notebooks) != 15:
        errors.append(f"expected 15 notebooks, found {len(notebooks)}")
    if len(lessons) != 15:
        errors.append(f"expected 15 authoritative lessons, found {len(lessons)}")
    actual_data = {path.name for path in (ROOT / "data").glob("*.csv")}
    if actual_data != expected_data:
        errors.append(f"expected data files {sorted(expected_data)}, found {sorted(actual_data)}")
    if not (ROOT / "data" / "readme.md").exists():
        errors.append("missing data/readme.md provenance guide")

    for path in [ROOT, *ROOT.rglob("*")]:
        if any(part.startswith(".") for part in path.relative_to(ROOT).parts):
            continue
        if not SNAKE_CASE_NAME.fullmatch(path.name):
            errors.append(f"non-snake-case path: {path.relative_to(ROOT.parent)}")

    for notebook in notebooks:
        nb = nbformat.read(notebook, as_version=4)
        nbformat.validate(nb)
        code = "\n".join(cell.source for cell in nb.cells if cell.cell_type == "code")
        if "pd.read_csv" not in code:
            errors.append(f"{notebook.name}: no real-data CSV load")
        for forbidden in ["rng.normal(", "rng.binomial(", "rng.lognormal(", "rng.exponential("]:
            if forbidden in code:
                errors.append(f"{notebook.name}: generated primary-data pattern {forbidden}")
        for cell in nb.cells:
            if cell.cell_type == "code" and cell.execution_count is None:
                errors.append(f"{notebook.name}: unexecuted code cell")
            for output in cell.get("outputs", []):
                if output.output_type == "error":
                    errors.append(f"{notebook.name}: stored error output")

    all_markdown = sorted(ROOT.rglob("*.md"))
    for path in all_markdown:
        text = path.read_text(encoding="utf-8")
        if any(ord(ch) < 32 and ch not in "\n\r\t" for ch in text):
            errors.append(f"{path.relative_to(ROOT)}: control character")
        if "<table" in text or "<div" in text or "<style" in text:
            errors.append(f"{path.relative_to(ROOT)}: embedded HTML table/style")
        local_headings = headings(text, anchor_fn)
        for match in re.finditer(r"!?\[[^\]]*\]\(([^)]+)\)", text):
            target = match.group(1).strip()
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            file_part, _, fragment = target.partition("#")
            target_path = path if not file_part else (path.parent / file_part).resolve()
            if not target_path.exists():
                errors.append(f"{path.relative_to(ROOT)}: missing link target {target}")
                continue
            if fragment and target_path.suffix.lower() == ".md":
                target_text = text if target_path == path.resolve() else target_path.read_text(encoding="utf-8")
                if fragment not in headings(target_text, anchor_fn):
                    errors.append(f"{path.relative_to(ROOT)}: missing heading #{fragment} in {file_part or path.name}")

    for number, lesson_meta in meta.items():
        lesson = next(ROOT.glob(f"level_*/markdown/lesson_{number:02d}_*.md"), None)
        notebook = next(ROOT.glob(f"level_*/lesson_{number:02d}_*.ipynb"), None)
        if lesson is None or notebook is None:
            errors.append(f"lesson {number}: missing notebook or Markdown")
            continue
        text = lesson.read_text(encoding="utf-8")
        nb = nbformat.read(notebook, as_version=4)
        if len(re.findall(r"^#\s+", without_fenced_code(text), flags=re.M)) != 1:
            errors.append(f"{lesson.name}: more than one level-1 heading")
        for required in [
            "> **Authoritative lesson:**", "## Lesson overview", "## Learning objectives",
            "## Concept map", "## Data used in this lesson", "## Notebook setup", "## Implementation reference",
            "## Best practices", "## Common mistakes and edge cases", "## Additional practice",
            "## Related lessons and source material",
        ]:
            if required not in text:
                errors.append(f"{lesson.name}: missing {required}")
        for concept, _, _, _ in lesson_meta["concepts"]:
            if concept not in text:
                errors.append(f"{lesson.name}: concept absent: {concept}")
            if concept not in coverage:
                errors.append(f"coverage absent: lesson {number} concept {concept}")
        for api, _, _ in lesson_meta["apis"]:
            plain = api.replace("\\|", "|")
            if plain not in text and api not in text:
                errors.append(f"{lesson.name}: API absent: {api}")
            if api not in coverage and api.replace("|", "\\|") not in coverage:
                errors.append(f"coverage absent: lesson {number} API {api}")
        if notebook.name not in text:
            errors.append(f"{lesson.name}: source notebook link absent")
        if notebook.name not in coverage:
            errors.append(f"coverage absent: {notebook.name}")

        for index, cell in enumerate(nb.cells):
            if cell.cell_type == "code" and index != 3 and cell.source.strip() not in text:
                errors.append(f"{lesson.name}: code cell {index} does not match notebook")
            if cell.cell_type == "markdown" and index >= 4:
                for heading in re.findall(r"^#{2,6}\s+(.+)$", cell.source, flags=re.M):
                    expected_heading = "Summary" if heading == "Key takeaways" else heading
                    if expected_heading not in text:
                        errors.append(f"{lesson.name}: notebook heading absent: {expected_heading}")
        figure_outputs = sum(
            "image/png" in output.get("data", {})
            for cell in nb.cells if cell.cell_type == "code"
            for output in cell.get("outputs", [])
        )
        figure_links = len(re.findall(r"!\[[^\]]*\]\([^)]+\.png\)", text))
        if figure_outputs != figure_links:
            errors.append(
                f"{lesson.name}: {figure_outputs} notebook figures but {figure_links} Markdown figures"
            )

    if errors:
        print("Markdown course validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    concept_count = sum(len(item["concepts"]) + len(item["apis"]) + 1 for item in meta.values())
    print(f"Validated {len(notebooks)} notebooks, {len(lessons)} authoritative lessons, and {concept_count} coverage entries.")
    print("All local Markdown links, heading anchors, source links, and image assets resolve.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
