#!/usr/bin/env python3
"""Validate the concept-first Learning Studio teaching interface."""

from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    path = ROOT / "course.html"
    if not path.exists():
        print("Missing course.html")
        return 1

    source = path.read_text(encoding="utf-8")
    soup = BeautifulSoup(source, "html.parser")
    errors: list[str] = []
    ids = {tag["id"] for tag in soup.find_all(attrs={"id": True})}
    pages = soup.select("article.course_page")
    lessons = [page for page in pages if page.get("id", "").startswith("lesson_")]

    expected_counts = {
        "teaching pages": (len(pages), 20),
        "lesson pages": (len(lessons), 15),
        "visual models": (len(soup.select(".visual_model")), 15),
        "misconception cards": (len(soup.select(".misconception")), 30),
        "scenario modules": (len(soup.select(".scenario")), 15),
        "progress controls": (len(soup.select("[data-progress]")), 15),
        "course level navigation groups": (len(soup.select("details.nav_level")), 3),
        "lesson reading phases": (len(soup.select(".lesson_phase")), 45),
    }
    for label, (actual, expected) in expected_counts.items():
        if actual != expected:
            errors.append(f"expected {expected} {label}, found {actual}")

    forbidden_elements = {
        "code blocks": "pre",
        "code elements": "code",
        "images or notebook plots": "img",
        "solution disclosures": "details:not(.nav_level)",
    }
    for label, selector in forbidden_elements.items():
        count = len(soup.select(selector))
        if count:
            errors.append(f"found {count} forbidden {label}")

    lower_source = source.lower()
    for phrase in [
        "implementation reference",
        "supporting notebook",
        "<summary>solution",
        "data:image/",
        "_files/lesson_",
    ]:
        if phrase in lower_source:
            errors.append(f"found forbidden implementation artifact: {phrase}")

    for lesson in lessons:
        worked = next((section for section in lesson.select("section.module")
                       if section.find("h3") and section.find("h3").get_text(strip=True) == "Worked example and interpretation"), None)
        if worked is None or len(worked.get_text(" ", strip=True).split()) < 120:
            errors.append(f"{lesson.get('id')} is missing a substantive worked interpretation")
        if [item.get_text(" ", strip=True) for item in lesson.select(".phase_header h2")] != [
            "Get oriented", "Build understanding", "Apply and reflect"
        ]:
            errors.append(f"{lesson.get('id')} has an incomplete reading sequence")
        if len(lesson.select("section.module")) < 5:
            errors.append(f"{lesson.get('id')} has fewer than five teaching modules")
        if len(lesson.get_text(" ", strip=True)) < 1200:
            errors.append(f"{lesson.get('id')} has too little teaching content")

    for link in soup.select('a[href^="#"]'):
        target = link.get("href", "")[1:]
        if target and target not in ids:
            errors.append(f"missing internal HTML target #{target}")

    if errors:
        print("Teaching HTML validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "Validated course.html: 20 teaching pages, 15 lessons, "
        "15 visual models, 30 misconception cards, 15 scenarios, and no code, solutions, outputs, or plots."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
