# Course Data Bundle

These local CSV files contain real, compact teaching data distributed with `statsmodels`. They replace the
per-lesson invented samples while keeping every notebook runnable without network access.

No single real table can honestly represent independent groups, paired measurements, panel clustering, a randomized
insurance experiment, and censored survival. The course therefore uses one primary dataset plus four small specialist
datasets whose observation structures match the statistical method.

| File | Rows | Role | Original source |
|---|---:|---|---|
| `anes96_clean.csv` | 944 | Primary cross-sectional dataset for foundations, group comparisons, ANOVA, categorical tests, correlation, regression, resampling, and multiplicity | American National Election Studies 1996 subset; public domain |
| `rand_hie_teaching_sample.csv` | 800 | Balanced real-row subset for experimental proportion and end-to-end examples | RAND Health Insurance Experiment subset; public domain |
| `grunfeld_investment.csv` | 220 | Paired and longitudinal examples: 20 years for 11 firms | Grunfeld investment data; public domain |
| `heart_transplant_survival.csv` | 69 | Censored time-to-event example | Miller (1976), heart-transplant survival data |
| `spector_program.csv` | 32 | Small 2x2 table and exact-test example | Spector and Mazzeo (1980), used with permission in statsmodels |

## Lesson map

| Dataset | Lessons using it |
|---|---|
| ANES 1996 | [1](../level_1_foundations/markdown/lesson_01_the_logic_of_hypothesis_testing.md), [2](../level_1_foundations/markdown/lesson_02_sampling_distributions_errors_and_power.md), [3](../level_1_foundations/markdown/lesson_03_one_sample_tests_for_means_and_proportions.md), [4](../level_1_foundations/markdown/lesson_04_two_independent_groups.md), [6](../level_2_applied_testing/markdown/lesson_06_three_or_more_independent_groups.md), [7](../level_2_applied_testing/markdown/lesson_07_factorial_designs_interactions_and_ancova.md), [8](../level_2_applied_testing/markdown/lesson_08_categorical_data_chi_square_fisher_and_mc_nemar.md), [10](../level_2_applied_testing/markdown/lesson_10_correlation_and_regression_based_tests.md), [11](../level_3_advanced_practice/markdown/lesson_11_nonparametric_permutation_and_bootstrap_methods.md), [12](../level_3_advanced_practice/markdown/lesson_12_multiple_testing_equivalence_and_evidence_beyond_significance.md), and [15](../level_3_advanced_practice/markdown/lesson_15_course_review_and_statistical_reporting.md) |
| RAND HIE | [9](../level_2_applied_testing/markdown/lesson_09_proportions_and_a_and_b_tests.md) and [14](../level_3_advanced_practice/markdown/lesson_14_test_selection_and_end_to_end_capstone.md) |
| Grunfeld | [5](../level_1_foundations/markdown/lesson_05_paired_and_repeated_measurements.md), [13](../level_3_advanced_practice/markdown/lesson_13_advanced_designs_clustering_and_time_to_event_outcomes.md), and [15](../level_3_advanced_practice/markdown/lesson_15_course_review_and_statistical_reporting.md) |
| Heart transplant | [13](../level_3_advanced_practice/markdown/lesson_13_advanced_designs_clustering_and_time_to_event_outcomes.md) and [15](../level_3_advanced_practice/markdown/lesson_15_course_review_and_statistical_reporting.md) |
| Spector | [3](../level_1_foundations/markdown/lesson_03_one_sample_tests_for_means_and_proportions.md), [8](../level_2_applied_testing/markdown/lesson_08_categorical_data_chi_square_fisher_and_mc_nemar.md), and [15](../level_3_advanced_practice/markdown/lesson_15_course_review_and_statistical_reporting.md) |

## Cleaning and derived fields

- Original numeric values are preserved and columns receive learner-friendly snake-case names.
- ANES adds readable `party_group`, `expected_vote`, and `age_group` labels from documented codes.
- RAND HIE adds readable plan labels and `any_physician_visit`; 400 real rows per plan group are selected with a fixed seed.
- Grunfeld changes only column names and stores year as an integer.
- Heart data renames the documented uncensored indicator to `event_observed` and adds a median-based age group.
- Spector adds a readable program label and stores binary fields as integers.

## Important interpretation boundaries

- ANES comparisons are observational associations, not causal effects.
- The RAND teaching file is a balanced subset for fast instruction; effect estimates are not substitutes for a full
  analysis of the complete experiment.
- Grunfeld observations are repeated within firms and must not be treated as independent rows.
- The heart age groups are derived for teaching a two-curve comparison and were not randomized.
- Spector is small; exact methods and wide uncertainty are expected.

## Rebuilding

Run `python tools/build_course_data.py` from anywhere inside the course repository. The script loads the datasets from
the installed `statsmodels` package and rewrites these CSV files deterministically.
