# Syllabus

## Course outcome

By the end of the course, learners can translate a research question into an estimand and testable hypotheses;
choose a method that respects outcome type and dependence; diagnose assumptions; compute and interpret estimates,
intervals, effect sizes, and p-values; and communicate uncertainty without overstating evidence.

## Modules

1. **Level 1 — Foundations (Lessons 1–5):** logic, power, one-sample, independent, and paired tests.
2. **Level 2 — Applied Testing (Lessons 6–10):** multi-group, factorial, categorical, experimental, and association tests.
3. **Level 3 — Advanced Practice (Lessons 11–15):** resampling, multiplicity, advanced designs, capstone, and review.

## Suggested pacing

- 15 sessions of 90–120 minutes.
- Before class: read the authoritative Markdown lesson.
- During class: run and modify the notebook examples.
- After class: complete the practice prompt without opening its solution.

Learners may use [course.html](../course.html) as a visual, concept-first teaching interface or read the authoritative
Markdown lessons directly. The Learning Studio preserves the explanations and reasoning goals while replacing
implementation detail with visual models, misconception clinics, and guided scenarios. Code, worked solutions,
raw outputs, and notebook plots remain in the Markdown/notebook study materials rather than the classroom HTML.

## Data progression

- **ANES 1996** is the main clean dataset for foundational and observational comparisons.
- **Spector** supplies a small exact-test example.
- **Grunfeld** introduces genuine pairing and repeated observations within firms.
- **RAND HIE** supports experimental proportion examples and the capstone.
- **Heart transplant survival** introduces censoring and time-to-event analysis.

Each lesson states its observation unit, analytic use, and interpretation boundary. Full provenance and cleaning notes
are in the [Course Data Bundle guide](../data/readme.md).

## Assessment plan

- Short concept checks after Lessons 1–3.
- Method-selection exercises after Lessons 4–10.
- Reproducible mini-analysis after Lesson 11.
- Pre-analysis plan covering power and multiplicity after Lesson 12.
- Final capstone: question, design audit, analysis, results paragraph, and limitations.

## Capstone rubric

| Criterion | Evidence |
|---|---|
| Question and estimand | Population, unit, outcome, contrast, time horizon |
| Design validity | Sampling/randomization, independence, missingness, confounding |
| Method choice | Test family justified from design and outcome |
| Diagnostics | Relevant plots and assumption checks |
| Complete inference | Estimate, CI, effect size, statistic, df, p-value |
| Multiplicity | Hypothesis family and correction documented |
| Communication | Practical meaning, uncertainty, limitations, next action |
| Reproducibility | Clean notebook that runs top to bottom |
