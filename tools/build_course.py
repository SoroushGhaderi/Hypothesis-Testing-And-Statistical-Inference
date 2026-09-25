#!/usr/bin/env python3
"""Legacy lesson definitions plus the current real-data course refresh entry point.

The historical lesson builders are retained for traceability but are no longer
called: they contain the original generated examples. Running this file now
rebuilds the local data bundle, applies the real-data notebook implementations,
executes them, synchronizes the authoritative Markdown, and validates the result.
"""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent
import subprocess
import sys

import nbformat as nbf


ROOT = Path(__file__).resolve().parents[1]


def clean(text: str) -> str:
    return dedent(text).strip() + "\n"


def md(text: str):
    return nbf.v4.new_markdown_cell(clean(text))


def code(text: str):
    return nbf.v4.new_code_cell(clean(text))


def slugify(title: str) -> str:
    return (title.replace(" ", "_").replace(":", "").replace(",", "")
            .replace("–", "-").replace("/", "_and_"))


def setup(seed: int):
    return code(
        f"""
        import warnings
        warnings.filterwarnings("ignore")

        import numpy as np
        import pandas as pd
        import matplotlib
        matplotlib.use("module://matplotlib_inline.backend_inline")
        import matplotlib.pyplot as plt
        import seaborn as sns
        from scipy import stats

        rng = np.random.default_rng({seed})
        sns.set_theme(style="whitegrid", context="notebook")
        plt.rcParams["figure.figsize"] = (10, 5)
        pd.set_option("display.precision", 4)
        """
    )


def lesson(number: int, title: str, objectives: list[str], body: list, prerequisites: str = "Basic Python and descriptive statistics"):
    objectives_md = "\n".join(f"{i}. {item}" for i, item in enumerate(objectives, 1))
    cells = [
        md(
            f"""
            # Lesson {number}: {title}

            **Course:** hypothesis_testing_and_statistical_inference  
            **Prerequisites:** {prerequisites}

            This lesson follows a repeatable workflow: define the question, encode the design,
            check assumptions, estimate the effect, quantify uncertainty, test the claim, and
            communicate both statistical and practical meaning.
            """
        ),
        md(f"## Learning objectives\n\n{objectives_md}"),
        md("## Setup\n\nRun this cell first. Every example uses a fixed random seed so results are reproducible."),
        setup(20260919 + number),
    ]
    cells.extend(body)
    cells.extend(
        [
            md(
                """
                ## Reproducibility checklist

                - State the population, outcome, groups, and sampling unit.
                - State $H_0$, $H_1$, alpha, and whether the test is one- or two-sided before looking at results.
                - Verify independence from the design; use plots and diagnostics for distributional assumptions.
                - Report the estimate, confidence interval, effect size, test statistic, degrees of freedom, and exact p-value.
                - Separate statistical evidence from practical importance and acknowledge design limitations.
                """
            )
        ]
    )
    nb = nbf.v4.new_notebook(
        cells=cells,
        metadata={
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3"},
            "course": {"lesson": number, "title": title},
        },
    )
    return nb


