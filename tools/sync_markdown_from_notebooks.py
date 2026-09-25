#!/usr/bin/env python3
"""Synchronize authoritative lesson examples with executed supporting notebooks."""

from __future__ import annotations

import importlib.util
import os
import re
from pathlib import Path

import nbformat
from nbconvert import MarkdownExporter


ROOT = Path(__file__).resolve().parents[1]


DATA_USAGE = {
    1: [("ANES 1996", "one survey respondent", "Age and expected-vote labels illustrate a permutation null and a one-sample mean test.", "The survey comparison is observational; the benchmark age of 45 is a teaching choice.")],
    2: [("ANES 1996", "one survey respondent", "The observed age distribution is resampled for empirical power and its vote-group age contrast motivates a planning example.", "The added standardized shifts are planning scenarios, not observed treatment effects.")],
    3: [("ANES 1996", "one survey respondent", "Respondent age supports the one-sample mean example.", "The age-45 benchmark is pedagogical, not a population claim."), ("Spector program", "one student", "Grade improvement supports the exact one-sample binomial example.", "The 50% benchmark is a teaching reference.")],
    4: [("ANES 1996", "one survey respondent", "Age is compared between respondents expecting to vote for Dole and Clinton.", "Vote groups were observed, not randomly assigned; inference is associational.")],
    5: [("Grunfeld investment", "one firm-year", "The same firms in 1935 and 1954 form genuine pairs for quantitative and derived binary comparisons.", "The threshold of 25 is an explicit teaching choice, and the main analysis uses log-transformed investment.")],
    6: [("ANES 1996", "one survey respondent", "Age is compared across three party-identification groups.", "The groups are observational; omnibus and post-hoc results do not establish causal party effects.")],
    7: [("ANES 1996", "one survey respondent", "Income category is modeled by age and party group; TV-news use is modeled by vote group with age adjustment.", "Both models describe adjusted associations, not randomized effects.")],
    8: [("ANES 1996", "one survey respondent", "Party identification and expected vote form the multi-category contingency table.", "Association does not imply causation."), ("Spector program", "one student", "Program group and grade improvement provide the sparse 2x2 example.", "Small samples produce wide odds-ratio intervals.")],
    9: [("RAND Health Insurance Experiment teaching sample", "one participant", "Any physician visit is compared between individual-deductible and other-plan groups.", "This balanced subset is for teaching; a full report requires the complete study design and sample.")],
    10: [("ANES 1996", "one survey respondent", "Age and weekly TV-news viewing illustrate correlation and simple regression.", "TV-news days are discrete and the survey association is not causal.")],
    11: [("ANES 1996", "one survey respondent", "Income-category differences between expected-vote groups illustrate permutation, rank, and bootstrap methods.", "Unrestricted permutation assumes exchangeability; the observational example is pedagogical.")],
    12: [("ANES 1996", "one survey respondent", "Seven vote-group comparisons define a multiplicity family; age supports a TOST example.", "The ±3-year equivalence margin is a teaching choice that would require substantive justification in practice.")],
    13: [("Grunfeld investment", "one firm-year", "Repeated firm observations support a random-intercept longitudinal model.", "The firm-size split is derived from the same data and is descriptive."), ("Heart-transplant survival", "one patient", "Follow-up time and observed deaths illustrate censoring, log-rank testing, and Kaplan–Meier curves.", "The age split is derived for teaching and was not randomized.")],
    14: [("RAND Health Insurance Experiment teaching sample", "one participant", "Physician-visit counts and any-visit indicators form the two-outcome capstone.", "The balanced subset is intentionally simple and does not replace a complete analysis of the original experiment.")],
    15: [("Course data bundle", "respondent, student, participant, firm-year, or patient depending on the file", "Four real datasets are loaded to connect outcome structure and dependence to a starting test family.", "The rule-based helper is an orientation tool, not an automated statistical decision maker.")],
}


