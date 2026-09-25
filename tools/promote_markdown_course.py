#!/usr/bin/env python3
"""One-time migration: promote notebook exports into authoritative course lessons."""

from __future__ import annotations

import ast
import os
import re
from io import StringIO
from pathlib import Path

import nbformat
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


META = {
    1: {
        "definition": "Hypothesis testing is a structured way to compare observed evidence with a precisely defined reference model.",
        "why": "It turns a research claim into an auditable decision while keeping uncertainty, effect magnitude, and assumptions visible.",
        "prereq": "Descriptive statistics, samples and populations, means, standard deviations, and basic Python.",
        "concepts": [
            ("Research question, parameter, and estimand", "The quantity the analysis is intended to learn about.", "1.1 From a question to a testable claim", "Markdown"),
            ("Null and alternative hypotheses", "Reference and competing claims, including one- and two-sided alternatives.", "1.1 From a question to a testable claim", "Markdown"),
            ("p-value interpretation", "Compatibility with the null model rather than the probability that the null is true.", "1.2 What a p-value is—and is not", "Markdown and simulation"),
            ("Significance level and false-positive simulation", "Long-run rejection behavior under a true null.", "1.2 What a p-value is—and is not", "Code and histogram output"),
            ("Signal-to-noise test statistic", "Estimate minus null value divided by its standard error.", "1.3 Test statistics, confidence intervals, and effect sizes", "Markdown"),
            ("Confidence intervals and test decisions", "Connection between a two-sided test and a compatible interval.", "1.3 Test statistics, confidence intervals, and effect sizes", "Markdown and code"),
            ("One-sample Cohen's d", "Standardized distance between a sample mean and its null value.", "1.3 Test statistics, confidence intervals, and effect sizes", "Code and output"),
        ],
        "apis": [
            ("`scipy.stats.ttest_ind(..., equal_var=False)`", "Run Welch's two-sample t-test in the null simulation.", "`equal_var=False` avoids an equal-variance assumption."),
            ("`scipy.stats.ttest_1samp`", "Test a sample mean against a benchmark.", "Pair the p-value with a raw difference, interval, and effect size."),
            ("`scipy.stats.t.interval`", "Construct a t-based confidence interval.", "Supply degrees of freedom, location, and standard error explicitly."),
            ("`Axes.hist` and `Axes.axvline`", "Visualize the null distribution of simulated p-values.", "A histogram is a diagnostic illustration, not evidence from real data."),
        ],
        "best": ["Define the estimand and sidedness before examining results.", "Report estimates and intervals before binary decisions.", "Use simulation to build intuition, not to replace design reasoning."],
        "mistakes": ["Reading a p-value as the probability that the null is true.", "Treating failure to reject as proof of no effect.", "Calling a statistically detectable effect practically important without a decision threshold."],
        "practice": ["Write hypotheses for a two-sided comparison of a population mean with 100.", "Explain why p=.08 and a wide interval can still be compatible with an important effect."],
    },
    2: {
        "definition": "Power analysis studies how often a planned procedure detects a specified effect while controlling its false-positive rate.",
        "why": "It connects sample size and minimum useful effects to a defensible design before data collection.",
        "prereq": "Lesson 1, probability, sampling variability, and the meaning of alpha.",
        "concepts": [
            ("Type I and Type II errors", "False rejection versus failure to detect a specified alternative.", "2.1 Two kinds of decision error", "Markdown"),
            ("Statistical power", "Probability of rejection for a specified true effect.", "2.1 Two kinds of decision error", "Markdown and simulation"),
            ("Power drivers", "Effect size, sample size, variability, alpha, and test design.", "2.1 Two kinds of decision error", "Code and power curves"),
            ("Monte Carlo power simulation", "Repeatedly generate data, apply a test, and estimate the rejection rate.", "2.1 Two kinds of decision error", "Code"),
            ("A priori sample-size planning", "Solve for sample size from alpha, target power, and a minimum effect.", "2.2 Planning before data collection", "Markdown and code"),
            ("Optional stopping", "Repeated unplanned testing inflates false positives.", "2.2 Planning before data collection", "Markdown"),
            ("Sensitivity analysis", "Evaluate several plausible effects instead of treating one pilot estimate as known.", "2.2 Planning before data collection", "Practice solution"),
        ],
        "apis": [
            ("`statsmodels.stats.power.TTestIndPower`", "Plan or evaluate independent two-sample t-test power.", "The effect size is standardized Cohen's d."),
            ("`solve_power`", "Solve for the unknown sample-size component.", "Round required sample sizes upward."),
            ("`power`", "Calculate achieved power for a specified design.", "Prospective power is more useful than observed post-hoc power."),
            ("`DataFrame.pivot` and `groupby`", "Reshape and plot a simulation grid.", "These operations organize results; they do not change inferential assumptions."),
        ],
        "best": ["Choose a minimum effect from a real decision threshold.", "Simulate the complete planned procedure when analytic formulas do not match the design.", "Pre-specify stopping rules."],
        "mistakes": ["Using the effect observed in the same small study as if it were known.", "Calling 80% power a universal law.", "Ignoring attrition, clustering, or multiplicity in the design calculation."],
        "practice": ["Sketch how power changes if variance doubles while all other inputs remain fixed.", "Design a sensitivity table for three plausible effect sizes and two power targets."],
    },
    3: {
        "definition": "One-sample tests compare a population mean or proportion with a fixed benchmark.",
        "why": "They support quality-control, target, baseline, and prevalence questions without introducing a second sample.",
        "prereq": "Lessons 1–2, standard errors, t distributions, and binomial outcomes.",
        "concepts": [
            ("One-sample t-test", "Test a quantitative population mean against a benchmark.", "3.1 One-sample mean", "Markdown and code"),
            ("Independence and shape assumptions", "Design-based independence plus distribution diagnostics for small samples.", "3.1 One-sample mean", "Markdown and plots"),
            ("Mean-difference confidence interval", "Estimate uncertainty in natural units.", "3.1 One-sample mean", "Code and output"),
            ("One-sample Cohen's d", "Standardized benchmark difference.", "3.1 One-sample mean", "Code"),
            ("Box, strip, and Q-Q diagnostics", "Reveal spread, individual values, and departures from normality.", "3.1 One-sample mean", "Code and plots"),
            ("Exact binomial test", "Test a binary proportion without a large-sample approximation.", "3.2 One-sample proportion", "Markdown and code"),
            ("Wilson proportion interval", "A stable interval for a binomial proportion.", "3.2 One-sample proportion", "Code"),
            ("Cohen's h", "Arcsine-scale standardized difference between proportions.", "3.2 One-sample proportion", "Code"),
        ],
        "apis": [
            ("`scipy.stats.ttest_1samp`", "Return the t statistic and p-value for a mean benchmark.", "The null value is passed through `popmean`."),
            ("`scipy.stats.probplot`", "Create a normal Q-Q diagnostic.", "Interpret the shape visually rather than using a mechanical pass/fail rule."),
            ("`scipy.stats.binomtest`", "Run an exact binomial test.", "This is the current API; deprecated `binom_test` should not be used."),
            ("`BinomTestResult.proportion_ci(method='wilson')`", "Calculate the Wilson interval.", "State the chosen confidence level and method."),
            ("`seaborn.boxplot` and `stripplot`", "Combine a summary with raw observations.", "Raw points make small-sample structure visible."),
        ],
        "best": ["State whether the benchmark is scientific, operational, or arbitrary.", "Use an exact proportion test for small or extreme expected counts.", "Report the raw-unit difference even when a standardized effect is useful."],
        "mistakes": ["Diagnosing the raw sample instead of the relevant model quantity.", "Using a Wald proportion interval near zero or one.", "Choosing a one-sided test after observing the sample direction."],
        "practice": ["Analyze 7 defects in 80 parts against a 5% benchmark using an exact test.", "Explain what a confidence interval crossing the benchmark means."],
    },
    4: {
        "definition": "Independent-group methods compare outcomes from different observational units assigned to or sampled into two groups.",
        "why": "They are the standard tools for parallel experiments and independent observational comparisons.",
        "prereq": "Lessons 1–3, independent sampling, means, variances, and confidence intervals.",
        "concepts": [
            ("Independent design and estimand", "Identify the independent unit and the group contrast of interest.", "4.1 Design and estimand", "Markdown"),
            ("Welch's t-test", "Compare means without assuming equal variances.", "4.1 Design and estimand", "Code and output"),
            ("Welch–Satterthwaite degrees of freedom", "Approximate degrees of freedom under unequal standard errors.", "4.1 Design and estimand", "Code"),
            ("Mean-difference confidence interval", "Express uncertainty in the original outcome units.", "4.1 Design and estimand", "Code"),
            ("Cohen's d and Hedges' g", "Standardized effects with a small-sample correction.", "4.1 Design and estimand", "Code"),
            ("Distribution diagnostics", "Violin, strip, and Q-Q plots expose shape and influential values.", "4.1 Design and estimand", "Code and plots"),
            ("Mann–Whitney U", "Rank-based contrast for independent groups.", "4.1 Design and estimand", "Code and output"),
            ("Rank-biserial correlation", "Effect size derived from the U statistic with direction set by group order.", "4.1 Design and estimand", "Code"),
        ],
        "apis": [
            ("`scipy.stats.ttest_ind(..., equal_var=False)`", "Run Welch's test.", "Use `equal_var=True` only when pooled variance is substantively justified."),
            ("`scipy.stats.t.ppf`", "Obtain the critical value for a manually constructed interval.", "Pass the calculated Welch degrees of freedom."),
            ("`scipy.stats.mannwhitneyu`", "Run the independent rank test.", "Specify `alternative` and document group order."),
            ("`seaborn.violinplot` and `stripplot`", "Show shape and observations together.", "Avoid hiding small samples behind only a smooth density."),
        ],
        "best": ["Use Welch's test as the default mean comparison.", "Choose a rank test because its estimand fits—not merely because a normality p-value is small.", "Name the subtraction direction for every effect."],
        "mistakes": ["Treating repeated observations from one person as independent.", "Interpreting Mann–Whitney as a median test when group shapes differ.", "Reporting only a standardized effect when original units drive decisions."],
        "practice": ["Compare the estimands of Welch and Mann–Whitney for skewed groups.", "Explain how reversing treatment and control changes the sign of the reported effects."],
    },
    5: {
        "definition": "Paired methods preserve the link between repeated or matched observations and analyze within-pair information.",
        "why": "Correct pairing removes between-unit noise and prevents false precision from pretending repeated measurements are independent.",
        "prereq": "Lesson 4 plus differences, matched designs, and binary contingency tables.",
        "concepts": [
            ("Paired design and unit of analysis", "The pair or subject—not each row independently—is the inferential unit.", "5.1 Pairing changes the unit of analysis", "Markdown"),
            ("Paired t-test", "One-sample t-test applied to within-pair differences.", "5.1 Pairing changes the unit of analysis", "Markdown and code"),
            ("Change-score confidence interval", "Estimate mean after-minus-before change.", "5.1 Pairing changes the unit of analysis", "Code"),
            ("Cohen's dz", "Mean change standardized by the standard deviation of changes.", "5.1 Pairing changes the unit of analysis", "Code"),
            ("Paired trajectory and change plots", "Show individual movement and the difference distribution.", "5.1 Pairing changes the unit of analysis", "Code and plots"),
            ("Wilcoxon signed-rank", "Rank-based paired procedure with symmetry considerations.", "5.2 Rank-based and binary paired tests", "Markdown and code"),
            ("McNemar's exact test", "Test change in paired binary outcomes using discordant pairs.", "5.2 Rank-based and binary paired tests", "Markdown and code"),
            ("Discordant-pair odds ratio", "Compare No-to-Yes with Yes-to-No transitions.", "5.2 Rank-based and binary paired tests", "Code"),
        ],
        "apis": [
            ("`scipy.stats.ttest_rel`", "Run a paired t-test.", "Input arrays must be aligned in the same subject order."),
            ("`scipy.stats.wilcoxon`", "Run the signed-rank test.", "Zero differences and ties require attention."),
            ("`statsmodels.stats.contingency_tables.mcnemar`", "Run approximate or exact McNemar inference.", "Use exact inference when discordant counts are small."),
            ("`Axes.plot` over paired points", "Draw subject-level trajectories.", "This reveals heterogeneous responses hidden by mean summaries."),
        ],
        "best": ["Verify pair identifiers and ordering before analysis.", "Diagnose the distribution of differences for the paired t-test.", "Report discordant counts for McNemar, not only the p-value."],
        "mistakes": ["Applying an independent t-test to paired observations.", "Checking normality separately for before and after instead of changes.", "Using McNemar for independent 2x2 groups."],
        "practice": ["Construct the four-cell McNemar table from paired binary records.", "Explain when a mixed model is preferable to a paired test."],
    },
    6: {
        "definition": "Omnibus multi-group tests ask whether any population group differs before locating specific contrasts.",
        "why": "They avoid a collection of unadjusted pairwise tests and provide a principled path to post-hoc analysis.",
        "prereq": "Independent two-group inference, variance, regression basics, and multiplicity awareness.",
        "concepts": [
            ("One-way ANOVA", "Compare three or more independent means with an omnibus F test.", "6.1 The omnibus question", "Markdown and code"),
            ("OLS formula representation", "Fit ANOVA as `score ~ C(group)`.", "6.1 The omnibus question", "Code"),
            ("ANOVA table", "Partition sums of squares into group and residual components.", "6.1 The omnibus question", "Code and output"),
            ("Omega-squared", "Less biased omnibus effect-size estimate than eta-squared.", "6.1 The omnibus question", "Code"),
            ("Tukey HSD", "Multiplicity-controlled all-pairs comparisons after ANOVA.", "6.1 The omnibus question", "Code and output"),
            ("Welch ANOVA", "Omnibus mean comparison for unequal variances.", "6.2 Robust alternatives", "Markdown and code"),
            ("Kruskal–Wallis and epsilon-squared", "Rank-based omnibus test and effect size.", "6.2 Robust alternatives", "Code"),
            ("Pairwise Mann–Whitney with Holm", "Follow-up rank comparisons with family-wise error control.", "6.2 Robust alternatives", "Code"),
            ("Planned contrasts versus post-hoc tests", "Separate targeted hypotheses from exploratory all-pairs searches.", "Practice and solution", "Markdown"),
        ],
        "apis": [
            ("`statsmodels.formula.api.ols`", "Fit the linear model behind ANOVA.", "`C(group)` marks the predictor as categorical."),
            ("`statsmodels.stats.anova.anova_lm`", "Produce the ANOVA decomposition.", "Document the chosen sum-of-squares type."),
            ("`pairwise_tukeyhsd`", "Run Tukey's all-pairs procedure.", "Use after an appropriate omnibus/model analysis."),
            ("`statsmodels.stats.oneway.anova_oneway(use_var='unequal')`", "Run Welch ANOVA.", "Useful when variances differ."),
            ("`scipy.stats.kruskal`", "Run Kruskal–Wallis.", "A significant result is not automatically a pure median difference."),
            ("`multipletests(..., method='holm')`", "Adjust pairwise p-values.", "Holm controls family-wise error and dominates simple Bonferroni."),
            ("`itertools.combinations`", "Generate each unique group pair.", "Keep the hypothesis family explicit."),
        ],
        "best": ["Inspect distributions and residuals before interpreting the omnibus table.", "Report omega-squared and group summaries.", "Use post-hoc procedures that match the omnibus model."],
        "mistakes": ["Inferring a particular pair difference from only the omnibus p-value.", "Running every pair at alpha .05 without correction.", "Interpreting a rank test as if it necessarily compared means."],
        "practice": ["Choose between standard ANOVA, Welch ANOVA, and Kruskal–Wallis for three scenarios.", "Write a planned contrast that compares one treatment with the average of two controls."],
    },
    7: {
        "definition": "Factorial models estimate main effects and interactions; ANCOVA adds quantitative covariates to improve precision or adjust comparisons.",
        "why": "Many real questions involve effect modification or baseline differences that a one-factor test cannot represent.",
        "prereq": "Lesson 6, linear-model notation, categorical coding, and confidence intervals.",
        "concepts": [
            ("Factorial design", "Study two categorical factors in one model.", "7.1 Factorial designs", "Markdown and code"),
            ("Interaction", "The effect of one factor changes across levels of another.", "7.1 Factorial designs", "Markdown and output"),
            ("Formula interaction syntax", "`C(method) * C(experience)` expands main effects and their interaction.", "7.1 Factorial designs", "Code"),
            ("Type II ANOVA", "Test model terms after accounting for the other main effect.", "7.1 Factorial designs", "Code and output"),
            ("Interaction plot", "Display cell means and intervals to interpret effect modification.", "7.1 Factorial designs", "Code and plot"),
            ("ANCOVA", "Compare groups while adjusting for a pre-treatment continuous covariate.", "7.2 ANCOVA", "Markdown and code"),
            ("Homogeneity of regression slopes", "Check group-by-covariate interaction before using a common slope.", "7.2 ANCOVA", "Code and ANOVA output"),
            ("Adjusted coefficients", "Interpret group effects conditional on the modeled covariate.", "7.2 ANCOVA", "Code and output"),
            ("Post-treatment adjustment bias", "Do not condition on variables caused by treatment without a causal rationale.", "7.2 ANCOVA", "Markdown"),
        ],
        "apis": [
            ("`ols('score ~ C(a) * C(b)')`", "Fit factorial main effects plus interaction.", "The `*` operator expands to `a + b + a:b`."),
            ("`anova_lm(..., typ=2)`", "Test factorial model terms.", "Sum-of-squares choice matters in unbalanced designs."),
            ("`DataFrame.groupby(...).mean()`", "Calculate cell means for interpretation.", "Use uncertainty intervals, not means alone."),
            ("`seaborn.pointplot(errorbar=('ci', 95))`", "Visualize interaction patterns and uncertainty.", "Nonparallel lines suggest an interaction but inference comes from the model."),
            ("`ols('outcome ~ baseline * C(group)')`", "Check slope homogeneity.", "If the interaction matters, report group-specific slopes."),
        ],
        "best": ["Interpret meaningful interactions before averaged main effects.", "Use pre-treatment covariates selected from the design and subject matter.", "Report adjusted estimates with their reference coding."],
        "mistakes": ["Reading main effects as universal when an interaction is present.", "Adjusting for a mediator caused by treatment.", "Ignoring sum-of-squares choices in unbalanced data."],
        "practice": ["Translate `A * B` into the model terms it creates.", "Explain how a baseline-by-treatment interaction changes an ANCOVA interpretation."],
    },
    8: {
        "definition": "Categorical-data tests compare observed cell counts with counts expected under a probability model.",
        "why": "They support association, goodness-of-fit, and sparse-table questions while retaining the count structure.",
        "prereq": "Probability, proportions, contingency tables, and independent versus paired designs.",
        "concepts": [
            ("Contingency tables", "Cross-classify counts for two categorical variables.", "8.1 Independence in a contingency table", "Markdown and code"),
            ("Expected counts under independence", "Row total times column total divided by the grand total.", "8.1 Independence in a contingency table", "Markdown and output"),
            ("Pearson chi-square independence test", "Aggregate observed-minus-expected discrepancies.", "8.1 Independence in a contingency table", "Code and output"),
            ("Degrees of freedom", "Determine the chi-square reference distribution from table dimensions.", "8.1 Independence in a contingency table", "Output"),
            ("Cramér's V", "Standardized association magnitude for contingency tables.", "8.1 Independence in a contingency table", "Code"),
            ("Pearson residuals", "Identify cells that contribute strongly to the omnibus association.", "8.1 Independence in a contingency table", "Code, table, and heatmap"),
            ("Fisher's exact test", "Exact conditional inference for sparse 2x2 tables.", "8.2 Sparse 2x2 tables and effect measures", "Markdown and code"),
            ("Odds ratio and confidence interval", "Quantify the direction and uncertainty of a 2x2 association.", "8.2 Sparse 2x2 tables and effect measures", "Code and output"),
            ("Goodness-of-fit versus independence versus McNemar", "Choose from one distribution, independent variables, or paired binary outcomes.", "Practice and solution", "Markdown"),
        ],
        "apis": [
            ("`scipy.stats.chi2_contingency`", "Return chi-square, p-value, degrees of freedom, and expected counts.", "Set continuity correction deliberately for 2x2 tables."),
            ("`seaborn.heatmap`", "Visualize signed cell residuals.", "Use a diverging palette centered at zero."),
            ("`scipy.stats.fisher_exact`", "Return a sample odds ratio and exact p-value for 2x2 data.", "The result depends on row/column orientation."),
            ("`statsmodels.stats.contingency_tables.Table2x2`", "Calculate odds-ratio confidence intervals and related measures.", "Report the table orientation."),
        ],
        "best": ["Display counts and percentages before the test.", "Inspect expected counts and residuals.", "Report an interpretable effect such as risk difference, relative risk, or odds ratio when design permits."],
        "mistakes": ["Using observed rather than expected counts to assess the approximation.", "Applying chi-square independence to paired observations.", "Reading an odds ratio without stating which outcome and group are in the numerator."],
        "practice": ["Compute expected counts for a 2x3 table by hand.", "Explain why a significant chi-square test does not identify a causal mechanism."],
    },
    9: {
        "definition": "An A/B test is a randomized comparison whose binary outcome is often analyzed through independent proportions.",
        "why": "The design can support causal decisions only when assignment, exposure, metrics, and stopping are handled correctly.",
        "prereq": "Lessons 2, 3, and 8; randomized experiments and binomial proportions.",
        "concepts": [
            ("Random assignment and intention-to-treat", "Analyze units according to assigned treatment to preserve the experiment.", "9.1 A/B tests are experiments, not just z-tests", "Markdown"),
            ("Two-proportion z-test", "Compare independent conversion rates.", "9.1 A/B tests are experiments, not just z-tests", "Code and output"),
            ("Score confidence interval for risk difference", "Estimate treatment-minus-control absolute lift.", "9.1 A/B tests are experiments, not just z-tests", "Code"),
            ("Absolute lift, relative risk, odds ratio, and NNT-style metric", "Express effect magnitude from complementary decision perspectives.", "9.1 A/B tests are experiments, not just z-tests", "Code and output"),
            ("Sample-ratio mismatch", "Test observed assignment counts against the planned allocation.", "9.2 Design checks", "Markdown and code"),
            ("Proportion power and sample size", "Plan from baseline rate and target rate through Cohen's h.", "9.2 Design checks", "Code"),
            ("Metric multiplicity, peeking, seasonality, and novelty", "Design threats that a correct z-test does not repair.", "9.2 Design checks", "Markdown"),
        ],
        "apis": [
            ("`statsmodels.stats.proportion.proportions_ztest`", "Test equality of independent proportions.", "The order of counts determines the sign of z."),
            ("`confint_proportions_2indep(method='score')`", "Build a score-based interval for a proportion difference.", "Document the subtraction order; the notebook reverses the returned control-minus-treatment interval."),
            ("`scipy.stats.chisquare`", "Check planned versus observed allocation counts.", "A small p-value is a diagnostic trigger, not a diagnosis of the logging fault."),
            ("`proportion_effectsize`", "Convert two rates to Cohen's h.", "Use rates tied to a minimum useful effect."),
            ("`NormalIndPower.solve_power`", "Calculate approximate per-group sample size.", "Round up and account for attrition or clustering separately."),
        ],
        "best": ["Pre-specify one primary metric and stopping rule.", "Report absolute lift and its interval before relative lift.", "Investigate data quality when sample-ratio mismatch appears."],
        "mistakes": ["Calling a z-test result causal without validating randomization and exposure.", "Repeatedly peeking until p<.05.", "Searching many segments and reporting only the smallest p-value."],
        "practice": ["Write an A/B analysis plan with one primary and two guardrail metrics.", "Calculate the absolute and relative lift from 5% to 6%."],
    },
    10: {
        "definition": "Correlation and regression quantify association between variables; regression additionally represents conditional mean structure.",
        "why": "They turn vague statements about relationships into estimable coefficients with diagnostics and uncertainty.",
        "prereq": "Scatterplots, continuous variables, linear functions, and lessons on confidence intervals.",
        "concepts": [
            ("Pearson correlation", "Linear association between two quantitative variables.", "10.1 Correlation is a model of association", "Markdown and code"),
            ("Spearman rho", "Monotonic association based on ranks.", "10.1 Correlation is a model of association", "Markdown and code"),
            ("Kendall tau", "Concordance-based association useful with small samples or ties.", "10.1 Correlation is a model of association", "Markdown and code"),
            ("Fisher z confidence interval", "Approximate interval for Pearson's correlation.", "10.1 Correlation is a model of association", "Code"),
            ("Outlier sensitivity and relationship form", "One influential point or nonlinearity can distort a coefficient.", "10.1 Correlation is a model of association", "Simulation and plot"),
            ("Simple OLS regression", "Estimate an intercept and slope for a linear mean model.", "10.2 Regression tests", "Markdown and code"),
            ("Correlation-slope equivalence", "In simple regression, testing zero slope matches testing zero Pearson correlation.", "10.2 Regression tests", "Markdown"),
            ("Residual diagnostics", "Residual-versus-fitted and Q-Q plots assess model patterns.", "10.2 Regression tests", "Code and plots"),
            ("Association versus causation", "Coefficients do not remove confounding by themselves.", "Practice and solution", "Markdown"),
        ],
        "apis": [
            ("`scipy.stats.pearsonr`, `spearmanr`, `kendalltau`", "Compute three association measures and p-values.", "Choose from relationship form and measurement scale."),
            ("`numpy.arctanh` and `numpy.tanh`", "Move between r and Fisher's z scale.", "The approximation assumes independent pairs and a suitable bivariate model."),
            ("`seaborn.regplot`", "Plot observations, fitted line, and interval.", "Inspect raw points; the line alone can conceal problems."),
            ("`statsmodels.api.add_constant`", "Add an intercept column to a design matrix.", "Statsmodels matrix API does not add it automatically."),
            ("`statsmodels.api.OLS(...).fit()`", "Fit ordinary least squares.", "Inference depends on the error and dependence assumptions."),
            ("`RegressionResults.summary2`", "Display coefficient estimates and inferential output.", "Extract and report only the quantities relevant to the question."),
        ],
        "best": ["Plot before calculating correlation.", "Report coefficient, interval, sample size, and relationship form.", "Use cluster- or time-aware models when pairs are not independent."],
        "mistakes": ["Equating correlation with causation.", "Ignoring influential points or range restriction.", "Using Pearson r for a strong nonlinear relationship."],
        "practice": ["Describe a dataset where Spearman is large but Pearson is modest.", "Explain what a slope confidence interval adds beyond a p-value."],
    },
    11: {
        "definition": "Rank, permutation, and bootstrap methods use ordering or resampling to answer questions that standard formulas may not address well.",
        "why": "They broaden inference while keeping the target statistic and independent sampling unit explicit.",
        "prereq": "Two-group tests, sampling distributions, randomization, and basic programming loops.",
        "concepts": [
            ("Rank tests", "Use relative order rather than raw distances.", "11.1 Three families, three ideas", "Markdown"),
            ("Permutation test", "Generate a null distribution by justified label rearrangement.", "11.1 Three families, three ideas", "Markdown and code"),
            ("Custom mean-difference statistic", "Define the exact estimand passed to the permutation engine.", "11.1 Three families, three ideas", "Code"),
            ("Mann–Whitney comparison", "Contrast the permutation mean test with a rank-based procedure.", "11.1 Three families, three ideas", "Code and output"),
            ("Bootstrap sampling distribution", "Resample within independent groups to estimate uncertainty.", "11.1 Three families, three ideas", "Code and histogram"),
            ("Percentile bootstrap interval", "Use empirical bootstrap quantiles as interval endpoints.", "11.1 Three families, three ideas", "Code"),
            ("Exchangeability", "Justifies which labels may be permuted under the null.", "11.2 Exchangeability is the key permutation assumption", "Markdown"),
            ("Cluster-aware resampling", "Resample patients or clusters rather than dependent rows.", "Practice and solution", "Markdown"),
        ],
        "apis": [
            ("`scipy.stats.permutation_test`", "Run a resampling test around a custom statistic.", "Match `permutation_type` to independent, paired, or sample structure."),
            ("`numpy.random.Generator.choice(..., replace=True)`", "Draw bootstrap samples.", "Resample the independent unit within the correct strata."),
            ("`numpy.quantile`", "Read percentile interval endpoints from bootstrap replicates.", "Percentile intervals are simple but not universally optimal."),
            ("`numpy.empty`", "Preallocate a simulation array.", "Preallocation avoids repeated array growth in loops."),
            ("`numpy.random.Generator.lognormal`", "Create reproducible skewed teaching data.", "Simulated data illustrate behavior; they are not empirical evidence."),
        ],
        "best": ["Define the statistic before choosing the resampling method.", "Resample the independent unit.", "Set and report the random seed and number of resamples."],
        "mistakes": ["Assuming nonparametric means assumption-free.", "Permuting labels that are not exchangeable.", "Bootstrapping rows independently in clustered data."],
        "practice": ["Design a paired permutation test using within-pair sign flips.", "Explain when a percentile bootstrap interval may be unreliable."],
    },
    12: {
        "definition": "Multiplicity procedures control error across a family of hypotheses, while equivalence tests evaluate whether effects are small enough to be practically negligible.",
        "why": "Both prevent common binary-significance errors: selective discoveries and declaring equivalence from non-significance.",
        "prereq": "Type I error, confidence intervals, t distributions, and families of related tests.",
        "concepts": [
            ("Family-wise error rate", "Probability of at least one false rejection in a family.", "12.1 Multiple comparisons", "Markdown, formula, and plot"),
            ("Bonferroni correction", "Conservative family-wise control by scaling thresholds or p-values.", "12.1 Multiple comparisons", "Code and output"),
            ("Holm correction", "Sequential family-wise procedure that improves on simple Bonferroni.", "12.1 Multiple comparisons", "Code and output"),
            ("Benjamini–Hochberg FDR", "Control the expected false discovery proportion under its conditions.", "12.1 Multiple comparisons", "Code and output"),
            ("Hypothesis family", "Define which tests belong to one error-control decision.", "12.1 Multiple comparisons", "Markdown"),
            ("Equivalence bounds", "Pre-specified smallest effects considered meaningfully different.", "12.2 Equivalence is not non-significance", "Markdown"),
            ("Two one-sided tests (TOST)", "Reject effects at or beyond both equivalence margins.", "12.2 Equivalence is not non-significance", "Markdown and code"),
            ("90% interval for equivalence at alpha .05", "Interval must lie entirely within the equivalence bounds.", "12.2 Equivalence is not non-significance", "Code and output"),
        ],
        "apis": [
            ("`statsmodels.stats.multitest.multipletests`", "Apply Bonferroni, Holm, or BH adjustments.", "Report the method, hypothesis family, and adjusted p-values."),
            ("`scipy.stats.t.sf` and `t.cdf`", "Calculate the two one-sided TOST p-values.", "The TOST p-value is the larger of the two component p-values."),
            ("`scipy.stats.t.ppf`", "Construct the 90% t interval used by alpha-.05 TOST.", "Equivalence bounds must be chosen before looking at the estimate."),
        ],
        "best": ["Define the family and error criterion before analysis.", "Label exploratory tests and validate them independently.", "Choose equivalence bounds from practical consequences."],
        "mistakes": ["Correcting an arbitrary set of unrelated tests.", "Treating adjusted p-values as effect sizes.", "Concluding equivalence because a difference test is non-significant."],
        "practice": ["Compare Holm and BH for a confirmatory versus exploratory study.", "Draw a 90% interval that supports equivalence and one that is inconclusive."],
    },
    13: {
        "definition": "Advanced designs model dependence between observations and partial observation of event times.",
        "why": "Ignoring clusters or censoring typically produces incorrect uncertainty and can change the question being answered.",
        "prereq": "Regression, interactions, repeated measurements, probability, and time-to-event terminology.",
        "concepts": [
            ("Clustering and pseudo-replication", "Rows within a person or site are correlated and are not independent replicates.", "13.1 Clustered and longitudinal data", "Markdown"),
            ("Random-intercept mixed model", "Represent cluster-specific baselines through a random effect.", "13.1 Clustered and longitudinal data", "Code and output"),
            ("Time-by-treatment interaction", "Compare longitudinal trajectories rather than only average levels.", "13.1 Clustered and longitudinal data", "Code"),
            ("Mixed models versus GEE or cluster-level analysis", "Different approaches target different inferential perspectives.", "13.1 Clustered and longitudinal data", "Markdown"),
            ("Censoring", "Event time is only known to exceed the last observed time.", "13.2 Time-to-event data and censoring", "Markdown and simulation"),
            ("Risk sets and log-rank test", "Compare observed and expected events at each event time.", "13.2 Time-to-event data and censoring", "Custom code"),
            ("Kaplan–Meier estimator", "Multiply conditional survival probabilities across event times.", "13.2 Time-to-event data and censoring", "Custom code and plot"),
            ("Cluster-randomized inference", "Power and analysis follow the randomized cluster, not the row count.", "Practice and solution", "Markdown"),
        ],
        "apis": [
            ("`statsmodels.formula.api.mixedlm`", "Fit a mixed model with patient-level grouping.", "The example fits a random intercept; more complex covariance structures require care."),
            ("`numpy.minimum`", "Combine event and censoring times into observed follow-up.", "The event indicator records which process occurred first."),
            ("`scipy.stats.chi2.sf`", "Convert the log-rank chi-square statistic to a p-value.", "The hand-built implementation is educational, not production-grade."),
            ("`Axes.step(..., where='post')`", "Draw a Kaplan–Meier-style step function.", "A validated survival implementation should handle ties and confidence bands in applied work."),
            ("`numpy.random.Generator.exponential`", "Simulate event times with constant hazards.", "Real survival distributions need not be exponential."),
        ],
        "best": ["Identify the independent sampling or randomization unit first.", "Use validated mixed-model and survival routines for applied analyses.", "Report censoring patterns and model assumptions."],
        "mistakes": ["Using the number of rows as the independent sample size.", "Dropping censored cases or treating censoring times as events.", "Using the teaching log-rank implementation as a production library."],
        "practice": ["Explain how intraclass correlation changes effective sample size.", "Construct a risk set at one event time and calculate its expected group event count."],
    },
    14: {
        "definition": "An end-to-end analysis aligns the decision, estimand, design, diagnostics, inference, and reporting in one reproducible workflow.",
        "why": "Correct individual tests can still produce a misleading project when the wrong unit, metric, contrast, or reporting frame is used.",
        "prereq": "Lessons 1–13, especially Welch tests, proportion tests, bootstrap intervals, and multiplicity.",
        "concepts": [
            ("Seven-step test-selection sequence", "Move from decision and estimand through design, diagnostics, inference, and communication.", "14.1 Decision sequence", "Markdown"),
            ("Randomized checkout capstone", "Analyze time among converters and conversion among randomized users.", "14.2 Capstone scenario", "Markdown and code"),
            ("Conditional versus assignment-based estimands", "Checkout time conditions on conversion; conversion follows randomized assignment.", "14.2 Capstone scenario", "Markdown and output"),
            ("Skewed outcome simulation", "Use lognormal checkout times and binomial conversions.", "14.2 Capstone scenario", "Code"),
            ("Welch test plus bootstrap interval", "Combine parametric testing with a resampled mean-difference interval.", "14.2 Capstone scenario", "Code"),
            ("Two-proportion test", "Analyze the secondary conversion outcome.", "14.2 Capstone scenario", "Code"),
            ("Holm adjustment across outcomes", "Control family-wise error for the two planned claims.", "14.2 Capstone scenario", "Code and output"),
            ("Comparative visualization", "Show outcome distributions and conversion rates.", "14.2 Capstone scenario", "Code and plots"),
            ("Results-paragraph template", "Report estimate, interval, statistic, adjustment, estimand, and decision threshold.", "14.3 Reporting template", "Markdown"),
        ],
        "apis": [
            ("`Generator.binomial` and `Generator.lognormal`", "Create reproducible binary and skewed outcomes.", "The examples are simulated and should be labeled as such."),
            ("`scipy.stats.ttest_ind(..., equal_var=False)`", "Test the checkout-time mean contrast.", "Conditioning on converters can create post-treatment selection."),
            ("Bootstrap loop with `Generator.choice`", "Estimate a percentile interval for the mean difference.", "Resample independently within randomized groups."),
            ("`proportions_ztest`", "Test the randomized-user conversion contrast.", "Use all randomized users for the intention-to-treat estimand."),
            ("`multipletests(..., method='holm')`", "Adjust two outcome p-values.", "Adjustment does not repair metric switching or unplanned analyses."),
        ],
        "best": ["Write the estimand before selecting the test.", "Keep primary, secondary, and exploratory claims distinct.", "End with a decision and limitations, not a p-value."],
        "mistakes": ["Combining conditional and assignment-based estimands as if they answer the same question.", "Ignoring post-treatment selection among converters.", "Treating a reproducible simulation as evidence about a real product."],
        "practice": ["Rewrite the capstone with revenue as the primary outcome and identify the new estimand.", "Audit the analysis for logging, interference, stopping, and missingness risks."],
    },
    15: {
        "definition": "Statistical reporting is the disciplined synthesis of question, design, method, evidence, uncertainty, practical meaning, and limitations.",
        "why": "A correct calculation is not useful until a reader can understand what was estimated, under which assumptions, and what action follows.",
        "prereq": "All earlier lessons or equivalent applied hypothesis-testing experience.",
        "concepts": [
            ("Test-selection map", "Match outcome type, group count, pairing, sparsity, clustering, and censoring to a method family.", "15.1 Quick selection map", "Markdown"),
            ("Minimum reporting standard", "Nine elements required for a transparent result.", "15.2 Minimum reporting standard", "Markdown"),
            ("Teaching decision helper", "Encode a simplified outcome/design branching rule.", "15.1 Quick selection map", "Code and output"),
            ("Common interpretation failures", "Avoid p-value, non-significance, multiplicity, dependence, and causality errors.", "15.3 Common mistakes to avoid", "Markdown"),
            ("Knowledge-check workflow", "Use short questions to verify transferable understanding.", "Final knowledge check", "Markdown"),
            ("Advanced learning path", "Generalized linear, hierarchical, causal, sequential, missing-data, robust, and Bayesian methods.", "Where to go next", "Markdown"),
        ],
        "apis": [
            ("`recommend_test` helper", "Demonstrate a readable rule-based teaching aid.", "It is not a validated automated method selector."),
            ("`pandas.DataFrame` from records", "Present scenario-to-method mappings in a scannable table.", "The table documents rules but does not encode all design nuance."),
        ],
        "best": ["Use the selection map as a starting point, then inspect the design and estimand.", "Report uncertainty and practical thresholds.", "Make deviations and limitations easy to find."],
        "mistakes": ["Automating test choice from column data types alone.", "Reporting a p-value without an estimate and interval.", "Hiding exploratory decisions behind confirmatory language."],
        "practice": ["Draft a complete results paragraph from any earlier worked example.", "Find one case where the same outcome type requires different methods because dependence changes."],
    },
}

