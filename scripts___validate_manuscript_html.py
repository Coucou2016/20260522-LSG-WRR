#!/usr/bin/env python3
"""Lightweight self-containment + structure check for manuscript.html."""
from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path

HTML = Path(__file__).resolve().parents[1] / "docs" / "paper" / "manuscript.html"
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr"}


class Balancer(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[str] = []
        self.errors: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack:
            self.errors.append(f"stray </{tag}>")
            return
        if self.stack[-1] == tag:
            self.stack.pop()
        elif tag in self.stack:
            while self.stack and self.stack[-1] != tag:
                self.errors.append(f"implicitly closed <{self.stack[-1]}> before </{tag}>")
                self.stack.pop()
            if self.stack:
                self.stack.pop()
        else:
            self.errors.append(f"unmatched </{tag}>")


def main() -> int:
    text = HTML.read_text(encoding="utf-8")
    errors: list[str] = []

    if not text.lstrip().startswith("<!DOCTYPE html>"):
        errors.append("missing DOCTYPE")
    for tag in ("<html", "<head", "<style", "<body", "</html>"):
        if tag not in text:
            errors.append(f"missing {tag}")

    if re.search(r'<link[^>]+href=["\']https?://', text, re.I):
        errors.append("external CSS link")
    if re.search(r'<script[^>]+src=["\']https?://', text, re.I):
        errors.append("external JS script")
    if re.search(r'src=["\']https?://', text, re.I):
        errors.append("http(s) src")
    if re.search(r'src=["\']file://', text, re.I):
        errors.append("file:// src")
    for m in re.finditer(r'<img\b[^>]*>', text, re.I):
        tag = m.group(0)
        if ('src="' in tag or "src='" in tag) and not re.search(r'src=["\']data:', tag, re.I):
            errors.append(f"non-data img: {tag[:100]}")

    required = [
        "capacity-controlled negative result",
        "6.8 Capacity-matched controls",
        "Table 6. Chowilla equal-capacity control",
        "Table 7. Burnett equal-capacity control",
        "Table 8. Chowilla H-LSG inducing-point",
        "force_n_modes",
        "does not survive",
    ]
    for r in required:
        if r not in text:
            errors.append(f"missing content: {r}")

    b = Balancer()
    b.feed(text)
    if b.stack:
        errors.append(f"unclosed tags at EOF: {b.stack[-8:]}")
    errors.extend(b.errors[:20])

    n_svg = len(re.findall(r"<svg\b", text, re.I))
    n_table = len(re.findall(r"<table\b", text, re.I))
    print(f"html_bytes={HTML.stat().st_size}")
    print(f"inline_svg_count={n_svg}")
    print(f"table_count={n_table}")

    if errors:
        print("FAIL")
        for e in errors:
            print(" -", e)
        return 1
    print("PASS self-containment, required-content, and tag-balance checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
