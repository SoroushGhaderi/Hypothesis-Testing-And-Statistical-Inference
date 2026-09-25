#!/usr/bin/env python3
"""Create the small, local, real-data bundle used by every course notebook."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import statsmodels.api as sm


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def build_anes():
    frame = sm.datasets.anes96.load_pandas().data.copy()
    frame = frame.rename(
        columns={
            "popul": "place_population_thousands",
            "TVnews": "tv_news_days_per_week",
            "PID": "party_id_code",
            "age": "age_years",
            "educ": "education_code",
            "income": "income_code",
            "vote": "expected_vote_code",
            "selfLR": "self_left_right",
            "ClinLR": "clinton_left_right",
            "DoleLR": "dole_left_right",
            "logpopul": "log_place_population",
        }
    )
    frame["party_group"] = pd.cut(
        frame["party_id_code"], [-0.1, 2.5, 3.5, 6.1],
        labels=["Democrat", "Independent", "Republican"],
    )
    frame["expected_vote"] = frame["expected_vote_code"].map({0.0: "Clinton", 1.0: "Dole"})
    frame["age_group"] = pd.cut(
        frame["age_years"], [0, 39, 59, 200], labels=["Under 40", "40-59", "60+"]
    )
    frame.to_csv(DATA / "anes96_clean.csv", index=False)


def build_rand_hie():
    frame = sm.datasets.randhie.load_pandas().data.copy()
    frame = frame.rename(
        columns={
            "mdvis": "physician_visits",
            "lncoins": "log_coinsurance_plus_1",
            "idp": "individual_deductible_plan",
            "lpi": "log_participation_incentive",
            "fmde": "family_max_deductible_log",
            "physlm": "physical_limitation",
            "disea": "chronic_disease_index",
            "hlthg": "health_good",
            "hlthf": "health_fair",
            "hlthp": "health_poor",
        }
    )
    frame["plan_group"] = frame["individual_deductible_plan"].map(
        {0: "Other plan", 1: "Individual deductible"}
    )
    frame["any_physician_visit"] = (frame["physician_visits"] > 0).astype(int)
    # A small, balanced teaching sample retains real rows while keeping lessons fast and readable.
    sample = (
        frame.groupby("plan_group", group_keys=False)
        .sample(n=400, random_state=20260920)
        .sort_values(["plan_group", "physician_visits"])
        .reset_index(drop=True)
    )
    sample.to_csv(DATA / "rand_hie_teaching_sample.csv", index=False)


def build_grunfeld():
    frame = sm.datasets.grunfeld.load_pandas().data.copy().rename(
        columns={"invest": "investment", "value": "market_value", "capital": "capital_stock"}
    )
    frame["year"] = frame["year"].astype(int)
    frame.to_csv(DATA / "grunfeld_investment.csv", index=False)


def build_heart():
    frame = sm.datasets.heart.load_pandas().data.copy().rename(
        columns={"survival": "survival_days", "censors": "event_observed", "age": "age_years"}
    )
    frame["event_observed"] = frame["event_observed"].astype(int)
    frame["age_group"] = pd.cut(
        frame["age_years"], [0, 47.999, 200], labels=["Under 48", "48 or older"]
    )
    frame.to_csv(DATA / "heart_transplant_survival.csv", index=False)


def build_spector():
    frame = sm.datasets.spector.load_pandas().data.copy().rename(
        columns={"GPA": "grade_point_average", "TUCE": "economics_test_score",
                 "PSI": "program_participation", "GRADE": "grade_improved"}
    )
    frame["program_group"] = frame["program_participation"].map({0.0: "No PSI", 1.0: "PSI"})
    frame[["program_participation", "grade_improved"]] = frame[
        ["program_participation", "grade_improved"]
    ].astype(int)
    frame.to_csv(DATA / "spector_program.csv", index=False)


def write_readme():
    text = """# Course Data Bundle

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
"""
    (DATA / "readme.md").write_text(text, encoding="utf-8")


def main():
    DATA.mkdir(parents=True, exist_ok=True)
    build_anes()
    build_rand_hie()
    build_grunfeld()
    build_heart()
    build_spector()
    write_readme()
    print(f"Wrote course data bundle to {DATA}")


if __name__ == "__main__":
    main()
