#!/usr/bin/env python3
"""Build Learning Studio with approved concept illustrations, without notebook artifacts."""

from __future__ import annotations

import html
import json
import os
import re
from pathlib import Path
from urllib.parse import unquote

import mistune

from mathml import render_math


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "course.html"
ILLUSTRATIONS = {
    item["lesson"]: item
    for item in json.loads((ROOT / "tools" / "course_illustrations.json").read_text(encoding="utf-8"))
}


LESSONS = [
    (1, "level_1_foundations", "Foundations", "lesson_01_the_logic_of_hypothesis_testing.md"),
    (2, "level_1_foundations", "Foundations", "lesson_02_sampling_distributions_errors_and_power.md"),
    (3, "level_1_foundations", "Foundations", "lesson_03_one_sample_tests_for_means_and_proportions.md"),
    (4, "level_1_foundations", "Foundations", "lesson_04_two_independent_groups.md"),
    (5, "level_1_foundations", "Foundations", "lesson_05_paired_and_repeated_measurements.md"),
    (6, "level_2_applied_testing", "Applied testing", "lesson_06_three_or_more_independent_groups.md"),
    (7, "level_2_applied_testing", "Applied testing", "lesson_07_factorial_designs_interactions_and_ancova.md"),
    (8, "level_2_applied_testing", "Applied testing", "lesson_08_categorical_data_chi_square_fisher_and_mc_nemar.md"),
    (9, "level_2_applied_testing", "Applied testing", "lesson_09_proportions_and_a_and_b_tests.md"),
    (10, "level_2_applied_testing", "Applied testing", "lesson_10_correlation_and_regression_based_tests.md"),
    (11, "level_3_advanced_practice", "Advanced practice", "lesson_11_nonparametric_permutation_and_bootstrap_methods.md"),
    (12, "level_3_advanced_practice", "Advanced practice", "lesson_12_multiple_testing_equivalence_and_evidence_beyond_significance.md"),
    (13, "level_3_advanced_practice", "Advanced practice", "lesson_13_advanced_designs_clustering_and_time_to_event_outcomes.md"),
    (14, "level_3_advanced_practice", "Advanced practice", "lesson_14_test_selection_and_end_to_end_capstone.md"),
    (15, "level_3_advanced_practice", "Advanced practice", "lesson_15_course_review_and_statistical_reporting.md"),
]


VISUALS = {
    1: ("flow", "The evidence journey", "A defensible conclusion is a chain of connected decisions.", ["Question", "Estimand", "Reference", "Evidence", "Decision"]),
    2: ("hub", "The power system", "Power changes when any of four connected design levers move.", ["Effect size", "Sample size", "Variability", "Alpha"]),
    3: ("split", "One sample, two outcome types", "The benchmark question stays constant while the data structure changes the method.", ["Quantitative outcome|Compare a population mean with a fixed target.", "Binary outcome|Compare a population proportion with a fixed target."]),
    4: ("split", "Independent means separate units", "Each person or unit belongs to only one comparison group.", ["Group A|A distinct set of observational units.", "Group B|A different, non-overlapping set of units."]),
    5: ("flow", "Pairing preserves identity", "The analysis follows each unit across conditions before summarizing change.", ["Unit", "Before", "Within-pair change", "After"]),
    6: ("hub", "Omnibus first, contrasts second", "A multi-group analysis separates the global question from specific follow-up comparisons.", ["Group summaries", "Omnibus test", "Effect magnitude", "Adjusted follow-ups"]),
    7: ("matrix", "Interactions change the story", "The effect of one factor can depend on the level of another.", ["Factor A: low", "Factor A: high", "Factor B: low", "Factor B: high"]),
    8: ("matrix", "Counts become evidence", "A contingency table compares observed combinations with the pattern expected under independence.", ["Observed cell", "Expected cell", "Residual", "Association size"]),
    9: ("flow", "An experiment is more than a test", "Validity depends on the full path from assignment to decision.", ["Randomize", "Expose", "Measure", "Check quality", "Estimate impact"]),
    10: ("ladder", "Association has layers", "Move from shape to coefficient to model before discussing meaning.", ["Draw the relationship", "Choose the association measure", "Estimate uncertainty", "Inspect residual patterns", "Limit causal claims"]),
    11: ("split", "Three robust ideas", "Rank, permutation, and bootstrap methods solve different inferential problems.", ["Rearrange labels|Permutation builds a null reference.", "Resample observations|Bootstrap approximates estimator uncertainty."]),
    12: ("split", "Two questions beyond significance", "Multiplicity asks how to control errors across claims; equivalence asks whether important effects can be ruled out.", ["Multiplicity|Protect a family of decisions.", "Equivalence|Test against pre-defined practical bounds."]),
    13: ("split", "Dependence takes two forms", "Repeated observations share a cluster; survival records may end before the event occurs.", ["Clustered data|Rows from the same unit are correlated.", "Time-to-event data|Censoring preserves partial follow-up information."]),
    14: ("flow", "The end-to-end analysis", "Method selection is one step inside a broader reasoning workflow.", ["Decision", "Estimand", "Design", "Diagnostics", "Inference", "Communication"]),
    15: ("hub", "The course compass", "Every test family is reached by answering a small set of design questions.", ["Outcome type", "Independent unit", "Group count", "Pairing or clustering", "Practical threshold"]),
}


