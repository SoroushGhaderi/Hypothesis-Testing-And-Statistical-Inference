# hypothesis_testing_and_statistical_inference

A complete, executable Python course on choosing, running, interpreting, and reporting hypothesis tests.
The course is split into three progressive levels so learners can stop at the depth they need. The Markdown
lessons are authoritative; Jupyter notebooks are supporting executable examples.

For a classroom-friendly presentation, open the generated [Learning Studio](course.html). It transforms the
authoritative lesson explanations into a concept-first experience with visual models, misconception checks, scenarios,
navigation, search, progress tracking, responsive layout, and print styling. Notebook code, worked solutions, raw
outputs, and notebook plots remain outside the student-facing HTML.

## Audience and prerequisites

The course is designed for beginner-to-intermediate data analysts, data scientists, and researchers who know
basic Python, descriptive statistics, probability, and confidence intervals. Lessons use plain English while
retaining the mathematical detail needed to analyze real studies responsibly.

## Course principles

- Start from the research question, design, and estimand—not a software menu.
- Check assumptions before interpreting a test.
- Report estimates, confidence intervals, and effect sizes alongside p-values.
- Respect pairing, clustering, randomization, censoring, and the true unit of analysis.
- Separate statistical evidence from practical importance and causal interpretation.

## Choose your level

### [Level 1 — Foundations](level_1_foundations/readme.md)

Learn the logic of testing and handle the most common one- and two-sample designs.

| # | Supporting notebook | Authoritative lesson |
|---:|---|---|
| 01 | [The Logic of Hypothesis Testing](level_1_foundations/lesson_01_the_logic_of_hypothesis_testing.ipynb) | [Lesson](level_1_foundations/markdown/lesson_01_the_logic_of_hypothesis_testing.md) |
| 02 | [Sampling Distributions, Errors, and Power](level_1_foundations/lesson_02_sampling_distributions_errors_and_power.ipynb) | [Lesson](level_1_foundations/markdown/lesson_02_sampling_distributions_errors_and_power.md) |
| 03 | [One-Sample Tests for Means and Proportions](level_1_foundations/lesson_03_one_sample_tests_for_means_and_proportions.ipynb) | [Lesson](level_1_foundations/markdown/lesson_03_one_sample_tests_for_means_and_proportions.md) |
| 04 | [Two Independent Groups](level_1_foundations/lesson_04_two_independent_groups.ipynb) | [Lesson](level_1_foundations/markdown/lesson_04_two_independent_groups.md) |
| 05 | [Paired and Repeated Measurements](level_1_foundations/lesson_05_paired_and_repeated_measurements.ipynb) | [Lesson](level_1_foundations/markdown/lesson_05_paired_and_repeated_measurements.md) |

### [Level 2 — Applied Testing](level_2_applied_testing/readme.md)

Analyze multi-group, factorial, categorical, experimental, correlation, and regression questions.

| # | Supporting notebook | Authoritative lesson |
|---:|---|---|
| 06 | [Three or More Independent Groups](level_2_applied_testing/lesson_06_three_or_more_independent_groups.ipynb) | [Lesson](level_2_applied_testing/markdown/lesson_06_three_or_more_independent_groups.md) |
| 07 | [Factorial Designs, Interactions, and ANCOVA](level_2_applied_testing/lesson_07_factorial_designs_interactions_and_ancova.ipynb) | [Lesson](level_2_applied_testing/markdown/lesson_07_factorial_designs_interactions_and_ancova.md) |
| 08 | [Categorical Data: Chi-Square, Fisher, and McNemar](level_2_applied_testing/lesson_08_categorical_data_chi_square_fisher_and_mc_nemar.ipynb) | [Lesson](level_2_applied_testing/markdown/lesson_08_categorical_data_chi_square_fisher_and_mc_nemar.md) |
| 09 | [Proportions and A/B Tests](level_2_applied_testing/lesson_09_proportions_and_a_and_b_tests.ipynb) | [Lesson](level_2_applied_testing/markdown/lesson_09_proportions_and_a_and_b_tests.md) |
| 10 | [Correlation and Regression-Based Tests](level_2_applied_testing/lesson_10_correlation_and_regression_based_tests.ipynb) | [Lesson](level_2_applied_testing/markdown/lesson_10_correlation_and_regression_based_tests.md) |

### [Level 3 — Advanced Practice](level_3_advanced_practice/readme.md)

Use resampling, multiplicity, equivalence, clustered and survival methods, then complete a capstone.