LESSONS = [
    {
        "title": "The Logic of Hypothesis Testing",
        "objectives": [
            "Translate a research question into a population parameter, null hypothesis, and alternative hypothesis",
            "Explain p-values, significance levels, Type I errors, and Type II errors without common misconceptions",
            "Connect hypothesis tests to confidence intervals and effect sizes",
            "Distinguish statistical significance from practical significance",
        ],
        "body": [
            md(
                r"""
                ## 1.1 From a question to a testable claim

                A useful hypothesis test begins with a **design**, not with a software menu.

                | Question | Parameter | Typical null | Typical alternative |
                |---|---:|---|---|
                | Is a mean different from a target? | $\mu$ | $\mu=\mu_0$ | $\mu\ne\mu_0$ |
                | Do two groups have different means? | $\mu_1-\mu_2$ | $\mu_1-\mu_2=0$ | $\mu_1-\mu_2\ne0$ |
                | Did a conversion rate change? | $p_1-p_2$ | $p_1-p_2=0$ | $p_1-p_2\ne0$ |
                | Are two categorical variables associated? | joint probabilities | independence | association |

                The **null hypothesis** is a precise reference model. The **alternative** describes departures
                that matter for the question. A two-sided alternative is the default unless direction was justified
                before observing the data.
                """
            ),
            md(
                r"""
                ## 1.2 What a p-value is—and is not

                A p-value is the probability, **assuming $H_0$ and the model assumptions are true**, of obtaining
                a test statistic at least as incompatible with $H_0$ as the observed statistic.

                It is **not**:

                - the probability that $H_0$ is true;
                - the probability the result happened "by chance";
                - the size or importance of an effect;
                - a guarantee that the result will replicate.

                At level $\alpha$, reject $H_0$ when $p\le\alpha$. Otherwise, **fail to reject** $H_0$.
                Failure to reject is not proof of no effect; it can reflect imprecision or low power.
                """
            ),
            code(
                """
                # Under a true null, p-values are approximately uniform.
                n_experiments, n_per_group = 5000, 20
                p_values = []
                for _ in range(n_experiments):
                    a = rng.normal(0, 1, n_per_group)
                    b = rng.normal(0, 1, n_per_group)
                    p_values.append(stats.ttest_ind(a, b, equal_var=False).pvalue)

                p_values = np.array(p_values)
                print(f"False-positive rate at alpha=.05: {(p_values < .05).mean():.3f}")

                fig, ax = plt.subplots()
                ax.hist(p_values, bins=20, edgecolor="white")
                ax.axvline(.05, color="crimson", linestyle="--", label="alpha = .05")
                ax.set(xlabel="p-value", ylabel="Number of experiments", title="P-values when the null is true")
                ax.legend()
                plt.show()
                """
            ),
            md(
                r"""
                ## 1.3 Test statistics, confidence intervals, and effect sizes

                Most test statistics have the form

                $$\text{signal-to-noise} = \frac{\text{estimate}-\text{null value}}{\text{standard error}}.$$

                A compatible confidence interval answers a richer question: which parameter values remain plausible?
                For a two-sided test at $\alpha=.05$, a 95% confidence interval that excludes the null value leads to
                rejection at the same level. Always pair the test with an effect size in the outcome's natural units.
                """
            ),
            code(
                """
                sample = rng.normal(loc=102, scale=12, size=40)
                null_mean = 100
                result = stats.ttest_1samp(sample, popmean=null_mean)
                estimate = sample.mean()
                se = sample.std(ddof=1) / np.sqrt(len(sample))
                ci = stats.t.interval(.95, df=len(sample)-1, loc=estimate, scale=se)
                d = (estimate - null_mean) / sample.std(ddof=1)

                pd.Series({
                    "sample mean": estimate,
                    "mean difference": estimate-null_mean,
                    "95% CI low": ci[0],
                    "95% CI high": ci[1],
                    "t": result.statistic,
                    "p": result.pvalue,
                    "Cohen d": d,
                })
                """
            ),
            md(
                """
                ## Practice and solution

                **Practice.** A result has $p=.08$ and a 95% CI for the mean difference of $[-0.4, 6.2]$.
                What can you conclude?

                <details><summary>Solution</summary>

                At alpha = .05, fail to reject a two-sided null of zero difference because the interval includes zero.
                The data are compatible with a small negative effect through a moderately positive effect, so the
                estimate is too imprecise to conclude either "no effect" or a clearly useful benefit.
                </details>

                ## Key takeaways

                1. Begin with the estimand and design.
                2. A p-value measures compatibility with a null model, not truth or importance.
                3. Confidence intervals and effect sizes carry information a binary decision discards.
                """
            ),
        ],
    },
    {
        "title": "Sampling Distributions, Errors, and Power",
        "objectives": [
            "Use sampling distributions to explain standard errors and critical regions",
            "Relate alpha, effect size, sample size, variability, and power",
            "Estimate power by simulation",
            "Recognize optional stopping and post-hoc power as poor analysis practices",
        ],
        "body": [
            md(
                r"""
                ## 2.1 Two kinds of decision error

                | Reality | Do not reject $H_0$ | Reject $H_0$ |
                |---|---|---|
                | $H_0$ true | correct | Type I error ($\alpha$) |
                | Meaningful alternative true | Type II error ($\beta$) | correct (power $=1-\beta$) |

                Power is the long-run probability that a planned procedure rejects $H_0$ for a specified true effect.
                It increases with larger effects, larger samples, lower noise, and (at a cost) larger $\alpha$.
                """
            ),
            code(
                """
                def simulated_power(effect, n, alpha=.05, repetitions=2500):
                    rejections = 0
                    for _ in range(repetitions):
                        control = rng.normal(0, 1, n)
                        treatment = rng.normal(effect, 1, n)
                        p = stats.ttest_ind(control, treatment, equal_var=False).pvalue
                        rejections += p < alpha
                    return rejections / repetitions

                rows = []
                for effect in [0.0, 0.2, 0.5, 0.8]:
                    for n in [10, 20, 40, 80]:
                        rows.append({"standardized effect": effect, "n per group": n,
                                     "rejection rate": simulated_power(effect, n)})
                power_table = pd.DataFrame(rows)
                power_table.pivot(index="n per group", columns="standardized effect", values="rejection rate")
                """
            ),
            code(
                """
                fig, ax = plt.subplots()
                for effect, group in power_table.groupby("standardized effect"):
                    ax.plot(group["n per group"], group["rejection rate"], marker="o", label=f"d={effect}")
                ax.axhline(.80, color="black", linestyle="--", alpha=.7, label="80% target")
                ax.set(xlabel="Sample size per group", ylabel="Rejection probability",
                       ylim=(0, 1), title="Power depends on effect size and sample size")
                ax.legend()
                plt.show()
                """
            ),
            md(
                r"""
                ## 2.2 Planning before data collection

                Power calculations need a **minimum effect of practical interest**, not the effect observed in the same
                noisy dataset. The planning effect should come from domain requirements, credible prior studies, or a
                smallest effect that would change a decision.

                Optional stopping—repeatedly testing and stopping as soon as $p<.05$—raises the false-positive rate.
                Pre-specify the sample size or use a valid sequential design.
                """
            ),
            code(
                """
                from statsmodels.stats.power import TTestIndPower

                analysis = TTestIndPower()
                required = analysis.solve_power(effect_size=.4, alpha=.05, power=.80, ratio=1)
                achieved = analysis.power(effect_size=.4, nobs1=np.ceil(required), alpha=.05, ratio=1)
                print(f"Required per group for d=.40: {np.ceil(required):.0f}")
                print(f"Achieved power after rounding: {achieved:.3f}")
                """
            ),
            md(
                """
                ## Practice and solution

                **Practice.** Name two defensible ways to choose an effect for a priori power analysis.

                <details><summary>Solution</summary>

                Use a smallest effect that would change a scientific or business decision, or use a conservative
                estimate from high-quality prior evidence. Do not select the observed effect from a small pilot as if it
                were known precisely; use sensitivity analysis across plausible values instead.
                </details>

                ## Key takeaways

                - Alpha controls false positives only under the planned procedure.
                - Power is tied to a specific alternative and must be planned prospectively.
                - Simulation is a flexible power tool when formulas do not match the design.
                """
            ),
        ],
    },
    {
        "title": "One-Sample Tests for Means and Proportions",
        "objectives": [
            "Run and report a one-sample t-test with a confidence interval and standardized effect",
            "Choose between an exact binomial test and a large-sample proportion test",
            "Check assumptions and identify when a one-sample test cannot support a causal claim",
            "Interpret one-sided tests correctly",
        ],
        "body": [
            md(
                r"""
                ## 3.1 One-sample mean

                For independent quantitative observations, the one-sample t statistic is
                $$t=\frac{\bar{x}-\mu_0}{s/\sqrt{n}},\qquad df=n-1.$$
                Independence comes from the sampling process. For small samples, inspect the distribution for severe
                skew or influential outliers; for large samples, the mean is often robust to modest non-normality.
                """
            ),
            code(
                """
                delivery_minutes = np.array([31, 28, 35, 29, 33, 37, 27, 30, 34, 32, 36, 29, 31, 38, 30])
                target = 30
                test = stats.ttest_1samp(delivery_minutes, popmean=target)
                n = len(delivery_minutes)
                mean = delivery_minutes.mean()
                sd = delivery_minutes.std(ddof=1)
                ci = stats.t.interval(.95, n-1, loc=mean, scale=sd/np.sqrt(n))
                d = (mean-target)/sd
                pd.Series({"n": n, "mean": mean, "SD": sd, "t": test.statistic,
                           "df": n-1, "p": test.pvalue, "Cohen d": d,
                           "CI low": ci[0], "CI high": ci[1]})
                """
            ),
            code(
                """
                fig, axes = plt.subplots(1, 2, figsize=(11, 4))
                sns.boxplot(y=delivery_minutes, ax=axes[0])
                sns.stripplot(y=delivery_minutes, color="black", ax=axes[0])
                axes[0].axhline(target, color="crimson", linestyle="--")
                axes[0].set_title("Observed values and target")
                stats.probplot(delivery_minutes, dist="norm", plot=axes[1])
                axes[1].set_title("Normal Q-Q plot")
                plt.tight_layout(); plt.show()
                """
            ),
            md(
                r"""
                ## 3.2 One-sample proportion

                Use the exact binomial test when the sample is small or the null proportion is near 0 or 1. A normal
                approximation is reasonable when $np_0$ and $n(1-p_0)$ are both sufficiently large. For intervals,
                Wilson or exact intervals behave better than the simple Wald interval.
                """
            ),
            code(
                """
                successes, trials, p0 = 19, 30, .50
                exact = stats.binomtest(successes, trials, p=p0, alternative="two-sided")
                ci = exact.proportion_ci(confidence_level=.95, method="wilson")
                p_hat = successes/trials
                cohen_h = 2*(np.arcsin(np.sqrt(p_hat))-np.arcsin(np.sqrt(p0)))
                pd.Series({"successes": successes, "n": trials, "p-hat": p_hat,
                           "exact p": exact.pvalue, "Cohen h": cohen_h,
                           "Wilson low": ci.low, "Wilson high": ci.high})
                """
            ),
            md(
                """
                ## Practice and solution

                **Practice.** A manufacturer claims fewer than 2% of parts are defective. In a random sample of 100,
                4 are defective. Write the hypotheses and identify an appropriate test.

                <details><summary>Solution</summary>

                For a claim that the defect rate is below 2%, use $H_0:p\ge .02$ versus $H_1:p<.02$, operationally
                tested at the boundary $p=.02$ with a one-sided exact binomial test. Because only two defects are
                expected under the boundary null, the exact test is preferable to a normal approximation. Observing
                four defects points opposite to the stated alternative, so the data cannot support "below 2%."
                </details>

                ## Key takeaways

                - Match the parameter and direction to the claim before seeing results.
                - Exact methods are especially useful for small or extreme proportions.
                - A test of a benchmark does not establish why a sample differs from it.
                """
            ),
        ],
    },
    {
        "title": "Two Independent Groups",
        "objectives": [
            "Use Welch's t-test as a robust default for independent means",
            "Compute a confidence interval for the mean difference and Hedges' g",
            "Use Mann–Whitney U for ordinal or rank-focused questions",
            "Explain why test choice depends on the estimand, not only a normality p-value",
        ],
        "body": [
            md(
                r"""
                ## 4.1 Design and estimand

                Two independent groups contain different observational units. Welch's t-test targets a difference in
                population means without assuming equal variances. It is generally a safer default than the pooled
                equal-variance t-test.

                Mann–Whitney U tests a rank/distributional contrast. Interpreting it as a median test requires similar
                distribution shapes; it is not automatically a drop-in test of means.
                """
            ),
            code(
                """
                control = rng.normal(72, 8, 35)
                treatment = rng.normal(78, 12, 29)

                welch = stats.ttest_ind(treatment, control, equal_var=False)
                n1, n2 = len(treatment), len(control)
                m1, m2 = treatment.mean(), control.mean()
                v1, v2 = treatment.var(ddof=1), control.var(ddof=1)
                se = np.sqrt(v1/n1 + v2/n2)
                df = (v1/n1 + v2/n2)**2 / ((v1/n1)**2/(n1-1) + (v2/n2)**2/(n2-1))
                diff = m1-m2
                ci = diff + np.array([-1, 1])*stats.t.ppf(.975, df)*se

                pooled_sd = np.sqrt(((n1-1)*v1+(n2-1)*v2)/(n1+n2-2))
                d = diff/pooled_sd
                correction = 1 - 3/(4*(n1+n2)-9)
                hedges_g = correction*d

                pd.Series({"treatment mean": m1, "control mean": m2, "difference": diff,
                           "95% CI low": ci[0], "95% CI high": ci[1], "Welch t": welch.statistic,
                           "df": df, "p": welch.pvalue, "Hedges g": hedges_g})
                """
            ),
            code(
                """
                tidy = pd.DataFrame({
                    "score": np.r_[control, treatment],
                    "group": ["Control"]*len(control)+["Treatment"]*len(treatment)
                })
                fig, axes = plt.subplots(1, 2, figsize=(12, 4))
                sns.violinplot(data=tidy, x="group", y="score", inner=None, ax=axes[0])
                sns.stripplot(data=tidy, x="group", y="score", color="black", alpha=.6, ax=axes[0])
                axes[0].set_title("Raw distributions")
                for values, label in [(control, "Control"), (treatment, "Treatment")]:
                    stats.probplot(values, dist="norm", plot=axes[1])
                axes[1].set_title("Q-Q diagnostics (overlaid)")
                plt.tight_layout(); plt.show()
                """
            ),
            code(
                """
                mw = stats.mannwhitneyu(treatment, control, alternative="two-sided")
                # Probability-of-superiority effect, adjusted to [-1, 1].
                rank_biserial = 2*mw.statistic/(n1*n2)-1
                pd.Series({"U": mw.statistic, "p": mw.pvalue,
                           "rank-biserial correlation": rank_biserial,
                           "treatment median": np.median(treatment),
                           "control median": np.median(control)})
                """
            ),
            md(
                """
                ## Practice and solution

                **Practice.** Why is selecting Welch versus Mann–Whitney solely from a Shapiro–Wilk p-value weak?

                <details><summary>Solution</summary>

                The tests target different quantities. Normality tests have low power in small samples and excessive
                sensitivity in large samples. Use the scientific estimand, design, plots, outlier influence, and sample
                size. Welch's test is often robust for means; Mann–Whitney is natural for ordinal outcomes or a
                probability-of-superiority/rank contrast.
                </details>

                ## Key takeaways

                - Verify independence from the design.
                - Prefer Welch for an independent mean difference unless equal-variance pooling is justified.
                - Report the raw-unit difference and CI alongside a standardized effect.
                """
            ),
        ],
    },
    {
        "title": "Paired and Repeated Measurements",
        "objectives": [
            "Recognize paired, matched, and repeated-measures designs",
            "Analyze paired quantitative outcomes using the distribution of within-pair differences",
            "Use Wilcoxon signed-rank and McNemar tests when their data structures match",
            "Avoid treating repeated observations as independent",
        ],
        "body": [
            md(
                r"""
                ## 5.1 Pairing changes the unit of analysis

                In a before/after design, each person is their own control. The paired t-test is a one-sample t-test on
                differences $d_i=\text{after}_i-\text{before}_i$. Its assumptions concern those differences—not the
                marginal before and after distributions.
                """
            ),
            code(
                """
                before = rng.normal(145, 12, 24)
                after = before - rng.normal(5, 7, 24)
                change = after-before
                paired = stats.ttest_rel(after, before)
                n = len(change)
                mean_change = change.mean()
                se = change.std(ddof=1)/np.sqrt(n)
                ci = stats.t.interval(.95, n-1, loc=mean_change, scale=se)
                dz = mean_change/change.std(ddof=1)
                pd.Series({"mean change (after-before)": mean_change, "CI low": ci[0], "CI high": ci[1],
                           "t": paired.statistic, "df": n-1, "p": paired.pvalue, "Cohen dz": dz})
                """
            ),
            code(
                """
                fig, axes = plt.subplots(1, 2, figsize=(12, 4))
                for b, a in zip(before, after):
                    axes[0].plot([0, 1], [b, a], color="gray", alpha=.5)
                axes[0].set(xticks=[0, 1], xticklabels=["Before", "After"], ylabel="Outcome",
                            title="Paired trajectories")
                sns.histplot(change, kde=True, ax=axes[1])
                axes[1].axvline(0, color="crimson", linestyle="--")
                axes[1].set(title="Distribution of paired changes", xlabel="After - before")
                plt.tight_layout(); plt.show()
                """
            ),
            md(
                """
                ## 5.2 Rank-based and binary paired tests

                - **Wilcoxon signed-rank:** paired quantitative/ordinal data; tests symmetry-centered change and assumes
                  a roughly symmetric difference distribution.
                - **Sign test:** weaker but needs fewer shape assumptions.
                - **McNemar:** paired binary outcomes; uses only discordant pairs.
                """
            ),
            code(
                """
                wilcoxon = stats.wilcoxon(after, before, alternative="two-sided")
                from statsmodels.stats.contingency_tables import mcnemar

                # Rows: before No/Yes; columns: after No/Yes
                paired_binary = np.array([[42, 18], [7, 33]])
                mc = mcnemar(paired_binary, exact=True)
                discordant_or = paired_binary[0, 1]/paired_binary[1, 0]
                pd.DataFrame({
                    "test": ["Wilcoxon signed-rank", "Exact McNemar"],
                    "statistic": [wilcoxon.statistic, mc.statistic],
                    "p": [wilcoxon.pvalue, mc.pvalue],
                    "effect/note": ["paired rank shift", f"discordant-pair OR={discordant_or:.2f}"]
                })
                """
            ),
            md(
                """
                ## Practice and solution

                **Practice.** A dataset has three measurements per participant. Why not run three independent t-tests?

                <details><summary>Solution</summary>

                Measurements within a person are correlated, violating independence, and three tests inflate the
                family-wise error rate. Use repeated-measures ANOVA, Friedman, or a mixed model, followed by adjusted
                planned contrasts when needed.
                </details>

                ## Key takeaways

                - Pairing must be represented in both plots and tests.
                - Diagnose the within-pair differences for a paired t-test.
                - McNemar is for paired binary outcomes, not independent contingency tables.
                """
            ),
        ],
    },
    {
        "title": "Three or More Independent Groups",
        "objectives": [
            "Run one-way ANOVA and quantify the omnibus effect with omega-squared",
            "Use Welch ANOVA or Kruskal–Wallis when appropriate",
            "Follow a significant omnibus test with multiplicity-aware comparisons",
            "Distinguish planned contrasts from exploratory post-hoc testing",
        ],
        "body": [
            md(
                r"""
                ## 6.1 The omnibus question

                One-way ANOVA tests $H_0:\mu_1=\cdots=\mu_k$. Rejection means at least one mean differs; it does not say
                which. The F statistic compares between-group variation with within-group variation. Independence is a
                design assumption; residual shape and variance patterns are model diagnostics.
                """
            ),
            code(
                """
                groups = {
                    "A": rng.normal(50, 6, 28),
                    "B": rng.normal(54, 7, 30),
                    "C": rng.normal(61, 6, 26),
                }
                df = pd.DataFrame([(g, x) for g, values in groups.items() for x in values],
                                  columns=["group", "score"])
                from statsmodels.formula.api import ols
                from statsmodels.stats.anova import anova_lm
                model = ols("score ~ C(group)", data=df).fit()
                table = anova_lm(model, typ=2)
                ss_between = table.loc["C(group)", "sum_sq"]
                ss_error = table.loc["Residual", "sum_sq"]
                df_between = table.loc["C(group)", "df"]
                ms_error = ss_error/table.loc["Residual", "df"]
                omega2 = (ss_between-df_between*ms_error)/(ss_between+ss_error+ms_error)
                display(table)
                print(f"Omega-squared: {omega2:.3f}")
                """
            ),
            code(
                """
                from statsmodels.stats.multicomp import pairwise_tukeyhsd
                tukey = pairwise_tukeyhsd(df["score"], df["group"], alpha=.05)
                print(tukey)

                fig, ax = plt.subplots()
                sns.boxplot(data=df, x="group", y="score", ax=ax)
                sns.stripplot(data=df, x="group", y="score", color="black", alpha=.5, ax=ax)
                ax.set_title("Always inspect distributions, not only means")
                plt.show()
                """
            ),
            md(
                """
                ## 6.2 Robust alternatives

                - **Welch ANOVA:** compares means with unequal variances; follow with Games–Howell when available.
                - **Kruskal–Wallis:** rank-based omnibus test for independent groups; follow with adjusted pairwise
                  rank tests. It is sensitive to distributional differences, not exclusively medians.
                """
            ),
            code(
                """
                from statsmodels.stats.oneway import anova_oneway
                from statsmodels.stats.multitest import multipletests
                from itertools import combinations

                welch = anova_oneway(list(groups.values()), use_var="unequal")
                kw = stats.kruskal(*groups.values())
                n_total, k = len(df), len(groups)
                epsilon2 = max(0, (kw.statistic-k+1)/(n_total-k))

                comparisons = []
                for a, b in combinations(groups, 2):
                    result = stats.mannwhitneyu(groups[a], groups[b], alternative="two-sided")
                    comparisons.append([a, b, result.statistic, result.pvalue])
                comp = pd.DataFrame(comparisons, columns=["group 1", "group 2", "U", "raw p"])
                comp["Holm p"] = multipletests(comp["raw p"], method="holm")[1]
                print(f"Welch ANOVA: F={welch.statistic:.3f}, p={welch.pvalue:.4g}")
                print(f"Kruskal-Wallis: H={kw.statistic:.3f}, p={kw.pvalue:.4g}, epsilon²={epsilon2:.3f}")
                comp
                """
            ),
            md(
                """
                ## Practice and solution

                **Practice.** The omnibus ANOVA p-value is .002. Can you report that group C exceeds group A?

                <details><summary>Solution</summary>

                Not from the omnibus result alone. Use a pre-specified contrast or a multiplicity-controlled post-hoc
                comparison and report the estimated difference with its interval. The omnibus test only establishes
                that not all population means are equal.
                </details>

                ## Key takeaways

                - Omnibus tests answer a global question; post-hoc tests locate differences.
                - Use omega-squared or another effect size, not only F and p.
                - Choose robust methods based on the estimand and diagnostics.
                """
            ),
        ],
    },
    {
        "title": "Factorial Designs, Interactions, and ANCOVA",
        "objectives": [
            "Interpret an interaction before interpreting main effects",
            "Fit a two-factor model and test model terms",
            "Use ANCOVA to improve precision while checking slope homogeneity",
            "Explain why post-treatment covariate adjustment can bias results",
        ],
        "body": [
            md(
                r"""
                ## 7.1 Factorial designs

                A two-factor model includes main effects and an interaction:
                $$Y=\beta_0+\beta_A A+\beta_B B+\beta_{AB}(A\times B)+\varepsilon.$$
                A meaningful interaction says the effect of one factor depends on the level of the other. Inspect the
                interaction first; a single averaged main effect can conceal opposing simple effects.
                """
            ),
            code(
                """
                rows = []
                for method in ["standard", "coached"]:
                    for experience in ["new", "experienced"]:
                        base = 70 + (5 if method == "coached" else 0) + (8 if experience == "experienced" else 0)
                        interaction = 7 if (method == "coached" and experience == "new") else 0
                        for value in rng.normal(base+interaction, 6, 25):
                            rows.append((method, experience, value))
                factorial = pd.DataFrame(rows, columns=["method", "experience", "score"])

                from statsmodels.formula.api import ols
                from statsmodels.stats.anova import anova_lm
                fit = ols("score ~ C(method) * C(experience)", data=factorial).fit()
                anova_lm(fit, typ=2)
                """
            ),
            code(
                """
                means = factorial.groupby(["method", "experience"], as_index=False)["score"].mean()
                fig, ax = plt.subplots()
                sns.pointplot(data=factorial, x="experience", y="score", hue="method",
                              errorbar=("ci", 95), dodge=.08, ax=ax)
                ax.set_title("Interaction plot with 95% confidence intervals")
                plt.show()
                means
                """
            ),
            md(
                r"""
                ## 7.2 ANCOVA

                ANCOVA compares groups while adjusting for a pre-existing quantitative covariate. Check whether the
                covariate-outcome slope is similar across groups by fitting a group-by-covariate interaction. Adjustment
                should be planned and should not condition on a variable caused by treatment.
                """
            ),
            code(
                """
                n = 100
                group = rng.choice(["control", "treatment"], n)
                baseline = rng.normal(50, 10, n)
                outcome = 15 + .75*baseline + 5*(group == "treatment") + rng.normal(0, 6, n)
                ancova_df = pd.DataFrame({"group": group, "baseline": baseline, "outcome": outcome})

                slope_check = ols("outcome ~ baseline * C(group)", data=ancova_df).fit()
                adjusted = ols("outcome ~ baseline + C(group)", data=ancova_df).fit()
                print("Slope-homogeneity model:")
                display(anova_lm(slope_check, typ=2))
                print()
                print("Adjusted model coefficients:")
                display(adjusted.summary2().tables[1])
                """
            ),
            md(
                """
                ## Practice and solution

                **Practice.** In a treatment-by-sex model, the interaction p-value is .01. What should be reported next?

                <details><summary>Solution</summary>

                Report estimated treatment effects within each sex (simple effects) with confidence intervals and a
                multiplicity plan, plus an interaction plot. Avoid summarizing the result only with the overall
                treatment main effect because it averages across meaningfully different effects.
                </details>

                ## Key takeaways

                - Interactions change the meaning of main effects.
                - ANCOVA can improve precision when covariates are pre-treatment and appropriately modeled.
                - Model diagnostics and study design remain essential; an ANOVA table does not establish causality.
                """
            ),
        ],
    },
    {
        "title": "Categorical Data: Chi-Square, Fisher, and McNemar",
        "objectives": [
            "Distinguish goodness-of-fit, independence, and paired categorical tests",
            "Check expected counts and use exact methods for sparse 2x2 tables",
            "Compute Cramér's V, odds ratios, and standardized residuals",
            "Report counts, percentages, uncertainty, and practical meaning",
        ],
        "body": [
            md(
                r"""
                ## 8.1 Independence in a contingency table

                For cell $(i,j)$, independence implies
                $$E_{ij}=\frac{(\text{row total}_i)(\text{column total}_j)}{N}.$$
                The Pearson statistic $\chi^2=\sum (O-E)^2/E$ aggregates discrepancies. Inspect expected counts and
                residuals; a small p-value alone does not identify the important cells.
                """
            ),
            code(
                """
                observed = np.array([[84, 36, 20], [55, 49, 36]])
                table = pd.DataFrame(observed, index=["Desktop", "Mobile"],
                                     columns=["No purchase", "Small", "Large"])
                chi2, p, dof, expected = stats.chi2_contingency(observed, correction=False)
                n = observed.sum()
                cramer_v = np.sqrt(chi2/(n*(min(observed.shape)-1)))
                residuals = (observed-expected)/np.sqrt(expected)
                display(table)
                print(f"chi-square({dof})={chi2:.3f}, p={p:.4g}, Cramer's V={cramer_v:.3f}")
                display(pd.DataFrame(expected, index=table.index, columns=table.columns).round(2))
                display(pd.DataFrame(residuals, index=table.index, columns=table.columns).round(2))
                """
            ),
            code(
                """
                fig, ax = plt.subplots()
                sns.heatmap(pd.DataFrame(residuals, index=table.index, columns=table.columns),
                            annot=True, center=0, cmap="coolwarm", ax=ax)
                ax.set_title("Pearson residuals: cells driving the association")
                plt.show()
                """
            ),
            md(
                """
                ## 8.2 Sparse 2x2 tables and effect measures

                Fisher's exact test conditions on the margins and is valid with small counts. For a 2x2 table, report
                an odds ratio and confidence interval. Relative risk is often easier to interpret in cohort or
                randomized designs; odds ratios are natural in case-control studies and logistic regression.
                """
            ),
            code(
                """
                sparse = np.array([[1, 9], [8, 4]])
                fisher = stats.fisher_exact(sparse, alternative="two-sided")
                from statsmodels.stats.contingency_tables import Table2x2
                t22 = Table2x2(sparse)
                ci = t22.oddsratio_confint()
                pd.Series({"odds ratio": fisher.statistic, "exact p": fisher.pvalue,
                           "OR CI low": ci[0], "OR CI high": ci[1]})
                """
            ),
            md(
                """
                ## Practice and solution

                **Practice.** Which test fits each case: (a) one die rolled 120 times; (b) device type versus conversion
                in independent users; (c) the same users' subscription status before and after a campaign?

                <details><summary>Solution</summary>

                (a) Chi-square goodness-of-fit against the six expected probabilities. (b) Chi-square independence or
                two-proportion test; use Fisher exact if expected counts are sparse. (c) McNemar, because outcomes are
                paired binary measurements.
                </details>

                ## Key takeaways

                - Select the categorical test from the sampling structure.
                - Check expected—not observed—counts for chi-square adequacy.
                - Report interpretable risks or odds with intervals, not only an association p-value.
                """
            ),
        ],
    },
    {
        "title": "Proportions and A/B Tests",
        "objectives": [
            "Analyze independent conversion rates with a two-proportion z-test",
            "Report absolute risk difference, relative risk, odds ratio, and confidence intervals",
            "Plan sample size using a minimum detectable effect",
            "Recognize peeking, sample-ratio mismatch, and metric multiplicity",
        ],
        "body": [
            md(
                r"""
                ## 9.1 A/B tests are experiments, not just z-tests

                Random assignment supports causal interpretation when assignment is implemented correctly, units do
                not interfere, attrition is handled, and the analysis follows the planned stopping rule. Analyze users
                at their assigned condition (intention-to-treat) unless the estimand explicitly differs.
                """
            ),
            code(
                """
                from statsmodels.stats.proportion import proportions_ztest, confint_proportions_2indep

                conversions = np.array([214, 252])
                visitors = np.array([4000, 3975])
                z, p = proportions_ztest(conversions, visitors)
                rates = conversions/visitors
                # CI is control minus treatment because arguments are passed in that order.
                ci_control_minus_treat = confint_proportions_2indep(
                    conversions[0], visitors[0], conversions[1], visitors[1], method="score")
                diff = rates[1]-rates[0]
                diff_ci = (-ci_control_minus_treat[1], -ci_control_minus_treat[0])
                rr = rates[1]/rates[0]
                odds_ratio = (rates[1]/(1-rates[1]))/(rates[0]/(1-rates[0]))
                nnt = 1/diff if diff > 0 else np.inf
                pd.Series({"control rate": rates[0], "treatment rate": rates[1],
                           "absolute lift": diff, "lift CI low": diff_ci[0], "lift CI high": diff_ci[1],
                           "z": z, "p": p, "relative risk": rr, "odds ratio": odds_ratio,
                           "users per extra conversion": nnt})
                """
            ),
            md(
                """
                ## 9.2 Design checks

                Before trusting the effect:

                1. Check assignment counts against the intended allocation (sample-ratio mismatch).
                2. Verify one row per randomized unit and correct exposure timing.
                3. Define one primary metric and a multiplicity strategy for secondary metrics.
                4. Use the pre-specified duration/sample size; account for seasonality and novelty effects.
                5. Report absolute lift because relative lift can exaggerate small baseline changes.
                """
            ),
            code(
                """
                # Sample-ratio mismatch check for a planned 50/50 allocation.
                allocation_check = stats.chisquare(visitors, f_exp=np.repeat(visitors.sum()/2, 2))

                from statsmodels.stats.power import NormalIndPower
                from statsmodels.stats.proportion import proportion_effectsize
                baseline, target = .05, .06
                h = abs(proportion_effectsize(target, baseline))
                required = NormalIndPower().solve_power(h, alpha=.05, power=.80, ratio=1)
                print(f"Allocation check p-value: {allocation_check.pvalue:.4f}")
                print(f"For 5% -> 6%, required per group: {np.ceil(required):,.0f}")
                """
            ),
            md(
                """
                ## Practice and solution

                **Practice.** Treatment conversion is 5.5% versus 5.0% in control, with p=.04. What else is needed
                before launch?

                <details><summary>Solution</summary>

                Report the 0.5 percentage-point absolute lift and its CI, relative effect, costs/benefits, guardrail
                metrics, assignment and data-quality checks, stopping compliance, and whether multiple metrics or
                segments were searched. A small p-value alone does not establish business value or validity.
                </details>

                ## Key takeaways

                - The experimental protocol makes the causal claim credible; the z-test summarizes uncertainty.
                - Absolute effects and intervals are central to decisions.
                - Plan sample size from a minimum useful effect and resist unplanned peeking.
                """
            ),
        ],
    },
    {
        "title": "Correlation and Regression-Based Tests",
        "objectives": [
            "Select Pearson, Spearman, Kendall, or point-biserial association measures",
            "Inspect form, outliers, and dependence before testing correlation",
            "Test regression coefficients and interpret confidence intervals",
            "Explain why association does not establish causation",
        ],
        "body": [
            md(
                r"""
                ## 10.1 Correlation is a model of association

                Pearson's $r$ summarizes linear association; Spearman's $\rho$ summarizes monotonic rank association;
                Kendall's $\tau$ is useful with small samples or many ties. Always draw the scatterplot: different
                relationships can have the same correlation.
                """
            ),
            code(
                """
                x = rng.uniform(0, 10, 80)
                y = 2.5*x + rng.normal(0, 6, 80)
                y[0] += 35  # an intentionally influential observation

                pearson = stats.pearsonr(x, y)
                spearman = stats.spearmanr(x, y)
                kendall = stats.kendalltau(x, y)
                z = np.arctanh(pearson.statistic)
                se = 1/np.sqrt(len(x)-3)
                r_ci = np.tanh(z + np.array([-1, 1])*stats.norm.ppf(.975)*se)
                pd.DataFrame({
                    "measure": ["Pearson r", "Spearman rho", "Kendall tau"],
                    "estimate": [pearson.statistic, spearman.statistic, kendall.statistic],
                    "p": [pearson.pvalue, spearman.pvalue, kendall.pvalue]
                }), r_ci
                """
            ),
            code(
                """
                fig, ax = plt.subplots()
                sns.regplot(x=x, y=y, ci=95, ax=ax)
                ax.set(title="Plot before interpreting correlation", xlabel="X", ylabel="Y")
                plt.show()
                """
            ),
            md(
                r"""
                ## 10.2 Regression tests

                In simple linear regression, the slope test $H_0:\beta_1=0$ is equivalent to the Pearson correlation
                test. Regression extends the question to adjustment, nonlinear terms, and interactions. Valid standard
                errors require an appropriate error structure; clustering and time dependence need specialized models.
                """
            ),
            code(
                """
                import statsmodels.api as sm
                X = sm.add_constant(x)
                regression = sm.OLS(y, X).fit()
                display(regression.summary2().tables[1])

                fig, axes = plt.subplots(1, 2, figsize=(12, 4))
                sns.scatterplot(x=regression.fittedvalues, y=regression.resid, ax=axes[0])
                axes[0].axhline(0, color="crimson", linestyle="--")
                axes[0].set(title="Residuals vs fitted", xlabel="Fitted", ylabel="Residual")
                stats.probplot(regression.resid, dist="norm", plot=axes[1])
                axes[1].set_title("Residual Q-Q plot")
                plt.tight_layout(); plt.show()
                """
            ),
            md(
                """
                ## Practice and solution

                **Practice.** A correlation of .60 is observed between ice-cream sales and drownings. What is wrong
                with concluding ice-cream causes drownings?

                <details><summary>Solution</summary>

                Association alone does not identify a causal effect. Temperature/season is a plausible common cause,
                and aggregated time-series data may violate independence. A causal claim needs a defensible design and
                adjustment strategy, not merely a small correlation p-value.
                </details>

                ## Key takeaways

                - Plot the relationship and inspect influential points.
                - Match the coefficient to the data scale and relationship form.
                - Regression adjusts associations under assumptions; it does not automatically remove confounding.
                """
            ),
        ],
    },
    {
        "title": "Nonparametric, Permutation, and Bootstrap Methods",
        "objectives": [
            "Choose rank tests for ordinal or rank-based estimands",
            "Construct a permutation test aligned with the null hypothesis",
            "Use bootstrap confidence intervals while respecting the sampling unit",
            "Recognize exchangeability and resampling limitations",
        ],
        "body": [
            md(
                r"""
                ## 11.1 Three families, three ideas

                - **Rank tests** replace raw values with order information and target rank/distribution contrasts.
                - **Permutation tests** generate a null distribution by shuffling labels in a way justified by the null.
                - **Bootstrap intervals** approximate sampling uncertainty by resampling observational units.

                None of these methods repairs biased sampling, dependence, confounding, or the wrong unit of analysis.
                """
            ),
            code(
                """
                a = rng.lognormal(mean=2.0, sigma=.7, size=32)
                b = rng.lognormal(mean=2.25, sigma=.7, size=29)
                observed_diff = b.mean()-a.mean()

                def mean_difference(x, y, axis=0):
                    return np.mean(y, axis=axis)-np.mean(x, axis=axis)

                perm = stats.permutation_test((a, b), mean_difference,
                                              permutation_type="independent",
                                              alternative="two-sided",
                                              n_resamples=9999, random_state=2026)
                mw = stats.mannwhitneyu(b, a, alternative="two-sided")
                pd.Series({"observed mean difference": observed_diff,
                           "permutation p": perm.pvalue, "Mann-Whitney U": mw.statistic,
                           "Mann-Whitney p": mw.pvalue})
                """
            ),
            code(
                """
                # Bootstrap the mean difference by resampling within each independent group.
                bootstrap_diffs = np.empty(10000)
                for i in range(len(bootstrap_diffs)):
                    a_star = rng.choice(a, size=len(a), replace=True)
                    b_star = rng.choice(b, size=len(b), replace=True)
                    bootstrap_diffs[i] = b_star.mean()-a_star.mean()
                percentile_ci = np.quantile(bootstrap_diffs, [.025, .975])

                fig, ax = plt.subplots()
                ax.hist(bootstrap_diffs, bins=40, edgecolor="white")
                ax.axvline(observed_diff, color="black", label="observed")
                ax.axvline(percentile_ci[0], color="crimson", linestyle="--")
                ax.axvline(percentile_ci[1], color="crimson", linestyle="--", label="95% percentile CI")
                ax.set(title="Bootstrap distribution of the mean difference", xlabel="B - A")
                ax.legend(); plt.show()
                print(f"95% bootstrap percentile CI: [{percentile_ci[0]:.2f}, {percentile_ci[1]:.2f}]")
                """
            ),
            md(
                """
                ## 11.2 Exchangeability is the key permutation assumption

                Under the sharp null in a randomized experiment, treatment labels can be shuffled according to the
                randomization scheme. In observational data, unrestricted shuffling assumes groups are exchangeable.
                Paired data require sign-flips or within-pair swaps; clustered experiments require cluster-level
                permutations.
                """
            ),
            md(
                """
                ## Practice and solution

                **Practice.** You have 10 measurements from each of 20 patients. What should a simple bootstrap resample?

                <details><summary>Solution</summary>

                If patients are the independent sampling units, resample patients (clusters), carrying all their
                measurements together. Resampling 200 rows independently creates pseudo-replication and usually
                understates uncertainty.
                </details>

                ## Key takeaways

                - Resample or permute the true independent unit.
                - Use a statistic that directly represents the estimand.
                - Computational methods still require design assumptions and transparent reporting.
                """
            ),
        ],
    },
    {
        "title": "Multiple Testing, Equivalence, and Evidence Beyond Significance",
        "objectives": [
            "Control family-wise error or false discovery rate for multiple hypotheses",
            "Distinguish confirmatory and exploratory analyses",
            "Use equivalence testing to support a claim of practically negligible difference",
            "Explain how estimation and sensitivity analyses improve binary decisions",
        ],
        "body": [
            md(
                r"""
                ## 12.1 Multiple comparisons

                With $m$ independent tests at level $\alpha$, the chance of at least one false positive is
                $1-(1-\alpha)^m$. Bonferroni and Holm control family-wise error; Benjamini–Hochberg controls the expected
                false discovery proportion under its assumptions. Define the hypothesis family from the decision
                context rather than correcting every p-value ever computed.
                """
            ),
            code(
                """
                from statsmodels.stats.multitest import multipletests

                raw_p = np.array([.0008, .009, .018, .031, .044, .12, .40, .81])
                results = pd.DataFrame({"raw p": raw_p})
                for method, label in [("bonferroni", "Bonferroni"), ("holm", "Holm"), ("fdr_bh", "BH-FDR")]:
                    reject, adjusted, _, _ = multipletests(raw_p, alpha=.05, method=method)
                    results[f"{label} p"] = adjusted
                    results[f"{label} reject"] = reject
                results
                """
            ),
            code(
                """
                m = np.arange(1, 101)
                fwer = 1-(1-.05)**m
                fig, ax = plt.subplots()
                ax.plot(m, fwer)
                ax.axhline(.05, color="crimson", linestyle="--")
                ax.set(xlabel="Number of independent tests", ylabel="Chance of >=1 false positive",
                       title="Unadjusted multiplicity inflates family-wise error")
                plt.show()
                """
            ),
            md(
                r"""
                ## 12.2 Equivalence is not non-significance

                To support that an effect is small enough to be practically negligible, define equivalence bounds
                $[-\Delta, +\Delta]$ before analysis. The two one-sided tests (TOST) procedure rejects effects at or
                beyond both bounds. Equivalently, the $(1-2\alpha)$ confidence interval must lie wholly inside the bounds.
                """
            ),
            code(
                """
                difference, se, df, margin = .12, .11, 118, .40
                t_lower = (difference-(-margin))/se  # test effect > -margin
                t_upper = (difference-margin)/se     # test effect < +margin
                p_lower = stats.t.sf(t_lower, df)
                p_upper = stats.t.cdf(t_upper, df)
                p_tost = max(p_lower, p_upper)
                ci90 = difference + np.array([-1, 1])*stats.t.ppf(.95, df)*se
                pd.Series({"estimate": difference, "equivalence margin": margin,
                           "90% CI low": ci90[0], "90% CI high": ci90[1],
                           "TOST p": p_tost, "equivalent at alpha=.05": p_tost < .05})
                """
            ),
            md(
                """
                ## Practice and solution

                **Practice.** A conventional test gives p=.40. Can you conclude equivalence within ±2 units?

                <details><summary>Solution</summary>

                No. A non-significant difference test only says the data do not clearly exclude zero. Run a planned
                equivalence test with bounds ±2. Equivalence is supported only if the corresponding 90% CI lies entirely
                within those bounds at alpha .05.
                </details>

                ## Key takeaways

                - Multiplicity control must match the hypothesis family and error criterion.
                - Exploratory findings should be labeled and independently validated.
                - Equivalence testing turns "close enough" into a precise, testable claim.
                """
            ),
        ],
    },
    {
        "title": "Advanced Designs: Clustering and Time-to-Event Outcomes",
        "objectives": [
            "Recognize pseudo-replication caused by clustered observations",
            "Fit and interpret a random-intercept mixed model",
            "Explain censoring and compare survival curves with a log-rank test",
            "Know when specialist methods are required instead of a basic test",
        ],
        "body": [
            md(
                r"""
                ## 13.1 Clustered and longitudinal data

                Students within schools, visits within patients, and transactions within users are correlated. Treating
                every row as independent makes standard errors too small. Mixed models represent cluster-specific random
                effects; cluster-robust standard errors and generalized estimating equations target other inferential
                perspectives.
                """
            ),
            code(
                """
                import statsmodels.formula.api as smf

                rows = []
                for patient in range(40):
                    random_intercept = rng.normal(0, 3)
                    treatment = patient >= 20
                    for time in range(4):
                        y = 20 + random_intercept + 1.2*time + 2.5*treatment + .8*time*treatment + rng.normal(0, 2)
                        rows.append((patient, time, int(treatment), y))
                longitudinal = pd.DataFrame(rows, columns=["patient", "time", "treatment", "outcome"])
                mixed = smf.mixedlm("outcome ~ time * treatment", longitudinal,
                                    groups=longitudinal["patient"]).fit()
                mixed.summary().tables[1]
                """
            ),
            md(
                r"""
                ## 13.2 Time-to-event data and censoring

                A censored observation contributes information up to its last known event-free time. Comparing only the
                observed times discards censoring information and can be biased. The log-rank test compares observed and
                expected event counts across risk sets under the null of equal survival curves.
                """
            ),
            code(
                """
                def logrank_two_sample(time, event, group):
                    event_times = np.sort(np.unique(time[event == 1]))
                    observed_1 = expected_1 = variance = 0.0
                    for t in event_times:
                        at_risk = time >= t
                        n1 = np.sum(at_risk & (group == 1)); n0 = np.sum(at_risk & (group == 0))
                        d1 = np.sum((time == t) & (event == 1) & (group == 1))
                        d0 = np.sum((time == t) & (event == 1) & (group == 0))
                        n, d = n1+n0, d1+d0
                        if n <= 1:
                            continue
                        observed_1 += d1
                        expected_1 += d*n1/n
                        variance += (n1*n0*d*(n-d))/(n**2*(n-1))
                    chi2 = (observed_1-expected_1)**2/variance
                    return chi2, stats.chi2.sf(chi2, 1)

                n = 160
                group = np.repeat([0, 1], n//2)
                event_time = np.r_[rng.exponential(12, n//2), rng.exponential(18, n//2)]
                censor_time = rng.uniform(6, 24, n)
                observed_time = np.minimum(event_time, censor_time)
                event = (event_time <= censor_time).astype(int)
                lr_chi2, lr_p = logrank_two_sample(observed_time, event, group)
                pd.Series({"events": event.sum(), "censored": n-event.sum(),
                           "log-rank chi-square": lr_chi2, "p": lr_p})
                """
            ),
            code(
                """
                def km_curve(time, event):
                    times = np.sort(np.unique(time[event == 1]))
                    survival = 1.0
                    xs, ys = [0.0], [1.0]
                    for t in times:
                        n_risk = np.sum(time >= t)
                        d = np.sum((time == t) & (event == 1))
                        survival *= (1-d/n_risk)
                        xs.extend([t, t]); ys.extend([ys[-1], survival])
                    return xs, ys

                fig, ax = plt.subplots()
                for g, label in [(0, "Control"), (1, "Treatment")]:
                    xg, yg = km_curve(observed_time[group == g], event[group == g])
                    ax.step(xg, yg, where="post", label=label)
                ax.set(xlabel="Time", ylabel="Estimated survival", ylim=(0, 1.02),
                       title="Kaplan-Meier curves")
                ax.legend(); plt.show()
                """
            ),
            md(
                """
                ## Practice and solution

                **Practice.** A trial randomizes 20 clinics, then measures 50 patients per clinic. Is $n=1000$ for an
                ordinary independent t-test?

                <details><summary>Solution</summary>

                No. Treatment was randomized at the clinic level and patients within clinics are correlated. The design
                has 20 independent clusters. Use a cluster-aware analysis—such as a clinic-level comparison, mixed
                model, GEE, or cluster-randomization method—and plan power using the intraclass correlation.
                </details>

                ## Key takeaways

                - The independent unit is determined by sampling and randomization, not the number of rows.
                - Censoring requires survival methods.
                - Advanced tests should be chosen with domain and design expertise.
                """
            ),
        ],
    },
    {
        "title": "Test Selection and End-to-End Capstone",
        "objectives": [
            "Use outcome type, design, estimand, and assumptions to select a test",
            "Complete a reproducible analysis from question through communication",
            "Audit a result for common validity threats",
            "Write a concise statistical results paragraph",
        ],
        "body": [
            md(
                """
                ## 14.1 Decision sequence

                1. **Question:** What decision will the analysis support?
                2. **Estimand:** Mean difference, risk difference, odds ratio, rank contrast, correlation, or survival contrast?
                3. **Outcome:** Quantitative, ordinal, categorical, count, or time-to-event?
                4. **Design:** One sample, independent groups, paired/repeated, clustered, randomized, or observational?
                5. **Diagnostics:** Independence, shape/outliers, variance pattern, expected counts, censoring mechanism?
                6. **Inference:** Estimate + CI + effect size + test, with multiplicity handling.
                7. **Communication:** Practical meaning, uncertainty, limitations, and next action.
                """
            ),
            md(
                """
                ## 14.2 Capstone scenario

                A product team randomized users to a redesigned checkout. The primary outcome is checkout time among
                users who began checkout; conversion is a pre-specified secondary outcome. We will analyze both, control
                the secondary claim using Holm adjustment, and distinguish the conditional time estimand from the
                all-randomized-user conversion estimand.
                """
            ),
            code(
                """
                n_control, n_treatment = 600, 610
                conv_control = rng.binomial(1, .58, n_control)
                conv_treatment = rng.binomial(1, .63, n_treatment)
                time_control = rng.lognormal(4.15, .35, conv_control.sum())
                time_treatment = rng.lognormal(4.02, .37, conv_treatment.sum())

                # Primary: mean time among converters, using Welch plus bootstrap CI due skew.
                time_test = stats.ttest_ind(time_treatment, time_control, equal_var=False)
                observed_time_diff = time_treatment.mean()-time_control.mean()
                boot = np.empty(5000)
                for i in range(len(boot)):
                    boot[i] = (rng.choice(time_treatment, len(time_treatment), replace=True).mean()
                               - rng.choice(time_control, len(time_control), replace=True).mean())
                time_ci = np.quantile(boot, [.025, .975])

                # Secondary: independent proportions.
                from statsmodels.stats.proportion import proportions_ztest
                successes = np.array([conv_treatment.sum(), conv_control.sum()])
                totals = np.array([n_treatment, n_control])
                z, conversion_p = proportions_ztest(successes, totals)
                raw_ps = [time_test.pvalue, conversion_p]
                from statsmodels.stats.multitest import multipletests
                holm_ps = multipletests(raw_ps, method="holm")[1]

                capstone = pd.DataFrame({
                    "outcome": ["Checkout time among converters", "Conversion among randomized users"],
                    "estimate": [observed_time_diff, successes[0]/totals[0]-successes[1]/totals[1]],
                    "raw p": raw_ps,
                    "Holm p": holm_ps,
                    "units": ["seconds (treatment-control)", "proportion points (treatment-control)"]
                })
                capstone
                """
            ),
            code(
                """
                fig, axes = plt.subplots(1, 2, figsize=(12, 4))
                sns.histplot(time_control, color="steelblue", alpha=.45, label="Control", ax=axes[0])
                sns.histplot(time_treatment, color="darkorange", alpha=.45, label="Treatment", ax=axes[0])
                axes[0].set(title="Checkout times among converters", xlabel="Seconds")
                axes[0].legend()
                rates = [conv_control.mean(), conv_treatment.mean()]
                axes[1].bar(["Control", "Treatment"], rates, color=["steelblue", "darkorange"])
                axes[1].set(title="Conversion rates", ylabel="Proportion", ylim=(0, .75))
                plt.tight_layout(); plt.show()
                print(f"Time difference 95% bootstrap CI: [{time_ci[0]:.2f}, {time_ci[1]:.2f}] seconds")
                """
            ),
            md(
                """
                ## 14.3 Reporting template

                > In the randomized experiment, the redesign changed mean checkout time among converters by **[estimate]**
                > seconds (95% CI **[low, high]**; Welch **t(df)=...**, Holm-adjusted **p=...**). Conversion among all
                > randomized users changed by **[absolute percentage points]** (adjusted **p=...**). These estimands answer
                > different questions: time is conditional on conversion, whereas conversion follows assignment. Results
                > should be weighed against the pre-specified minimum useful effects and guardrail metrics.
                """
            ),
            md(
                """
                ## Practice and solution

                **Practice.** List three threats that remain even if both adjusted p-values are below .05.

                <details><summary>Solution</summary>

                Examples: sample-ratio mismatch or logging errors; interference or repeated users; noncompliance with the
                stopping rule; missing outcomes; novelty or seasonality; the conditional time analysis being affected by
                treatment-induced selection; effects too small to matter; or unreported segment/metric searches.
                </details>

                ## Key takeaways

                - Test selection is a design-and-estimand problem.
                - A complete analysis makes uncertainty and practical thresholds visible.
                - Reproducibility includes code, data lineage, pre-specification, and an honest limitations section.
                """
            ),
        ],
    },
    {
        "title": "Course Review and Statistical Reporting",
        "objectives": [
            "Navigate the complete hypothesis-test selection map",
            "Recognize recurring interpretation and reporting mistakes",
            "Use a minimum reporting standard for any test family",
            "Plan next steps for more advanced inference",
        ],
        "body": [
            md(
                """
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
                """
            ),
            md(
                """
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
                """
            ),
            code(
                """
                def recommend_test(outcome, groups=1, paired=False, expected_sparse=False):
                    # A teaching aid—not a substitute for design expertise.
                    if outcome == "time-to-event":
                        return "Log-rank for unadjusted curves; Cox model for covariate adjustment"
                    if outcome == "categorical":
                        if paired:
                            return "McNemar (2 conditions) or Cochran Q (3+ conditions)"
                        if groups == 1:
                            return "Chi-square goodness-of-fit or exact multinomial/binomial method"
                        return "Fisher exact" if expected_sparse else "Chi-square independence / proportion test"
                    if outcome in {"continuous", "ordinal"}:
                        if groups == 1:
                            return "One-sample t; signed-rank/permutation when the estimand supports it"
                        if groups == 2:
                            return "Paired t / signed-rank" if paired else "Welch t / Mann-Whitney"
                        return "RM-ANOVA/mixed model/Friedman" if paired else "ANOVA/Welch ANOVA/Kruskal-Wallis"
                    return "Clarify the outcome, estimand, and dependence structure"

                scenarios = [
                    ("continuous", 2, False, False),
                    ("continuous", 3, True, False),
                    ("categorical", 2, False, True),
                    ("categorical", 2, True, False),
                    ("time-to-event", 2, False, False),
                ]
                pd.DataFrame([
                    {"outcome": o, "groups": g, "paired": p, "sparse": s,
                     "starting point": recommend_test(o, g, p, s)}
                    for o, g, p, s in scenarios
                ])
                """
            ),
            md(
                """
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
                """
            ),
            md(
                """
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
                """
            ),
        ],
    },
]