MISCONCEPTIONS = {
    1: [("The p-value is the probability the null is true", "It is calculated under the assumption that the null model is true."), ("Significant means important", "Detectability and practical value are separate questions.")],
    2: [("Eighty percent power is a universal rule", "The target should reflect the consequences of missing a meaningful effect."), ("Observed power explains a null result", "The confidence interval already shows the study's precision after data are observed.")],
    3: [("The benchmark can be chosen after seeing the sample", "A reference chosen from the same outcome data changes the meaning of the test."), ("A normality test mechanically chooses the method", "Design, estimand, sample size, and shape matter together.")],
    4: [("Equal variances are required for every mean comparison", "Welch's method directly allows unequal variances."), ("Mann–Whitney is always a median test", "Its interpretation depends on the shapes and ordering of the distributions.")],
    5: [("Before and after observations are independent", "They come from the same units and share person- or firm-specific information."), ("Check normality separately at each time", "The paired mean procedure concerns the distribution of within-pair differences.")],
    6: [("A significant omnibus result names the different groups", "It only establishes that at least one population contrast differs."), ("Every pair can be tested at the original alpha", "Unadjusted follow-ups inflate the chance of at least one false positive.")],
    7: [("Main effects are always meaningful with an interaction", "A strong interaction can make a single averaged main effect misleading."), ("Covariate adjustment creates causality", "Adjustment only addresses modeled variables and can introduce bias when poorly chosen.")],
    8: [("A large chi-square means a large association", "The statistic also grows with sample size; report an association measure."), ("Fisher's exact test is only for tiny samples", "It is chosen for sparse 2×2 structure, not by one universal sample-size cutoff.")],
    9: [("A valid z-test guarantees a valid experiment", "Randomization, exposure, logging, stopping, and metric definitions must also be sound."), ("Relative lift is enough", "Absolute differences reveal the real number of changed outcomes.")],
    10: [("Correlation proves causation", "Temporal order and alternative explanations remain unresolved."), ("A coefficient summarizes every relationship", "Nonlinearity, ties, and influential observations can make one number misleading.")],
    11: [("Nonparametric means assumption-free", "Independence and a defensible resampling scheme remain essential."), ("Any row can be resampled", "Resampling must preserve the original independent unit and dependence structure.")],
    12: [("Only large test families need correction", "Even two unplanned tests increase family-wise error."), ("Non-significance establishes equivalence", "Equivalence requires pre-specified bounds and two directional tests.")],
    13: [("More rows always mean more independent information", "Repeated rows within a cluster share information."), ("Censored means missing", "A censored record still contributes risk information up to its final observation time.")],
    14: [("Test selection begins with normality", "Begin with the decision, estimand, outcome, and dependence structure."), ("One significant secondary outcome rescues the project", "The planned hypothesis family determines how evidence should be combined.")],
    15: [("A decision tree can replace statistical judgment", "Selection guides orient the analysis but cannot diagnose every design nuance."), ("A complete report ends at the p-value", "Magnitude, precision, assumptions, provenance, and limitations complete the argument.")],
}