def load_course_module():
    path = ROOT / "tools" / "promote_markdown_course.py"
    spec = importlib.util.spec_from_file_location("course_manifest", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def data_section(number: int) -> str:
    rows = []
    for dataset, unit, use, limitation in DATA_USAGE[number]:
        rows.append(f"| {dataset} | {unit} | {use} | {limitation} |")
    return """## Data used in this lesson

The examples use the local, documented real-data bundle. See the [dataset guide](../../data/readme.md) for provenance,
variable definitions, cleaning decisions, and reuse notes.

| Dataset | Observation unit | Lesson use | Interpretation boundary |
|---|---|---|---|
""" + "\n".join(rows)


def replace_section(text: str, heading: str, replacement: str, next_heading: str) -> str:
    pattern = rf"^{re.escape(heading)}\n.*?(?=^{re.escape(next_heading)}\n)"
    updated, count = re.subn(
        pattern, lambda _: replacement.rstrip() + "\n\n", text, flags=re.M | re.S
    )
    if count != 1:
        raise ValueError(f"Expected one {heading!r} section, found {count}")
    return updated


def synchronize(notebook: Path, course_module) -> None:
    number = int(re.search(r"lesson_(\d+)_", notebook.name).group(1))
    md_path = notebook.parent / "markdown" / f"{notebook.stem}.md"
    nb = nbformat.read(notebook, as_version=4)
    exporter = MarkdownExporter()
    asset_dir_name = f"{notebook.stem}_files"
    body, resources = exporter.from_notebook_node(
        nb,
        resources={"unique_key": notebook.stem, "output_files_dir": asset_dir_name},
    )

    first_core = re.search(rf"^## {number}\.1\b", body, flags=re.M)
    if not first_core:
        raise ValueError(f"Could not locate first teaching section in {notebook.name}")
    core = body[first_core.start():].strip().replace("## Key takeaways", "## Summary")

    text = md_path.read_text(encoding="utf-8")
    core_pattern = rf"^## {number}\.1\b.*?(?=^## Implementation reference\n)"
    text, count = re.subn(
        core_pattern, lambda _: core + "\n\n", text, flags=re.M | re.S
    )
    if count != 1:
        raise ValueError(f"Could not replace notebook-derived core in {md_path.name}")

    if "## Data used in this lesson" in text:
        text = replace_section(text, "## Data used in this lesson", data_section(number), "## Notebook setup")
    else:
        text = text.replace("## Notebook setup\n", data_section(number) + "\n\n## Notebook setup\n", 1)

    meta = course_module.META[number]
    concept_rows = [
        (name, definition, f"[{section}](#{course_module.md_anchor(section)})")
        for name, definition, section, _ in meta["concepts"]
    ]
    concept_section = """## Concept map

The lesson covers the following concepts explicitly.

""" + course_module.markdown_table(concept_rows, ["Concept", "Meaning", "Teaching section"])
    text = replace_section(text, "## Concept map", concept_section, "## Data used in this lesson")

    implementation = """## Implementation reference

These APIs and code patterns are demonstrated in the supporting notebook.

""" + course_module.markdown_table(meta["apis"], ["API or pattern", "Purpose", "Usage guidance"])
    text = replace_section(text, "## Implementation reference", implementation, "## Best practices")
    md_path.write_text(text.rstrip() + "\n", encoding="utf-8")

    asset_dir = md_path.parent / asset_dir_name
    asset_dir.mkdir(exist_ok=True)
    expected = set()
    for relative_name, content in resources.get("outputs", {}).items():
        relative_path = Path(relative_name)
        target = md_path.parent / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        expected.add(target.resolve())
    for old_asset in asset_dir.glob("*"):
        if old_asset.is_file() and old_asset.resolve() not in expected:
            old_asset.unlink()
    if not any(asset_dir.iterdir()):
        asset_dir.rmdir()

    print(f"Synchronized {md_path.relative_to(ROOT)}")


def main() -> None:
    module = load_course_module()
    notebooks = sorted(ROOT.glob("level_*/*.ipynb"))
    if len(notebooks) != 15:
        raise SystemExit(f"Expected 15 notebooks, found {len(notebooks)}")
    for notebook in notebooks:
        synchronize(notebook, module)
    module.convert_html_tables()
    module.fix_coverage_links()
    module.write_toolkit()
    module.write_coverage()
    module.write_quality_report()
    print("Refreshed tables, links, toolkit, coverage index, and completion report.")


if __name__ == "__main__":
    main()