LEVELS = [
    {
        "folder": "level_1_foundations",
        "title": "Level 1 — Foundations",
        "lessons": range(1, 6),
        "description": "Learn the logic of testing and handle the most common one- and two-sample designs.",
    },
    {
        "folder": "level_2_applied_testing",
        "title": "Level 2 — Applied Testing",
        "lessons": range(6, 11),
        "description": "Analyze multi-group, factorial, categorical, experimental, correlation, and regression questions.",
    },
    {
        "folder": "level_3_advanced_practice",
        "title": "Level 3 — Advanced Practice",
        "lessons": range(11, 16),
        "description": "Use resampling, multiplicity, equivalence, clustered and survival methods, then complete a capstone.",
    },
]


def level_for_lesson(number: int) -> dict:
    for level in LEVELS:
        if number in level["lessons"]:
            return level
    raise ValueError(f"No level configured for lesson {number}")


def build_notebooks():
    for i, spec in enumerate(LESSONS, 1):
        level_dir = ROOT / level_for_lesson(i)["folder"]
        level_dir.mkdir(parents=True, exist_ok=True)
        filename = f"lesson_{i:02d}_{slugify(spec['title'])}.ipynb"
        nb = lesson(i, spec["title"], spec["objectives"], spec["body"])
        nbf.write(nb, level_dir / filename)