SCENARIOS = {
    1: "A study reports p = .08 with a wide interval. Which important effects are still compatible with the evidence?",
    2: "A team can recruit more participants or improve measurement precision. Which power lever should they prioritize, and why?",
    3: "A quality target was set after inspecting the sample. How does that change the credibility of the test?",
    4: "Two independent groups differ in shape and spread. Which estimand—means or relative ranks—matches the real question?",
    5: "Three measurements come from every participant. What information would be lost by pretending all rows are independent?",
    6: "An omnibus test detects a difference among four groups. What must happen before naming a specific pair?",
    7: "A group difference reverses across age categories. Why is the interaction more informative than one overall main effect?",
    8: "A table has several very small expected counts. What changes in the inferential strategy and reporting?",
    9: "An experiment has a small p-value but an unexpected assignment imbalance. Which issue should be investigated first?",
    10: "Age and media use are associated in a survey. Which statements remain valid without a causal design?",
    11: "Repeated measurements are nested within patients. What should be shuffled or resampled—the rows or the patients?",
    12: "A conventional difference test is inconclusive. What additional information is required before claiming equivalence?",
    13: "A clinic study measures many patients within only 20 clinics. Which count controls the independent information most directly?",
    14: "Two outcomes tell different stories in the same experiment. How should the primary question and multiplicity plan guide the conclusion?",
    15: "Before selecting a test, can you name the outcome, estimand, independent unit, dependence structure, and practical threshold?",
}


EXCLUDED_SECTIONS = {
    "concept map",
    "notebook setup",
    "implementation reference",
    "related lessons and source material",
}


def title_of(path: Path) -> str:
    match = re.search(r"^#\s+(.+)$", path.read_text(encoding="utf-8"), flags=re.M)
    return match.group(1).strip() if match else path.stem.replace("_", " ").title()


def clean_markdown(text: str) -> str:
    """Keep explanatory prose while removing notebook implementation artifacts."""
    text = re.sub(
        r"^> \*\*Authoritative lesson:\*\*.*\n(?:>.*\n?)+",
        "",
        text,
        count=1,
        flags=re.M,
    )
    output: list[str] = []
    skip_fence = False
    after_code = False
    skip_section = False
    skip_details = False
    for line in text.splitlines():
        if line.startswith("# "):
            continue
        heading = re.match(r"^##\s+(.+)$", line)
        if heading:
            name = heading.group(1).strip()
            normalized = name.lower()
            skip_section = normalized in EXCLUDED_SECTIONS
            after_code = False
            if skip_section:
                continue
            if normalized == "practice and solution":
                line = "## Guided reflection"
            if normalized == "additional practice":
                line = "## Independent practice"
        if skip_section:
            continue
        if line.startswith("```"):
            skip_fence = not skip_fence
            if not skip_fence:
                after_code = True
            continue
        if skip_fence:
            continue
        if after_code:
            if line.startswith("## "):
                after_code = False
            else:
                continue
        if "<details" in line:
            skip_details = True
            continue
        if skip_details:
            if "</details>" in line:
                skip_details = False
            continue
        if re.search(r"!\[[^\]]*\]\([^)]+\)", line):
            continue
        line = line.replace("**Practice.**", "**Reflection prompt.**")
        line = re.sub(r"`([^`]+)`", r"\1", line)
        output.append(line)
    cleaned = "\n".join(output)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