# The course originally used generated teaching samples. These metadata entries
# reflect the later migration to the local real-data bundle.
META[1]["concepts"][3] = (
    "Significance level and permutation-null false positives",
    "Long-run rejection behavior after breaking the observed age–vote relationship.",
    "1.2 What a p-value is—and is not",
    "Code and histogram output",
)
META[1]["apis"][0] = (
    "`scipy.stats.ttest_ind(..., equal_var=False)`",
    "Test age differences after each permutation of the observed vote labels.",
    "The permutation step creates the reference distribution; Welch's statistic measures each shuffled contrast.",
)
META[1]["apis"][3] = (
    "`numpy.random.Generator.permutation`",
    "Break the age–vote relationship while retaining the observed values.",
    "Permute labels only when exchangeability is justified by the null model or design.",
)
META[2]["concepts"][3] = (
    "Empirical power simulation",
    "Resample observed ages, add a planned shift, apply the test, and estimate the rejection rate.",
    "2.1 Two kinds of decision error",
    "Code",
)
META[5]["apis"].extend([
    ("`DataFrame.pivot`", "Align each firm's 1935 and 1954 observations.", "Verify one value per firm-year before pivoting."),
    ("`numpy.log1p`", "Reduce investment skew while retaining zeros.", "Interpret the resulting contrast on the log scale."),
    ("`pandas.crosstab`", "Create the paired binary transition table.", "Retain the same firm ordering in both periods."),
])
META[7]["concepts"][2] = (
    "Formula interaction syntax",
    "`C(party_group) * C(age_group)` expands main effects and their interaction.",
    "7.1 Factorial designs",
    "Code",
)
META[7]["apis"][0] = (
    "`ols('income_code ~ C(party_group) * C(age_group)')`",
    "Fit the observational factorial ANES model.",
    "The `*` operator expands to both main effects and their interaction.",
)
META[7]["apis"][4] = (
    "`ols('tv_news_days_per_week ~ age_years * C(expected_vote)')`",
    "Check slope homogeneity before the simpler adjusted model.",
    "Because the data are observational, coefficients describe adjusted associations rather than treatment effects.",
)
META[9]["concepts"][1] = (
    "Two-proportion z-test",
    "Compare independent any-physician-visit rates in two RAND plan groups.",
    "9.1 A/B tests are experiments, not just z-tests",
    "Code and output",
)
META[9]["concepts"][2] = (
    "Score confidence interval for risk difference",
    "Estimate the individual-deductible-minus-other-plan absolute rate difference.",
    "9.1 A/B tests are experiments, not just z-tests",
    "Code",
)
META[10]["concepts"][4] = (
    "Outlier sensitivity and relationship form",
    "Raw-data plots reveal influential points, ties, discreteness, and nonlinearity.",
    "10.1 Correlation is a model of association",
    "Discussion and raw-data plot",
)
META[11]["apis"] = [item for item in META[11]["apis"] if "lognormal" not in item[0]]
META[11]["apis"].insert(0, (
    "`pandas.read_csv`",
    "Load the cleaned ANES observations used in the resampling examples.",
    "Resample the independent observational unit, not arbitrary dependent rows.",
))
META[13]["concepts"] = [
    ("Clustering and pseudo-replication", "Repeated rows within a firm are correlated and are not independent replicates.", "13.1 Clustered and longitudinal data", "Markdown"),
    ("Random-intercept mixed model", "Represent firm-specific investment baselines through a random effect.", "13.1 Clustered and longitudinal data", "Code and output"),
    ("Time-by-firm-size interaction", "Compare longitudinal investment trajectories across data-derived firm-size groups.", "13.1 Clustered and longitudinal data", "Code"),
    ("Mixed models versus GEE or cluster-level analysis", "Different approaches target different inferential perspectives.", "13.1 Clustered and longitudinal data", "Markdown"),
    ("Censoring", "Observed survival is a lower bound when the event was not recorded during follow-up.", "13.2 Time-to-event data and censoring", "Markdown and real data"),
    ("Risk sets and log-rank test", "Compare observed and expected deaths across age groups at each event time.", "13.2 Time-to-event data and censoring", "Custom code"),
    ("Kaplan–Meier estimator", "Multiply conditional survival probabilities across observed event times.", "13.2 Time-to-event data and censoring", "Custom code and plot"),
    ("Cluster-randomized inference", "Power and analysis follow the randomized cluster, not the row count.", "Practice and solution", "Markdown"),
]
META[13]["apis"] = [
    ("`statsmodels.formula.api.mixedlm`", "Fit a random-intercept model grouped by firm.", "Name the grouping unit and interpret the time interaction on the log-investment scale."),
    ("`DataFrame.groupby(...).transform`", "Create a data-derived firm-size indicator without losing rows.", "The grouping is descriptive and was not randomized."),
    ("`scipy.stats.chi2.sf`", "Convert the educational log-rank statistic to a p-value.", "Use a validated survival library for production analyses."),
    ("`Axes.step(..., where='post')`", "Draw Kaplan–Meier-style survival curves.", "Production plots should also show censoring marks and confidence bands."),
]
META[14]["concepts"] = [
    ("Seven-step test-selection sequence", "Move from decision and estimand through design, diagnostics, inference, and communication.", "14.1 Decision sequence", "Markdown"),
    ("RAND HIE capstone", "Compare physician-use outcomes between two insurance-plan groups in the balanced teaching subset.", "14.2 Capstone scenario", "Markdown and code"),
    ("Primary and secondary estimands", "Distinguish the mean visit-count difference from the any-visit risk difference.", "14.2 Capstone scenario", "Markdown and output"),
    ("Welch test plus bootstrap interval", "Combine a mean comparison with a resampled interval for the visit-count difference.", "14.2 Capstone scenario", "Code"),
    ("Two-proportion test", "Analyze the secondary any-physician-visit outcome.", "14.2 Capstone scenario", "Code"),
    ("Holm adjustment across outcomes", "Control family-wise error for the two planned claims.", "14.2 Capstone scenario", "Code and output"),
    ("Comparative visualization", "Show visit-count distributions and any-visit rates.", "14.2 Capstone scenario", "Code and plots"),
    ("Results-paragraph template", "Report estimates, intervals, statistics, adjustment, provenance, and limitations.", "14.3 Reporting template", "Markdown"),
]
META[14]["apis"] = [
    ("`pandas.read_csv`", "Load the local RAND HIE teaching sample.", "Keep provenance and the teaching-subset limitation visible."),
    ("`scipy.stats.ttest_ind(..., equal_var=False)`", "Test the mean physician-visit contrast.", "Count outcomes may need a dedicated count model in applied work."),
    ("Bootstrap loop with `Generator.choice`", "Estimate a percentile interval for the mean visit difference.", "Resample participants within plan groups."),
    ("`proportions_ztest`", "Test the any-physician-visit rate contrast.", "Report the absolute rate difference as well as the p-value."),
    ("`multipletests(..., method='holm')`", "Adjust the two outcome p-values.", "Define the hypothesis family before seeing results."),
]
META[15]["apis"].insert(0, (
    "`pandas.read_csv`",
    "Load each real dataset represented in the final selection exercise.",
    "Dataset structure informs the method; filenames alone do not.",
))


