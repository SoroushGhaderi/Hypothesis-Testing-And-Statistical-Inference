# Lesson 9: Proportions and A/B Tests

> **Authoritative lesson:** This Markdown file is the maintained teaching source. The notebook is a supporting,
> executable example and should not be used to overwrite this lesson.

## Lesson overview

An A/B test is a randomized comparison whose binary outcome is often analyzed through independent proportions.

### Why this matters

The design can support causal decisions only when assignment, exposure, metrics, and stopping are handled correctly.

### Prerequisites

Lessons 2, 3, and 8; randomized experiments and binomial proportions.

## Learning objectives

1. Analyze independent conversion rates with a two-proportion z-test
2. Report absolute risk difference, relative risk, odds ratio, and confidence intervals
3. Plan sample size using a minimum detectable effect
4. Recognize peeking, sample-ratio mismatch, and metric multiplicity

## Concept map

The lesson covers the following concepts explicitly.

| Concept | Meaning | Teaching section |
|---|---|---|
| Random assignment and intention-to-treat | Analyze units according to assigned treatment to preserve the experiment. | [9.1 A/B tests are experiments, not just z-tests](#91-ab-tests-are-experiments-not-just-z-tests) |
| Two-proportion z-test | Compare independent any-physician-visit rates in two RAND plan groups. | [9.1 A/B tests are experiments, not just z-tests](#91-ab-tests-are-experiments-not-just-z-tests) |
| Score confidence interval for risk difference | Estimate the individual-deductible-minus-other-plan absolute rate difference. | [9.1 A/B tests are experiments, not just z-tests](#91-ab-tests-are-experiments-not-just-z-tests) |
| Absolute lift, relative risk, odds ratio, and NNT-style metric | Express effect magnitude from complementary decision perspectives. | [9.1 A/B tests are experiments, not just z-tests](#91-ab-tests-are-experiments-not-just-z-tests) |
| Sample-ratio mismatch | Test observed assignment counts against the planned allocation. | [9.2 Design checks](#92-design-checks) |
| Proportion power and sample size | Plan from baseline rate and target rate through Cohen's h. | [9.2 Design checks](#92-design-checks) |
| Metric multiplicity, peeking, seasonality, and novelty | Design threats that a correct z-test does not repair. | [9.2 Design checks](#92-design-checks) |

## Data used in this lesson

The examples use the local, documented real-data bundle. See the [dataset guide](../../data/readme.md) for provenance,
variable definitions, cleaning decisions, and reuse notes.

| Dataset | Observation unit | Lesson use | Interpretation boundary |
|---|---|---|---|
| RAND Health Insurance Experiment teaching sample | one participant | Any physician visit is compared between individual-deductible and other-plan groups. | This balanced subset is for teaching; a full report requires the complete study design and sample. |

## Notebook setup

The examples use the shared scientific-Python setup described in the
[Notebook Implementation Toolkit](../../docs/maintenance/notebook_toolkit.md). That reference explains imports, deterministic random-number
generation, plotting configuration, output behavior, and why global warning suppression is discouraged.

## 9.1 A/B tests are experiments, not just z-tests

The RAND Health Insurance Experiment teaching sample compares individual-deductible plans with other plans. The binary
outcome is whether a participant recorded any physician visit. This real experiment illustrates the same proportion
workflow used in online A/B testing, while the interpretation remains specific to health-insurance plans.



```python
from statsmodels.stats.proportion import proportions_ztest, confint_proportions_2indep

rand = pd.read_csv(DATA_DIR / "rand_hie_teaching_sample.csv")
summary = rand.groupby("plan_group")["any_physician_visit"].agg(["sum", "count", "mean"])
control_name, treatment_name = "Other plan", "Individual deductible"
successes = np.array([summary.loc[control_name, "sum"], summary.loc[treatment_name, "sum"]], dtype=int)
visitors = np.array([summary.loc[control_name, "count"], summary.loc[treatment_name, "count"]], dtype=int)
z, p = proportions_ztest(successes, visitors)
rates = successes/visitors
ci_control_minus_treatment = confint_proportions_2indep(
    successes[0], visitors[0], successes[1], visitors[1], method="score")
diff = rates[1]-rates[0]
diff_ci = (-ci_control_minus_treatment[1], -ci_control_minus_treatment[0])
rr = rates[1]/rates[0]
odds_ratio = (rates[1]/(1-rates[1]))/(rates[0]/(1-rates[0]))
nnt_style = 1/abs(diff) if diff else np.inf
display(summary)
pd.Series({"other-plan rate": rates[0], "deductible-plan rate": rates[1],
           "absolute difference": diff, "difference CI low": diff_ci[0],
           "difference CI high": diff_ci[1], "z": z, "p": p,
           "relative risk": rr, "odds ratio": odds_ratio,
           "people per one-event difference": nnt_style})

```


| ('Unnamed: 0_level_0', 'plan_group') | ('sum', 'Unnamed: 1_level_1') | ('count', 'Unnamed: 2_level_1') | ('mean', 'Unnamed: 3_level_1') |
|---|---|---|---|
| Individual deductible | 258 | 400 | 0.645 |
| Other plan | 268 | 400 | 0.67 |





    other-plan rate                     0.6700
    deductible-plan rate                0.6450
    absolute difference                -0.0250
    difference CI low                  -0.0908
    difference CI high                  0.0408
    z                                   0.7450
    p                                   0.4563
    relative risk                       0.9627
    odds ratio                          0.8949
    people per one-event difference    40.0000
    dtype: float64



## 9.2 Design checks

Before trusting the effect:

1. Check assignment counts against the intended allocation (sample-ratio mismatch).
2. Verify one row per randomized unit and correct exposure timing.
3. Define one primary metric and a multiplicity strategy for secondary metrics.
4. Use the pre-specified duration/sample size; account for seasonality and novelty effects.
5. Report absolute lift because relative lift can exaggerate small baseline changes.



```python
allocation_check = stats.chisquare(visitors, f_exp=np.repeat(visitors.sum()/2, 2))

from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize
baseline = rates[0]
minimum_useful_change = .05
target = min(baseline+minimum_useful_change, .99)
h = abs(proportion_effectsize(target, baseline))
required = NormalIndPower().solve_power(h, alpha=.05, power=.80, ratio=1)
print(f"Teaching-sample allocation check p-value: {allocation_check.pvalue:.4f}")
print(f"Baseline any-visit rate: {baseline:.3f}")
print(f"For a +5 percentage-point change, required per group: {np.ceil(required):,.0f}")

```

    Teaching-sample allocation check p-value: 1.0000
    Baseline any-visit rate: 0.670
    For a +5 percentage-point change, required per group: 1,329


## Worked example and interpretation

### Estimate before testing

The RAND HIE teaching subset has 400 participants in each displayed plan group. At least one physician visit occurred for 268/400 (67.0%) in the other-plan group and 258/400 (64.5%) in the individual-deductible group. The estimated **deductible minus other-plan** risk difference is −2.5 percentage points. Its score-based 95% interval extends from −9.08 to +4.08 percentage points, while the two-proportion z-test gives p = 0.456. The relative risk is 0.963 and odds ratio 0.895, but the absolute difference and its interval are easier to connect to a decision. The interval includes both a practically meaningful reduction and a small increase, so the subset does not resolve a modest plan effect.

### Check the design claim

The displayed allocation counts are exactly 400 and 400, producing an allocation chi-square p-value of 1.0. That equality is a feature of this **balanced teaching subset**, not proof that the original randomization, exposure, or outcome logging worked perfectly. A separate design calculation uses the observed 67% baseline and a prechosen +5 percentage-point change, estimating about 1,329 participants per group for 80% power under its assumptions. The current subset is much smaller. A responsible A/B readout also checks eligibility, missingness, stopping rules, and whether the metric was specified before looking at results.

## Practice and solution

**Practice.** Treatment conversion is 5.5% versus 5.0% in control, with p=.04. What else is needed
before launch?

<details><summary>Solution</summary>

Report the 0.5 percentage-point absolute lift and its CI, relative effect, costs/benefits, guardrail
metrics, assignment and data-quality checks, stopping compliance, and whether multiple metrics or
segments were searched. A small p-value alone does not establish business value or validity.
</details>

## Summary

- The experimental protocol makes the causal claim credible; the z-test summarizes uncertainty.
- Absolute effects and intervals are central to decisions.
- Plan sample size from a minimum useful effect and resist unplanned peeking.


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
| `statsmodels.stats.proportion.proportions_ztest` | Test equality of independent proportions. | The order of counts determines the sign of z. |
| `confint_proportions_2indep(method='score')` | Build a score-based interval for a proportion difference. | Document the subtraction order; the notebook reverses the returned control-minus-treatment interval. |
| `scipy.stats.chisquare` | Check planned versus observed allocation counts. | A small p-value is a diagnostic trigger, not a diagnosis of the logging fault. |
| `proportion_effectsize` | Convert two rates to Cohen's h. | Use rates tied to a minimum useful effect. |
| `NormalIndPower.solve_power` | Calculate approximate per-group sample size. | Round up and account for attrition or clustering separately. |

## Best practices

- Pre-specify one primary metric and stopping rule.
- Report absolute lift and its interval before relative lift.
- Investigate data quality when sample-ratio mismatch appears.

## Common mistakes and edge cases

- Calling a z-test result causal without validating randomization and exposure.
- Repeatedly peeking until p<.05.
- Searching many segments and reporting only the smallest p-value.

## Additional practice

1. Write an A/B analysis plan with one primary and two guardrail metrics.
2. Calculate the absolute and relative lift from 5% to 6%.

## Related lessons and source material

- **Previous:** [Lesson 08 Categorical Data Chi-Square Fisher and McNemar](lesson_08_categorical_data_chi_square_fisher_and_mc_nemar.md)
- **Next:** [Lesson 10 Correlation and Regression-Based Tests](lesson_10_correlation_and_regression_based_tests.md)
- **Supporting notebook:** [lesson_09_proportions_and_a_and_b_tests.ipynb](../lesson_09_proportions_and_a_and_b_tests.ipynb)
- **Coverage record:** [Course Coverage Index](../../docs/maintenance/course_coverage_index.md#lesson-9-proportions-and-ab-tests)
