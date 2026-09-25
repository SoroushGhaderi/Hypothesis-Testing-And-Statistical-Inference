# Lesson 15: Course Review and Statistical Reporting

> **Authoritative lesson:** This Markdown file is the maintained teaching source. The notebook is a supporting,
> executable example and should not be used to overwrite this lesson.

## Lesson overview

Statistical reporting is the disciplined synthesis of question, design, method, evidence, uncertainty, practical meaning, and limitations.

### Why this matters

A correct calculation is not useful until a reader can understand what was estimated, under which assumptions, and what action follows.

### Prerequisites

All earlier lessons or equivalent applied hypothesis-testing experience.

## Learning objectives

1. Navigate the complete hypothesis-test selection map
2. Recognize recurring interpretation and reporting mistakes
3. Use a minimum reporting standard for any test family
4. Plan next steps for more advanced inference

## Concept map

The lesson covers the following concepts explicitly.

| Concept | Meaning | Teaching section |
|---|---|---|
| Test-selection map | Match outcome type, group count, pairing, sparsity, clustering, and censoring to a method family. | [15.1 Quick selection map](#151-quick-selection-map) |
| Minimum reporting standard | Nine elements required for a transparent result. | [15.2 Minimum reporting standard](#152-minimum-reporting-standard) |
| Teaching decision helper | Encode a simplified outcome/design branching rule. | [15.1 Quick selection map](#151-quick-selection-map) |
| Common interpretation failures | Avoid p-value, non-significance, multiplicity, dependence, and causality errors. | [15.3 Common mistakes to avoid](#153-common-mistakes-to-avoid) |
| Knowledge-check workflow | Use short questions to verify transferable understanding. | [Final knowledge check](#final-knowledge-check) |
| Advanced learning path | Generalized linear, hierarchical, causal, sequential, missing-data, robust, and Bayesian methods. | [Where to go next](#where-to-go-next) |

## Data used in this lesson

The examples use the local, documented real-data bundle. See the [dataset guide](../../data/readme.md) for provenance,
variable definitions, cleaning decisions, and reuse notes.

| Dataset | Observation unit | Lesson use | Interpretation boundary |
|---|---|---|---|
| Course data bundle | respondent, student, participant, firm-year, or patient depending on the file | Four real datasets are loaded to connect outcome structure and dependence to a starting test family. | The rule-based helper is an orientation tool, not an automated statistical decision maker. |

## Notebook setup

The examples use the shared scientific-Python setup described in the
[Notebook Implementation Toolkit](../../docs/maintenance/notebook_toolkit.md). That reference explains imports, deterministic random-number
generation, plotting configuration, output behavior, and why global warning suppression is discouraged.

## 15.1 Quick selection map

| Outcome and design | Primary family | Common alternative or extension |
|---|---|---|
| One quantitative sample vs target | one-sample t | signed-rank / permutation |
| Two independent quantitative groups | Welch t | Mann–Whitney / permutation |
| Two paired quantitative conditions | paired t | signed-rank |
| 3+ independent quantitative groups | ANOVA / Welch ANOVA | Kruskal–Wallis |
| 3+ repeated quantitative conditions | RM-ANOVA / mixed model | Friedman |
| One proportion vs target | exact binomial / z | — |
| Two independent proportions | two-proportion z / chi-square | Fisher exact |
| Two paired binary outcomes | McNemar | exact McNemar |
| Two categorical variables | chi-square independence | exact/simulation methods |
| Continuous association | Pearson / regression | Spearman / Kendall |
| Time-to-event by group | log-rank | Cox model |
| Clustered/repeated observations | mixed model / GEE | cluster-level analysis |


## 15.2 Minimum reporting standard

Every result should make these visible:

1. Research question, population, outcome, groups, and observational unit.
2. Design and sampling/randomization process.
3. Estimand and hypotheses, including sidedness and alpha.
4. Descriptive statistics and a plot of the raw data or sufficient counts.
5. Assumption checks and any deviations from the analysis plan.
6. Estimate in natural units, confidence interval, and effect size.
7. Test statistic, degrees of freedom when applicable, and exact p-value.
8. Multiplicity method and hypothesis family.
9. Practical interpretation, limitations, and next decision.



```python
def recommend_test(outcome, groups=1, paired=False, expected_sparse=False):
    # A teaching aid—not a substitute for design expertise.
    if outcome == "time-to-event":
        return "Log-rank for curves; survival regression for adjustment"
    if outcome == "categorical":
        if paired:
            return "McNemar (2 conditions) or Cochran Q (3+ conditions)"
        if groups == 1:
            return "Chi-square goodness-of-fit or exact binomial/multinomial"
        return "Fisher exact" if expected_sparse else "Chi-square independence / proportion test"
    if outcome in {"continuous", "ordinal"}:
        if groups == 1:
            return "One-sample t; signed-rank/permutation when appropriate"
        if groups == 2:
            return "Paired t / signed-rank" if paired else "Welch t / Mann-Whitney"
        return "RM-ANOVA/mixed model/Friedman" if paired else "ANOVA/Welch ANOVA/Kruskal-Wallis"
    return "Clarify the outcome, estimand, and dependence structure"

# Load each real course dataset so the review is anchored in the same evidence
# used throughout the earlier lessons.
dataset_rows = {
    "ANES": len(pd.read_csv(DATA_DIR / "anes96_clean.csv")),
    "Grunfeld": len(pd.read_csv(DATA_DIR / "grunfeld_investment.csv")),
    "Spector": len(pd.read_csv(DATA_DIR / "spector_program.csv")),
    "Heart transplant": len(pd.read_csv(DATA_DIR / "heart_transplant_survival.csv")),
}

data_examples = [
    {"dataset": "ANES", "outcome": "continuous", "groups": 2, "paired": False, "sparse": False},
    {"dataset": "Grunfeld", "outcome": "continuous", "groups": 2, "paired": True, "sparse": False},
    {"dataset": "Spector", "outcome": "categorical", "groups": 2, "paired": False, "sparse": True},
    {"dataset": "Heart transplant", "outcome": "time-to-event", "groups": 2, "paired": False, "sparse": False},
]
pd.DataFrame([{**row, "rows": dataset_rows[row["dataset"]],
               "starting point": recommend_test(
                   row["outcome"], row["groups"], row["paired"], row["sparse"])}
              for row in data_examples])

```




| Term | dataset | outcome | groups | paired | sparse | rows | starting point |
|---|---|---|---|---|---|---|---|
| 0 | ANES | continuous | 2 | False | False | 944 | Welch t / Mann-Whitney |
| 1 | Grunfeld | continuous | 2 | True | False | 220 | Paired t / signed-rank |
| 2 | Spector | categorical | 2 | False | True | 32 | Fisher exact |
| 3 | Heart transplant | time-to-event | 2 | False | False | 69 | Log-rank for curves; survival regression for a... |



## 15.3 Common mistakes to avoid

- Treating p-values as probabilities that a hypothesis is true.
- Declaring "no effect" from a non-significant result.
- Choosing a test only from a normality test p-value.
- Ignoring pairing, clustering, repeated users, or time dependence.
- Reporting standardized effects without raw-unit effects and intervals.
- Running many analyses and presenting only the smallest p-value.
- Switching to a one-sided test after seeing the direction.
- Confusing association with causation.
- Treating statistical significance as a decision rule without costs and practical thresholds.


## Worked example and interpretation

### What the helper actually does

The final notebook uses a short rule-based `recommend_test` helper to map four dataset examples to *starting* method families. It identifies ANES as an independent continuous-group comparison (Welch or Mann–Whitney), Grunfeld as paired continuous observations (paired t or signed-rank), Spector as a sparse independent categorical table (Fisher), and heart-transplant data as time-to-event observations (log-rank or survival regression). The row counts—944, 220, 32, and 69—are dataset sizes, **not** always counts of independent units. Grunfeld's 220 rows, for example, belong to 11 repeated firms.

### What still requires judgment

This helper cannot infer the actual estimand, missing-data mechanism, causal design, distribution shape, multiplicity family, censoring assumptions, or practical threshold from a few input flags. Its answer is therefore a prompt to inspect the relevant lesson, not an automated statistical recommendation. A complete report names the data source and independent unit; gives the effect in natural units with an interval; states the chosen method and assumptions; explains statistical and practical uncertainty; and describes what the analysis cannot establish. The final knowledge check asks the learner to defend those choices rather than merely recall a test name.

## Final knowledge check

1. Why does a 95% confidence interval that includes zero not prove zero effect?
2. What changes when observations are paired?
3. When is Fisher exact preferable to chi-square?
4. Why should effect sizes be reported in natural units?
5. How do Holm and Benjamini–Hochberg control different error criteria?

<details><summary>Answer guide</summary>

1. The interval contains a range of effects compatible with the data; zero is only one value.
2. Inference must use within-pair information and cannot assume row-level independence.
3. For sparse 2x2 tables or small expected counts where the chi-square approximation is unreliable.
4. Natural units connect uncertainty to scientific, operational, or clinical decisions.
5. Holm controls the chance of any false rejection in a family; BH controls the expected false discovery
   proportion among rejections under its assumptions.
</details>

## Where to go next

Study generalized linear models, hierarchical models, causal inference, sequential testing, missing-data
methods, robust statistics, and Bayesian modeling. The central habit remains the same: align the question,
design, estimand, model, uncertainty statement, and decision.


## Reproducibility checklist

- State the population, outcome, groups, and sampling unit.
- State $H_0$, $H_1$, alpha, and whether the test is one- or two-sided before looking at results.
- Verify independence from the design; use plots and diagnostics for distributional assumptions.
- Report the estimate, confidence interval, effect size, test statistic, degrees of freedom, and exact p-value.
- Separate statistical evidence from practical importance and acknowledge design limitations.

## Implementation reference

These APIs and code patterns are demonstrated in the supporting notebook.

| API or pattern | Purpose | Usage guidance |
|---|---|---|
| `pandas.read_csv` | Load each real dataset represented in the final selection exercise. | Dataset structure informs the method; filenames alone do not. |
| `recommend_test` helper | Demonstrate a readable rule-based teaching aid. | It is not a validated automated method selector. |
| `pandas.DataFrame` from records | Present scenario-to-method mappings in a scannable table. | The table documents rules but does not encode all design nuance. |

## Best practices

- Use the selection map as a starting point, then inspect the design and estimand.
- Report uncertainty and practical thresholds.
- Make deviations and limitations easy to find.

## Common mistakes and edge cases

- Automating test choice from column data types alone.
- Reporting a p-value without an estimate and interval.
- Hiding exploratory decisions behind confirmatory language.

## Additional practice

1. Draft a complete results paragraph from any earlier worked example.
2. Find one case where the same outcome type requires different methods because dependence changes.

## Related lessons and source material

- **Previous:** [Lesson 14 Test Selection and End-to-End Capstone](lesson_14_test_selection_and_end_to_end_capstone.md)
- **Supporting notebook:** [lesson_15_course_review_and_statistical_reporting.ipynb](../lesson_15_course_review_and_statistical_reporting.ipynb)
- **Coverage record:** [Course Coverage Index](../../docs/maintenance/course_coverage_index.md#lesson-15-course-review-and-statistical-reporting)
