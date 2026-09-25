#!/usr/bin/env python3
"""Replace invented notebook samples with the local real-data course bundle."""

from __future__ import annotations

import re
from pathlib import Path

import nbformat


ROOT = Path(__file__).resolve().parents[1]


SETUP = '''from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("module://matplotlib_inline.backend_inline")
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Work whether the kernel starts in the course root or a level folder.
working_dir = Path.cwd()
COURSE_ROOT = working_dir if (working_dir / "data").exists() else working_dir.parent
DATA_DIR = COURSE_ROOT / "data"

rng = np.random.default_rng(20260920)
sns.set_theme(style="whitegrid", context="notebook")
plt.rcParams["figure.figsize"] = (10, 5)
pd.set_option("display.precision", 4)
'''


CODE = {
    1: {
        6: '''# Use real ANES ages and expected-vote labels to build a permutation null.
anes = pd.read_csv(DATA_DIR / "anes96_clean.csv")
ages = anes["age_years"].to_numpy()
vote = anes["expected_vote"].to_numpy()
n_dole = np.sum(vote == "Dole")

p_values = []
for _ in range(2000):
    shuffled = rng.permutation(vote)
    dole_age = ages[shuffled == "Dole"]
    clinton_age = ages[shuffled == "Clinton"]
    p_values.append(stats.ttest_ind(dole_age, clinton_age, equal_var=False).pvalue)

p_values = np.asarray(p_values)
print(f"Permutation-null rejection rate at alpha=.05: {(p_values < .05).mean():.3f}")

fig, ax = plt.subplots()
ax.hist(p_values, bins=20, edgecolor="white")
ax.axvline(.05, color="crimson", linestyle="--", label="alpha = .05")
ax.set(xlabel="p-value", ylabel="Permutation samples",
       title="P-values after breaking the age–vote relationship")
ax.legend()
plt.show()
''',
        8: '''# One-sample example using respondents' real ages.
sample = anes["age_years"].dropna().to_numpy()
null_mean = 45
result = stats.ttest_1samp(sample, popmean=null_mean)
estimate = sample.mean()
se = sample.std(ddof=1) / np.sqrt(len(sample))
ci = stats.t.interval(.95, df=len(sample)-1, loc=estimate, scale=se)
d = (estimate-null_mean) / sample.std(ddof=1)

pd.Series({"sample mean age": estimate, "mean difference from 45": estimate-null_mean,
           "95% CI low": ci[0], "95% CI high": ci[1], "t": result.statistic,
           "p": result.pvalue, "Cohen d": d, "n": len(sample)})
''',
    },
    2: {
        5: '''# Empirical power simulation based on the real ANES age distribution.
anes = pd.read_csv(DATA_DIR / "anes96_clean.csv")
age_pool = anes["age_years"].dropna().to_numpy()
age_sd = age_pool.std(ddof=1)

def empirical_power(effect, n, alpha=.05, repetitions=1500):
    """Resample real ages and add a planned standardized shift to one group."""
    rejections = 0
    for _ in range(repetitions):
        control = rng.choice(age_pool, size=n, replace=True)
        treatment = rng.choice(age_pool, size=n, replace=True) + effect*age_sd
        p = stats.ttest_ind(control, treatment, equal_var=False).pvalue
        rejections += p < alpha
    return rejections/repetitions

rows = []
for effect in [0.0, 0.2, 0.5, 0.8]:
    for n in [10, 20, 40, 80]:
        rows.append({"standardized effect": effect, "n per group": n,
                     "rejection rate": empirical_power(effect, n)})
power_table = pd.DataFrame(rows)
power_table.pivot(index="n per group", columns="standardized effect", values="rejection rate")
''',
        6: '''fig, ax = plt.subplots()
for effect, group in power_table.groupby("standardized effect"):
    ax.plot(group["n per group"], group["rejection rate"], marker="o", label=f"d={effect}")
ax.axhline(.80, color="black", linestyle="--", alpha=.7, label="80% target")
ax.set(xlabel="Sample size per group", ylabel="Estimated power",
       ylim=(0, 1), title="Power from resampled ANES ages")
ax.legend()
plt.show()
''',
        8: '''from statsmodels.stats.power import TTestIndPower

# Use the observed age contrast only as a transparent planning illustration.
dole = anes.loc[anes["expected_vote"] == "Dole", "age_years"].to_numpy()
clinton = anes.loc[anes["expected_vote"] == "Clinton", "age_years"].to_numpy()
pooled_sd = np.sqrt(((len(dole)-1)*dole.var(ddof=1) + (len(clinton)-1)*clinton.var(ddof=1)) /
                    (len(dole)+len(clinton)-2))
observed_d = abs((dole.mean()-clinton.mean())/pooled_sd)

analysis = TTestIndPower()
required = analysis.solve_power(effect_size=observed_d, alpha=.05, power=.80, ratio=1)
achieved = analysis.power(effect_size=observed_d, nobs1=np.ceil(required), alpha=.05, ratio=1)
print(f"Observed ANES age effect size: d={observed_d:.3f}")
print(f"Illustrative required n per group: {np.ceil(required):.0f}")
print(f"Achieved power after rounding: {achieved:.3f}")
''',
    },
    3: {
        5: '''anes = pd.read_csv(DATA_DIR / "anes96_clean.csv")
respondent_age = anes["age_years"].dropna().to_numpy()
target = 45
test = stats.ttest_1samp(respondent_age, popmean=target)
n = len(respondent_age)
mean = respondent_age.mean()
sd = respondent_age.std(ddof=1)
ci = stats.t.interval(.95, n-1, loc=mean, scale=sd/np.sqrt(n))
d = (mean-target)/sd
pd.Series({"n": n, "mean age": mean, "SD": sd, "t": test.statistic,
           "df": n-1, "p": test.pvalue, "Cohen d": d,
           "CI low": ci[0], "CI high": ci[1]})
''',
        6: '''fig, axes = plt.subplots(1, 2, figsize=(11, 4))
sns.boxplot(y=respondent_age, ax=axes[0])
sns.stripplot(y=respondent_age, color="black", alpha=.25, ax=axes[0])
axes[0].axhline(target, color="crimson", linestyle="--", label="benchmark = 45")
axes[0].set(title="ANES respondent ages", ylabel="Age (years)")
axes[0].legend()
stats.probplot(respondent_age, dist="norm", plot=axes[1])
axes[1].set_title("Normal Q-Q plot")
plt.tight_layout(); plt.show()
''',
        8: '''spector = pd.read_csv(DATA_DIR / "spector_program.csv")
successes = int(spector["grade_improved"].sum())
trials = len(spector)
p0 = .50
exact = stats.binomtest(successes, trials, p=p0, alternative="two-sided")
ci = exact.proportion_ci(confidence_level=.95, method="wilson")
p_hat = successes/trials
cohen_h = 2*(np.arcsin(np.sqrt(p_hat))-np.arcsin(np.sqrt(p0)))
pd.Series({"students whose grade improved": successes, "n": trials, "p-hat": p_hat,
           "exact p": exact.pvalue, "Cohen h": cohen_h,
           "Wilson low": ci.low, "Wilson high": ci.high})
''',
    },
    4: {
        5: '''anes = pd.read_csv(DATA_DIR / "anes96_clean.csv")
clinton = anes.loc[anes["expected_vote"] == "Clinton", "age_years"].to_numpy()
dole = anes.loc[anes["expected_vote"] == "Dole", "age_years"].to_numpy()

welch = stats.ttest_ind(dole, clinton, equal_var=False)
n1, n2 = len(dole), len(clinton)
m1, m2 = dole.mean(), clinton.mean()
v1, v2 = dole.var(ddof=1), clinton.var(ddof=1)
se = np.sqrt(v1/n1 + v2/n2)
df = (v1/n1 + v2/n2)**2 / ((v1/n1)**2/(n1-1) + (v2/n2)**2/(n2-1))
diff = m1-m2
ci = diff + np.array([-1, 1])*stats.t.ppf(.975, df)*se
pooled_sd = np.sqrt(((n1-1)*v1+(n2-1)*v2)/(n1+n2-2))
d = diff/pooled_sd
hedges_g = (1-3/(4*(n1+n2)-9))*d

pd.Series({"Dole mean age": m1, "Clinton mean age": m2, "difference": diff,
           "95% CI low": ci[0], "95% CI high": ci[1], "Welch t": welch.statistic,
           "df": df, "p": welch.pvalue, "Hedges g": hedges_g})
''',
        6: '''tidy = anes[["age_years", "expected_vote"]].rename(
    columns={"age_years": "age", "expected_vote": "group"})
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
sns.violinplot(data=tidy, x="group", y="age", inner=None, ax=axes[0])
sns.stripplot(data=tidy, x="group", y="age", color="black", alpha=.2, ax=axes[0])
axes[0].set_title("ANES age distributions by expected vote")
stats.probplot(clinton, dist="norm", plot=axes[1])
axes[1].set_title("Q-Q diagnostic: Clinton group")
plt.tight_layout(); plt.show()
''',
        7: '''mw = stats.mannwhitneyu(dole, clinton, alternative="two-sided")
rank_biserial = 2*mw.statistic/(n1*n2)-1
pd.Series({"U": mw.statistic, "p": mw.pvalue,
           "rank-biserial correlation (Dole-Clinton)": rank_biserial,
           "Dole median age": np.median(dole),
           "Clinton median age": np.median(clinton)})
''',
    },
    5: {
        5: '''grunfeld = pd.read_csv(DATA_DIR / "grunfeld_investment.csv")
paired = grunfeld.pivot(index="firm", columns="year", values="investment")[[1935, 1954]].dropna()
before_raw = paired[1935].to_numpy()
after_raw = paired[1954].to_numpy()
before = np.log1p(before_raw)
after = np.log1p(after_raw)
change = after-before

paired_test = stats.ttest_rel(after, before)
n = len(change)
mean_change = change.mean()
se = change.std(ddof=1)/np.sqrt(n)
ci = stats.t.interval(.95, n-1, loc=mean_change, scale=se)
dz = mean_change/change.std(ddof=1)
pd.Series({"firms": n, "mean log-investment change": mean_change,
           "CI low": ci[0], "CI high": ci[1], "t": paired_test.statistic,
           "df": n-1, "p": paired_test.pvalue, "Cohen dz": dz})
''',
        6: '''fig, axes = plt.subplots(1, 2, figsize=(12, 4))
for firm, row in paired.iterrows():
    axes[0].plot([1935, 1954], np.log1p(row.values), marker="o", alpha=.65)
axes[0].set(xticks=[1935, 1954], ylabel="log(1 + investment)",
            title="Paired investment by firm")
sns.histplot(change, kde=True, ax=axes[1])
axes[1].axvline(0, color="crimson", linestyle="--")
axes[1].set(title="Within-firm log changes", xlabel="1954 - 1935")
plt.tight_layout(); plt.show()
''',
        8: '''wilcoxon = stats.wilcoxon(after, before, alternative="two-sided")
from statsmodels.stats.contingency_tables import mcnemar

# A simple paired binary teaching outcome: investment at least 25 (1947 dollars).
threshold = 25
high_1935 = before_raw >= threshold
high_1954 = after_raw >= threshold
paired_binary = pd.crosstab(high_1935, high_1954).reindex(
    index=[False, True], columns=[False, True], fill_value=0).to_numpy()
mc = mcnemar(paired_binary, exact=True)
b, c = paired_binary[0, 1], paired_binary[1, 0]
discordant_or = b/c if c else np.inf
display(pd.DataFrame(paired_binary, index=["1935 below", "1935 at/above"],
                     columns=["1954 below", "1954 at/above"]))
pd.DataFrame({"test": ["Wilcoxon signed-rank", "Exact McNemar"],
              "statistic": [wilcoxon.statistic, mc.statistic],
              "p": [wilcoxon.pvalue, mc.pvalue],
              "effect/note": ["paired log-investment shift", f"discordant OR={discordant_or}"]})
''',
    },
    6: {
        5: '''anes = pd.read_csv(DATA_DIR / "anes96_clean.csv")
df = anes[["party_group", "age_years"]].dropna().rename(
    columns={"party_group": "group", "age_years": "score"})
groups = {name: part["score"].to_numpy() for name, part in df.groupby("group", observed=True)}

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
''',
        6: '''from statsmodels.stats.multicomp import pairwise_tukeyhsd
tukey = pairwise_tukeyhsd(df["score"], df["group"], alpha=.05)
print(tukey)

fig, ax = plt.subplots()
sns.boxplot(data=df, x="group", y="score", ax=ax)
sns.stripplot(data=df, x="group", y="score", color="black", alpha=.2, ax=ax)
ax.set(title="ANES age by party-identification group", ylabel="Age (years)")
plt.show()
''',
        8: '''from statsmodels.stats.oneway import anova_oneway
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
''',
    },
    7: {
        5: '''anes = pd.read_csv(DATA_DIR / "anes96_clean.csv")
factorial = anes[["income_code", "party_group", "age_group"]].dropna()

from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm
fit = ols("income_code ~ C(party_group) * C(age_group)", data=factorial).fit()
anova_lm(fit, typ=2)
''',
        6: '''means = factorial.groupby(["party_group", "age_group"], observed=True,
                           as_index=False)["income_code"].mean()
fig, ax = plt.subplots()
sns.pointplot(data=factorial, x="age_group", y="income_code", hue="party_group",
              errorbar=("ci", 95), dodge=.08, ax=ax)
ax.set(title="ANES income-code means by age and party group",
       xlabel="Age group", ylabel="Income category code")
plt.show()
means
''',
        8: '''ancova_df = anes[["expected_vote", "age_years", "tv_news_days_per_week"]].dropna()
slope_check = ols("tv_news_days_per_week ~ age_years * C(expected_vote)", data=ancova_df).fit()
adjusted = ols("tv_news_days_per_week ~ age_years + C(expected_vote)", data=ancova_df).fit()
print("Slope-homogeneity model:")
display(anova_lm(slope_check, typ=2))
print()
print("Adjusted observational model coefficients:")
display(adjusted.summary2().tables[1])
''',
    },
    8: {
        5: '''anes = pd.read_csv(DATA_DIR / "anes96_clean.csv")
table = pd.crosstab(anes["party_group"], anes["expected_vote"])
observed = table.to_numpy()
chi2, p, dof, expected = stats.chi2_contingency(observed, correction=False)
n = observed.sum()
cramer_v = np.sqrt(chi2/(n*(min(observed.shape)-1)))
residuals = (observed-expected)/np.sqrt(expected)
display(table)
print(f"chi-square({dof})={chi2:.3f}, p={p:.4g}, Cramer's V={cramer_v:.3f}")
display(pd.DataFrame(expected, index=table.index, columns=table.columns).round(2))
display(pd.DataFrame(residuals, index=table.index, columns=table.columns).round(2))
''',
        6: '''fig, ax = plt.subplots()
sns.heatmap(pd.DataFrame(residuals, index=table.index, columns=table.columns),
            annot=True, center=0, cmap="coolwarm", ax=ax)
ax.set_title("ANES Pearson residuals: cells driving association")
plt.show()
''',
        8: '''spector = pd.read_csv(DATA_DIR / "spector_program.csv")
sparse_table = pd.crosstab(spector["program_group"], spector["grade_improved"])
sparse = sparse_table.to_numpy()
fisher = stats.fisher_exact(sparse, alternative="two-sided")
from statsmodels.stats.contingency_tables import Table2x2
t22 = Table2x2(sparse)
ci = t22.oddsratio_confint()
display(sparse_table)
pd.Series({"odds ratio": fisher.statistic, "exact p": fisher.pvalue,
           "OR CI low": ci[0], "OR CI high": ci[1]})
''',
    },
    9: {
        5: '''from statsmodels.stats.proportion import proportions_ztest, confint_proportions_2indep

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
''',
        7: '''allocation_check = stats.chisquare(visitors, f_exp=np.repeat(visitors.sum()/2, 2))

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
''',
    },
    10: {
        5: '''anes = pd.read_csv(DATA_DIR / "anes96_clean.csv")
x = anes["age_years"].to_numpy()
y = anes["tv_news_days_per_week"].to_numpy()

pearson = stats.pearsonr(x, y)
spearman = stats.spearmanr(x, y)
kendall = stats.kendalltau(x, y)
z = np.arctanh(pearson.statistic)
se = 1/np.sqrt(len(x)-3)
r_ci = np.tanh(z + np.array([-1, 1])*stats.norm.ppf(.975)*se)
display(pd.DataFrame({"measure": ["Pearson r", "Spearman rho", "Kendall tau"],
                      "estimate": [pearson.statistic, spearman.statistic, kendall.statistic],
                      "p": [pearson.pvalue, spearman.pvalue, kendall.pvalue]}))
print(f"Pearson 95% CI: [{r_ci[0]:.3f}, {r_ci[1]:.3f}]")
''',
        6: '''fig, ax = plt.subplots()
sns.regplot(x=x, y=y, scatter_kws={"alpha": .25}, ci=95, ax=ax)
ax.set(title="ANES age and weekly TV-news viewing", xlabel="Age (years)",
       ylabel="TV-news days per week")
plt.show()
''',
        8: '''import statsmodels.api as sm
X = sm.add_constant(x)
regression = sm.OLS(y, X).fit()
display(regression.summary2().tables[1])

fig, axes = plt.subplots(1, 2, figsize=(12, 4))
sns.scatterplot(x=regression.fittedvalues, y=regression.resid, alpha=.35, ax=axes[0])
axes[0].axhline(0, color="crimson", linestyle="--")
axes[0].set(title="Residuals vs fitted", xlabel="Fitted", ylabel="Residual")
stats.probplot(regression.resid, dist="norm", plot=axes[1])
axes[1].set_title("Residual Q-Q plot")
plt.tight_layout(); plt.show()
''',
    },
    11: {
        5: '''anes = pd.read_csv(DATA_DIR / "anes96_clean.csv")
clinton = anes.loc[anes["expected_vote"] == "Clinton", "income_code"].to_numpy()
dole = anes.loc[anes["expected_vote"] == "Dole", "income_code"].to_numpy()
observed_diff = dole.mean()-clinton.mean()

def mean_difference(x, y, axis=0):
    return np.mean(y, axis=axis)-np.mean(x, axis=axis)

perm = stats.permutation_test((clinton, dole), mean_difference,
                              permutation_type="independent", alternative="two-sided",
                              n_resamples=9999, random_state=20260920)
mw = stats.mannwhitneyu(dole, clinton, alternative="two-sided")
pd.Series({"observed income-code difference (Dole-Clinton)": observed_diff,
           "permutation p": perm.pvalue, "Mann-Whitney U": mw.statistic,
           "Mann-Whitney p": mw.pvalue})
''',
        6: '''bootstrap_diffs = np.empty(10000)
for i in range(len(bootstrap_diffs)):
    clinton_star = rng.choice(clinton, size=len(clinton), replace=True)
    dole_star = rng.choice(dole, size=len(dole), replace=True)
    bootstrap_diffs[i] = dole_star.mean()-clinton_star.mean()
percentile_ci = np.quantile(bootstrap_diffs, [.025, .975])

fig, ax = plt.subplots()
ax.hist(bootstrap_diffs, bins=40, edgecolor="white")
ax.axvline(observed_diff, color="black", label="observed")
ax.axvline(percentile_ci[0], color="crimson", linestyle="--")
ax.axvline(percentile_ci[1], color="crimson", linestyle="--", label="95% percentile CI")
ax.set(title="Bootstrap distribution: ANES income-code difference", xlabel="Dole - Clinton")
ax.legend(); plt.show()
print(f"95% bootstrap percentile CI: [{percentile_ci[0]:.2f}, {percentile_ci[1]:.2f}]")
''',
    },
    12: {
        5: '''from statsmodels.stats.multitest import multipletests

anes = pd.read_csv(DATA_DIR / "anes96_clean.csv")
variables = ["age_years", "tv_news_days_per_week", "education_code", "income_code",
             "self_left_right", "clinton_left_right", "dole_left_right"]
rows = []
for variable in variables:
    clinton = anes.loc[anes["expected_vote"] == "Clinton", variable].dropna()
    dole = anes.loc[anes["expected_vote"] == "Dole", variable].dropna()
    result = stats.ttest_ind(dole, clinton, equal_var=False)
    rows.append({"variable": variable, "Dole-Clinton difference": dole.mean()-clinton.mean(),
                 "raw p": result.pvalue})
results = pd.DataFrame(rows)
for method, label in [("bonferroni", "Bonferroni"), ("holm", "Holm"), ("fdr_bh", "BH-FDR")]:
    reject, adjusted, _, _ = multipletests(results["raw p"], alpha=.05, method=method)
    results[f"{label} p"] = adjusted
    results[f"{label} reject"] = reject
results
''',
        6: '''m = np.arange(1, 101)
fwer = 1-(1-.05)**m
fig, ax = plt.subplots()
ax.plot(m, fwer)
ax.axhline(.05, color="crimson", linestyle="--")
ax.set(xlabel="Number of independent tests", ylabel="Chance of >=1 false positive",
       title="Why the ANES variable family needs multiplicity control")
plt.show()
''',
        8: '''dole_age = anes.loc[anes["expected_vote"] == "Dole", "age_years"].to_numpy()
clinton_age = anes.loc[anes["expected_vote"] == "Clinton", "age_years"].to_numpy()
difference = dole_age.mean()-clinton_age.mean()
v1, v2 = dole_age.var(ddof=1), clinton_age.var(ddof=1)
n1, n2 = len(dole_age), len(clinton_age)
se = np.sqrt(v1/n1+v2/n2)
df = (v1/n1+v2/n2)**2/((v1/n1)**2/(n1-1)+(v2/n2)**2/(n2-1))
margin = 3.0  # years; a teaching equivalence threshold
t_lower = (difference-(-margin))/se
t_upper = (difference-margin)/se
p_lower = stats.t.sf(t_lower, df)
p_upper = stats.t.cdf(t_upper, df)
p_tost = max(p_lower, p_upper)
ci90 = difference + np.array([-1, 1])*stats.t.ppf(.95, df)*se
pd.Series({"age difference (Dole-Clinton)": difference, "equivalence margin": margin,
           "90% CI low": ci90[0], "90% CI high": ci90[1],
           "TOST p": p_tost, "equivalent within +/-3 years": p_tost < .05})
''',
    },
    13: {
        5: '''import statsmodels.formula.api as smf

longitudinal = pd.read_csv(DATA_DIR / "grunfeld_investment.csv")
longitudinal["year_centered"] = longitudinal["year"]-longitudinal["year"].min()
firm_mean_value = longitudinal.groupby("firm")["market_value"].transform("mean")
longitudinal["large_firm"] = (firm_mean_value >= firm_mean_value.median()).astype(int)
longitudinal["log_investment"] = np.log1p(longitudinal["investment"])

mixed = smf.mixedlm("log_investment ~ year_centered * large_firm", longitudinal,
                    groups=longitudinal["firm"]).fit()
mixed.summary().tables[1]
''',
        7: '''def logrank_two_sample(time, event, group):
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

heart = pd.read_csv(DATA_DIR / "heart_transplant_survival.csv")
time = heart["survival_days"].to_numpy()
event = heart["event_observed"].to_numpy()
group = (heart["age_group"] == "48 or older").astype(int).to_numpy()
lr_chi2, lr_p = logrank_two_sample(time, event, group)
pd.Series({"patients": len(heart), "events": event.sum(), "censored": len(heart)-event.sum(),
           "log-rank chi-square": lr_chi2, "p": lr_p})
''',
        8: '''def km_curve(time, event):
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
for label, g in [("Under 48", 0), ("48 or older", 1)]:
    xg, yg = km_curve(time[group == g], event[group == g])
    ax.step(xg, yg, where="post", label=label)
ax.set(xlabel="Days after transplant", ylabel="Estimated survival", ylim=(0, 1.02),
       title="Heart-transplant survival by age group")
ax.legend(); plt.show()
''',
    },
    14: {
        6: '''rand = pd.read_csv(DATA_DIR / "rand_hie_teaching_sample.csv")
other = rand.loc[rand["plan_group"] == "Other plan", "physician_visits"].to_numpy()
deductible = rand.loc[rand["plan_group"] == "Individual deductible", "physician_visits"].to_numpy()

visit_test = stats.ttest_ind(deductible, other, equal_var=False)
observed_visit_diff = deductible.mean()-other.mean()
boot = np.empty(5000)
for i in range(len(boot)):
    boot[i] = (rng.choice(deductible, len(deductible), replace=True).mean()
               - rng.choice(other, len(other), replace=True).mean())
visit_ci = np.quantile(boot, [.025, .975])

from statsmodels.stats.proportion import proportions_ztest
summary = rand.groupby("plan_group")["any_physician_visit"].agg(["sum", "count"])
successes = np.array([summary.loc["Individual deductible", "sum"], summary.loc["Other plan", "sum"]])
totals = np.array([summary.loc["Individual deductible", "count"], summary.loc["Other plan", "count"]])
z, any_visit_p = proportions_ztest(successes, totals)

from statsmodels.stats.multitest import multipletests
raw_ps = [visit_test.pvalue, any_visit_p]
holm_ps = multipletests(raw_ps, method="holm")[1]
capstone = pd.DataFrame({
    "outcome": ["Number of physician visits", "Any physician visit"],
    "estimate": [observed_visit_diff, successes[0]/totals[0]-successes[1]/totals[1]],
    "raw p": raw_ps, "Holm p": holm_ps,
    "units": ["visits (deductible-other)", "proportion points (deductible-other)"]})
capstone
''',
        7: '''fig, axes = plt.subplots(1, 2, figsize=(12, 4))
sns.histplot(other, discrete=True, color="steelblue", alpha=.45, label="Other plan", ax=axes[0])
sns.histplot(deductible, discrete=True, color="darkorange", alpha=.45,
             label="Individual deductible", ax=axes[0])
axes[0].set(title="Physician visits in the RAND teaching sample", xlabel="Visits")
axes[0].legend()
rates = [rand.loc[rand["plan_group"] == name, "any_physician_visit"].mean()
         for name in ["Other plan", "Individual deductible"]]
axes[1].bar(["Other plan", "Deductible"], rates, color=["steelblue", "darkorange"])
axes[1].set(title="Any-visit rates", ylabel="Proportion", ylim=(0, 1))
plt.tight_layout(); plt.show()
print(f"Visit difference 95% bootstrap CI: [{visit_ci[0]:.2f}, {visit_ci[1]:.2f}]")
''',
    },
    15: {
        6: '''def recommend_test(outcome, groups=1, paired=False, expected_sparse=False):
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
''',
    },
}