def md_anchor(text: str) -> str:
    text = text.lower().replace("–", "-").replace("—", "-").replace("&", "and")
    text = re.sub(r"[`'’]", "", text)
    text = re.sub(r"[^a-z0-9 -]", "", text)
    return re.sub(r"-+", "-", re.sub(r"\s+", "-", text)).strip("-")


def lesson_number(path: Path) -> int:
    return int(re.search(r"lesson_(\d+)_", path.name).group(1))


def lesson_heading(path: Path) -> str:
    """Return the human-readable notebook title used by coverage anchors."""
    nb = nbformat.read(path, as_version=4)
    first_line = nb.cells[0].source.splitlines()[0].removeprefix("# ").strip()
    return first_line


def notebook_inventory(path: Path):
    nb = nbformat.read(path, as_version=4)
    imports, output_types = [], []
    for cell in nb.cells:
        if cell.cell_type == "code":
            output_types.extend(output.output_type for output in cell.get("outputs", []))
            try:
                tree = ast.parse(cell.source)
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    imports.append(ast.unparse(node))
    return {
        "cells": len(nb.cells),
        "markdown": sum(c.cell_type == "markdown" for c in nb.cells),
        "code": sum(c.cell_type == "code" for c in nb.cells),
        "executed": sum(c.cell_type == "code" and c.execution_count is not None for c in nb.cells),
        "outputs": len(output_types),
        "output_types": ", ".join(sorted(set(output_types))) or "none",
        "imports": list(dict.fromkeys(imports)),
    }


