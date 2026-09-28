#!/usr/bin/env python3
"""Build the site's static Persian translation table using the local Ollama model."""

from __future__ import annotations

import json
import re
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "course.html"
OUTPUT = ROOT / "tools" / "site_translations.fa.json"
MODEL = "gemma4-local:latest"
BATCH_SIZE = 12
MAX_BATCH_CHARS = 1400

PERSIAN_PROMPT = """این متن‌ها از یک وب‌سایت آموزشی آمار هستند. هر بخش انگلیسیِ قابل ترجمه را کامل، دقیق و روان به فارسی ترجمه کن. همه اصطلاحات تخصصی آماری و نام روش‌ها و آزمون‌ها باید دقیقاً به انگلیسی باقی بمانند؛ جایگزین یا ترجمه نشوند. فرمول، نام داده‌ها، عددها و رقم‌ها را عیناً حفظ کن و رقم‌ها را فارسی نکن. عنوان برند و عبارت‌های رابط کاربری را ترجمه کن. ترجمه‌ها را با همان شناسه‌های ثابت برگردان و هیچ ورودی را خلاصه، جابه‌جا یا حذف نکن. فقط یک JSON با همان کلیدهای ورودی و مقدارهای ترجمه‌شده برگردان."""

TECHNICAL_TERMS = [
    "hypothesis testing", "statistical inference", "null hypothesis", "alternative hypothesis",
    "confidence interval", "p-value", "effect size", "Type I error", "Type II error",
    "standard error", "sampling distribution", "minimum detectable effect", "practical significance",
    "false discovery rate", "family-wise error rate", "resampling distribution", "randomization inference",
    "equivalence test", "permutation test", "Fisher's exact test", "Fisher’s exact test",
    "McNemar's test", "McNemar’s test", "Welch's t-test", "Welch’s t-test",
    "Mann-Whitney", "Mann–Whitney", "Wilcoxon signed-rank", "chi-square test", "chi-square",
    "A/B test", "Cox model", "Kaplan-Meier", "Kaplan–Meier", "survival analysis",
    "odds ratio", "risk ratio", "hazard ratio", "confidence level", "test statistic",
    "F statistic", "t statistic", "z statistic", "degrees of freedom", "pooled standard deviation",
    "regression", "correlation", "ANOVA", "ANCOVA", "bootstrap", "permutation",
    "exchangeability", "estimand", "randomization", "censoring", "independence",
    "alpha", "beta", "power", "logistic regression", "linear regression",
    "Bonferroni", "Holm", "Benjamini-Hochberg", "Benjamini–Hochberg",
    "Cramer's V", "Cramer's V", "Hedges' g", "Cohen's d", "Phi coefficient",
    "intention-to-treat", "pseudo-replication", "pre-registration",
    "random intercept", "random slope", "mixed model", "mixed-effects model",
    "random-intercept", "random-slope", "intercept", "slope",
    "fixed effect", "random effect", "panel data", "cluster-robust", "robust standard errors",
    "generalized linear model", "linear model", "logistic model", "paired t-test",
    "paired t test", "independent-samples t-test", "signed-rank test", "Mann-Whitney U",
    "Games-Howell", "Tukey HSD", "Levene's test", "Shapiro-Wilk", "Anderson-Darling",
    "contingency table", "expected counts", "standardized residual", "residuals",
    "normality", "heteroskedasticity", "homoscedasticity", "central limit theorem",
    "difference-in-differences", "counterfactual", "intention to treat", "random assignment",
    "randomized experiment", "bootstrap percentile interval", "non-inferiority",
]

MANUAL = {
    "Inference Learning Studio": "استودیوی یادگیری آمار استنباطی",
    "Hypothesis Testing · Learning Studio": "آزمون فرض · استودیوی یادگیری",
    "Start here": "از اینجا شروع کنید",
    "Foundations": "مبانی",
    "Applied testing": "آزمون‌های کاربردی",
    "Advanced practice": "تمرین پیشرفته",
    "Reference": "منابع و مراجع",
    "Language": "زبان",
    "English": "English",
    "فارسی": "فارسی",
}


