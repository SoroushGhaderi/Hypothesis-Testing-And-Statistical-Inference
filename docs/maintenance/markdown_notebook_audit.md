# Markdown and Notebook Alignment Audit

## Audit scope

This audit checks every executed notebook against its authoritative Markdown lesson. It verifies that analytical code
cells appear verbatim in the lesson, stored notebook figures have matching Markdown assets, real dataset filenames are
visible, and each lesson remains connected to the maintained concept manifest.

## Lesson parity

| Lesson | Supporting notebook | Authoritative Markdown | Real datasets loaded | Code cells matched | Figures notebook/Markdown | Concepts | Status |
|---:|---|---|---|---:|---:|---:|---|
| 1 | [lesson_01_the_logic_of_hypothesis_testing.ipynb](../../level_1_foundations/lesson_01_the_logic_of_hypothesis_testing.ipynb) | [lesson_01_the_logic_of_hypothesis_testing.md](../../level_1_foundations/markdown/lesson_01_the_logic_of_hypothesis_testing.md) | `anes96_clean.csv` | 2/2 | 1/1 | 7 | pass |
| 2 | [lesson_02_sampling_distributions_errors_and_power.ipynb](../../level_1_foundations/lesson_02_sampling_distributions_errors_and_power.ipynb) | [lesson_02_sampling_distributions_errors_and_power.md](../../level_1_foundations/markdown/lesson_02_sampling_distributions_errors_and_power.md) | `anes96_clean.csv` | 3/3 | 1/1 | 7 | pass |
| 3 | [lesson_03_one_sample_tests_for_means_and_proportions.ipynb](../../level_1_foundations/lesson_03_one_sample_tests_for_means_and_proportions.ipynb) | [lesson_03_one_sample_tests_for_means_and_proportions.md](../../level_1_foundations/markdown/lesson_03_one_sample_tests_for_means_and_proportions.md) | `anes96_clean.csv`, `spector_program.csv` | 3/3 | 1/1 | 8 | pass |
| 4 | [lesson_04_two_independent_groups.ipynb](../../level_1_foundations/lesson_04_two_independent_groups.ipynb) | [lesson_04_two_independent_groups.md](../../level_1_foundations/markdown/lesson_04_two_independent_groups.md) | `anes96_clean.csv` | 3/3 | 1/1 | 8 | pass |
| 5 | [lesson_05_paired_and_repeated_measurements.ipynb](../../level_1_foundations/lesson_05_paired_and_repeated_measurements.ipynb) | [lesson_05_paired_and_repeated_measurements.md](../../level_1_foundations/markdown/lesson_05_paired_and_repeated_measurements.md) | `grunfeld_investment.csv` | 3/3 | 1/1 | 8 | pass |
| 6 | [lesson_06_three_or_more_independent_groups.ipynb](../../level_2_applied_testing/lesson_06_three_or_more_independent_groups.ipynb) | [lesson_06_three_or_more_independent_groups.md](../../level_2_applied_testing/markdown/lesson_06_three_or_more_independent_groups.md) | `anes96_clean.csv` | 3/3 | 1/1 | 9 | pass |
| 7 | [lesson_07_factorial_designs_interactions_and_ancova.ipynb](../../level_2_applied_testing/lesson_07_factorial_designs_interactions_and_ancova.ipynb) | [lesson_07_factorial_designs_interactions_and_ancova.md](../../level_2_applied_testing/markdown/lesson_07_factorial_designs_interactions_and_ancova.md) | `anes96_clean.csv` | 3/3 | 1/1 | 9 | pass |
| 8 | [lesson_08_categorical_data_chi_square_fisher_and_mc_nemar.ipynb](../../level_2_applied_testing/lesson_08_categorical_data_chi_square_fisher_and_mc_nemar.ipynb) | [lesson_08_categorical_data_chi_square_fisher_and_mc_nemar.md](../../level_2_applied_testing/markdown/lesson_08_categorical_data_chi_square_fisher_and_mc_nemar.md) | `anes96_clean.csv`, `spector_program.csv` | 3/3 | 1/1 | 9 | pass |
| 9 | [lesson_09_proportions_and_a_and_b_tests.ipynb](../../level_2_applied_testing/lesson_09_proportions_and_a_and_b_tests.ipynb) | [lesson_09_proportions_and_a_and_b_tests.md](../../level_2_applied_testing/markdown/lesson_09_proportions_and_a_and_b_tests.md) | `rand_hie_teaching_sample.csv` | 2/2 | 0/0 | 7 | pass |
| 10 | [lesson_10_correlation_and_regression_based_tests.ipynb](../../level_2_applied_testing/lesson_10_correlation_and_regression_based_tests.ipynb) | [lesson_10_correlation_and_regression_based_tests.md](../../level_2_applied_testing/markdown/lesson_10_correlation_and_regression_based_tests.md) | `anes96_clean.csv` | 3/3 | 2/2 | 9 | pass |
| 11 | [lesson_11_nonparametric_permutation_and_bootstrap_methods.ipynb](../../level_3_advanced_practice/lesson_11_nonparametric_permutation_and_bootstrap_methods.ipynb) | [lesson_11_nonparametric_permutation_and_bootstrap_methods.md](../../level_3_advanced_practice/markdown/lesson_11_nonparametric_permutation_and_bootstrap_methods.md) | `anes96_clean.csv` | 2/2 | 1/1 | 8 | pass |
| 12 | [lesson_12_multiple_testing_equivalence_and_evidence_beyond_significance.ipynb](../../level_3_advanced_practice/lesson_12_multiple_testing_equivalence_and_evidence_beyond_significance.ipynb) | [lesson_12_multiple_testing_equivalence_and_evidence_beyond_significance.md](../../level_3_advanced_practice/markdown/lesson_12_multiple_testing_equivalence_and_evidence_beyond_significance.md) | `anes96_clean.csv` | 3/3 | 1/1 | 8 | pass |
| 13 | [lesson_13_advanced_designs_clustering_and_time_to_event_outcomes.ipynb](../../level_3_advanced_practice/lesson_13_advanced_designs_clustering_and_time_to_event_outcomes.ipynb) | [lesson_13_advanced_designs_clustering_and_time_to_event_outcomes.md](../../level_3_advanced_practice/markdown/lesson_13_advanced_designs_clustering_and_time_to_event_outcomes.md) | `grunfeld_investment.csv`, `heart_transplant_survival.csv` | 3/3 | 1/1 | 8 | pass |
| 14 | [lesson_14_test_selection_and_end_to_end_capstone.ipynb](../../level_3_advanced_practice/lesson_14_test_selection_and_end_to_end_capstone.ipynb) | [lesson_14_test_selection_and_end_to_end_capstone.md](../../level_3_advanced_practice/markdown/lesson_14_test_selection_and_end_to_end_capstone.md) | `rand_hie_teaching_sample.csv` | 2/2 | 1/1 | 8 | pass |
| 15 | [lesson_15_course_review_and_statistical_reporting.ipynb](../../level_3_advanced_practice/lesson_15_course_review_and_statistical_reporting.ipynb) | [lesson_15_course_review_and_statistical_reporting.md](../../level_3_advanced_practice/markdown/lesson_15_course_review_and_statistical_reporting.md) | `anes96_clean.csv`, `grunfeld_investment.csv`, `heart_transplant_survival.csv`, `spector_program.csv` | 1/1 | 0/0 | 6 | pass |

## Supporting Markdown review

| Markdown file | Relationship to notebook work | Status |
|---|---|---|
| [readme.md](../../readme.md) | Course entry point and three-level learning path | pass |
| [syllabus.md](../syllabus.md) | Outcomes, pacing, assessment, and data progression | pass |
| [test_selection_guide.md](../test_selection_guide.md) | Cross-lesson method-selection reference | pass |
| [glossary.md](../glossary.md) | Terminology used by notebooks and lessons | pass |
| [readme.md](../../data/readme.md) | Dataset provenance, cleaning, lesson mapping, and limits | pass |
| [notebook_toolkit.md](notebook_toolkit.md) | Shared notebook setup, data loading, resampling, and warnings | pass |
| [course_coverage_index.md](course_coverage_index.md) | Notebook-to-concept and API traceability | pass |

## Result

All 15 notebooks and their authoritative lessons passed the
parity audit. The detailed statistical coverage remains in the [course coverage index](course_coverage_index.md), and
dataset-specific interpretation boundaries remain in the [data guide](../../data/readme.md).