def markdown_table(rows, headers):
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(str(value).replace("|", "\\|").replace("\n", " ") for value in row) + " |")
    return "\n".join(lines)


def extract_export_body(text: str):
    objectives_at = text.find("## Learning objectives")
    setup_at = text.find("## Setup", objectives_at)
    if objectives_at < 0 or setup_at < 0:
        raise ValueError("Expected Learning objectives and Setup headings")
    objectives = text[objectives_at:setup_at].strip()
    next_heading = re.search(r"^## (?!Setup).+", text[setup_at + len("## Setup"):], flags=re.M)
    if not next_heading:
        raise ValueError("Expected a lesson section after Setup")
    core_start = setup_at + len("## Setup") + next_heading.start()
    core = text[core_start:].strip()
    core = core.replace("## Key takeaways", "## Summary")
    return objectives, core


def related_links(number: int, md_path: Path):
    links = []
    for other in [number - 1, number + 1]:
        if other not in META:
            continue
        other_nb = next(ROOT.glob(f"level_*/*lesson_{other:02d}_*.ipynb"))
        other_md = other_nb.parent / "markdown" / f"{other_nb.stem}.md"
        label = "Previous" if other < number else "Next"
        links.append(f"- **{label}:** [{other_nb.stem.replace('_', ' ')}]({os.path.relpath(other_md, md_path.parent)})")
    return "\n".join(links)


