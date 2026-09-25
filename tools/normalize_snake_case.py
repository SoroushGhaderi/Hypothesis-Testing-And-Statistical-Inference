#!/usr/bin/env python3
"""Rename every course path to lowercase snake_case and repair references."""

from __future__ import annotations

import re
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".md", ".py", ".ipynb", ".txt", ".html", ".css", ".js"}


def snake_case(name: str) -> str:
    path = Path(name)
    suffix = "".join(path.suffixes).lower()
    stem = name[:-len(suffix)] if suffix else name
    stem = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", stem)
    stem = re.sub(r"[^A-Za-z0-9]+", "_", stem)
    stem = re.sub(r"_+", "_", stem).strip("_").lower()
    return stem + suffix


def replace_references(name_map: dict[str, str]) -> None:
    replacements = sorted(name_map.items(), key=lambda item: len(item[0]), reverse=True)
    extra = [
        ("level_*", "level_*"),
        ("lesson_*", "lesson_*"),
        ("lesson_{", "lesson_{"),
        ("*lesson_", "*lesson_"),
        ("lesson_(", "lesson_("),
    ]
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8")
        updated = text
        for old, new in replacements + extra:
            updated = updated.replace(old, new)
        if updated != text:
            path.write_text(updated, encoding="utf-8")


def safe_rename(source: Path, target: Path) -> None:
    if source == target:
        return
    temporary = source.with_name(f".__rename_{uuid.uuid4().hex}")
    source.rename(temporary)
    temporary.rename(target)


def main() -> None:
    paths = [path for path in ROOT.rglob("*") if not any(part.startswith(".") for part in path.relative_to(ROOT).parts)]
    name_map = {path.name: snake_case(path.name) for path in paths if path.name != snake_case(path.name)}
    name_map[ROOT.name] = snake_case(ROOT.name)
    replace_references(name_map)

    for path in sorted(paths, key=lambda item: len(item.parts), reverse=True):
        new_name = snake_case(path.name)
        if new_name != path.name:
            safe_rename(path, path.with_name(new_name))

    new_root = ROOT.with_name(snake_case(ROOT.name))
    safe_rename(ROOT, new_root)
    print(f"Normalized course paths under {new_root}")


if __name__ == "__main__":
    main()