class TeachingRenderer(mistune.HTMLRenderer):
    def __init__(self, source: Path, page_map: dict[Path, str], heading_offset: int = 0):
        super().__init__(escape=True)
        self.source = source
        self.page_map = page_map
        self.heading_offset = heading_offset

    def heading(self, text: str, level: int, **attrs: object) -> str:
        return super().heading(text, min(level + self.heading_offset, 6), **attrs)

    def block_code(self, code: str, info: str | None = None) -> str:
        return ""

    def inline_code(self, text: str) -> str:
        return f'<span class="term">{html.escape(text)}</span>'

    def image(self, text: str, url: str, title: str | None = None) -> str:
        return ""

    def link(self, text: str, url: str, title: str | None = None) -> str:
        if re.match(r"^[a-z]+://", url):
            return f'<a href="{html.escape(url, quote=True)}" target="_blank" rel="noopener">{text}</a>'
        target_text, _, _ = url.partition("#")
        target = (self.source.parent / unquote(target_text)).resolve()
        if target in self.page_map:
            return f'<a href="#{self.page_map[target]}">{text}</a>'
        return text


def illustration_html(spec: dict) -> str:
    source = spec["src"]
    asset = (ROOT / source).resolve()
    if not source.startswith("assets/illustrations/") or not asset.is_relative_to(ROOT / "assets" / "illustrations") or not asset.is_file():
        raise ValueError(f"Missing or invalid approved illustration: {source}")
    return (
        f'<figure class="lesson_illustration" data-illustration="lesson_{spec["lesson"]:02d}">'
        f'<a class="illustration_open" href="{html.escape(source, quote=True)}" target="_blank" rel="noopener" aria-label="Open illustration at full size">'
        f'<img src="{html.escape(source, quote=True)}" width="{spec["width"]}" height="{spec["height"]}" loading="lazy" decoding="async" alt="{html.escape(spec["alt"], quote=True)}">'
        '<span class="illustration_open_label">View full size</span></a>'
        f'<figcaption><p>{html.escape(spec["caption"])}</p>'
        f'<p class="illustration_labels">{html.escape(spec["labels_text"])}</p></figcaption></figure>'
    )


def render_sections(path: Path, page_map: dict[Path, str], lesson_number: int | None = None) -> str:
    cleaned = clean_markdown(path.read_text(encoding="utf-8"))
    renderer = TeachingRenderer(path, page_map, heading_offset=1 if lesson_number is not None else 0)
    markdown = mistune.create_markdown(renderer=renderer, plugins=["table", "strikethrough", "math"])
    renderer.register("inline_math", lambda _, expression: render_math(expression, display=False))
    renderer.register("block_math", lambda _, expression: render_math(expression, display=True))
    parts = re.split(r"(?=^##\s+)", cleaned, flags=re.M)
    rendered = []
    phases: dict[str, list[str]] = {"orient": [], "explore": [], "apply": []}
    illustration = ILLUSTRATIONS.get(lesson_number)
    illustration_inserted = False
    for index, part in enumerate(parts):
        if not part.strip():
            continue
        body = markdown(part)
        heading = re.search(r"^##\s+(.+)$", part, flags=re.M)
        name = heading.group(1).lower() if heading else "lesson overview"
        if illustration and name == illustration["section"].lower():
            figure = illustration_html(illustration)
            before = illustration.get("before_heading")
            if before:
                marker = re.search(r"<h([1-6])>" + re.escape(before) + r"</h\1>", body)
                if not marker:
                    raise ValueError(f"Illustration insertion heading missing in lesson {lesson_number}: {before}")
                body = body[:marker.start()] + figure + body[marker.start():]
            else:
                body += figure
            illustration_inserted = True
        wide = " wide" if index in {0, 1} or any(label in part.lower() for label in ["summary", "learning objectives", "data used", "reproducibility"]) else ""
        module = f'<section class="module{wide}">{body}</section>'
        rendered.append(module)
        if lesson_number is not None:
            if name in {"lesson overview", "learning objectives", "data used in this lesson"}:
                phases["orient"].append(module)
            elif re.match(r"\d+\.\d+\s", name) or name == "worked example and interpretation":
                phases["explore"].append(module)
            else:
                phases["apply"].append(module)
    if lesson_number is not None:
        if illustration and not illustration_inserted:
            raise ValueError(f"Illustration insertion section missing in lesson {lesson_number}: {illustration['section']}")
        def phase(number: str, title: str, description: str, content: str) -> str:
            return (f'<section class="lesson_phase" aria-label="{title}">'
                    f'<header class="phase_header"><span>{number}</span><div><h2>{title}</h2><p>{description}</p></div></header>'
                    f'<div class="studio_board">{content}</div></section>')
        return "\n".join([
            phase("01", "Get oriented", "The question, learning goals, and visual model.",
                  visual_module(lesson_number) + "".join(phases["orient"])),
            phase("02", "Build understanding", "Follow the ideas in sequence, then check common misconceptions.",
                  "".join(phases["explore"]) + misconception_module(lesson_number)),
            phase("03", "Apply and reflect", "Use the scenario and take away the practical lessons.",
                  scenario_module(lesson_number) + "".join(phases["apply"])),
        ])
    return "\n".join(rendered)