MARKDOWN_REPLACEMENTS = {
    5: {4: """## 5.1 Pairing changes the unit of analysis

The Grunfeld dataset follows the same 11 firms across years. Comparing each firm's investment in 1935 with its own
investment in 1954 creates a genuine paired design. The paired t-test is a one-sample t-test on within-firm log changes.
Its assumptions concern those changes—not the two marginal year distributions."""},
    7: {
        4: """## 7.1 Factorial designs

The ANES example studies household-income category across age and party-identification groups. This is an observational
factorial analysis: interactions describe association patterns and must not be interpreted as randomized effects.

A two-factor model includes main effects and an interaction:
$$Y=\\beta_0+\\beta_A A+\\beta_B B+\\beta_{AB}(A\\times B)+\\varepsilon.$$
A meaningful interaction says the association with one factor depends on the level of the other.""",
        7: """## 7.2 ANCOVA

The ANES ANCOVA models weekly TV-news viewing by expected vote while adjusting for age. Because ANES is observational,
the adjusted coefficient is an association, not a treatment effect. The group-by-age interaction checks whether a common
age slope is reasonable before fitting the simpler adjusted model.""",
    },
    9: {4: """## 9.1 A/B tests are experiments, not just z-tests

The RAND Health Insurance Experiment teaching sample compares individual-deductible plans with other plans. The binary
outcome is whether a participant recorded any physician visit. This real experiment illustrates the same proportion
workflow used in online A/B testing, while the interpretation remains specific to health-insurance plans."""},
    13: {
        4: """## 13.1 Clustered and longitudinal data

The Grunfeld investment data contain 20 yearly observations for each of 11 firms. Rows from the same firm are correlated,
so treating all 220 rows as independent would understate uncertainty. A random-intercept model represents firm-specific
baselines while estimating change over time.""",
        6: """## 13.2 Time-to-event data and censoring

The heart-transplant dataset records follow-up days, age, and whether death was observed. A censored patient contributes
information up to the last known follow-up time. The log-rank test compares observed and expected events across age-group
risk sets; the age groups are derived for teaching and were not randomized.""",
    },
    14: {
        5: """## 14.2 Capstone scenario

The capstone uses the balanced RAND Health Insurance Experiment teaching sample. The primary outcome is the number of
physician visits; the secondary outcome is whether any visit occurred. We compare individual-deductible and other plans,
bootstrap the mean visit difference, test the binary rate difference, and apply Holm adjustment across the two claims.""",
        8: """## 14.3 Reporting template

> In the RAND teaching sample, the individual-deductible group differed from the other-plan group by **[estimate]**
> physician visits (95% bootstrap CI **[low, high]**; Welch **t(df)=...**, Holm-adjusted **p=...**). The any-visit rate
> differed by **[absolute percentage points]** (adjusted **p=...**). These outcomes answer related but distinct questions.
> Interpretation is limited to the documented teaching subset and should include practical thresholds and uncertainty.""",
        9: """## Practice and solution

**Practice.** List three checks needed before treating this teaching analysis as a complete experiment report.

<details><summary>Solution</summary>

Examples include analyzing the complete RAND sample rather than only the balanced teaching subset; verifying the original
randomization and observation unit; pre-specifying the primary outcome and useful effect; assessing count-model choices,
missingness, and adherence; and documenting whether additional outcomes or subgroups were examined.
</details>

## Key takeaways

- Test selection begins with the design, outcome, and estimand.
- Real data remove arbitrary generated values but do not remove modeling assumptions.
- A complete report includes uncertainty, practical importance, provenance, and limitations.""",
    },
}


def apply():
    notebooks = sorted(ROOT.glob("level_*/*.ipynb"))
    if len(notebooks) != 15:
        raise SystemExit(f"Expected 15 notebooks, found {len(notebooks)}")
    for path in notebooks:
        number = int(re.search(r"lesson_(\d+)_", path.name).group(1))
        nb = nbformat.read(path, as_version=4)
        nb.cells[3].source = SETUP
        for index, source in CODE[number].items():
            if nb.cells[index].cell_type != "code":
                raise ValueError(f"{path.name} cell {index} is not code")
            nb.cells[index].source = source.strip() + "\n"
        for index, source in MARKDOWN_REPLACEMENTS.get(number, {}).items():
            if nb.cells[index].cell_type != "markdown":
                raise ValueError(f"{path.name} cell {index} is not markdown")
            nb.cells[index].source = source.strip() + "\n"
        for cell in nb.cells:
            if cell.cell_type == "code":
                cell.execution_count = None
                cell.outputs = []
        nbformat.write(nb, path)
        print(f"Updated {path.name}")


if __name__ == "__main__":
    apply()
