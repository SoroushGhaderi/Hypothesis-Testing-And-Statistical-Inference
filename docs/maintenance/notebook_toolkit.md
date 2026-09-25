# Notebook Implementation Toolkit

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

- [lesson_01_the_logic_of_hypothesis_testing.ipynb](../../level_1_foundations/lesson_01_the_logic_of_hypothesis_testing.ipynb)
- [lesson_02_sampling_distributions_errors_and_power.ipynb](../../level_1_foundations/lesson_02_sampling_distributions_errors_and_power.ipynb)
- [lesson_03_one_sample_tests_for_means_and_proportions.ipynb](../../level_1_foundations/lesson_03_one_sample_tests_for_means_and_proportions.ipynb)
- [lesson_04_two_independent_groups.ipynb](../../level_1_foundations/lesson_04_two_independent_groups.ipynb)
- [lesson_05_paired_and_repeated_measurements.ipynb](../../level_1_foundations/lesson_05_paired_and_repeated_measurements.ipynb)
- [lesson_06_three_or_more_independent_groups.ipynb](../../level_2_applied_testing/lesson_06_three_or_more_independent_groups.ipynb)
- [lesson_07_factorial_designs_interactions_and_ancova.ipynb](../../level_2_applied_testing/lesson_07_factorial_designs_interactions_and_ancova.ipynb)
- [lesson_08_categorical_data_chi_square_fisher_and_mc_nemar.ipynb](../../level_2_applied_testing/lesson_08_categorical_data_chi_square_fisher_and_mc_nemar.ipynb)
- [lesson_09_proportions_and_a_and_b_tests.ipynb](../../level_2_applied_testing/lesson_09_proportions_and_a_and_b_tests.ipynb)
- [lesson_10_correlation_and_regression_based_tests.ipynb](../../level_2_applied_testing/lesson_10_correlation_and_regression_based_tests.ipynb)
- [lesson_11_nonparametric_permutation_and_bootstrap_methods.ipynb](../../level_3_advanced_practice/lesson_11_nonparametric_permutation_and_bootstrap_methods.ipynb)
- [lesson_12_multiple_testing_equivalence_and_evidence_beyond_significance.ipynb](../../level_3_advanced_practice/lesson_12_multiple_testing_equivalence_and_evidence_beyond_significance.ipynb)
- [lesson_13_advanced_designs_clustering_and_time_to_event_outcomes.ipynb](../../level_3_advanced_practice/lesson_13_advanced_designs_clustering_and_time_to_event_outcomes.ipynb)
- [lesson_14_test_selection_and_end_to_end_capstone.ipynb](../../level_3_advanced_practice/lesson_14_test_selection_and_end_to_end_capstone.ipynb)
- [lesson_15_course_review_and_statistical_reporting.ipynb](../../level_3_advanced_practice/lesson_15_course_review_and_statistical_reporting.ipynb)
