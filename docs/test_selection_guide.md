# Hypothesis Test Selection Guide

Use this as a starting point. The correct method is determined by the estimand, sampling/randomization unit,
dependence structure, and assumptions—not merely by the data type.

The authoritative lessons apply this guide to the included [real-data bundle](../data/readme.md): ANES for
cross-sectional examples, Grunfeld for paired and longitudinal data, RAND HIE for experimental comparisons,
Spector for small exact tests, and heart-transplant data for censored outcomes.

| Situation | Primary method | Important companion output |
|---|---|---|
| Mean vs benchmark | One-sample t | Mean difference, CI, Cohen's d |
| Proportion vs benchmark | Exact binomial or one-proportion z | Wilson/exact CI, Cohen's h |
| Two independent means | Welch t | Raw difference CI, Hedges' g |
| Two paired means | Paired t | Mean change CI, Cohen's dz |
| Two independent ordinal/rank outcomes | Mann–Whitney U | Medians/IQRs, rank-biserial effect |
| Two paired ordinal/rank outcomes | Wilcoxon signed-rank | Paired summaries, rank effect |
| 3+ independent means | ANOVA or Welch ANOVA | Omega-squared, adjusted post-hoc |
| 3+ independent rank outcomes | Kruskal–Wallis | Epsilon-squared, adjusted post-hoc |
| Factorial quantitative outcome | Factorial ANOVA/regression | Interaction estimates and plots |
| Two independent proportions | Two-proportion z / chi-square | Risk difference, RR/OR, CIs |
| Sparse independent 2x2 table | Fisher exact | Odds ratio and exact/compatible CI |
| Paired binary outcomes | McNemar | Discordant-pair counts and OR |
| Categorical goodness-of-fit | Chi-square GOF | Observed/expected counts, Cohen's w |
| Categorical association | Chi-square independence | Cramér's V, residuals, risks/odds |
| Linear continuous association | Pearson/regression | Scatterplot, r/slope CI, diagnostics |
| Monotonic/ordinal association | Spearman or Kendall | Scatter/rank plot, coefficient CI |
| Time-to-event by group | Log-rank | Kaplan–Meier curves; Cox model if adjusted |
| Clustered/repeated observations | Mixed model/GEE | Cluster-aware intervals and effects |

## Five checks before pressing “run”

1. What is the population parameter or causal estimand?
2. Which units are statistically independent?
3. Was sidedness, alpha, stopping, and multiplicity decided in advance?
4. Which assumptions are design facts, and which can be diagnosed from data?
5. What effect would be large enough to matter?

## Reporting sentence

> **[Group/condition]** differed from **[reference]** by **[effect in natural units]** (95% CI **[low, high]**;
> **[test statistic and df]**, **p=[value]**; **[effect size]**). **[Assumptions/adjustments]**. The result
> **[does/does not]** exceed the pre-specified practical threshold of **[threshold]**. Main limitations are **[items]**.