def visual_module(number: int) -> str:
    kind, title, intro, items = VISUALS[number]
    blocks = []
    for index, item in enumerate(items, 1):
        if "|" in item:
            heading, description = item.split("|", 1)
        else:
            heading, description = item, ""
        blocks.append(
            f'<div class="visual_item"><span>{index:02d}</span><strong>{html.escape(heading)}</strong>'
            f'{f"<small>{html.escape(description)}</small>" if description else ""}</div>'
        )
    return f"""<section class="module wide visual_lesson">
      <span class="eyebrow">Visual model</span><h3>{html.escape(title)}</h3><p>{html.escape(intro)}</p>
      <div class="visual_model {kind}" aria-label="{html.escape(title)}">{''.join(blocks)}</div>
    </section>"""


def misconception_module(number: int) -> str:
    cards = "".join(
        f'<article class="misconception"><span aria-hidden="true">×</span><div><h3>{html.escape(wrong)}</h3><p>{html.escape(right)}</p></div></article>'
        for wrong, right in MISCONCEPTIONS[number]
    )
    return f"""<section class="module wide"><span class="eyebrow">Misconception clinic</span>
      <h3>Pause before making these claims</h3><div class="misconception_grid">{cards}</div></section>"""


def scenario_module(number: int) -> str:
    return f"""<section class="module wide scenario"><span class="eyebrow">Scenario prompt</span>
      <h3>Apply the idea before moving on</h3><p>{html.escape(SCENARIOS[number])}</p>
      <div class="thinking_steps"><span>Clarify the estimand</span><span>Check the design</span><span>Describe the uncertainty</span><span>State the limit</span></div></section>"""


def lesson_article(number: int, level: str, path: Path, page_map: dict[Path, str]) -> tuple[str, str]:
    title = title_of(path)
    sections = render_sections(path, page_map, lesson_number=number)
    article = f"""<article class="course_page" id="lesson_{number:02d}" data-title="{html.escape(title, quote=True)}" data-group="{html.escape(level, quote=True)}">
      <header class="lesson_header"><div><span class="eyebrow">Lesson {number:02d} / 15 · {html.escape(level)}</span><h1>{html.escape(title.removeprefix(f'Lesson {number}: '))}</h1></div>
      <label class="lesson_complete"><input type="checkbox" data-progress="lesson_{number:02d}"> Mark lesson complete</label></header>
      {sections}
      <nav class="page_nav" aria-label="Lesson navigation"></nav></article>"""
    return title, article