def localize_batch(values: list[str]) -> list[str]:
    ids = [f"S{index:02d}" for index in range(len(values))]
    saved_terms: dict[str, str] = {}
    protected_values = []
    for value in values:
        protected = value
        for term in sorted(TECHNICAL_TERMS, key=len, reverse=True):
            pattern = re.compile(r"(?<!\w)" + re.escape(term) + r"(?!\w)", re.IGNORECASE)
            def save(match: re.Match[str]) -> str:
                key = f"ZXQTERM{len(saved_terms):03d}QXZ"
                saved_terms[key] = match.group(0)
                return key
            protected = pattern.sub(save, protected)
        protected_values.append(protected)
    input_map = dict(zip(ids, protected_values))
    properties = {key: {"type": "string"} for key in ids}
    schema = {
        "type": "object",
        "properties": {"translations": {"type": "object", "properties": properties, "required": ids, "additionalProperties": False}},
        "required": ["translations"],
    }
    prompt = PERSIAN_PROMPT + "\n\n" + json.dumps(input_map, ensure_ascii=False)
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "think": False,
        "format": schema,
        "keep_alive": "30m",
        "options": {"temperature": 0.1, "num_ctx": 8192, "num_predict": 4096},
    }
    request = urllib.request.Request(
        "http://127.0.0.1:11434/api/generate",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=900) as response:
        result = json.loads(response.read())
    try:
        decoded = json.loads(result["response"])
    except json.JSONDecodeError:
        if len(values) > 1:
            middle = len(values) // 2
            return localize_batch(values[:middle]) + localize_batch(values[middle:])
        return localize_single(values[0], saved_terms)
    translations = decoded.get("translations", decoded)
    if set(translations) != set(ids):
        if len(values) > 1:
            middle = len(values) // 2
            return localize_batch(values[:middle]) + localize_batch(values[middle:])
        return localize_single(values[0], saved_terms)
    output = [translations[key] for key in ids]
    for key, term in saved_terms.items():
        output = [value.replace(key, term) for value in output]
    return output


def localize_single(value: str, saved_terms: dict[str, str]) -> list[str]:
    protected = value
    for term in sorted(TECHNICAL_TERMS, key=len, reverse=True):
        pattern = re.compile(r"(?<!\w)" + re.escape(term) + r"(?!\w)", re.IGNORECASE)
        def save(match: re.Match[str]) -> str:
            key = f"ZXQTERM{len(saved_terms):03d}QXZ"
            saved_terms[key] = match.group(0)
            return key
        protected = pattern.sub(save, protected)
    prompt = PERSIAN_PROMPT + "\n\nاین یک رشته است. فقط ترجمهٔ فارسی آن را بنویس و توضیح اضافه نده:\n" + protected
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "think": False,
        "keep_alive": "30m",
        "options": {"temperature": 0.1, "num_ctx": 8192, "num_predict": 4096},
    }
    request = urllib.request.Request(
        "http://127.0.0.1:11434/api/generate",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=900) as response:
        output = json.loads(response.read())["response"].strip()
    for key, term in saved_terms.items():
        output = output.replace(key, term)
    return [output]


def main() -> None:
    soup = BeautifulSoup(HTML.read_text(encoding="utf-8"), "html.parser")
    values: set[str] = set()
    for node in soup.body.descendants:
        if not isinstance(node, NavigableString):
            continue
        parent = node.parent
        if parent.name in {"script", "style", "math", "code", "select", "option"} or parent.find_parent(["script", "style", "math", "code", "select", "option"]):
            continue
        if "term" in (parent.get("class") or []) or parent.find_parent(class_="term"):
            continue
        value = str(node).strip()
        if value and re.search(r"[A-Za-z]", value):
            values.add(value)
    for element in soup.select("head title, meta[name='description'], [aria-label], [title], [placeholder], [alt]"):
        for attr in ("content", "aria-label", "title", "placeholder", "alt"):
            value = element.get(attr)
            if isinstance(value, str) and re.search(r"[A-Za-z]", value.strip()):
                values.add(value.strip())

    ordered = sorted(values, key=lambda value: len(value), reverse=True)
    translations: dict[str, str] = {}
    if OUTPUT.exists():
        try:
            translations = json.loads(OUTPUT.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            translations = {}
    allowed_keys = set(ordered) | set(MANUAL)
    translations = {key: value for key, value in translations.items() if key in allowed_keys}
    pending = [value for value in ordered if value not in translations]
    batches: list[list[str]] = []
    batch: list[str] = []
    batch_chars = 0
    for value in pending:
        if batch and (len(batch) >= BATCH_SIZE or batch_chars + len(value) > MAX_BATCH_CHARS):
            batches.append(batch)
            batch = []
            batch_chars = 0
        batch.append(value)
        batch_chars += len(value)
    if batch:
        batches.append(batch)
    total = len(pending)
    completed = 0
    for index, batch in enumerate(batches, 1):
        translated = localize_batch(batch)
        translations.update(zip(batch, translated))
        translations.update(MANUAL)
        OUTPUT.write_text(json.dumps(translations, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        completed += len(batch)
        print(f"Translated {completed} of {total} site strings ({index}/{len(batches)} batches).", flush=True)
    translations.update(MANUAL)
    OUTPUT.write_text(json.dumps(translations, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {len(translations)} static Persian strings to {OUTPUT}.")


if __name__ == "__main__":
    main()