def promote_lesson(notebook: Path):
    number = lesson_number(notebook)
    meta = META[number]
    md_path = notebook.parent / "markdown" / f"{notebook.stem}.md"
    original = md_path.read_text(encoding="utf-8")
    if "> **Authoritative lesson:**" in original:
        raise RuntimeError(f"Refusing to promote {md_path.name} twice")
    title = original.splitlines()[0].removeprefix("# ").strip()
    objectives, core = extract_export_body(original)

    concept_rows = [(name, definition, f"[{section}](#{md_anchor(section)})") for name, definition, section, _ in meta["concepts"]]
    api_rows = meta["apis"]
    source_rel = os.path.relpath(notebook, md_path.parent)
    toolkit_rel = os.path.relpath(ROOT / "docs" / "maintenance" / "notebook_toolkit.md", md_path.parent)
    coverage_rel = os.path.relpath(ROOT / "docs" / "maintenance" / "course_coverage_index.md", md_path.parent)
    coverage_heading = lesson_heading(notebook)

    content = f"""# {title}

> **Authoritative lesson:** This Markdown file is the maintained teaching source. The notebook is a supporting,
> executable example and should not be used to overwrite this lesson.

## Lesson overview

{meta['definition']}

### Why this matters

{meta['why']}

### Prerequisites

{meta['prereq']}

{objectives}

## Concept map

The lesson covers the following concepts explicitly.

{markdown_table(concept_rows, ['Concept', 'Meaning', 'Teaching section'])}

## Notebook setup

The examples use the shared scientific-Python setup described in the
[Notebook Implementation Toolkit]({toolkit_rel}). That reference explains imports, deterministic random-number
generation, plotting configuration, output behavior, and why global warning suppression is discouraged.

{core}

## Implementation reference

These APIs and code patterns are demonstrated in the supporting notebook.

{markdown_table(api_rows, ['API or pattern', 'Purpose', 'Usage guidance'])}

## Best practices

{chr(10).join(f'- {item}' for item in meta['best'])}

## Common mistakes and edge cases

{chr(10).join(f'- {item}' for item in meta['mistakes'])}

## Additional practice

{chr(10).join(f'{i}. {item}' for i, item in enumerate(meta['practice'], 1))}

## Related lessons and source material

{related_links(number, md_path)}
- **Supporting notebook:** [{notebook.name}]({source_rel})
- **Coverage record:** [Course Coverage Index]({coverage_rel}#{md_anchor(coverage_heading)})
"""
    md_path.write_text(content.rstrip() + "\n", encoding="utf-8")