def lesson_rows(numbers, *, from_level: bool = False) -> str:
    rows = []
    for i in numbers:
        spec = LESSONS[i - 1]
        slug = slugify(spec["title"])
        filename = f"lesson_{i:02d}_{slug}"
        prefix = "" if from_level else f"{level_for_lesson(i)['folder']}/"
        rows.append(f"| {i:02d} | [{spec['title']}]({prefix}{filename}.ipynb) | [Lesson]({prefix}markdown/{filename}.md) |")
    return "\n".join(rows)


def build_docs():
    level_sections = []
    for level in LEVELS:
        level_sections.append(
            f"### [{level['title']}]({level['folder']}/readme.md)\n\n"
            f"{level['description']}\n\n"
            "| # | Supporting notebook | Authoritative lesson |\n|---:|---|---|\n"
            f"{lesson_rows(level['lessons'])}\n"
        )
    readme = f"""# hypothesis_testing_and_statistical_inference

A complete, executable Python course on choosing, running, interpreting, and reporting hypothesis tests.
The course is split into three progressive levels so learners can stop at the depth they need. The Markdown lessons
are authoritative; Jupyter notebooks are supporting executable examples.

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

{(chr(10) * 2).join(level_sections)}

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
jupyter notebook
```

Read the Markdown lessons in order. Open the supporting notebooks when you want to run or modify an example.
All examples are deterministic and use generated data, so no download is required.

## Recommended path

- Start with **Level 1** for essential hypothesis-testing literacy.
- Continue to **Level 2** for routine professional analysis.
- Add **Level 3** only when you need modern or advanced methods and an end-to-end capstone.

## Repository map

- `level_1_foundations/` — five essential introductory lessons.
- `level_2_applied_testing/` — five lessons for everyday applied analysis.
- `level_3_advanced_practice/` — five advanced and synthesis lessons.
- Each level contains supporting notebooks, a short README, and an authoritative `markdown/` course folder.
- `docs/` — syllabus, learner references, and maintenance records.
- `requirements.txt` — Python dependencies.
- `tools/build_course.py` — reproducible course generator.
- `tools/validate_course.py` — structural and execution validation.

## Relationship to the local statistics courses

This course follows the lesson-oriented structure used by the neighboring probability, discrete-data, and
time-series courses: numbered notebooks, learning objectives, plain-English explanations, runnable Python,
visualizations, practice with solutions, and summaries. It adds a consistent inferential workflow, modern APIs,
effect sizes, confidence intervals, power, multiplicity, equivalence, resampling, clustered data, and survival analysis.
"""
    (ROOT / "readme.md").write_text(readme, encoding="utf-8")

    for level in LEVELS:
        level_readme = f"""# {level['title']}

{level['description']}

Complete these five lessons in order. Read the authoritative Markdown lesson first; open the notebook for interactive examples.

| # | Supporting notebook | Authoritative lesson |
|---:|---|---|
{lesson_rows(level['lessons'], from_level=True)}

[Back to the course overview](../readme.md)
"""
        level_dir = ROOT / level["folder"]
        level_dir.mkdir(parents=True, exist_ok=True)
        (level_dir / "readme.md").write_text(level_readme, encoding="utf-8")

    syllabus = """# Syllabus

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
"""
    (ROOT / "docs" / "syllabus.md").write_text(syllabus, encoding="utf-8")

    guide = """# Hypothesis Test Selection Guide

Use this as a starting point. The correct method is determined by the estimand, sampling/randomization unit,
dependence structure, and assumptions—not merely by the data type.

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
"""
    (ROOT / "docs" / "test_selection_guide.md").write_text(guide, encoding="utf-8")

    glossary = """# Glossary

**Alpha ($\\alpha$)** — Planned long-run Type I error rate for a testing procedure.  
**Alternative hypothesis ($H_1$)** — Parameter values or models contrasted with the null.  
**Confidence interval** — Values compatible with the data and procedure at a stated confidence level.  
**Censoring** — Event time is only partially observed, common in survival analysis.  
**Effect size** — Magnitude of an effect in natural or standardized units.  
**Estimand** — Precisely defined quantity the analysis seeks to estimate.  
**Exchangeability** — Condition allowing observations or labels to be permuted under a null model.  
**False discovery rate** — Expected proportion of false rejections among rejected hypotheses.  
**Family-wise error rate** — Probability of at least one false rejection in a hypothesis family.  
**Independence** — One observational unit does not provide repeated/correlated information with another.  
**Minimum detectable effect** — Effect size a design is powered to detect at chosen alpha and power.  
**Null hypothesis ($H_0$)** — Reference model or parameter value used to calculate the test statistic's null distribution.  
**p-value** — Under $H_0$ and assumptions, probability of a statistic at least as incompatible with $H_0$ as observed.  
**Power** — Probability a procedure rejects $H_0$ for a specified true alternative.  
**Practical significance** — Whether an effect is large enough to matter for the decision.  
**Pre-registration** — Time-stamped specification of hypotheses and analysis choices before outcomes are examined.  
**Pseudo-replication** — Treating correlated rows as independent replicates.  
**Standard error** — Estimated sampling variability of an estimator.  
**Type I error** — Rejecting a true null within the model and procedure.  
**Type II error** — Failing to reject for a specified meaningful alternative.  
"""
    (ROOT / "docs" / "glossary.md").write_text(glossary, encoding="utf-8")

    requirements = """jupyter>=1.0
nbformat>=5.9
nbconvert>=7.10
numpy>=1.24
pandas>=2.0
scipy>=1.11
statsmodels>=0.14
matplotlib>=3.7
matplotlib-inline>=0.1
seaborn>=0.13
mistune>=3.0
pygments>=2.16
beautifulsoup4>=4.12
"""
    (ROOT / "requirements.txt").write_text(requirements, encoding="utf-8")


def refresh_real_data_course():
    commands = [
        [sys.executable, "tools/build_course_data.py"],
        [sys.executable, "tools/apply_course_data.py"],
        [sys.executable, "tools/validate_course.py", "--execute"],
        [sys.executable, "tools/sync_markdown_from_notebooks.py"],
        [sys.executable, "tools/validate_course.py"],
        [sys.executable, "tools/validate_markdown_course.py"],
        [sys.executable, "tools/audit_markdown_notebooks.py"],
        [sys.executable, "tools/build_teaching_html.py"],
        [sys.executable, "tools/validate_teaching_html.py"],
        [sys.executable, "tools/validate_math.py"],
    ]
    for command in commands:
        subprocess.run(command, cwd=ROOT, check=True)


if __name__ == "__main__":
    refresh_real_data_course()
    print(f"Refreshed the real-data course in {ROOT}")