| # | Supporting notebook | Authoritative lesson |
|---:|---|---|
| 11 | [Nonparametric, Permutation, and Bootstrap Methods](level_3_advanced_practice/lesson_11_nonparametric_permutation_and_bootstrap_methods.ipynb) | [Lesson](level_3_advanced_practice/markdown/lesson_11_nonparametric_permutation_and_bootstrap_methods.md) |
| 12 | [Multiple Testing, Equivalence, and Evidence Beyond Significance](level_3_advanced_practice/lesson_12_multiple_testing_equivalence_and_evidence_beyond_significance.ipynb) | [Lesson](level_3_advanced_practice/markdown/lesson_12_multiple_testing_equivalence_and_evidence_beyond_significance.md) |
| 13 | [Advanced Designs: Clustering and Time-to-Event Outcomes](level_3_advanced_practice/lesson_13_advanced_designs_clustering_and_time_to_event_outcomes.ipynb) | [Lesson](level_3_advanced_practice/markdown/lesson_13_advanced_designs_clustering_and_time_to_event_outcomes.md) |
| 14 | [Test Selection and End-to-End Capstone](level_3_advanced_practice/lesson_14_test_selection_and_end_to_end_capstone.ipynb) | [Lesson](level_3_advanced_practice/markdown/lesson_14_test_selection_and_end_to_end_capstone.md) |
| 15 | [Course Review and Statistical Reporting](level_3_advanced_practice/lesson_15_course_review_and_statistical_reporting.ipynb) | [Lesson](level_3_advanced_practice/markdown/lesson_15_course_review_and_statistical_reporting.md) |

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
jupyter notebook
```

Read the Markdown lessons in order. Open the supporting notebooks when you want to run or modify an example.
All primary examples use the included real-data CSV files, so no network download is required. Randomness is limited
to reproducible permutation, bootstrap, and power-resampling procedures.

## Course data

The course uses one primary survey dataset and four compact specialist datasets so each lesson has a data structure
that honestly matches its design: independent observations, paired firms, a real experiment, or censored follow-up.
Read the [Course Data Bundle guide](data/readme.md) for provenance, variables, cleaning, and interpretation boundaries.

## Recommended path

- Start with **Level 1** for essential hypothesis-testing literacy.
- Continue to **Level 2** for routine professional analysis.
- Add **Level 3** only when you need modern or advanced methods and an end-to-end capstone.

## Repository map

- `level_1_foundations/` — five essential introductory lessons.
- `level_2_applied_testing/` — five lessons for everyday applied analysis.
- `level_3_advanced_practice/` — five advanced and synthesis lessons.
- Each level contains supporting notebooks, a short README, and an authoritative `markdown/` course folder.
- `data/` — five local real-data CSV files plus provenance and cleaning documentation.
- [Documentation index](docs/readme.md) — syllabus, learner references, and maintenance records.
- `course.html` — single-file visual Learning Studio derived from the authoritative teaching content.
- `requirements.txt` — Python dependencies.
- `tools/build_course.py` — end-to-end real-data refresh and validation entry point.
- `tools/build_course_data.py` — deterministic dataset builder from statsmodels sources.
- `tools/apply_course_data.py` — real-data notebook implementation manifest.
- `tools/sync_markdown_from_notebooks.py` — synchronizes executed examples into authoritative lessons.
- `tools/audit_markdown_notebooks.py` — verifies notebook/Markdown teaching parity.
- `tools/build_teaching_html.py` — builds the concept-first Learning Studio from authoritative Markdown lessons.
- `tools/build_learning_studio.py` — defines lesson visuals, misconception clinics, scenarios, and HTML content policy.
- `tools/validate_course.py` — structural and execution validation.
- `tools/validate_markdown_course.py` — Markdown coverage, structure, and link validation.
- `tools/validate_teaching_html.py` — checks pages, anchors, visual teaching modules, and the no-code/no-solution policy.
- `tools/validate_math.py` — checks formulas in Markdown, notebook text, and the standalone HTML.

## Relationship to the local statistics courses

This course follows the lesson-oriented structure used by the neighboring probability, discrete-data, and
time-series courses: numbered notebooks, learning objectives, plain-English explanations, runnable Python,
visualizations, practice with solutions, and summaries. It adds a consistent inferential workflow, modern APIs,
effect sizes, confidence intervals, power, multiplicity, equivalence, resampling, clustered data, and survival analysis.