def write_toolkit():
    notebook_links = [
        f"[{p.name}](../../{p.relative_to(ROOT)})" for p in sorted(ROOT.glob("level_*/*.ipynb"))
    ]
    content = f"""# Notebook Implementation Toolkit

## Purpose

This reference documents the Python setup and implementation practices shared by the 15 supporting notebooks.
The Markdown lessons are authoritative; notebooks provide executable demonstrations and stored outputs.

## Shared scientific-Python stack

| Library | Role in the notebooks | Recommended practice |
|---|---|---|
| NumPy | Arrays, resampling, permutations, transforms, and quantiles | Use `numpy.random.default_rng(seed)` rather than global random state. |
| pandas | Tidy tables, summaries, reshaping, and displayed results | Keep one observation per row and name comparison directions explicitly. |
| SciPy | Probability distributions, classical tests, intervals, and resampling | Read each result object's statistic and p-value; do not report p alone. |
| statsmodels | Power, proportions, contingency tables, regression, ANOVA, multiplicity, and mixed models | State model formula, reference group, covariance assumptions, and adjustment method. |
| Matplotlib | Figure construction and low-level plot control | Label axes, units, reference lines, and uncertainty. |
| seaborn | Distribution, categorical, regression, and heatmap displays | Show raw data when feasible; do not let smoothing hide sample structure. |

## Reproducible random-number generation

The shared setup creates a local generator with `numpy.random.default_rng(seed)`. It is used for permutation,
bootstrap, and power-resampling procedures; it does not generate the primary observations.

```python
import numpy as np

rng = np.random.default_rng(20260920)
bootstrap_sample = rng.choice(observed_values, size=len(observed_values), replace=True)
```

A fixed seed reproduces the resampling path. It does not make a modeling assumption true or guarantee that different
library versions produce byte-identical plots.

## Local data loading

Every notebook resolves the course root before loading a documented CSV from `data/`.

```python
from pathlib import Path
import pandas as pd

working_dir = Path.cwd()
COURSE_ROOT = working_dir if (working_dir / "data").exists() else working_dir.parent
DATA_DIR = COURSE_ROOT / "data"
anes = pd.read_csv(DATA_DIR / "anes96_clean.csv")
```

This works when a kernel starts either in the course root or inside a level folder. The
[dataset guide](../../data/readme.md) records provenance, observation units, cleaning, and interpretation boundaries.

## Notebook execution and outputs

Code cells are intended to run from top to bottom. Execution order matters because later cells use variables created
earlier. Stored outputs include text streams, displayed tables, calculated result objects, and figures. If results look
inconsistent, restart the kernel and run all cells in order.

The course validation checks that every code cell has executed and that no stored output has type `error`.

## Plotting configuration

The notebooks select the inline Matplotlib backend, set a seaborn theme, and choose a default figure size. Those choices
improve notebook readability but are not statistical assumptions. Applied work should also consider accessibility,
color contrast, units, and whether a plot exposes individual observations.

## Warning handling

The notebooks deliberately leave warnings visible. Convergence, deprecation, numerical, and model warnings are part
of the evidence that an analysis needs attention and should not be hidden globally.

Prefer a scoped filter when a specific, understood warning is unavoidable:

```python
import warnings

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", message="specific known warning")
    result = operation_that_emits_the_known_warning()
```

Use scoped suppression only after the exact warning has been investigated and documented.

## Display and formatting helpers

- `pandas.set_option("display.precision", 4)` changes display only, not stored values.
- `display(...)` renders DataFrames and statsmodels tables in notebooks.
- f-strings format explanatory output; retain unrounded values for calculations.
- `plt.tight_layout()` reduces label overlap; `plt.show()` emits the figure output.

## Source notebook inventory

{chr(10).join(f'- {link}' for link in notebook_links)}
"""
    (ROOT / "docs" / "maintenance" / "notebook_toolkit.md").write_text(content, encoding="utf-8")