def supporting_article(identifier: str, group: str, path: Path, page_map: dict[Path, str]) -> tuple[str, str]:
    title = title_of(path)
    return title, f"""<article class="course_page" id="{identifier}" data-title="{html.escape(title, quote=True)}" data-group="{html.escape(group, quote=True)}">
      <header class="lesson_header"><div><span class="eyebrow">{html.escape(group)}</span><h1>{html.escape(title)}</h1></div></header>
      <div class="studio_board">{render_sections(path, page_map)}</div><nav class="page_nav" aria-label="Page navigation"></nav></article>"""


def home_article() -> tuple[str, str]:
    title = "Hypothesis Testing and Statistical Inference"
    levels = "".join(
        f'<article class="level_card"><span>Level {index} · Lessons {start:02d}–{start + 4:02d}</span>'
        f'<h2>{name}</h2><p>{description}</p><ol class="level_lessons">' +
        "".join(f'<li><a href="#lesson_{number:02d}"><span>{number:02d}</span>{html.escape(title_of(ROOT / level_dir / "markdown" / filename).split(": ", 1)[-1])}</a></li>'
                for number, level_dir, _, filename in LESSONS if start <= number < start + 5) +
        '</ol></article>'
        for index, name, start, description in [
            (1, "Foundations", 1, "Build accurate intuition for evidence, uncertainty, one-sample, independent, and paired questions."),
            (2, "Applied testing", 6, "Handle multi-group, factorial, categorical, experimental, correlation, and regression questions."),
            (3, "Advanced practice", 11, "Use resampling, multiplicity, equivalence, clustered and survival methods, then synthesize the workflow."),
        ]
    )
    article = f"""<article class="course_page active" id="course_overview" data-title="{title}" data-group="Start here">
      <header class="course_hero"><span class="eyebrow">A visual concept course</span><h1>Learn to reason from questions to defensible decisions</h1>
      <p>Fifteen lessons teach hypothesis testing through explanations, visual models, misconceptions, scenarios, and reflection—without notebook code or answer keys.</p>
      <a class="button primary" href="#lesson_01">Start with Lesson 1</a></header>
      <section class="course_path" aria-labelledby="course_path_title"><div class="path_intro"><span class="eyebrow">Your learning path</span><h2 id="course_path_title">Three levels, one clear progression</h2><p>Begin with the foundations, then move through applied methods to advanced decisions.</p></div><div class="level_grid">{levels}</div></section>
      <section class="module wide course_principles"><span class="eyebrow">Course principles</span><h2>What students practice in every lesson</h2>
      <div class="principle_grid"><div><strong>Start with design</strong><span>Identify the population, independent unit, and comparison.</span></div><div><strong>Name the estimand</strong><span>Define exactly what the analysis aims to learn.</span></div><div><strong>Show uncertainty</strong><span>Interpret intervals and compatible effects, not only thresholds.</span></div><div><strong>End with meaning</strong><span>Separate evidence, magnitude, causality, and practical action.</span></div></div></section>
      <nav class="page_nav" aria-label="Page navigation"></nav></article>"""
    return title, article


