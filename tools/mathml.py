"""Render the course's limited LaTeX vocabulary as standalone MathML."""

from __future__ import annotations

from xml.etree import ElementTree as ET


SYMBOLS = {
    "alpha": "α", "beta": "β", "chi": "χ", "Delta": "Δ",
    "epsilon": "ϵ", "varepsilon": "ε", "mu": "μ", "rho": "ρ", "tau": "τ",
    "cdots": "⋯", "times": "×", "sum": "∑", "ne": "≠",
    "ge": "≥", "le": "≤", "pm": "±", "infty": "∞",
}


def element(tag: str, value: str | None = None, **attributes: str) -> ET.Element:
    node = ET.Element(tag, attributes)
    if value is not None:
        node.text = value
    return node


def row(parts: list[ET.Element]) -> ET.Element:
    if len(parts) == 1:
        return parts[0]
    node = element("mrow")
    node.extend(parts)
    return node


class LatexParser:
    def __init__(self, source: str):
        self.source = source.strip()
        self.position = 0

    def parse(self) -> ET.Element:
        result = self.sequence()
        if self.position != len(self.source):
            raise ValueError(f"Unparsed LaTeX: {self.source[self.position:]!r}")
        return result

    def sequence(self, close: str | None = None) -> ET.Element:
        parts: list[ET.Element] = []
        while self.position < len(self.source):
            char = self.source[self.position]
            if char.isspace():
                self.position += 1
                continue
            if char == "}":
                if close != "}":
                    raise ValueError(f"Unexpected closing brace in {self.source!r}")
                self.position += 1
                return row(parts)
            if char in "_^":
                if not parts:
                    raise ValueError(f"Script without base in {self.source!r}")
                self.position += 1
                script = self.atom()
                base = parts.pop()
                if base.tag == "msub" and char == "^":
                    combined = element("msubsup")
                    combined.extend([*base, script])
                    parts.append(combined)
                elif base.tag == "msup" and char == "_":
                    combined = element("msubsup")
                    combined.extend([base[0], script, base[1]])
                    parts.append(combined)
                else:
                    wrapper = element("msub" if char == "_" else "msup")
                    wrapper.extend([base, script])
                    parts.append(wrapper)
                continue
            parts.append(self.atom())
        if close:
            raise ValueError(f"Unclosed brace in {self.source!r}")
        return row(parts)

    def group(self) -> ET.Element:
        if self.position >= len(self.source) or self.source[self.position] != "{":
            raise ValueError(f"Expected braced argument in {self.source!r}")
        self.position += 1
        return self.sequence(close="}")

    def text_group(self) -> str:
        if self.position >= len(self.source) or self.source[self.position] != "{":
            raise ValueError(f"Expected text argument in {self.source!r}")
        self.position += 1
        start = self.position
        depth = 1
        while self.position < len(self.source) and depth:
            if self.source[self.position] == "{":
                depth += 1
            elif self.source[self.position] == "}":
                depth -= 1
            self.position += 1
        if depth:
            raise ValueError(f"Unclosed text argument in {self.source!r}")
        return self.source[start:self.position - 1]

    def atom(self) -> ET.Element:
        char = self.source[self.position]
        if char == "{":
            return self.group()
        if char == "\\":
            self.position += 1
            start = self.position
            while self.position < len(self.source) and self.source[self.position].isalpha():
                self.position += 1
            command = self.source[start:self.position]
            if command in SYMBOLS:
                return element("mo" if command in {"cdots", "times", "sum", "ne", "ge", "le", "pm"} else "mi", SYMBOLS[command])
            if command == "frac":
                node = element("mfrac")
                node.extend([self.group(), self.group()])
                return node
            if command == "sqrt":
                node = element("msqrt")
                node.append(self.group())
                return node
            if command == "bar":
                node = element("mover", accent="true")
                node.extend([self.group(), element("mo", "¯")])
                return node
            if command == "text":
                return element("mtext", self.text_group())
            if command in {"qquad", "quad"}:
                return element("mspace", width="1.5em" if command == "qquad" else "1em")
            if command in {"left", "right"}:
                return self.atom()
            raise ValueError(f"Unsupported LaTeX command \\{command} in {self.source!r}")
        if char.isdigit() or (char == "." and self.position + 1 < len(self.source) and self.source[self.position + 1].isdigit()):
            start = self.position
            self.position += 1
            while self.position < len(self.source) and (self.source[self.position].isdigit() or self.source[self.position] == "."):
                self.position += 1
            return element("mn", self.source[start:self.position])
        self.position += 1
        if char.isalpha():
            return element("mi", char)
        if char in "+−-=<>/(),.[]:;":
            return element("mo", char)
        raise ValueError(f"Unsupported LaTeX character {char!r} in {self.source!r}")


def render_math(expression: str, display: bool) -> str:
    math = element("math", xmlns="http://www.w3.org/1998/Math/MathML", display="block" if display else "inline")
    semantics = element("semantics")
    semantics.append(LatexParser(expression).parse())
    semantics.append(element("annotation", expression.strip(), encoding="application/x-tex"))
    math.append(semantics)
    output = ET.tostring(math, encoding="unicode", method="xml")
    return f'<div class="math_display">{output}</div>\n' if display else output