def write_coverage():
    notebooks = sorted(ROOT.glob("level_*/*.ipynb"))
    summary_rows = []
    sections = []
    for notebook in notebooks:
        number = lesson_number(notebook)
        info = notebook_inventory(notebook)
        md_path = notebook.parent / "markdown" / f"{notebook.stem}.md"
        nb_rel = Path(os.path.relpath(notebook, ROOT / "docs" / "maintenance"))
        md_rel = Path(os.path.relpath(md_path, ROOT / "docs" / "maintenance"))
        summary_rows.append((f"[{notebook.name}]({nb_rel})", info["cells"], info["markdown"], info["code"], info["executed"], info["outputs"], f"[{md_path.name}]({md_rel})"))
        coverage_rows = []
        for concept, definition, section, evidence in META[number]["concepts"]:
            coverage_rows.append((concept, evidence, f"[{md_path.name} — {section}]({md_rel}#{md_anchor(section)})"))
        for api, purpose, _ in META[number]["apis"]:
            coverage_rows.append((f"API/pattern: {api}", "Code", f"[{md_path.name} — Implementation reference]({md_rel}#implementation-reference)"))
        coverage_rows.append(("Real-data source, observation unit, lesson use, and interpretation boundary", "Data-loading code and lesson context", f"[{md_path.name} — Data used in this lesson]({md_rel}#data-used-in-this-lesson)"))
        coverage_rows.append(("Shared imports, deterministic RNG, plotting, display, execution order, and warning handling", "Setup code", "[Notebook Implementation Toolkit](notebook_toolkit.md)"))
        sections.append(f"""## {lesson_heading(notebook)}

**Notebook:** [{notebook.name}]({nb_rel})  
**Authoritative lesson:** [{md_path.name}]({md_rel})  
**Imports observed:** {', '.join(f'`{item}`' for item in info['imports'])}  
**Stored output types:** {info['output_types']}

{markdown_table(coverage_rows, ['Concept or implementation practice', 'Notebook evidence', 'Authoritative Markdown location'])}
""")

    content = f"""# Course Coverage Index

## Purpose

This index records the recursive review of every notebook in the course and maps every identified statistical concept,
important API, algorithm, workflow, and implementation practice to its authoritative Markdown documentation.

## Review status

- Notebooks discovered recursively: **{len(notebooks)}**
- Notebooks reviewed: **{len(notebooks)}**
- Notebook cells reviewed: **{sum(notebook_inventory(p)['cells'] for p in notebooks)}**
- Markdown cells reviewed: **{sum(notebook_inventory(p)['markdown'] for p in notebooks)}**
- Code cells reviewed: **{sum(notebook_inventory(p)['code'] for p in notebooks)}**
- Executed code cells reviewed: **{sum(notebook_inventory(p)['executed'] for p in notebooks)}**
- Authoritative lesson files: **{len(notebooks)}**
- Local documented CSV datasets: **{len(list((ROOT / 'data').glob('*.csv')))}**

Dataset provenance and cleaning are documented in the [course data guide](../../data/readme.md).

## Notebook inventory

{markdown_table(summary_rows, ['Notebook', 'Cells', 'Markdown', 'Code', 'Executed', 'Outputs', 'Authoritative lesson'])}

{chr(10).join(sections)}

## Coverage limitations

The inventory treats routine Python syntax such as assignment, loops, list construction, indexing, and formatted strings
as supporting implementation rather than separate statistical concepts. Important library APIs, algorithms, data-shaping
patterns, visualization practices, model formulas, data-loading steps, and resampling workflows are mapped explicitly
above. Shared setup practices are centralized in the Notebook Implementation Toolkit to avoid fifteen duplicated
explanations.

## Known teaching limits

- The Lesson 11 percentile bootstrap is introductory and omits more advanced interval refinements.
- The Lesson 12 equivalence margin is a teaching example; applied work needs a substantive margin set in advance.
- The Lesson 13 hand-built survival routines are educational examples, not production replacements for validated tools.
- The Lesson 14 capstone uses a balanced teaching subset of RAND HIE and simplifies the count outcome analysis.
- The Lesson 15 test-selection helper is a teaching aid that still requires design judgment.
"""
    (ROOT / "docs" / "maintenance" / "course_coverage_index.md").write_text(content, encoding="utf-8")