def main() -> None:
    lesson_paths = [ROOT / level / "markdown" / filename for _, level, _, filename in LESSONS]
    supporting = {
        (ROOT / "docs" / "syllabus.md").resolve(): "syllabus",
        (ROOT / "data" / "readme.md").resolve(): "data_stories",
        (ROOT / "docs" / "test_selection_guide.md").resolve(): "test_selection_guide",
        (ROOT / "docs" / "glossary.md").resolve(): "glossary",
    }
    page_map = {path.resolve(): f"lesson_{number:02d}" for (number, _, _, _), path in zip(LESSONS, lesson_paths)}
    page_map.update(supporting)

    pages: list[tuple[str, str, str]] = []
    home_title, home_html = home_article()
    pages.append(("Start here", home_title, home_html))
    for identifier, group, path in [
        ("syllabus", "Start here", ROOT / "docs" / "syllabus.md"),
        ("data_stories", "Start here", ROOT / "data" / "readme.md"),
    ]:
        title, article = supporting_article(identifier, group, path, page_map)
        pages.append((group, title, article))
    for (number, _, level, _), path in zip(LESSONS, lesson_paths):
        title, article = lesson_article(number, level, path, page_map)
        pages.append((level, title, article))
    for identifier, path in [
        ("test_selection_guide", ROOT / "docs" / "test_selection_guide.md"),
        ("glossary", ROOT / "docs" / "glossary.md"),
    ]:
        title, article = supporting_article(identifier, "Reference", path, page_map)
        pages.append(("Reference", title, article))

    navigation = []
    for group in ["Start here", "Foundations", "Applied testing", "Advanced practice", "Reference"]:
        entries = [(index, title, article) for index, (page_group, title, article) in enumerate(pages) if page_group == group]
        is_level = group in {"Foundations", "Applied testing", "Advanced practice"}
        number = {"Foundations": 1, "Applied testing": 2, "Advanced practice": 3}.get(group)
        if is_level:
            navigation.append(f'<details class="nav_group nav_level" data-level="{number}"{" open" if number == 1 else ""}><summary><span class="nav_level_number">{number:02d}</span><span><strong>{html.escape(group)}</strong><small>Lessons {5 * number - 4:02d}–{5 * number:02d}</small></span></summary><div class="nav_children">')
        else:
            navigation.append(f'<section class="nav_group"><h2>{html.escape(group)}</h2>')
        for index, title, article in entries:
            identifier = re.search(r'<article class="[^"]*\bcourse_page\b[^"]*" id="([^"]+)"', article).group(1)
            number = re.match(r"lesson_(\d+)", identifier)
            marker = f'<span class="lesson_number">{number.group(1)}</span>' if number else '<span class="doc_dot">•</span>'
            navigation.append(f'<a class="nav_link" href="#{identifier}" data-page="{identifier}" data-search="{html.escape((group + " " + title).lower(), quote=True)}">{marker}<span>{html.escape(title.removeprefix("Lesson "))}</span></a>')
        navigation.append("</div></details>" if is_level else "</section>")

    template = (ROOT / "tools" / "learning_studio_template.html").read_text(encoding="utf-8")
    course_css = (ROOT / "tools" / "course_styles.css").read_text(encoding="utf-8")
    translation_path = ROOT / "tools" / "site_translations.fa.json"
    if not translation_path.exists():
        raise SystemExit("Static Persian website translations are missing.")
    translations = json.loads(translation_path.read_text(encoding="utf-8"))
    for spec in ILLUSTRATIONS.values():
        for field in ["caption", "alt", "labels_text"]:
            translations[spec[field]] = spec[field + "_fa"]
    translations.update({
        "View full size": "مشاهده در اندازهٔ کامل",
        "Open illustration at full size": "باز کردن تصویر در اندازهٔ کامل",
    })
    translation_json = json.dumps(translations, ensure_ascii=False).replace("<", "\\u003c")
    order = [re.search(r'id="([^"]+)"', article).group(1) for _, _, article in pages]
    result = (
        template.replace("__COURSE_CSS__", course_css)
        .replace("__FA_TRANSLATIONS__", translation_json)
        .replace("__NAVIGATION__", "\n".join(navigation))
        .replace("__ARTICLES__", "\n".join(article for _, _, article in pages))
        .replace("__PAGE_ORDER__", json.dumps(order))
    )
    OUTPUT.write_text(result, encoding="utf-8")
    print(f"Built Learning Studio with {len(pages)} teaching pages and 15 lessons.")


if __name__ == "__main__":
    main()