def convert_html_tables():
    """Replace nbconvert's embedded DataFrame HTML with readable Markdown tables."""

    def format_value(value):
        if pd.isna(value):
            return ""
        if isinstance(value, float):
            return f"{value:.4g}"
        return str(value)

    def replace_block(match):
        frame = pd.read_html(StringIO(match.group(0)))[0]
        headers = ["Term" if str(col).startswith("Unnamed:") else str(col) for col in frame.columns]
        rows = [[format_value(value) for value in row] for row in frame.itertuples(index=False, name=None)]
        return markdown_table(rows, headers)

    for path in sorted(ROOT.glob("level_*/markdown/lesson_*.md")):
        text = path.read_text(encoding="utf-8")
        text = re.sub(r"<div>.*?</div>", replace_block, text, flags=re.S)
        path.write_text(text, encoding="utf-8")


def fix_coverage_links():
    for notebook in sorted(ROOT.glob("level_*/*.ipynb")):
        number = lesson_number(notebook)
        md_path = notebook.parent / "markdown" / f"{notebook.stem}.md"
        heading = lesson_heading(notebook)
        text = md_path.read_text(encoding="utf-8")
        text = re.sub(
            rf"course_coverage_index\.md#lesson-{number}[^)]*\)",
            f"course_coverage_index.md#{md_anchor(heading)})",
            text,
        )
        md_path.write_text(text, encoding="utf-8")


def update_navigation():
    readme = (ROOT / "readme.md").read_text(encoding="utf-8")
    readme = readme.replace(
        "The course is split into three progressive levels so learners can stop at the depth they need. Jupyter notebooks\nare the canonical lessons; each level also contains generated Markdown reading versions.",
        "The course is split into three progressive levels so learners can stop at the depth they need. The Markdown\nlessons are authoritative; Jupyter notebooks are supporting executable examples."
    )
    readme = readme.replace("| # | Notebook | Reading version |", "| # | Supporting notebook | Authoritative lesson |")
    readme = readme.replace(
        "Run each notebook from top to bottom. All examples are deterministic and use generated data, so no download is\nrequired. The notebooks were executed during course validation.",
        "Read the Markdown lessons in order. Open the supporting notebooks when you want to run or modify an example.\nAll examples are deterministic and use generated data, so no download is required."
    )
    readme = readme.replace(
        "- Each level contains its canonical notebooks, a short README, and a `markdown/` export folder.",
        "- Each level contains supporting notebooks, a short README, and an authoritative `markdown/` course folder."
    )
    (ROOT / "readme.md").write_text(readme, encoding="utf-8")

    for level in sorted(ROOT.glob("level_*")):
        path = level / "readme.md"
        text = path.read_text(encoding="utf-8")
        text = text.replace("Open the notebook for interactive study or the Markdown version for reading.",
                            "Read the authoritative Markdown lesson first; open the notebook for interactive examples.")
        text = text.replace("| # | Notebook | Reading version |", "| # | Supporting notebook | Authoritative lesson |")
        path.write_text(text, encoding="utf-8")



def main():
    notebooks = sorted(ROOT.glob("level_*/*.ipynb"))
    if len(notebooks) != 15:
        raise SystemExit(f"Expected 15 notebooks, found {len(notebooks)}")
    write_toolkit()
    for notebook in notebooks:
        promote_lesson(notebook)
    write_coverage()
    convert_html_tables()
    fix_coverage_links()
    update_navigation()
    print(f"Promoted {len(notebooks)} lessons and wrote coverage documentation.")


if __name__ == "__main__":
    main()
